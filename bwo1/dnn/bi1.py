import os
import shutil
import time
import re
import math

BASE_DIR = ".../bwo1/dnn"
BASEC_DIR = ".../bwo1/c_dnn"
SOURCE_FILES = [
    "1.dat", "a.dat", "w.dat", "kernel.cpp", "kernel_testbench.cpp", "compile1.py",
    "NangateOpenCellLibrary_typical.db"
]

def copy_files_to_round(round_folder):
    dest_dir = os.path.join(BASE_DIR, round_folder)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    p_dir = os.path.join(dest_dir, "p")
    if not os.path.exists(p_dir):
        os.makedirs(p_dir)
    for filename in SOURCE_FILES:
        src = os.path.join(BASE_DIR, filename)
        dst = os.path.join(dest_dir, filename)
        try:
            shutil.copy(src, dst)
        except Exception as e:
            print(f"Error copying file {filename}: : {e}")

def update_compile_py(round_folder):
    compile_py_path = os.path.join(BASE_DIR, round_folder, "compile1.py")
    try:
        with open(compile_py_path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {compile_py_path}: : {e}")
        return
    new_base = os.path.join(BASE_DIR, round_folder)
    content = content.replace(BASE_DIR, new_base)
    with open(compile_py_path, "w") as f:
        f.write(content)

def update_kernel_bitwidth(round_folder, new_int, new_frac):
    new_total = new_int + new_frac
    pattern = r"(typedef\s+ac_fixed<)\s*\d+\s*,\s*\d+\s*,\s*true\s*>(\s*DataType\s*;)"
    replacement = r"\g<1>{}, {}, true>\g<2>".format(new_total, new_int)
    for filename in ["kernel.cpp", "kernel_testbench.cpp"]:
        file_path = os.path.join(BASE_DIR, round_folder, filename)
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: : {e}")
            continue
        new_content = re.sub(pattern, replacement, content)
        with open(file_path, "w") as f:
            f.write(new_content)

def update_testbench_output_dir(round_folder):
    testbench_path = os.path.join(BASE_DIR, round_folder, "kernel_testbench.cpp")
    try:
        with open(testbench_path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {testbench_path}: : {e}")
        return
    new_output = os.path.join(BASE_DIR, round_folder, "p").replace(os.sep, "/")
    pattern = r'(const\s+string\s+OUTPUT_DIR\s*=\s*")[^"]*(";)'
    replacement = r'\1' + new_output + r'\2'
    new_content = re.sub(pattern, replacement, content)
    with open(testbench_path, "w") as f:
        f.write(new_content)

def update_kernel_paths(round_folder):
    new_base = os.path.join(BASE_DIR, round_folder).replace(os.sep, "/")
    pattern = r'(")' + re.escape(BASE_DIR) + r'(?!/' + re.escape(round_folder) + r')(/[^"]*)(")'
    def repl(match):
        return match.group(1) + new_base + match.group(2) + match.group(3)
    for filename in ["kernel.cpp", "kernel_testbench.cpp"]:
        file_path = os.path.join(BASE_DIR, round_folder, filename)
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: : {e}")
            continue
        new_content = re.sub(pattern, repl, content)
        with open(file_path, "w") as f:
            f.write(new_content)
    print(f"Updated kernel paths in {round_folder}.")

def parse_all_txt_files(round_folder):
    p_dir = os.path.join(BASEC_DIR, "p")
    all_values = []
    if not os.path.isdir(p_dir):
        print(f"Directory {p_dir} does not exist.")
        return all_values
    for filename in os.listdir(p_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(p_dir, filename)
            try:
                with open(file_path, "r") as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {file_path}: : {e}")
                continue
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", content)
            all_values.extend([float(x) for x in nums])
    return all_values

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

def main():
    ref_folder = "c"
    ref_folder_path = os.path.join(BASE_DIR, ref_folder)
    if not os.path.exists(ref_folder_path):
        print("Reference folder 'c'  does not exist; creating the reference design folder ...")
        copy_files_to_round(ref_folder)
        update_compile_py(ref_folder)
        update_kernel_paths(ref_folder)
        print("Please manually enter folder 'c'  and run compile.py to complete synthesis before continuing.")
        input("Press Enter after completing reference design synthesis...")
    update_kernel_paths(ref_folder)
    ref_values = parse_all_txt_files(ref_folder)
    if not ref_values:
        print("Failed to get numeric data from reference folder 'c'; please confirm that act_3.txt exists.")
    else:
        print("Reference folder 'c'  extracted numeric data:")
        print(ref_values)
    baseline_int = determine_integer_bitwidth(ref_values)
    print("Integer bit width (m) determined from reference data: ", baseline_int)
    summary_path = os.path.join(BASE_DIR, "synthesis_summary.txt")
    with open(summary_path, "w") as summary_file:
        header = ("Round\tReference Values (act_3.txt)\tCurrent Values (act_3.txt)\t"
                  "Avg Relative Error (%)\n")
        summary_file.write(header)
        summary_file.write("-" * len(header) + "\n")
        for round_num in range(1, 6):
            current_frac = round_num + 4
            round_folder = f"dnn{round_num}"
            print(f"\n===== Preparing Round {round_num}（{round_folder}），fractional bits = {current_frac} =====")
            copy_files_to_round(round_folder)
            update_compile_py(round_folder)
            update_testbench_output_dir(round_folder)
            update_kernel_bitwidth(round_folder, baseline_int, current_frac)
            update_kernel_paths(round_folder)
            print(f"{round_folder}  preprocessing is complete.")
            print("Please manually enter this folder and run compile.py to complete synthesis.")
    print("\n===== All preprocessing is complete =====")
    print(f"Preprocessing result summary is saved to: {summary_path}")
    print("Please manually run compile.py in each folder to complete the subsequent synthesis work.")
if __name__ == "__main__":
    main()
