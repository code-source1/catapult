#!/usr/bin/env python3
import random

MAX_HEIGHT = 15
MAX_WIDTH = 15

def generate_test_input():
    with open("1.dat", "w") as f:
        for i in range(MAX_HEIGHT):
            # 生成一行15个随机浮点数（范围0到128）
            row = " ".join("{:.2f}".format(random.uniform(0, 128)) for _ in range(MAX_WIDTH))
            f.write(row + "\n")
    print("Test input file '1.dat' has been generated.")

if __name__ == "__main__":
    generate_test_input()
