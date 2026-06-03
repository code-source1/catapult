import os
import subprocess
import sys

BASE_DIR = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/c_id"
BUILD_DIR = os.path.join(BASE_DIR, "build")
EXECUTABLE = os.path.join(BUILD_DIR, "ed_exe")

def compile_code():
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)
    # 编译 kernel.cpp 和 kernel_testbench.cpp，注意需要链接标准库
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
