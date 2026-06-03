import os
import re
import subprocess
import sys

def reorder_modules(verilog_file_path):
    try:
        with open(verilog_file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print("Error reading RTL file:", e)
        return
    module_pattern = re.compile(r'//\s*-*\s*Design Unit:.*?\nmodule\s+.*?endmodule', re.DOTALL)
    modules = module_pattern.findall(content)
    if len(modules) < 2:
        print("Not enough modules to reorder. Skipping reordering.")
        return
    new_order = [modules[-1]] + modules[:-1]
    new_content = "\n\n".join(new_order)
    with open(verilog_file_path, 'w') as f:
        f.write(new_content)
    print("Modules have been reordered in", verilog_file_path)

def generate_dc_tcl_script(rtl_file):
    tcl_path = os.path.join(os.getcwd(), "design_compiler.tcl")
    with open(tcl_path, "w") as f:
        f.write("set target_library ./NangateOpenCellLibrary_typical.db\n")
        f.write("set link_library ./NangateOpenCellLibrary_typical.db\n")
        f.write("read_verilog " + rtl_file + "\n")
        f.write("suppress_message UID-401\n")
        f.write("check_design\n")
        f.write("link\n")
        f.write("set timing_enable_through_paths true\n")
        f.write("set timing_through_path_max_segments 10\n")
        f.write("create_clock clk -period 900\n")
        f.write("link\n")
        f.write("compile_ultra\n")
        f.write("write -f verilog -hierarchy -output netlist.v\n")
        f.write("report_area\n")
        f.write("report_timing -delay max\n")
        f.write("report_power\n")
        f.write("quit\n")
    print("TCL script generated:", tcl_path)
    return tcl_path

def run_design_compiler():
    current_dir = os.getcwd()
    rtl_file = os.path.join(current_dir, "Catapult", "dnn.v1", "rtl.v")
    if not os.path.exists(rtl_file):
        print("RTL file not found:", rtl_file)
        sys.exit(1)
    reorder_modules(rtl_file)
    tcl_script = generate_dc_tcl_script(rtl_file)
    report_file = os.path.join(current_dir, "dc_report.txt")
    dc_cmd = f'/usr/local/tools/synopsys/syn/J-2014.09-SP3/bin/dc_shell -f {tcl_script} | tee {report_file}'
    print("Running Design Compiler synthesis with command:")
    print(dc_cmd)
    os.system(dc_cmd)
    parse_design_compiler_report(report_file)

def parse_design_compiler_report(report_file):
    try:
        with open(report_file, 'r') as f:
            report = f.read()
    except Exception as e:
        print("Error reading Design Compiler report:", e)
        return
    def match_text(start_str, end_str, text):
        pattern = re.compile(re.escape(start_str) + r'(.*?)' + re.escape(end_str), re.DOTALL)
        match = pattern.search(text)
        return match.group(1).strip() if match else "N/A"
    total_cell_area = match_text("Total cell area:", "\n", report)
    data_arrival_time = match_text("data arrival time", "\n", report)
    total_dynamic_power = match_text("Total Dynamic Power", "\n", report)
    print("\n=== Design Compiler Report Summary ===")
    print("Total Cell Area:", total_cell_area)
    print("Data Arrival Time:", data_arrival_time)
    print("Total Dynamic Power:", total_dynamic_power)
    print("========================================\n")

def main():
    run_design_compiler()
if __name__ == "__main__":
    main()
