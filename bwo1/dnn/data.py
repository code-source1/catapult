import random
import os

def generate_w_dat(filename, layers, nodes_per_layer, value_range, frac_digits=4):
    with open(filename, 'w') as f:
        f.write(f"{layers}\n")
        for l in range(layers):
            nodes_in = nodes_per_layer[l]
            nodes_out = nodes_per_layer[l + 1]
            f.write(f"{nodes_in} {nodes_out}\n")
            for _ in range(nodes_out):
                weights = [f"{random.uniform(value_range[0], value_range[1]):.{frac_digits}f}" for _ in range(nodes_in)]
                f.write(" ".join(weights) + "\n")

def generate_a_dat(filename, layers, nodes_per_layer, value_range, frac_digits=4):
    with open(filename, 'w') as f:
        f.write(f"{layers}\n")
        for nodes_out in nodes_per_layer[1:]:
            f.write(f"{nodes_out}\n")
            biases = [f"{random.uniform(value_range[0], value_range[1]):.{frac_digits}f}" for _ in range(nodes_out)]
            f.write(" ".join(biases) + "\n")

def generate_input_dat(filename, num_cases, input_size, value_range, frac_digits=4):
    with open(filename, 'w') as f:
        for _ in range(num_cases):
            inputs1 = [f"{random.uniform(value_range[0], value_range[1]):.{frac_digits}f}" for _ in range(input_size)]
            inputs2 = [f"{random.uniform(value_range[0], value_range[1]):.{frac_digits}f}" for _ in range(input_size)]
            f.write(" ".join(inputs1) + "\n")
            f.write(" ".join(inputs2) + "\n")

def main():
    output_dir = ".../bwo1/dnn"
    os.makedirs(output_dir, exist_ok=True)
    layers = 3
    nodes_per_layer = [5, 8, 9, 6]
    value_range = (-5, 5)
    num_cases = 3
    generate_w_dat(os.path.join(output_dir, "w.dat"), layers, nodes_per_layer, value_range, frac_digits=4)
    generate_a_dat(os.path.join(output_dir, "a.dat"), layers, nodes_per_layer, value_range, frac_digits=4)
    generate_input_dat(os.path.join(output_dir, "1.dat"), num_cases, nodes_per_layer[0], value_range, frac_digits=4)
    print(f"Files generated in '{output_dir}' as fixed‐point numbers with 4 decimal digits.")
if __name__ == "__main__":
    main()
