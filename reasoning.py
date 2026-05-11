import os
import openai

# === Configuration ===
base_path = ".../BFS"
main_cpp_file = os.path.join(base_path, "main.cpp")
reasoning_path = os.path.join(base_path, "reasoning")

os.makedirs(reasoning_path, exist_ok=True)

def read_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading {file_path}: {e}"

def generate_prompt(step, previous_history=""):
    code_content = read_file_content(main_cpp_file)

    if step == 1:
        # WHAT
        prompt = (
            "You are an expert in High-Level Synthesis (HLS). Based solely on the following main.cpp source code, "
            "detect **all potential issues** that may cause HLS incompatibility, incorrect functionality, "
            "timing violations, or resource inefficiency.\n\n"
            "Follow the 3-step reasoning process. This is **Step 1: WHAT** — only list potential issues, "
            "label them as E1, E2, E3, etc. Do NOT provide locations, causes, or fixes.\n\n"
            "Requirements:\n"
            "1) Analyze **only main.cpp**; do not refer to any other files or perform diff analysis.\n"
            "2) Focus on HLS-specific risks, such as: dynamic memory, recursion, unbounded loops, "
            "unsupported libraries, uninitialized arrays, pointer aliasing or out-of-bound access, "
            "bitwidth mismatches, interface or pragma conflicts, and synthesis constraints.\n\n"
            "===== main.cpp =====\n"
            f"{code_content}\n"
            "====================\n"
        )
    elif step == 2:
        # WHERE
        prompt = (
            "Now continue with **Step 2: WHERE** — based on the previous step’s findings (see below), "
            "locate where each potential issue (E1, E2, ...) appears in the source code.\n\n"
            "Requirements:\n"
            "1) For each Ei, specify: the function/scope, relevant variable or statement, and any related pragma.\n"
            "2) Provide an **estimated line number** (starting from 1) and a short code snippet (1–2 lines) "
            "as context for localization.\n"
            "3) Analyze only main.cpp. Do not infer or reference any other files.\n\n"
            "—— Previous Step History ——\n"
            f"{previous_history}\n"
            "—— For reference, here is main.cpp again ——\n"
            "===== main.cpp =====\n"
            f"{read_file_content(main_cpp_file)}\n"
            "====================\n"
        )
    elif step == 3:
        # WHY
        prompt = (
            "Proceed to **Step 3: WHY** — explain why each issue (E1, E2, ...) causes HLS incompatibility or risks.\n\n"
            "Requirements:\n"
            "1) For each Ei, provide a technical explanation referencing common HLS rules, "
            "such as restrictions on recursion, dynamic memory, non-static loop bounds, system calls, "
            "unsupported library functions, data dependencies, or interface mismatches.\n"
            "2) Optionally mention cross-tool implications (e.g., differences among Vitis HLS, LegUp, SmartHLS), "
            "but do NOT provide fix suggestions.\n"
            "3) Use only the content of main.cpp and previous reasoning steps — do not infer missing files.\n\n"
            "—— Previous Two Steps ——\n"
            f"{previous_history}\n"
        )
    else:
        raise ValueError("Invalid step number. Must be 1, 2, or 3.")

    return prompt

def query_gpt(prompt):
    client = openai.OpenAI()
    messages = [
        {
            "role": "system",
            "content": (
                "Your task: analyze only the .../E3_BFS/main.cpp file for potential HLS-related issues. "
                "You must reason in three steps (WHAT → WHERE → WHY). "
                "Do NOT perform diff analysis, use images, or reference any external files."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content

def save_history(round_number, step, prompt, response):
    round_folder = os.path.join(reasoning_path, str(round_number))
    os.makedirs(round_folder, exist_ok=True)
    prompt_file = os.path.join(round_folder, f"step_{step}_prompt.txt")
    response_file = os.path.join(round_folder, f"step_{step}_response.txt")

    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)
    with open(response_file, "w", encoding="utf-8") as f:
        f.write(response)

    print(f"Saved: {prompt_file}")
    print(f"Saved: {response_file}")

def main():
    # Perform one reasoning round with three steps
    round_number = 1
    print(f"Starting Round {round_number}...")
    history = ""

    # Step 1: WHAT
    prompt1 = generate_prompt(step=1)
    response1 = query_gpt(prompt1)
    save_history(round_number, 1, prompt1, response1)
    history += f"[Step 1 - WHAT]\n{response1}\n\n"

    # Step 2: WHERE
    prompt2 = generate_prompt(step=2, previous_history=history)
    response2 = query_gpt(prompt2)
    save_history(round_number, 2, prompt2, response2)
    history += f"[Step 2 - WHERE]\n{response2}\n\n"

    # Step 3: WHY
    prompt3 = generate_prompt(step=3, previous_history=history)
    response3 = query_gpt(prompt3)
    save_history(round_number, 3, prompt3, response3)

    print(f"Round {round_number} Completed.\n")

if __name__ == "__main__":
    main()
