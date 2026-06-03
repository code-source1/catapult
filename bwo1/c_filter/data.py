#!/usr/bin/env python3
import random


NUM_TEST_CASES = 12
ARRAY_LENGTH = 16

output_filename = "1.dat"

with open(output_filename, "w") as f:
    for _ in range(NUM_TEST_CASES):

        line1 = " ".join("{:.2f}".format(random.uniform(0, 10)) for _ in range(ARRAY_LENGTH))

        line2 = " ".join("{:.2f}".format(random.uniform(0, 10)) for _ in range(ARRAY_LENGTH))
        f.write(line1 + "\n")
        f.write(line2 + "\n")

print(f"Test input file '{output_filename}' has been generated.")
