import os
import time
import re
import sys
import subprocess
import math

BASE_DIR = ".../bwo1/dnn"
BASEC_DIR = ".../bwo1/c_dnn"

def create_catapult_tcl_script(kernel_path, testbench_path, extra_files):
    tcl_script_path = os.path.join(os.getcwd(), 'run_catapult.tcl')
    with open(tcl_script_path, 'w') as f:
        f.write("solution new -state initial\n")
        f.write("solution options defaults\n")
        f.write("solution options set /OnTheFly/VthAttributeType cell_lib\n")
        f.write(f"solution file add {kernel_path} -type C++\n")
        for file in extra_files:
            f.write(f"solution file add {file} -type C++\n")
        f.write(f"solution file add {testbench_path} -type C++\n")
        f.write("go new\n")
        f.write("go analyze\n")
        f.write("go compile\n")
        f.write("solution library add nangate-45nm_beh -- -rtlsyntool DesignCompiler -vendor Nangate -technology 045nm\n")
        f.write("go libraries\n")
        f.write('directive set -CLOCKS {clk {-CLOCK_PERIOD 1.0 -CLOCK_EDGE rising -CLOCK_UNCERTAINTY 0.0 -CLOCK_HIGH_TIME 0.5 -RESET_SYNC_NAME rst -RESET_ASYNC_NAME arst_n -RESET_KIND sync -RESET_SYNC_ACTIVE high -RESET_ASYNC_ACTIVE low -ENABLE_ACTIVE high}}\n')
        f.write('directive set -REGISTER_THRESHOLD 3000\n')
        f.write("go assembly\n")
        f.write("go extract\n")
        f.write("flow run /SCVerify/launch_make ./scverify/Verify_orig_cxx_osci.mk {} SIMTOOL=osci sim\n")
        f.write("quit -force\n")
    return tcl_script_path

def run_catapult_synthesis(kernel_path, testbench_path, catapult_bin):
    extra_files = []
    tcl_script_path = create_catapult_tcl_script(kernel_path, testbench_path, extra_files)
    command = f'{catapult_bin}/catapult -shell -f {tcl_script_path}'
    print("Running Catapult synthesis with command:")
    print(command)
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    timeout = 80
    start_time = time.time()
    output = ""
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
    return

def reorder_modules(verilog_file_path):
    try:
        with open(verilog_file_path, 'r') as file:
            content = file.read()
    except Exception as e:
        print("Error reading RTL file:", e)
        return
    module_pattern = re.compile(r'//\s*-*\s*Design Unit:.*?\nmodule\s+.*?endmodule', re.DOTALL)
    modules = module_pattern.findall(content)
    if len(modules) < 2:
        print("Not enough modules to reorder. Need at least two modules.")
        return
    new_order_modules = [modules[-1]] + modules[:-1]
    new_content = '\n\n'.join(new_order_modules)
    with open(verilog_file_path, 'w') as file:
        file.write(new_content)
    print("Modules have been reordered successfully in", verilog_file_path)

def run_design_compiler_synthesis(iteration):
    rtl_path = os.path.join(BASE_DIR, "Catapult", "dnn.v1", "rtl.v")
    if not os.path.exists(rtl_path):
        print("RTL file not found:", rtl_path)
        return None, None, None, None
    reorder_modules(rtl_path)
    run_tcl_path = os.path.join(BASE_DIR, f"design_compiler_{iteration}.tcl")
    report_path = os.path.join(BASE_DIR, f"dc_report_{iteration}.txt")
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
        f.write('write -f verilog -hierarchy -output ' + BASE_DIR + '/netlist.v\n')
        f.write('report_area\n')
        f.write('report_timing -delay max\n')
        f.write('report_power\n')
        f.write('quit\n')
    dc_command = '/usr/local/tools/synopsys/syn/J-2014.09-SP3/bin/dc_shell -f ' + run_tcl_path + ' | tee ' + report_path
    print("Running Design Compiler synthesis with command:")
    print(dc_command)
    os.system(dc_command)
    def match_area(begin, end, string):
        pattern = re.compile(re.escape(begin) + r'(.+?)' + re.escape(end))
        matches = pattern.findall(string)
        return matches[0].strip() if matches else None
    try:
        with open(report_path, 'r') as f:
            report = f.read()
    except Exception as e:
        print("Error reading Design Compiler report:", e)
        return None, None, None, None
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
    total_cell_area = info[4]
    data_arrival_time = info[5]
    total_dynamic_power = info[11]
    return total_cell_area, data_arrival_time, total_dynamic_power, info

def parse_act_file(folder):
    p_dir = os.path.join(folder, "p")
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

def main():
    current_folder = os.path.basename(os.getcwd())
    m = re.match(r"dnn(\d+)", current_folder)
    if m:
        iteration = int(m.group(1))
    else:
        print("Current folder name does not match 'dnnX' format; exiting！")
        sys.exit(1)
    print(f"========== Current iteration: dnn{iteration} ==========")
    kernel_path = os.path.join(os.getcwd(), "kernel.cpp")
    testbench_path = os.path.join(os.getcwd(), "kernel_testbench.cpp")
    catapult_bin = '/usr/local/tools/mentor/catapult/2022.2-1008433/Mgc_home/bin'
    run_catapult_synthesis(kernel_path, testbench_path, catapult_bin)
    ref_folder = os.path.join(BASEC_DIR)
    reference_values = parse_act_file(ref_folder)
    current_values = parse_act_file(os.getcwd())
    if reference_values and current_values:
        if len(reference_values) == len(current_values):
            error_percent = compute_average_relative_error(reference_values, current_values)
            print(f"Average relative error: {error_percent:.2f} %")
        else:
            print("Reference and current data lengths do not match; cannot calculate error.")
            error_percent = None
    else:
        print("Unable to obtain reference or current act_3.txt data; skipping error calculation.")
        error_percent = None
    summary_file = os.path.join(BASE_DIR, "synthesis_summary.txt")
    with open(summary_file, "a") as sf:
        sf.write(f"Iteration: dnn{iteration}\n")
        sf.write(f"Reference act_3.txt: {reference_values}\n")
        sf.write(f"Current act_3.txt: {current_values}\n")
        if error_percent is not None:
            sf.write(f"Average Relative Error (%): {error_percent:.2f}\n")
        sf.write("="*40 + "\n")
    print("Synthesis finished; summary results saved to: ", summary_file)
if __name__ == "__main__":
    main()
    sys.exit(0)
