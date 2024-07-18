import os
import subprocess
import time
import re
import sys 

def create_catapult_tcl_script(kernel_path):
    # Path to the TCL script to be generated
    tcl_script_path = '/.../run_catapult.tcl'
    with open(tcl_script_path, 'w') as f:
        f.write(f'''
solution new -state initial
solution options defaults
solution options set /OnTheFly/VthAttributeType cell_lib
solution file add {kernel_path} -type C++
go new
go analyze
go compile
solution library add nangate-45nm_beh -- -rtlsyntool DesignCompiler -vendor Nangate -technology 045nm
go libraries
directive set -CLOCKS {{clk {{-CLOCK_PERIOD 1.0 -CLOCK_EDGE rising -CLOCK_UNCERTAINTY 0.0 -CLOCK_HIGH_TIME 0.5 -RESET_SYNC_NAME rst -RESET_ASYNC_NAME arst_n -RESET_KIND sync -RESET_SYNC_ACTIVE high -RESET_ASYNC_ACTIVE low -ENABLE_ACTIVE high}}}}
go assembly
go architect
go allocate

go extract
flow run /SCVerify/launch_make ./scverify/Verify_orig_cxx_osci.mk {{}} SIMTOOL=osci sim
quit
''')
        # solution design set Solution -top
# options set Message/ErrorOverride HIER-10 -remove
# options set Message/ErrorOverride ASSERT-1 -remove
# options set Message/ErrorOverride HIER-47 -remove

# flow run /SCVerify/launch_make ./scverify/Verify_rtl_v_msim.mk {{}} SIMTOOL=msim sim
    return tcl_script_path

def run_tcl_script(tcl_script_path, catapult_bin):
    # Run the TCL script using the Catapult tool
    command = f'{catapult_bin}/catapult -shell -f {tcl_script_path}'
    os.system(command)  # Removed redirection to tee or any file


def check_report():
    log_file_path = '/.../catapult.log'
    # Wait for the log file to be created and then read it
    while not os.path.exists(log_file_path):
        time.sleep(1)
    
    with open(log_file_path, 'r') as file:
        report_content = file.read()

    error_patterns = ['Error', 'errors', 'Failed']
    result = 'PASS'

    # Check for errors or failures in the log
    for pattern in error_patterns:
        if re.search(pattern, report_content, re.IGNORECASE):
            result = 'FAIL'
            break

    metrics = {}
    return result, metrics

def main(kernel_path, catapult_bin):
    tcl_script_path = create_catapult_tcl_script(kernel_path)
    run_tcl_script(tcl_script_path, catapult_bin)
    result, metrics = check_report()
    print(result, metrics)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        kernel_path = sys.argv[1]
        catapult_bin = '/.../catapult/2022.2-1008433/Mgc_home/bin'
        main(kernel_path, catapult_bin)
    else:
        print("No kernel file specified.")
        sys.exit(1)