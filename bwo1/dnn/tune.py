import os
import shutil
import subprocess
import time
import re
import math
import pandas as pd

BASE_DIR = ".../bwo1/dnn"
SOURCE_FILES = ["kernel.cpp", "kernel_testbench.cpp", "compile.py", "NangateOpenCellLibrary_typical.db"]

def copy_files_to_round(round_folder):
    dest_dir = os.path.join(BASE_DIR, round_folder)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for filename in SOURCE_FILES:
        src = os.path.join(BASE_DIR, filename)
        dst = os.path.join(dest_dir, filename)
        shutil.copy(src, dst)

def update_compile_py(round_folder):
    compile_py_path = os.path.join(BASE_DIR, round_folder, "compile.py")
    with open(compile_py_path, "r") as f:
        content = f.read()
    new_base = os.path.join(BASE_DIR, round_folder)
    content = content.replace(BASE_DIR, new_base)
    with open(compile_py_path, "w") as f:
        f.write(content)

def update_kernel_bitwidth(round_folder, new_int, new_frac):
    new_total = new_int + new_frac
    pattern = r"(typedef\s+ac_fixed<)\s*\d+\s*,\s*\d+\s*,\s*true\s*>(\s*DataType\s*;)"
    replacement = r"\g<1>{}, {} , true>\g<2>".format(new_total, new_int)
    for filename in ["kernel.cpp", "kernel_testbench.cpp"]:
        file_path = os.path.join(BASE_DIR, round_folder, filename)
        with open(file_path, "r") as f:
            content = f.read()
        new_content = re.sub(pattern, replacement, content)
        with open(file_path, "w") as f:
            f.write(new_content)

def update_testbench_output_dir(round_folder):
    testbench_path = os.path.join(BASE_DIR, round_folder, "kernel_testbench.cpp")
    with open(testbench_path, "r") as f:
        content = f.read()
    new_output = os.path.join(BASE_DIR, round_folder, "p").replace(os.sep, "/")
    pattern = r'(const\s+string\s+OUTPUT_DIR\s*=\s*")[^"]*(";)'
    replacement = r'\1' + new_output + r'\2'
    new_content = re.sub(pattern, replacement, content)
    with open(testbench_path, "w") as f:
        f.write(new_content)

def run_compile(round_folder):
    cwd = os.path.join(BASE_DIR, round_folder)
    cmd = "python3 compile.py"
    print(f"Running compile in {cwd} with command: {cmd}")
    proc = subprocess.Popen(cmd, cwd=cwd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)
    output = ""
    timeout = 60
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            print("Timeout exceeded, forcing process termination.")
            proc.kill()
            break
        line = proc.stdout.readline()
        if line:
            output += line
            print(line, end="")
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

def check_compile_success(round_folder, compile_output):
    p_dir = os.path.join(BASE_DIR, round_folder, "p")
    act_file = os.path.join(p_dir, "act_3.txt")
    if os.path.exists(act_file):
        return True
    if "# > quit -force" in compile_output or "# > quit" in compile_output:
        return True
    return False

def parse_all_txt_files(round_folder):
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
    if not baseline:
        return 8
    abs_max = max(abs(x) for x in baseline)
    if abs_max < 1:
        return 1
    return math.ceil(math.log2(abs_max)) + 1

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
    reorder_modules(rtl_path)
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

def main():
    ref_folder = "c"
    ref_folder_path = os.path.join(BASE_DIR, ref_folder)
    if not os.path.exists(ref_folder_path):
        print("Reference folder 'c' does not exist. Creating and synthesizing reference design.")
        copy_files_to_round(ref_folder)
        update_compile_py(ref_folder)
        update_testbench_output_dir(ref_folder)
        compile_output_c = run_compile(ref_folder)
        time.sleep(5)
        if not check_compile_success(ref_folder, compile_output_c):
            print("Reference synthesis in folder 'c' did not complete successfully. Exiting.")
            return
    ref_values = parse_all_txt_files(ref_folder)
    if not ref_values:
        print("Failed to obtain reference values from folder 'c'. Exiting.")
        return
    print("Reference values from folder 'c' obtained:")
    print(ref_values)
    baseline_int = determine_integer_bitwidth(ref_values)
    print("Baseline integer bitwidth (m) determined from reference:", baseline_int)
    summary_path = os.path.join(BASE_DIR, "synthesis_summary.txt")
    with open(summary_path, "w") as summary_file:
        header = ("Round\tReference Values\tCurrent Values\tAvg Relative Error (%)\t"
                  "Total cell area\tData arrival time\tTotal Dynamic Power\n")
        summary_file.write(header)
        summary_file.write("-" * len(header) + "\n")
        current_frac = 7
        for round_num in range(1, 6):
            round_folder = f"dnn{round_num}"
            print(f"\n===== Starting Round {round_num} with fractional bits = {current_frac} =====")
            copy_files_to_round(round_folder)
            update_compile_py(round_folder)
            update_testbench_output_dir(round_folder)
            update_kernel_bitwidth(round_folder, baseline_int, current_frac)
            compile_output = run_compile(round_folder)
            time.sleep(5)
            if not check_compile_success(round_folder, compile_output):
                print(f"Round {round_num} synthesis did not complete successfully, forcing next round.")
            current_values = parse_act_file(round_folder)
            error_percent = compute_average_relative_error(parse_act_file(ref_folder), current_values)
            if error_percent is None:
                print("Error computing relative error; stopping iteration.")
                break
            print(f"Round {round_num} average relative error (vs. reference folder 'c'/act_3.txt): {error_percent:.2f}%")
            dc_total_cell_area, dc_total_dynamic_power, dc_data_arrival_time = run_design_compiler(round_num, BASE_DIR)
            summary_file.write(f"dnn{round_num}\t")
            summary_file.write(f"{parse_act_file(ref_folder)}\t")
            summary_file.write(f"{current_values}\t")
            summary_file.write(f"{error_percent:.2f}\t")
            summary_file.write(f"{dc_total_cell_area}\t")
            summary_file.write(f"{dc_data_arrival_time}\t")
            summary_file.write(f"{dc_total_dynamic_power}\n")
            summary_file.flush()
            if 0.5 <= error_percent <= 1:
                print("Desired accuracy achieved (error between 0.5% and 1%). Stopping further rounds.")
                break
            elif error_percent > 1:
                current_frac += 1
                print(f"Error > 1%. Increasing fractional bits for next round to {current_frac}")
            elif error_percent < 0.5:
                if current_frac > 1:
                    current_frac -= 1
                    print(f"Error < 0.5%. Decreasing fractional bits for next round to {current_frac}")
                else:
                    print("Fractional bits already at minimum (1).")
                    break
    print("\n===== HLS and Design Compiler Synthesis Process Completed =====")
    print(f"Summary of results saved to {summary_path}")
if __name__ == "__main__":
    main()
