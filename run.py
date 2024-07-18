import os
import shutil
import subprocess

def create_folders_and_copy_files(base_dir, num_folders, all_files, files_to_modify):
    for i in range(1, num_folders + 1):
        new_dir = os.path.join(base_dir, f"E3_{i}_BFS")
        os.makedirs(new_dir, exist_ok=True)

        for filename in all_files:
            src_file = os.path.join(base_dir, filename)
            dest_file = os.path.join(new_dir, filename)
            shutil.copy(src_file, dest_file)

            # Check if the file needs content modification
            if filename in files_to_modify:
                modify_file_contents(dest_file, base_dir, new_dir)

def modify_file_contents(file_path, original_path, new_path):
    with open(file_path, 'r') as file:
        content = file.read()
    modified_content = content.replace(original_path, new_path)
    with open(file_path, 'w') as file:
        file.write(modified_content)

def run_inter_compile_scripts(base_dir, num_folders):
    for i in range(1, num_folders + 1):
        dir_path = os.path.join(base_dir, f"E3_{i}_BFS")
        script_path = os.path.join(dir_path, 'inter_compile.py')
        subprocess.run(['python3', script_path], cwd=dir_path)

def collect_results(base_dir, num_folders, final_file):
    compilation_success = 0
    compilation_failed = 0
    simulation_success = 0
    simulation_failed = 0

    with open(final_file, 'w') as f_out:
        for i in range(1, num_folders + 1):
            re_file = os.path.join(base_dir, f"E3_{i}_BFS", 're.txt')
            with open(re_file, 'r') as f:
                content = f.read()
                f_out.write(f"E3_{i}_BFS:\n{content}\n")
                
                # Count statuses
                if "Compilation successfully" in content:
                    compilation_success += 1
                else:
                    compilation_failed += 1
                if "Simulation successfully" in content:
                    simulation_success += 1
                else:
                    simulation_failed += 1


    print(f"Compilation successfully: {compilation_success}")
    print(f"Compilation failed: {compilation_failed}")
    print(f"Simulation successfully: {simulation_success}")
    print(f"Simulation failed: {simulation_failed}")

def main():
    base_dir = "/.../E3_BFS"
    num_folders = 30
    all_files = ['compile.py', 'emb.py', 'inter_compile.py', 'tb.cpp', 'main.cpp', 'NangateOpenCellLibrary_typical.db']
    files_to_modify = ['compile.py', 'emb.py', 'inter_compile.py']
    final_output_file = os.path.join(base_dir, 'final.txt')
    
    create_folders_and_copy_files(base_dir, num_folders, all_files, files_to_modify)
    run_inter_compile_scripts(base_dir, num_folders)
    collect_results(base_dir, num_folders, final_output_file)

if __name__ == "__main__":
    main()
