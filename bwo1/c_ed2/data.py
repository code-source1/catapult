#!/usr/bin/env python3
import random

def generate_test_data(filename, rows, cols):
    with open(filename, 'w') as f:
        for _ in range(rows):
            row = " ".join(f"{random.uniform(0, 100):.2f}" for _ in range(cols))
            f.write(row + "\n")

if __name__ == "__main__":
    filename = "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/bwo1/c_ed2/1.dat"
    rows = 15
    cols = 15
    generate_test_data(filename, rows, cols)
    print(f"Test data generated in {filename}")
