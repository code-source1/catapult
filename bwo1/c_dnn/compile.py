import os
import subprocess
import sys


BASE_DIR = ".../bwo1/dnn/c"
BUILD_DIR = os.path.join(BASE_DIR, "build")
EXECUTABLE = os.path.join(BUILD_DIR, "dnn_exe")

def compile_code():
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)
    compile_cmd = f"g++ -std=c++11 -O2 -o {EXECUTABLE} {os.path.join(BASE_DIR, 'kernel.cpp')} {os.path.join(BASE_DIR, 'kernel_testbench.cpp')}"
    print("Compiling with command:")
    print(compile_cmd)
    result = subprocess.run(compile_cmd, shell=True)
    if result.returncode != 0:
        print("Compilation failed!")
        sys.exit(1)

def run_executable():
    print("Running executable:", EXECUTABLE)
    result = subprocess.run(EXECUTABLE, shell=True)
    if result.returncode != 0:
        print("Execution failed!")
        sys.exit(1)

def main():
    compile_code()
    run_executable()

if __name__ == "__main__":
    main()
