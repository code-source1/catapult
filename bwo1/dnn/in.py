import random

def generate_input_file(file_path, num_cases, max_vector_size, max_value):
    with open(file_path, 'w') as f:
        for _ in range(num_cases):
            size1 = random.randint(1, max_vector_size)
            size2 = random.randint(1, max_vector_size)
            nums1 = [random.randint(-max_value, max_value) for _ in range(size1)]
            nums2 = [random.randint(-max_value, max_value) for _ in range(size2)]
            f.write(",".join(map(str, nums1)) + "\n")
            f.write(",".join(map(str, nums2)) + "\n")
    print(f"Generated {num_cases} test cases in {file_path}.")
file_path = "1.dat"
num_cases = 1
max_vector_size = 20
max_value = 100
generate_input_file(file_path, num_cases, max_vector_size, max_value)
