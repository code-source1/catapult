#!/usr/bin/env python3
import os
import shutil
import subprocess
import time
import re
import math
import sys
import pandas as pd  # Used to save the DC report as a CSV file

# Base directory (please ensure this script is located at /nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/dnn)
BASE_DIR = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/dnn"
SOURCE_FILES = ["1.dat", "a.dat", "w.dat", "kernel.cpp", "kernel_testbench.cpp", "compile.py", "NangateOpenCellLibrary_typical.db"]

def print_source_files(round_folder):
    """
    Read and print the contents of 1.dat, a.dat, and w.dat in the specified round_folder.
    """
    files_to_print = ["1.dat", "a.dat", "w.dat"]
    for filename in files_to_print:
        file_path = os.path.join(BASE_DIR, round_folder, filename)
        if os.path.exists(file_path):
            print(f"\n--- Contents of {filename} in {round_folder}: ---")
            with open(file_path, "r") as f:
                content = f.read()
                print(content)
        else:
            print(f"File {filename} does not exist in {round_folder}.")

def clean_round_folder(round_folder):
    folder_path = os.path.join(BASE_DIR, round_folder)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

def copy_files_to_round(round_folder):
    dest_dir = os.path.join(BASE_DIR, round_folder)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for filename in SOURCE_FILES:
        src = os.path.join(BASE_DIR, filename)
        dst = os.path.join(dest_dir, filename)
        shutil.copy(src, dst)

def update_compile_py(round_folder):
    """
    Modify all occurrences of BASE_DIR in the compile.py file under the specified round_folder,
    replacing it with the new directory (for example, replacing BASE_DIR with BASE_DIR/round_folder).
    """
    compile_py_path = os.path.join(BASE_DIR, round_folder, "compile.py")
    with open(compile_py_path, "r") as f:
        content = f.read()
    new_base = os.path.join(BASE_DIR, round_folder)
    content = content.replace(BASE_DIR, new_base)
    with open(compile_py_path, "w") as f:
        f.write(content)

def update_kernel_bitwidth(round_folder, new_int, new_frac):
    """
    In the kernel.cpp and kernel_testbench.cpp files under the specified round_folder,
    modify the type definition lines, replacing the original "ac_fixed<..., ... , true>" with
    "ac_fixed<new_total, new_int, true>", where new_total = new_int + new_frac.
    For example, if new_int=10 and new_frac=7, it should be replaced with ac_fixed<17, 10, true>.
    """
    new_total = new_int + new_frac
    pattern = r"(typedef\s+ac_fixed<)\s*\d+\s*,\s*\d+\s*,\s*true\s*>(\s*DataType\s*;)"
    replacement = r"\g<1>{}, {}, true>\g<2>".format(new_total, new_int)
    for filename in ["kernel.cpp", "kernel_testbench.cpp"]:
        file_path = os.path.join(BASE_DIR, round_folder, filename)
        with open(file_path, "r") as f:
            content = f.read()
        new_content = re.sub(pattern, replacement, content)
        with open(file_path, "w") as f:
            f.write(new_content)

def update_testbench_output_dir(round_folder):
    """
    Modify the hardcoded OUTPUT_DIR constant in kernel_testbench.cpp under the specified round_folder,
    replacing it with the p directory under the current round_folder, i.e.:
    const string OUTPUT_DIR = "<BASE_DIR>/<round_folder>/p";
    """
    testbench_path = os.path.join(BASE_DIR, round_folder, "kernel_testbench.cpp")
    with open(testbench_path, "r") as f:
        content = f.read()
    new_output = os.path.join(BASE_DIR, round_folder, "p").replace(os.sep, "/")
    pattern = r'(const\s+string\s+OUTPUT_DIR\s*=\s*")[^"]*(";)'
    replacement = r'\1' + new_output + r'\2'
    new_content = re.sub(pattern, replacement, content)
    with open(testbench_path, "w") as f:
        f.write(new_content)

def update_kernel_paths(round_folder):
    """
    In the kernel.cpp and kernel_testbench.cpp files under the specified round_folder,
    replace the hardcoded BASE_DIR path with BASE_DIR/<round_folder>.
    
    For example, if the original file contains:
      const string INPUT_FILE_PATH = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/dnn/1.dat";
    it should be replaced with:
      const string INPUT_FILE_PATH = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/dnn/dnn1/1.dat";
      
    If the file already has:
      const string OUTPUT_DIR = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/dnn/dnn1/p";
    then it should not be replaced again (i.e., avoid having .../dnn1/dnn1/p).
    """
    new_base = os.path.join(BASE_DIR, round_folder).replace(os.sep, "/")
    pattern = r'(")' + re.escape(BASE_DIR) + r'(?!/' + re.escape(round_folder) + r')(/[^"]*)(")'
    
    def repl(match):
        return match.group(1) + new_base + match.group(2) + match.group(3)
    
    for filename in ["kernel.cpp", "kernel_testbench.cpp"]:
        file_path = os.path.join(BASE_DIR, round_folder, filename)
        with open(file_path, "r") as f:
            content = f.read()
        new_content = re.sub(pattern, repl, content)
        with open(file_path, "w") as f:
            f.write(new_content)
    print(f"Updated kernel paths in {round_folder}.")

def run_compile():
    """
    Change directory to the current working directory and run the compile.py script 
    (this script internally calls Catapult). Reads the console output in real time and sets a timeout (e.g., 70 seconds);
    if the timeout is exceeded or if the output contains "# > quit" or "# > quit -force", forcefully kill the process and return all output.
    
    Note: This function no longer accepts a round_folder parameter; it is assumed that the current directory has already been changed accordingly.
    """
    cwd = os.getcwd()
    cmd = "python3 compile.py"
    print(f"Running compile in {cwd} with command: {cmd}")
    proc = subprocess.Popen(cmd, cwd=cwd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)
    output = ""
    timeout = 70  # Timeout in seconds
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            print("Timeout exceeded, forcing process termination.")
            proc.kill()
            break
        line = proc.stdout.readline()
        if line:
            output += line
            print(line, end="")  # Print output in real time
            if "# > quit -force" in line or "# > quit" in line:
                print("Quit detected, forcing process termination.")
                proc.kill()
                break
        else:
            time.sleep(0.5)
        if proc.poll() is not None:
            break
    remaining = proc.stdout.read()
    output += remaining
    return output

def check_compile_success(compile_output):
    """
    Check whether p/act_3.txt exists in the current working directory,
    or if the console output contains "# > quit". If so, the synthesis for the current round is considered complete and ready for the next round.
    """
    p_dir = os.path.join(os.getcwd(), "p")
    act_file = os.path.join(p_dir, "act_3.txt")
    if os.path.exists(act_file):
        return True
    if "# > quit -force" in compile_output or "# > quit" in compile_output:
        return True
    return False

def parse_all_txt_files(round_folder):
    """
    Traverse all .txt files in the BASE_DIR/round_folder/p directory,
    extract all numbers (floats) from the files, and return a list of floats.
    """
    p_dir = os.path.join(BASE_DIR, round_folder, "p")
    all_values = []
    if not os.path.isdir(p_dir):
        print(f"Directory {p_dir} does not exist.")
        return all_values
    for filename in os.listdir(p_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(p_dir, filename)
            with open(file_path, "r") as f:
                content = f.read()
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", content)
            all_values.extend([float(x) for x in nums])
    return all_values

def parse_act_file(round_folder):
    """
    Only parse the act_3.txt file in the BASE_DIR/round_folder/p directory,
    extract all numbers (floats) from it, and return a list of floats.
    """
    p_dir = os.path.join(BASE_DIR, round_folder, "p")
    act_file = os.path.join(p_dir, "act_3.txt")
    if not os.path.exists(act_file):
        print(f"act_3.txt does not exist in {p_dir}")
        return []
    with open(act_file, "r") as f:
        content = f.read()
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", content)
    return [float(x) for x in nums]

def compute_average_relative_error(reference, current):
    """
    Compare the numbers in the reference and current lists, and return the average relative error as a percentage.
    If a number in reference is 0, use 1 as the denominator.
    """
    if len(reference) == 0 or len(reference) != len(current):
        return None
    errors = []
    for r, c in zip(reference, current):
        if r == 0:
            err = abs(c - r)
        else:
            err = abs(c - r) / abs(r)
        errors.append(err)
    return sum(errors) / len(errors) * 100

def determine_integer_bitwidth(baseline):
    """
    Determine the integer bitwidth (m) for signed numbers based on the maximum absolute value of all data in baseline.
    For signed numbers, the range is -2^(m-1) to 2^(m-1)-1,
    so m = ceil(log2(abs_max)) + 1.
    """
    if not baseline:
        return 8  
    abs_max = max(abs(x) for x in baseline)
    if abs_max < 1:
        return 1
    return math.ceil(math.log2(abs_max)) + 2

# --- The following functions run_design_compiler and reorder_modules are related to Design Compiler synthesis ---
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

    excel_info = [['Iteration', 'Combinational area', 'Buf/Inv area', 'Noncombinational area',
                   'Total cell area', 'Data arrival time', 'Slack (VIOLATED)', 'Slack (MET)',
                   'Cell Internal Power', 'Net Switching Power', 'Cell Leakage Power', 'Total Dynamic Power']]
    rtl_path = os.path.join(base_dir, f"dnn{iteration}", "Catapult", "dnn.v1", "rtl.v")
    # reorder_modules(rtl_path)
    run_tcl_path = os.path.join(base_dir, f"design_compiler_{iteration}.tcl")
    report_path = os.path.join(base_dir, f"dc_report_{iteration}.txt")
    with open(run_tcl_path, 'w') as f:
        f.write('set target_library ./NangateOpenCellLibrary_typical.db\n')
        f.write('set link_library ./NangateOpenCellLibrary_typical.db\n')
        f.write('read_verilog ' + rtl_path + '\n')
        f.write('suppress_message UID-401\n')
        f.write('check_design\n')
        f.write('link\n')
        f.write('set timing_enable_through_paths true\n')
        f.write('set timing_through_path_max_segments 10\n')
        f.write('create_clock clk -period 1000\n')
        f.write('link\n')
        f.write('compile_ultra\n')
        f.write('write -f verilog -hierarchy -output ' + base_dir + '/netlist.v\n')
        f.write('report_area\n')
        f.write('report_timing -delay max\n')
        f.write('report_power\n')
        f.write('quit\n')
    command = '/usr/local/tools/synopsys/syn/J-2014.09-SP3/bin/dc_shell -f ' + run_tcl_path
    os.system(command + ' | tee ' + report_path)
    with open(report_path, 'r') as f:
        report = f.read()
    info = [
        iteration,
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
    print(f"Design Compiler synthesis completed for iteration {iteration}. Report saved to {report_path}")
    total_cell_area = info[4]
    data_arrival_time = info[5]
    total_dynamic_power = info[11]
    return total_cell_area, total_dynamic_power, data_arrival_time

# --- Main process: Decide whether to run the reference design or a specific round based on the command line argument ---
def main():
    if len(sys.argv) < 2:
        print("Usage: {} <round>".format(sys.argv[0]))
        print("  round: 'c' means reference design; or provide a round number (e.g., 1,2,3...)")
        sys.exit(1)
    round_id = sys.argv[1]
    
    if round_id == "c":
        # Process reference design
        ref_folder = "c"
        ref_folder_path = os.path.join(BASE_DIR, ref_folder)
        if not os.path.exists(ref_folder_path):
            print("Reference folder 'c' does not exist, creating it and synthesizing the reference design.")
            clean_round_folder(ref_folder)
            copy_files_to_round(ref_folder)
            update_compile_py(ref_folder)
            update_kernel_paths(ref_folder)
            update_testbench_output_dir(ref_folder)
        # Change to the reference design directory and run compile.py
        os.chdir(os.path.join(BASE_DIR, ref_folder))
        compile_output = run_compile()
        time.sleep(5)
        if not check_compile_success(compile_output):
            print("Reference design 'c' synthesis did not complete successfully.")
        else:
            print("Reference design 'c' synthesized successfully.")
        # Optionally, save the reference design results to a separate file (e.g., synthesis_summary_c.txt)
        summary_path = os.path.join(BASE_DIR, "synthesis_summary_c.txt")
        with open(summary_path, "w") as f:
            f.write("Reference Design (folder c):\n")
            f.write(f"Reference Values (act_3.txt): {parse_act_file(ref_folder)}\n")
        sys.exit(0)
    else:
        # Process specific rounds (e.g., round_id as "1", "2", ...)
        try:
            round_num_int = int(round_id)
        except ValueError:
            print("Invalid round. Please enter a number (e.g., 1,2,3...) or 'c' for reference design.")
            sys.exit(1)
        round_folder = f"dnn{round_id}"
        print(f"\n===== Starting round {round_id} (folder {round_folder}) =====")
        
        # Prepare the working directory for the current round
        clean_round_folder(round_folder)
        copy_files_to_round(round_folder)
        update_compile_py(round_folder)
        update_testbench_output_dir(round_folder)
        
        # Get reference data to determine the baseline integer bitwidth
        ref_folder = "c"
        if not os.path.exists(os.path.join(BASE_DIR, ref_folder)):
            print("Reference folder 'c' not found. Please synthesize the reference design first!")
            sys.exit(1)
        ref_values = parse_all_txt_files(ref_folder)
        if not ref_values:
            print("Failed to obtain data from reference folder 'c'. Exiting.")
            sys.exit(1)
        baseline_int = determine_integer_bitwidth(ref_values)
        print("Baseline integer bitwidth obtained from the reference design =", baseline_int)
        
        # Determine the fractional bitwidth based on the round number (for example, using round_num as fractional bits)
        current_frac = round_num_int + 8
        update_kernel_bitwidth(round_folder, baseline_int, current_frac)
        update_kernel_paths(round_folder)
        print_source_files(round_folder)
        
        # Change to the current round folder and execute compile.py
        os.chdir(os.path.join(BASE_DIR, round_folder))
        compile_output = run_compile()
        time.sleep(5)
        if not check_compile_success(compile_output):
            print(f"Round {round_id} synthesis did not complete successfully.")
        else:
            print(f"Round {round_id} synthesized successfully.")
        
        # For the current round, the error calculation uses only the data from act_3.txt
        current_values = parse_act_file(round_folder)
        ref_act = parse_act_file(ref_folder)
        error_percent = compute_average_relative_error(ref_act, current_values)
        if error_percent is None:
            print("Error computing relative error; recording error as 'N/A'.")
            error_str = "N/A"
        else:
            error_str = f"{error_percent:.2f}"
        print(f"Round {round_id} average relative error (vs. reference folder 'c'/act_3.txt): {error_str}")
        # dc_total_cell_area, dc_total_dynamic_power, dc_data_arrival_time = run_design_compiler(round_num, BASE_DIR)

        # Write key information of the current round to a separate txt file (filename: synthesis_summary_dnnX.txt)
        summary_path = os.path.join(BASE_DIR, f"synthesis_summary_dnn{round_id}.txt")
        with open(summary_path, "w") as summary_file:
            summary_file.write(f"Round: dnn{round_id}\n")
            summary_file.write(f"Reference Values (act_3.txt): {ref_act}\n")
            summary_file.write(f"Current Values (act_3.txt): {current_values}\n")
            summary_file.write(f"Average Relative Error (%): {error_str}\n")
            # If using Design Compiler synthesis, additional key metrics can be added here
            # summary_file.write(f"Total cell area: {dc_total_cell_area}\n")
            # summary_file.write(f"Data arrival time: {dc_data_arrival_time}\n")
            # summary_file.write(f"Total Dynamic Power: {dc_total_dynamic_power}\n")
        print(f"Synthesis results for this round have been saved to {summary_path}")
        
        # Exit completely after processing the current round
        sys.exit(0)

if __name__ == "__main__":
    main()
