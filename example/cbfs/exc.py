import subprocess

def run_cpp_test():
    print("Compiling...")
    compile_cmd = "g++ tb.cpp -o test_bfs"
    res = subprocess.run(compile_cmd, shell=True)
    if res.returncode != 0:
        print("Compilation failed!")
        return
    print("Running...")
    run_cmd = "./test_bfs"
    subprocess.run(run_cmd, shell=True)

if __name__ == "__main__":
    run_cpp_test()
