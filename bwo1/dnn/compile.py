import os
import time
import re
import sys

def create_catapult_tcl_script(kernel_path, testbench_path, extra_files):
    tcl_script_path = '.../bwo1/dnn/run_catapult.tcl'
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
        f.write(f"flow run /SCVerify/launch_make ./scverify/Verify_orig_cxx_osci.mk {{}} SIMTOOL=osci sim\n")
        f.write("quit -force\n")
    return tcl_script_path

def run_tcl_script(tcl_script_path, catapult_bin):
    command = f'{catapult_bin}/catapult -shell -f {tcl_script_path}'
    os.system(command)

def check_report():
    log_file_path = '.../bwo1/dnn/logs/hls_run_tcl.log'
    while not os.path.exists(log_file_path):
        time.sleep(1)
    with open(log_file_path, 'r') as file:
        report_content = file.read()
    error_patterns = ['Error', 'errors', 'Failed']
    result = 'PASS'
    for pattern in error_patterns:
        if re.search(pattern, report_content, re.IGNORECASE):
            result = ''
            break
    metrics = {}
    return result, metrics

def main(kernel_path, testbench_path, catapult_bin):
    output_dir = '.../bwo1/dnn/p'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    extra_files = []
    tcl_script_path = create_catapult_tcl_script(kernel_path, testbench_path, extra_files)
    run_tcl_script(tcl_script_path, catapult_bin)
    result, metrics = check_report()
    print(result, metrics)
if __name__ == "__main__":
    kernel_path = '.../bwo1/dnn/kernel.cpp'
    testbench_path = '.../bwo1/dnn/kernel_testbench.cpp'
    catapult_bin = '/usr/local/tools/mentor/catapult/2022.2-1008433/Mgc_home/bin'
    main(kernel_path, testbench_path, catapult_bin)
    sys.exit(1)
