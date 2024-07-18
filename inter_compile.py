import subprocess
import os
import openai
import shutil
import time
import re
import pandas as pd
import sys

def run_compile(script_path, tb_file, output_text_file, header_file):
    """Run the Python compilation script and capture the output in a text file after modifying tb.cpp to include the correct header."""
    # Modify tb.cpp to include the correct header file
    with open(tb_file, 'r') as file:
        tb_content = file.readlines()
    
    # Change the include line to the current header file
    for i, line in enumerate(tb_content):
        if line.strip().startswith('#include'):
            tb_content[i] = f'#include "{header_file}"\n'
            break

    with open(tb_file, 'w') as file:
        file.writelines(tb_content)

    # Run compilation script
    compile_command = f"python3 {script_path} {tb_file}"
    subprocess.run(compile_command, shell=True, check=True)

    # Copy the log file to the output text file, assuming log location known
    log_file_path = "/.../catapult.log"
    if os.path.exists(log_file_path):
        shutil.copyfile(log_file_path, output_text_file)
    else:
        raise FileNotFoundError(f"Expected compile report file not found: {log_file_path}")


def extract_errors(text_file):
    """Extract error messages from the text output file."""
    error_lines = []
    with open(text_file, 'r') as file:
        for line in file:
            if any(error_word in line for error_word in ['Error', 'errors', 'Failed']):
                error_lines.append(line.strip())
    return error_lines

def get_template(emb_script_path, library_dir, error_message):
    """Run the emb.py script to get the closest correct template based on the error message."""
    template_command = f"python3 {emb_script_path} '{error_message}' {library_dir}"
    result = subprocess.run(template_command, shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        output = result.stdout.strip().split(',')
        if len(output) >= 2:
            template_file_name = output[0].strip()
            highest_similarity = float(output[1].strip())
            template_file_path = os.path.join(library_dir, template_file_name)
            try:
                with open(template_file_path, 'r') as file:
                    template_content = file.read()
                print(f"Debug: Template content for {template_file_name} is {'empty' if not template_content else 'not empty'}")
                return template_file_name, template_content, highest_similarity
            except FileNotFoundError:
                print(f"File not found: {template_file_path}")
                return "", "", 0.0
    return "", "", 0.0


def consult_gpt(errors, code_content, prompt_file, template_content=""):
    """Consult GPT for code correction suggestions based on provided errors and code."""
    message_content = "A comprehensive High-Level Synthesis (HLS) flow takes C++ as the design input and targets hardware implementations. Some of the C++ codes are prohibited in HLS design because HLS tools don't support recursion. As a HLS professional programmer, here are some compilation errors while running C++ code in the Siemens Catapult HLS tool:\n" + "\n".join(errors)
    message_content += "\nThe full C++ code for HLS is as follows:\n" + code_content
    if template_content:
        message_content += "\nThe HLS template for reference and correction is as follows:\n" + template_content
    message_content += "\nThoroughly review and ensure that all modifications do not affect the functionality of the original C++ code. Please provide a complete corrected HLS-compatible C++ code that compiles successfully. Please be sure to provide a complete code. Don't add a main or test function in the modified C++ code."


    # Save the prompt to a file
    with open(prompt_file, 'w') as f:
        f.write(message_content)

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant for fixing HLS cpp code."},
            {"role": "user", "content": message_content}
        ]
    )
    return response.choices[0].message.content

def extract_code_from_gpt_output(gpt_output_file):
    """Extracts C++ code from the GPT output file that is between triple backticks labeled with cpp."""
    code_content = ""
    capture = False
    with open(gpt_output_file, 'r') as file:
        for line in file:
            if line.strip() == '```cpp':
                capture = True
                continue
            elif line.strip() == '```':
                if capture:
                    break
                continue
            if capture:
                code_content += line
    return code_content

def count_tokens(filename):
    with open(filename, 'r') as file:
        content = file.read()
    
    tokens = re.findall(r'\w+|[^\w\s]', content)
    return len(tokens)

def calculate_delta_loc(main_file, correct_file):
    def extract_code_lines(file_path):
        code_lines = []
        with open(file_path, 'r') as file:
            for line in file:
                
                stripped_line = line.strip()
                
                if stripped_line and not stripped_line.startswith("//"):
                    
                    code_line = stripped_line.split("//")[0].strip()
                    code_lines.append(code_line)
        return code_lines


    main_lines = extract_code_lines(main_file)
    correct_lines = extract_code_lines(correct_file)

    main_set = set(main_lines)
    correct_set = set(correct_lines)

    different_lines = main_set.symmetric_difference(correct_set)
    return len(different_lines)

# def find_top_module(verilog_path):
#     """ Extracts the last defined module from a Verilog file. """
#     with open(verilog_path, 'r') as file:
#         content = file.read()
    
#     # Regex to find all module definitions
#     module_defs = re.findall(r'\bmodule\s+(\w+)', content)
#     return module_defs[-1] if module_defs else None

def reorder_modules(verilog_file_path):
    with open(verilog_file_path, 'r') as file:
        content = file.read()

    module_pattern = re.compile(r'//\s*-*\s*Design Unit:.*?\nmodule\s+.*?endmodule', re.DOTALL)
    modules = module_pattern.findall(content)

    if len(modules) < 2:
        print("Not enough modules to reorder. Need at least two modules.")
        return
    new_order_modules = [modules[-1]] + modules[:-1]
    new_content = '\n\n'.join(new_order_modules)
    with open(verilog_file_path, 'w') as file:
        file.write(new_content)
    print("Modules have been reordered successfully.")

def run_design_compiler(iteration, base_dir):
    def match_area(begin, end, string):
        pattern = re.compile(re.escape(begin) + r'(.+?)' + re.escape(end))
        matches = pattern.findall(string)
        return matches[0].strip() if matches else None
    excel_info = [['Iteration', 'Combinational area', 'Buf/Inv area', 'Noncombinational area', 'Total cell area', 'Data arrival time', 'Slack (VIOLATED)', 'Slack (MET)', 'Cell Internal Power', 'Net Switching Power', 'Cell Leakage Power', 'Total Dynamic Power']]
    rtl_path = f"{base_dir}/Catapult_{iteration}/process_top.v1/rtl.v"
    if iteration == 0:
        rtl_path = rtl_path.replace("Catapult_0", "Catapult")  # Correct path for first iteration
    reorder_modules(rtl_path)
    run_tcl_path = f"{base_dir}/design_compiler_{iteration}.tcl"
    report_path = f"{base_dir}/dc_report_{iteration}.txt"
    report_csv = f"{base_dir}/dc_report_{iteration}.csv"
    with open(run_tcl_path, 'w') as f:
        f.write('set target_library ./NangateOpenCellLibrary_typical.db\n')
        f.write('set link_library ./NangateOpenCellLibrary_typical.db\n')
        f.write('read_verilog ' + rtl_path + '\n')
        #f.write(f'current_design {top_module}\n')
        f.write('suppress_message UID-401\n')
        f.write('check_design\n')
        f.write('link\n')
        f.write('set timing_enable_through_paths true\n')
        f.write('set timing_through_path_max_segments 10\n')
        f.write('create_clock clk -period 2500\n')
        f.write('link\n')
        f.write('compile_ultra\n')
        f.write('write -f verilog -hierarchy -output ' + base_dir + '/netlist.v\n')
        f.write('report_area\n')
        f.write('report_timing -delay max\n')
        f.write('report_power\n')
        f.write('quit\n')

    command = '/.../synopsys/syn/J-2014.09-SP3/bin/dc_shell -f ' + run_tcl_path
    os.system(command + ' | tee ' + report_path)

    with open(report_path, 'r') as f:
        report = f.read()

    info = [
        iteration + 1,
        match_area('Combinational area:', '\n', report),
        match_area('Buf/Inv area:', '\n', report),
        match_area('Noncombinational area:', '\n', report),
        match_area('Total cell area:', '\n', report),
        match_area('data arrival time', '\n', report),
        match_area('slack (VIOLATED)', '\n', report),
        match_area('slack (MET)', '\n', report),
        match_area('Cell Internal Power  =', '\n', report),
        match_area('Net Switching Power  =', '\n', report),
        match_area('Cell Leakage Power     =', '\n', report),
        match_area('Total Dynamic Power    =', '\n', report)
    ]
    excel_info.append(info)
    pd.DataFrame(excel_info).to_csv(report_csv)
    print(f"Design Compiler synthesis completed for iteration {iteration}. Report saved to {report_path}")


def main():
    iteration_limit = 2
    base_dir = "/.../E3_BFS"
    compile_script = os.path.join(base_dir, "compile.py")
    emb_script_path = os.path.join(base_dir, "emb.py")
    library_dir = "/.../library"
    previous_errors = []
    total_tokens = 0

    # Start with the initial tb file
    initial_tb_file = os.path.join(base_dir, "tb.cpp")  
    tb_file = initial_tb_file
    main_file = os.path.join(base_dir, "main.cpp")
    token_counts = []  
    total_tokens = 0  

    for iteration in range(iteration_limit):
        # Define the header file for the current iteration
        if iteration == 0:
            header_file = "main.cpp"
        else:
            header_file = f"main_c{iteration + 1}.cpp"
        output_text_file = os.path.join(base_dir, f"text{iteration + 1}.txt")
        prompt_file = os.path.join(base_dir, f"prompt{iteration + 1}.txt")
        gpt_output_file = os.path.join(base_dir, f"GPT{iteration + 1}.txt")

        # Run compilation with the current header file
        run_compile(compile_script, tb_file, output_text_file, header_file)
        errors = extract_errors(output_text_file)

        if not errors:
            print(f"Success: Code compiled without errors after {iteration + 1} iterations.")
            correct_file_name = os.path.basename(main_file).replace('.cpp', '_correct.cpp')
            correct_file_path = os.path.join(base_dir, correct_file_name)
            # Copy and rename the main file to indicate it is the correct version
            shutil.copy(main_file, correct_file_path)
            print(f"Correct code output as {correct_file_name}")
            delta_loc = calculate_delta_loc(main_file, correct_file_path)
            with open(output_text_file, 'a') as f:
                f.write(f"\nδLOC (Difference in Lines of Code): {delta_loc}\n")
            run_design_compiler(iteration, base_dir)
            break

        if iteration > 0 and errors == previous_errors:
            template_file_name, template_content = "", ""
        else:
            error_message = ' '.join(errors)
            template_file_name, template_content, highest_similarity = get_template(emb_script_path, library_dir, error_message)
            print(f"Template Name: {template_file_name}, Similarity: {highest_similarity}")

        code_content = open(main_file).read()
        fixed_code = consult_gpt(errors, code_content, prompt_file, template_content)
        print(f"Consulting GPT with Template: {template_content[:100]}")

        with open(gpt_output_file, 'w') as file:
            file.write(fixed_code)

        # Extract the C++ code from the GPT output file
        full_code = extract_code_from_gpt_output(gpt_output_file)

        # Define new main file for the next iteration
        new_main_file = os.path.join(base_dir, f"main_c{iteration + 2}.cpp")
        with open(new_main_file, 'w') as file:
            file.write(full_code)

        # Update main_file to the new main file for the next iteration
        main_file = new_main_file
        previous_errors = errors

        # Print template information
        if template_file_name:
            print(f"Iteration {iteration + 1}: Selected template '{template_file_name}' with '{highest_similarity}' error similarity.")
            print(f"Template content:\n{template_content}\n")
        
        prompt_tokens = count_tokens(prompt_file)
        token_counts.append(prompt_tokens)
        total_tokens += prompt_tokens

        with open(output_text_file, 'a') as f:
            f.write(f"\nToken count for this iteration: {prompt_tokens}\n")

    # Determine the path for the last text output file
    last_text_file = os.path.join(base_dir, f"text{iteration + 1}.txt")
    re_file_path = os.path.join(base_dir, "re.txt")

    # Analyze the last text file and write the result to re.txt
    compilation_status = "Compilation failed"
    simulation_status = "Simulation failed"

    if os.path.exists(last_text_file):
        with open(last_text_file, 'r') as file:
            content = file.read()
            if "go libraries" in content:
                compilation_status = "Compilation successfully"
            if "# Saving project file" in content:
                simulation_status = "Simulation successfully"

    # Write the status to the re.txt file
    with open(re_file_path, 'w') as re_file:
        re_file.write(f"{compilation_status}, {simulation_status}.\n")

    with open(output_text_file, 'a') as f:
        for i, tokens in enumerate(token_counts, 1):
            f.write(f"Token count for iteration {i}: {tokens}\n")
        f.write(f"Total token count across all iterations: {total_tokens}\n")

    print("Completed all iterations.")


if __name__ == "__main__":
    main()
