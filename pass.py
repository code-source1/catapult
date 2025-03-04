import os

base_paths = [
    ".../E1_linear_program",
    ".../E2_binary_tree"
]

counters = {
    "compilation and simulation successful": 0,
    "compilation and simulation failed": 0,
    "compilation successful but simulation failed": 0,
    "other": 0
}

status_counters = {}
folder_details = {}


for base_path in base_paths:
    base_name = base_path.split('/')[-1]  
    prefix, suffix = base_name.split('_', 1)  
    
    counters = {
        "11": 0,
        "00": 0,
        "10": 0,
        "other": 0
    }
    folder_status = []

    for i in range(1, 31):
        sub_folder_name = f"{prefix}_{i}_{suffix}"  
        sub_folder = os.path.join(base_path, sub_folder_name)  
        file_path = os.path.join(sub_folder, "re.txt")  

        try:
            with open(file_path, 'r') as file:
                content = file.read()
                if "Compilation successfully, Simulation successfully." in content:
                    status = "11"
                elif "Compilation failed, Simulation failed." in content:
                    status = "00"
                elif "Compilation successfully, Simulation failed." in content:
                    status = "10"
                else:
                    status = "other"
                
                counters[status] += 1
                folder_status.append(f"{sub_folder}: {status}")
        except FileNotFoundError:
            folder_status.append(f"{sub_folder}: File not found")
    
    status_counters[base_path] = counters
    folder_details[base_path] = folder_status

with open("pass.txt", "w") as outfile:
    for base_path in base_paths:
        outfile.write(f"\nResults for {base_path}:\n")
        outfile.write("\nSummary:\n")
        for key, value in status_counters[base_path].items():
            outfile.write(f"{key}: {value}\n")
        outfile.write("\n")
        for status in folder_details[base_path]:
            outfile.write(f"{status}\n")
