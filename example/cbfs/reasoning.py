import os
import openai

base_path      = "/nas/ei/share/TUEIEDAscratch/ge86pak/mlcad_test/bfs/cbfs"
main_cpp_file  = os.path.join(base_path, "bfs.cpp")
# Log directory: all prompts & responses saved here as flat txt files
llmlog_path    = "/nas/ei/share/TUEIEDAscratch/ge86pak/mlcad_test/bfs/cbfs/reasoning_log"

os.makedirs(llmlog_path, exist_ok=True)

# ============================================================
# Seven HLS Incompatibility Types (from HLSRewriter paper)
# ============================================================
HLS_INCOMPATIBILITY_SUMMARY = """
The 7 common types of HLS-incompatible errors are summarized as follows.
For each error type, a brief overview and the common symptom error code are provided:

(1) Dynamic Pointer:
    - Symptom: "Unsupported feature 'pointers-to-pointers' (CIN-243)"
    - Description: HLS tools cannot synthesize dynamic pointer operations (e.g., malloc/free,
      pointer-to-pointer, NULL-initialized global pointers). All memory must be statically
      allocated and bounded at compile time.
    - Refactoring: Convert to array access with static allocation.

(2) Dynamic Array:
    - Symptom: "Unsupported feature 'variable length array' (CIN-15)"
    - Description: Variable-length arrays (VLAs) or heap-allocated arrays whose size is
      determined at runtime are not synthesizable. HLS requires all array dimensions to be
      compile-time constants.
    - Refactoring: Specify the static array size using compile-time constants or macros.

(3) Recursion:
    - Symptom: "Unsupported feature 'recursion' (CIN-15)"
    - Description: HLS tools do not support recursive function calls because the call depth
      is unknown at compile time, making it impossible to statically allocate resources.
    - Refactoring: Replace with a loop iteration (iterative equivalent using an explicit stack).

(4) Operator Constraint:
    - Symptom: "Incrementing a bool value is deprecated (CRD-708)"
    - Description: Certain C++ operators are restricted or behave differently in HLS context,
      such as incrementing bool values, unsupported operator overloading, or deprecated
      arithmetic on non-integer types.
    - Refactoring: Convert to integer type (e.g., replace bool with int/uint).

(5) Incomplete Statement:
    - Symptom: "Expected a statement (CRD-127)"
    - Description: Constructs such as goto labels, empty label bodies, or control-flow
      patterns (e.g., goto-based error handling) that generate incomplete or unreachable
      statements confuse the HLS front-end parser.
    - Refactoring: Add a complete statement (e.g., replace goto with structured control flow).

(6) Unsupported Struct:
    - Symptom: "Unsupported structs create deadlocks. (HIER-10)"
    - Description: Structs containing pointers, virtual methods, or self-referential fields
      (linked-list style nodes) cannot be directly synthesized because they imply dynamic
      memory topology unknown at compile time.
    - Refactoring: Add explicit descriptions / flatten struct to use index-based arrays.

(7) Exception-Handling:
    - Symptom: "Out-of-bounds read/write access (CRD-175)"
    - Description: C++ exception handling (try/catch/throw) and implicit out-of-bounds
      accesses are not supported in HLS. All error conditions must be handled through
      explicit conditional checks.
    - Refactoring: Add a read/write bound check (explicit guard conditions).
"""

# ============================================================
# Helper
# ============================================================
def read_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading {file_path}: {e}"


# ============================================================
# Prompt Construction  (aligned with HLSRewriter paper)
# ============================================================
def generate_prompt(step, previous_history=""):
    code_content = read_file_content(main_cpp_file)

    # ── System prompt (shared across all steps) ──────────────
    # Kept separate; injected via the 'system' role in query_gpt().

    if step == 1:
        # ── Step 1: WHAT ─────────────────────────────────────
        prompt = (
            "You are now tasked with step-by-step analysis of standard C++ code. "
            "The HLS tool reports two actual issues in the code below: "
            "dynamic pointers and dynamic arrays.\n\n"
            + HLS_INCOMPATIBILITY_SUMMARY
            + "\nHere is a typical breadth-first search (BFS) C++ code with HLS-incompatible errors. "
            "This code involves creating a binary tree, initializing the tree structure, "
            "adding nodes, and performing a BFS to visit and process each node. "
            "The code is given as follows:\n\n"
            "===== bfs.cpp =====\n"
            f"{code_content}\n"
            "===================\n\n"
            "Your task is to detect all potential HLS-incompatible errors.\n\n"
            "Attention: Please follow the following steps below to analyze:\n"
            "Step 1: Analyze 'what' the potential errors are;\n"
            "Step 2: Locate 'where' the potential errors are;\n"
            "Step 3: Give the reasons for each potential error.\n\n"
            "This is **Step 1: Analyze 'what' the potential errors are**.\n"
            "List every HLS-incompatible issue you find, label them E1, E2, E3, … "
            "and identify which Incompatibility Type (from the 7 types above) each belongs to.\n"
            "Do NOT provide locations or fixes at this step."
        )

    elif step == 2:
        # ── Step 2: WHERE ────────────────────────────────────
        prompt = (
            "This is **Step 2: Locate 'where' the potential errors are**.\n\n"
            "Based on the Step 1 findings listed below, locate exactly where each error "
            "(E1, E2, …) appears in the source code.\n\n"
            "Requirements:\n"
            "1) For each Ei, specify: the function/scope, the relevant variable or statement, "
            "and the corresponding Incompatibility Type and its typical HLS symptom \n"
            "2) Provide an estimated line number and a short code snippet (1–2 lines) "
            "as context for localization.\n"
            "3) Analyze only bfs.cpp. Do not reference any other files.\n\n"
            "—— Previous Step History ——\n"
            f"{previous_history}\n"
            "—— For reference, here is bfs.cpp again ——\n"
            "===== bfs.cpp =====\n"
            f"{read_file_content(main_cpp_file)}\n"
            "===================\n"
        )

    elif step == 3:
        # ── Step 3: WHY ──────────────────────────────────────
        prompt = (
            "This is **Step 3: Give the reasons for each potential error**.\n\n"
            "Based on the previous two steps, explain WHY each issue (E1, E2, …) causes "
            "HLS incompatibility or synthesis failure.\n\n"
            "Requirements:\n"
            "1) For each Ei, provide a technical explanation that references the specific "
            "HLS restriction violated (e.g., static memory allocation requirement, "
            "compile-time loop bounds, no recursion, no dynamic dispatch).\n"
            "2) Map each error to its Incompatibility Type and Corresponding Refactoring "
            "strategy from the HLSRewriter taxonomy:\n"
            "   - Dynamic Pointer      → Convert to array access\n"
            "   - Dynamic Array        → Specify the static array size\n"
            "   - Recursion            → Replace with a loop iteration\n"
            "   - Operator Constraint  → Convert to integer type\n"
            "   - Incomplete Statement → Add a complete statement\n"
            "   - Unsupported Struct   → Add explicit descriptions\n"
            "   - Exception-Handling   → Add a read/write bound check\n"
            "3) Do NOT provide corrected code at this step. "
            "Use only bfs.cpp and the previous reasoning steps.\n\n"
            "—— Previous Two Steps ——\n"
            f"{previous_history}\n"
        )

    else:
        raise ValueError("Invalid step number. Must be 1, 2, or 3.")

    return prompt


# ============================================================
# GPT Query
# ============================================================
def query_gpt(prompt):
    client = openai.OpenAI()

    system_prompt = (
        "You are an expert in identifying the High-Level Synthesis (HLS) incompatible errors "
        "in the regular C/C++ program. "
        "You must reason in three structured steps: "
        "Step 1 — 'what' the potential errors are; "
        "Step 2 — 'where' the potential errors are; "
        "Step 3 — the reasons for each potential error. "
        "Always classify each error using the exact Incompatibility Type names from the "
        "HLSRewriter taxonomy: Dynamic Pointer, Dynamic Array, Recursion, Operator Constraint, "
        "Incomplete Statement, Unsupported Struct, Exception-Handling. "
        "Do NOT perform diff analysis or reference any files other than bfs.cpp."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": prompt},
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content


# ============================================================
# Save
# ============================================================
def save_history(round_number, step, prompt, response):
    """Save prompt and response as flat files under llmlog_path.
    File naming: step1_prompt.txt, step1_response.txt, ...
    """
    prompt_file   = os.path.join(llmlog_path, f"step{step}_prompt.txt")
    response_file = os.path.join(llmlog_path, f"step{step}_response.txt")

    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)
    with open(response_file, "w", encoding="utf-8") as f:
        f.write(response)

    print(f"  Saved: {prompt_file}")
    print(f"  Saved: {response_file}")


# ============================================================
# Main
# ============================================================
def main():
    round_number = 1
    print(f"=== HLSRewriter Reasoning — Round {round_number} ===\n")
    history = ""

    # Step 1: WHAT
    print("[Step 1] Analyzing WHAT the potential HLS-incompatible errors are ...")
    prompt1   = generate_prompt(step=1)
    response1 = query_gpt(prompt1)
    save_history(round_number, 1, prompt1, response1)
    history += f"[Step 1 — WHAT]\n{response1}\n\n"
    print(f"\n--- Step 1 Response ---\n{response1}\n")

    # Step 2: WHERE
    print("[Step 2] Locating WHERE each error appears ...")
    prompt2   = generate_prompt(step=2, previous_history=history)
    response2 = query_gpt(prompt2)
    save_history(round_number, 2, prompt2, response2)
    history += f"[Step 2 — WHERE]\n{response2}\n\n"
    print(f"\n--- Step 2 Response ---\n{response2}\n")

    # Step 3: WHY
    print("[Step 3] Explaining WHY each error causes HLS incompatibility ...")
    prompt3   = generate_prompt(step=3, previous_history=history)
    response3 = query_gpt(prompt3)
    save_history(round_number, 3, prompt3, response3)
    print(f"\n--- Step 3 Response ---\n{response3}\n")

    print(f"=== Round {round_number} Completed. Results saved to: {llmlog_path} ===\n")


if __name__ == "__main__":
    main()
