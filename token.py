import os

main_folders = [
    "/.../E1_linear_program",
    "/.../E2_binary_tree"
]

# def count_tokens_in_file(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             text = file.read()
#             tokens = text.split()
#         return len(tokens)
#     except FileNotFoundError:
#         return 0

# def process_folder(main_folder):
#     results = []
#     folder_name = os.path.basename(main_folder)
#     base_name, _ = folder_name.split('_', 1)  

#     
#     for prefix in [f"1{base_name}", base_name]:
#         total_tokens = 0
#         for i in range(1, 16):  
#             subfolder_name = f"{prefix}_{i}_{folder_name[len(base_name)+1:]}" if len(folder_name) > len(base_name) else f"{prefix}_{i}"
#             subfolder_path = os.path.join(main_folder, subfolder_name)
#             if os.path.isdir(subfolder_path):
#                 for file_name in ["GPT1.txt", "GPT2.txt", "GPT3.txt", "prompt1.txt", "prompt2.txt", "prompt3.txt"]:
#                     file_path = os.path.join(subfolder_path, file_name)
#                     total_tokens += count_tokens_in_file(file_path)
#         results.append((f"{prefix} series in {folder_name}", total_tokens))
#     return results

def count_tokens_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            tokens = text.split()
        return len(tokens)
    except FileNotFoundError:
        return 0

def process_folder(main_folder):
    results = [0, 0]  # Initialize results for both 1Ex and Ex series
    folder_name = os.path.basename(main_folder)
    base_name, _ = folder_name.split('_', 1)  # Assume folder naming format is "Ex_*"

    # Handling two types of subfolders
    for index, prefix in enumerate([f"1{base_name}", base_name]):
        for i in range(1, 16):  # Assume there are 15 subfolders of each type
            subfolder_name = f"{prefix}_{i}_{folder_name[len(base_name)+1:]}" if len(folder_name) > len(base_name) else f"{prefix}_{i}"
            subfolder_path = os.path.join(main_folder, subfolder_name)
            if os.path.isdir(subfolder_path):
                for file_name in ["GPT.txt", "prompt.txt"]:
                    file_path = os.path.join(subfolder_path, file_name)
                    results[index] += count_tokens_in_file(file_path)
    return results

def main():
    all_results = []
    # for main_folder in main_folders:
    #     results = process_folder(main_folder)
    #     for result in results:
    #         all_results.append(f"{result[0]}: {result[1]} tokens")

    # with open("token.txt", "w", encoding='utf-8') as f:
    #     for result in all_results:
    #         f.write(result + "\n")

    grouped_folders = [main_folders[i:i+3] for i in range(0, len(main_folders), 3)]
    for group in grouped_folders:
        group_result = [0, 0]  # [sum for 1Ex series, sum for Ex series]
        for folder in group:
            folder_results = process_folder(folder)
            group_result[0] += folder_results[0]
            group_result[1] += folder_results[1]
        all_results.append(group_result)

    with open("token_summary.txt", "w", encoding='utf-8') as f:
        for i, result in enumerate(all_results):
            f.write(f"Group {i+1} - 1Ex series: {result[0]} tokens, Ex series: {result[1]} tokens\n")


if __name__ == "__main__":
    main()
