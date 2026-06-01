import os
import re
import shutil
import subprocess
import sys

import openai


# ============================================================
# Paths
# ============================================================
BASE_DIR = "/nas/ei/share/TUEIEDAscratch/ge86pak/mlcad_test/bfs/cbfs"
LIBRARY_DIR = "/nas/ei/share/TUEIEDAscratch/ge86pak/mlcad_test/library"

REASONING_LOG_DIR = os.path.join(BASE_DIR, "reasoning_log")
CATAPULT_LOG_DIR = os.path.join(BASE_DIR, "catapult_log")
CORRECTED_CODE_DIR = os.path.join(BASE_DIR, "corrected_code")
REPAIR_LOG_DIR = os.path.join(BASE_DIR, "repair_log")

REASONING_SCRIPT = os.path.join(BASE_DIR, "reasoning.py")
COMPILE_SCRIPT = os.path.join(BASE_DIR, "compile.py")
EMB_SCRIPT = os.path.join(BASE_DIR, "emb.py")
TB_FILE = os.path.join(BASE_DIR, "tb.cpp")
ORIG_CPP_FILE = os.path.join(BASE_DIR, "bfs.cpp")

# compile.py in this project has historically used different Catapult work dirs.
# Copy the first log that exists after each compile into CATAPULT_LOG_DIR.
CATAPULT_LOG_CANDIDATES = [
    os.path.join(BASE_DIR, "catapult.log"),
    "/nas/ei/share/TUEIEDAscratch/ge86pak/hls/Recursive/E3_BFS_op/catapult.log",
]

ITERATION_LIMIT = 6
RAG_TOP_K = 5
LLM_MODEL = "gpt-5.1"


SYSTEM_PROMPT = (
    "You are an expert in repairing High-Level Synthesis (HLS) incompatible errors "
    "in regular C/C++ programs."
)

PRAGMA_INSTRUCTION = (
    "HARD REQUIREMENT: The final code must select the Catapult top design with exactly one "
    "`#pragma hls_design top` immediately before the `process_top` function definition. "
    "Do not place this pragma before helper functions, outside the `extern \"C\"` block, "
    "or more than once. The required shape is:\n"
    "extern \"C\" {\n"
    "#pragma hls_design top\n"
    "void process_top(...) {\n"
    "    ...\n"
    "}\n"
    "}\n"
)

REPAIR_CONSTRAINTS = """
Critical constraints:
- The intended maximum problem size is small and fixed: use a compile-time MAX value of 10 unless the original code explicitly requires another bound.
- Do NOT introduce arrays of size 1024. Do NOT use n, input size, or output size as an array dimension.
- The top function should have statically bounded array interfaces, for example input[MAX] and output[MAX], not int* interfaces.
- The code must contain exactly one Catapult top pragma: `#pragma hls_design top` immediately before `void process_top(...)`.
"""


# ============================================================
# File helpers
# ============================================================
def ensure_output_dirs():
    for path in [REASONING_LOG_DIR, CATAPULT_LOG_DIR, CORRECTED_CODE_DIR, REPAIR_LOG_DIR]:
        os.makedirs(path, exist_ok=True)


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as exc:
        print(f"[WARN] Cannot read {path}: {exc}")
        return ""


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# Reasoning stage
# ============================================================
def run_reasoning():
    print("[REASONING] Running reasoning.py ...")
    result = subprocess.run(
        [sys.executable, REASONING_SCRIPT],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    write_file(os.path.join(REASONING_LOG_DIR, "reasoning_stdout.txt"), result.stdout)
    write_file(os.path.join(REASONING_LOG_DIR, "reasoning_stderr.txt"), result.stderr)

    if result.returncode != 0:
        stderr_tail = "\n".join(result.stderr.strip().splitlines()[-20:])
        stdout_tail = "\n".join(result.stdout.strip().splitlines()[-20:])
        detail = stderr_tail or stdout_tail or "No stdout/stderr captured."
        raise RuntimeError(
            f"reasoning.py failed with exit code {result.returncode}. "
            f"See {REASONING_LOG_DIR}/reasoning_stderr.txt\n\n"
            f"Last reasoning.py output:\n{detail}"
        )


def load_reasoning_analysis():
    parts = []
    step_labels = {1: "WHAT", 2: "WHERE", 3: "WHY"}
    for step in [1, 2, 3]:
        response_file = os.path.join(REASONING_LOG_DIR, f"step{step}_response.txt")
        content = read_file(response_file).strip()
        if content:
            parts.append(f"[Step {step} - {step_labels[step]}]\n{content}")
    return "\n\n".join(parts)


# ============================================================
# Compile stage
# ============================================================
def update_tb_include(include_path):
    tb_content = read_file(TB_FILE)
    if not tb_content:
        raise FileNotFoundError(f"Cannot read tb.cpp: {TB_FILE}")

    lines = tb_content.splitlines(keepends=True)
    replaced = False
    for idx, line in enumerate(lines):
        if line.strip().startswith("#include") and ".cpp" in line:
            lines[idx] = f'#include "{include_path}"\n'
            replaced = True
            break

    if not replaced:
        lines.insert(0, f'#include "{include_path}"\n')

    write_file(TB_FILE, "".join(lines))


def copy_catapult_log(output_log_file):
    for candidate in CATAPULT_LOG_CANDIDATES:
        if os.path.exists(candidate):
            shutil.copyfile(candidate, output_log_file)
            return True
    return False


def run_compile(include_path, repair_round):
    compile_log = os.path.join(CATAPULT_LOG_DIR, f"compile_iter{repair_round}.txt")
    compile_stdout = os.path.join(CATAPULT_LOG_DIR, f"compile_iter{repair_round}_stdout.txt")
    compile_stderr = os.path.join(CATAPULT_LOG_DIR, f"compile_iter{repair_round}_stderr.txt")

    update_tb_include(include_path)

    result = subprocess.run(
        [sys.executable, COMPILE_SCRIPT, TB_FILE],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    write_file(compile_stdout, result.stdout)
    write_file(compile_stderr, result.stderr)

    if not copy_catapult_log(compile_log):
        message = (
            "Catapult log not found. Checked:\n"
            + "\n".join(f"- {path}" for path in CATAPULT_LOG_CANDIDATES)
            + f"\ncompile.py exit code: {result.returncode}\n"
        )
        write_file(compile_log, message)
        print(f"[COMPILE WARN] {message.strip()}")

    return compile_log


def extract_errors(log_file):
    log_text = read_file(log_file)
    if is_successful_catapult_log(log_text):
        return []

    error_lines = []
    for line in log_text.splitlines():
        stripped = line.strip()
        if is_real_compile_error(stripped):
            error_lines.append(stripped)
    return error_lines


def is_successful_catapult_log(log_text):
    if re.search(r"\bexit status\s+0\b", log_text, re.IGNORECASE):
        return True
    if "Synthesis finished for design" in log_text and not re.search(r"^#\s*Error:", log_text, re.IGNORECASE | re.MULTILINE):
        return True
    return False


def is_real_compile_error(line):
    if not line:
        return False

    # Catapult summary tables contain headers like "Errors|Warnings|Status";
    # those are not actual compile failures.
    if "Errors|Warnings|Status" in line or "|Errors|Warnings|" in line:
        return False

    # Informational report text can mention "error" in descriptions.
    lowered = line.lower()
    if lowered.startswith("# info:") or lowered.startswith("# warning:"):
        return False

    error_patterns = [
        r"^#\s*Error:",
        r"^Error:",
        r"\bCompilation aborted\b",
        r"\bgo\s+\w+:\s+Failed\b",
        r"\bFailed\s+(compile|analyze|synthesis|synthesize)\b",
        r"\bexit status\s+[1-9]\d*\b",
    ]
    return any(re.search(pattern, line, re.IGNORECASE) for pattern in error_patterns)


# ============================================================
# RAG for repair round 2 and every later repair round
# ============================================================
def retrieve_templates(error_message, top_k=RAG_TOP_K):
    if not error_message.strip():
        print("[RAG WARN] Empty compiler error text; no templates retrieved.")
        return []

    result = subprocess.run(
        [sys.executable, EMB_SCRIPT, error_message, LIBRARY_DIR, str(top_k)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.stderr.strip():
        print(f"[RAG WARN] {result.stderr.strip()}")
    if result.returncode != 0:
        print(f"[RAG WARN] emb.py failed with exit code {result.returncode}; continuing without templates.")
        return []

    templates = []
    library_root = os.path.abspath(LIBRARY_DIR)
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue

        fields = line.rsplit(",", 1)
        if len(fields) != 2:
            print(f"[RAG WARN] Cannot parse emb.py output: {line}")
            continue

        template_name = fields[0].strip()
        try:
            similarity = float(fields[1].strip())
        except ValueError:
            print(f"[RAG WARN] Cannot parse similarity score: {line}")
            continue

        template_path = os.path.abspath(os.path.normpath(os.path.join(LIBRARY_DIR, template_name)))
        if template_path != library_root and not template_path.startswith(library_root + os.sep):
            print(f"[RAG WARN] Ignoring template outside library: {template_name}")
            continue

        content = read_file(template_path).strip()
        if content:
            templates.append((template_name, content, similarity))
            print(f"[RAG] {template_name} similarity={similarity:.4f}")

    return templates


# ============================================================
# Prompt builders
# ============================================================
def build_round1_prompt(code_content, reasoning_analysis):
    prompt = "The complete C++ code for HLS is as follows:\n"
    prompt += f"<C_Orig>\n{code_content}\n</C_Orig>\n\n"
    if reasoning_analysis:
        prompt += "Here is the prior analysis produced by reasoning.py:\n"
        prompt += f"<Reasoning_Log>\n{reasoning_analysis}\n</Reasoning_Log>\n\n"
    prompt += "Repair all HLS-incompatible errors identified above.\n\n"
    prompt += REPAIR_CONSTRAINTS + "\n"
    prompt += PRAGMA_INSTRUCTION
    prompt += (
        "Preserve the original functionality. Return only the complete corrected C++ code. "
        "Do NOT add a main function or test function.\n"
    )
    return prompt


def build_rag_repair_prompt(code_content, errors, templates, repair_round):
    prompt = "The complete C++ code for HLS is as follows:\n"
    prompt += f"<C_Current>\n{code_content}\n</C_Current>\n\n"
    prompt += "Here are the compiler errors returned by Catapult HLS:\n"
    for err in errors:
        prompt += f"- {err}\n"
    prompt += "\n"

    prompt += (
        f"This is repair round {repair_round}. Use the following matched repair templates "
        "from the library as guidance. These templates are references; adapt them to the current code.\n\n"
    )
    if templates:
        for idx, (name, content, similarity) in enumerate(templates, 1):
            prompt += f"<T_Ref{idx} name=\"{name}\" similarity=\"{similarity:.4f}\">\n"
            prompt += f"{content}\n"
            prompt += f"</T_Ref{idx}>\n\n"
    else:
        prompt += "No repair template was retrieved for this round; rely on the compiler errors above.\n\n"

    prompt += "Repair the code according to the compiler errors and the templates above.\n\n"
    prompt += REPAIR_CONSTRAINTS + "\n"
    prompt += PRAGMA_INSTRUCTION
    prompt += (
        "Preserve the original functionality. Return only the complete corrected C++ code. "
        "Do NOT add a main function or test function.\n"
    )
    return prompt


# ============================================================
# LLM helpers
# ============================================================
def query_llm(prompt):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def extract_code_from_response(response_text):
    match = re.search(r"```(?:cpp|c\+\+|cxx|c)?\s*\n(.*?)```", response_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip() + "\n"
    return response_text.strip() + "\n"


def enforce_top_pragma(code):
    lines = code.splitlines()
    cleaned = [
        line for line in lines
        if line.strip() != "#pragma hls_design top"
    ]

    for idx, line in enumerate(cleaned):
        if re.search(r"\bvoid\s+process_top\s*\(", line):
            cleaned.insert(idx, "#pragma hls_design top")
            return "\n".join(cleaned).rstrip() + "\n"

    print("[WARN] process_top not found; cannot enforce #pragma hls_design top.")
    return code


def save_repair_log(repair_round, prompt, response):
    prompt_file = os.path.join(REPAIR_LOG_DIR, f"repair_iter{repair_round}_prompt.txt")
    response_file = os.path.join(REPAIR_LOG_DIR, f"repair_iter{repair_round}_response.txt")
    write_file(prompt_file, prompt)
    write_file(response_file, response)
    print(f"[LOG] Saved {prompt_file}")
    print(f"[LOG] Saved {response_file}")


# ============================================================
# Main
# ============================================================
def main():
    ensure_output_dirs()

    print("=" * 70)
    print("HLSRewriter: reasoning stage + iterative repair stage")
    print("=" * 70)

    run_reasoning()
    reasoning_analysis = load_reasoning_analysis()
    if not reasoning_analysis:
        raise RuntimeError(f"No reasoning responses found in {REASONING_LOG_DIR}")
    print(f"[REASONING] Loaded {len(reasoning_analysis)} characters from reasoning_log.")

    current_code = read_file(ORIG_CPP_FILE)
    if not current_code:
        raise RuntimeError(f"Cannot read original source: {ORIG_CPP_FILE}")

    previous_errors = []

    for repair_round in range(1, ITERATION_LIMIT + 1):
        print("\n" + "=" * 50)
        print(f"Repair round {repair_round}/{ITERATION_LIMIT}")
        print("=" * 50)

        if repair_round == 1:
            prompt = build_round1_prompt(current_code, reasoning_analysis)
        else:
            error_text = "\n".join(previous_errors)
            templates = retrieve_templates(error_text)
            prompt = build_rag_repair_prompt(current_code, previous_errors, templates, repair_round)

        print(f"[LLM] Querying {LLM_MODEL} ...")
        response = query_llm(prompt)
        save_repair_log(repair_round, prompt, response)

        fixed_code = extract_code_from_response(response)
        fixed_code = enforce_top_pragma(fixed_code)
        if not fixed_code.strip():
            raise RuntimeError(f"LLM returned empty code in repair round {repair_round}")

        fixed_name = f"bfs_c{repair_round}.cpp"
        fixed_path = os.path.join(CORRECTED_CODE_DIR, fixed_name)
        write_file(fixed_path, fixed_code)
        print(f"[SAVE] Corrected code saved to {fixed_path}")

        include_path = os.path.join("corrected_code", fixed_name).replace("\\", "/")
        compile_log = run_compile(include_path, repair_round)
        errors = extract_errors(compile_log)

        if not errors:
            correct_path = os.path.join(BASE_DIR, "bfs_correct.cpp")
            shutil.copyfile(fixed_path, correct_path)
            write_file(os.path.join(BASE_DIR, "re.txt"), f"Compilation successfully after {repair_round} repair rounds.\n")
            print(f"[SUCCESS] Compilation succeeded after repair round {repair_round}.")
            print(f"[SUCCESS] Final code saved to {correct_path}")
            break

        print(f"[COMPILE] {len(errors)} error line(s) found. Continuing to next round.")
        for err in errors[:8]:
            print(f"  {err}")

        previous_errors = errors
        current_code = fixed_code
    else:
        write_file(os.path.join(BASE_DIR, "re.txt"), f"Compilation failed after {ITERATION_LIMIT} repair rounds.\n")
        print(f"[FAILED] Could not fix all errors after {ITERATION_LIMIT} repair rounds.")

    print("\nOutputs:")
    print(f"- reasoning logs: {REASONING_LOG_DIR}")
    print(f"- repair prompts/responses: {REPAIR_LOG_DIR}")
    print(f"- corrected code: {CORRECTED_CODE_DIR}")
    print(f"- Catapult logs: {CATAPULT_LOG_DIR}")


if __name__ == "__main__":
    main()
