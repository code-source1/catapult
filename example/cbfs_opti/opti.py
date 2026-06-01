import argparse
import os
import re
import shutil
import subprocess
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.environ.get("CBFS_OPTI_BASE_DIR", SCRIPT_DIR)
OPTIMIZATION_DIR = os.environ.get(
    "OPTIMIZATION_DIR",
    os.path.abspath(os.path.join(BASE_DIR, "..", "..", "optimization")),
)
EMB_OPTI_SCRIPT = os.path.join(BASE_DIR, "emb_opti.py")
BASE_COMPILE_SCRIPT = os.path.join(BASE_DIR, "compile.py")
GENERATED_COMPILE_SCRIPT = os.path.join(BASE_DIR, "compile_opti.py")
BFS_CPP_FILE = os.path.join(BASE_DIR, "bfs_correct.cpp")
FALLBACK_CPP_FILE = os.path.join(BASE_DIR, "bfs.cpp")
OPTI_LOG_DIR = os.path.join(BASE_DIR, "opti_log")
DEFAULT_KERNEL = os.path.join(BASE_DIR, "tb.cpp")
DEFAULT_MODEL = "gpt-5.1"
DEFAULT_TOP_K = 5


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as exc:
        print(f"[WARN] Cannot read {path}: {exc}", flush=True)
        return ""


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def get_cpp_source():
    if os.path.exists(BFS_CPP_FILE):
        return BFS_CPP_FILE, read_file(BFS_CPP_FILE)
    return FALLBACK_CPP_FILE, read_file(FALLBACK_CPP_FILE)


def detect_top_function(cpp_code):
    pragma_match = re.search(
        r"#pragma\s+hls_design\s+top\s*\n\s*(?:extern\s+\"C\"\s*)?(?:\{)?\s*(?:[\w:<>,\s*&]+)\s+(\w+)\s*\(",
        cpp_code,
        re.MULTILINE,
    )
    if pragma_match:
        return pragma_match.group(1)

    process_match = re.search(r"\bvoid\s+(process_top)\s*\(", cpp_code)
    if process_match:
        return process_match.group(1)

    extern_match = re.search(r"extern\s+\"C\"\s*\{.*?\bvoid\s+(\w+)\s*\(", cpp_code, re.DOTALL)
    if extern_match:
        return extern_match.group(1)

    return "process_top"


def estimate_numeric_hints(cpp_code):
    max_values = re.findall(r"#define\s+\w*MAX\w*\s+(\d+)", cpp_code)
    array_sizes = re.findall(r"\[[ \t]*(\d+)[ \t]*\]", cpp_code)
    loop_bounds = re.findall(r"<\s*(\d+)", cpp_code)
    numbers = [int(x) for x in max_values + array_sizes + loop_bounds if x.isdigit()]
    useful = [x for x in numbers if 0 < x <= 4096]
    max_problem_size = min(useful) if useful else 10
    area_goal = max(200, max_problem_size * 120)
    return {
        "max_problem_size": max_problem_size,
        "area_goal": area_goal,
        "pipeline_ii": 1,
        "unroll_factor": 2 if max_problem_size >= 4 else 1,
    }


def retrieve_templates(goal_text, top_k):
    result = subprocess.run(
        [sys.executable, EMB_OPTI_SCRIPT, goal_text, OPTIMIZATION_DIR, str(top_k)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stderr.strip():
        print(result.stderr.strip(), flush=True)
    if result.returncode != 0:
        raise RuntimeError(f"emb_opti.py failed with exit code {result.returncode}")

    templates = []
    for line in result.stdout.splitlines():
        fields = line.rsplit(",", 1)
        if len(fields) != 2:
            continue
        name = fields[0].strip()
        try:
            score = float(fields[1].strip())
        except ValueError:
            continue
        content = read_file(os.path.join(OPTIMIZATION_DIR, name)).strip()
        if content:
            templates.append((name, score, content))
            print(f"[RAG] {name} score={score:.4f}", flush=True)
    return templates


def build_generation_prompt(goal_text, templates):
    template_text = ""
    for idx, (name, score, content) in enumerate(templates, 1):
        template_text += f"<T_Opt{idx} name=\"{name}\" score=\"{score:.4f}\">\n{content}\n</T_Opt{idx}>\n\n"

    compile_py = read_file(BASE_COMPILE_SCRIPT)
    cpp_path, bfs_cpp = get_cpp_source()
    top_function = detect_top_function(bfs_cpp)
    numeric_hints = estimate_numeric_hints(bfs_cpp)

    return f"""
You are an expert in Catapult HLS TCL optimization.

User optimization request:
{goal_text}

Matched optimization templates:
{template_text}

Current C++ source path:
{cpp_path}

Detected top function name:
{top_function}

Estimated numeric hints from the C++ source:
- max_problem_size: {numeric_hints["max_problem_size"]}
- suggested AREA_GOAL value: {numeric_hints["area_goal"]}
- suggested PIPELINE_INIT_INTERVAL: {numeric_hints["pipeline_ii"]}
- suggested UNROLL factor: {numeric_hints["unroll_factor"]}

Current C++ source:
```cpp
{bfs_cpp}
```

Current compile.py:
```python
{compile_py}
```

Generate the complete optimized compile_opti.py.

STRICT RULES:
1. The output file must be identical to current compile.py except for function create_catapult_tcl_script().
2. You may only modify the TCL script text inside create_catapult_tcl_script().
3. Do NOT modify imports, run_tcl_script(), check_report(), main(), command line parsing, catapult_bin,
   log paths, Python control flow, or any Python code outside create_catapult_tcl_script().
4. In create_catapult_tcl_script(), keep the original Catapult flow order:
   solution new, options defaults, solution file add, pre-analyze optimization directives,
   go new, go analyze, go compile, post-compile optimization directives, library add,
   go libraries, clocks, go assembly, go architect, go allocate, go extract, OasysRTL launch, quit.
5. HARD REQUIREMENT: insert at most TWO optimization hardware directives total.
   Do not insert five directives. Do not insert more than two `directive set ...` optimization lines.
   The clock directive does not count toward this limit.
6. Directive placement rule:
   - Pre-analyze only: ARRAY_INDEX_OPTIMIZATION and global DESIGN_GOAL.
   - Post-compile only for path-specific hierarchy directives such as AREA_GOAL, UNROLL,
     PIPELINE_INIT_INTERVAL, CLUSTER_INLINE, or BOUNDARY_OPT.
7. Path rule:
   - The detected top function is `{top_function}`.
   - Never use bare `/{top_function}` as a directive path.
   - If a path is required, use `/{top_function}/core` or a deeper loop path only if it is clearly valid.
   - If uncertain, prefer a global directive without a hierarchy path.
8. Numeric value rule:
   - If a directive needs a number, estimate it from the C++ source and the hints above.
   - For AREA_GOAL, use a concrete integer near {numeric_hints["area_goal"]}; do not use placeholder values.
   - For PIPELINE_INIT_INTERVAL, use {numeric_hints["pipeline_ii"]} unless the template suggests otherwise.
   - For UNROLL, use {numeric_hints["unroll_factor"]} unless that would over-parallelize the design.
   - The script will ask the human to confirm/replace numeric values for AREA_GOAL, UNROLL,
     and PIPELINE_INIT_INTERVAL before writing the final compile_opti.py.
9. For area, prefer `directive set -DESIGN_GOAL area` as one of the directives.
   For latency, prefer `directive set -DESIGN_GOAL latency` as one of the directives.
10. Return only one Python code block containing the full compile_opti.py.
"""


def extract_code_block(text):
    match = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip() + "\n"
    return text.strip() + "\n"


def query_llm_for_compile_opti(goal_text, templates, model):
    import openai

    prompt = build_generation_prompt(goal_text, templates)
    write_file(os.path.join(OPTI_LOG_DIR, "opti_prompt.txt"), prompt)
    client = openai.OpenAI(timeout=300)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate Catapult HLS compile scripts. You must preserve Python code "
                    "outside create_catapult_tcl_script exactly."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    text = response.choices[0].message.content
    write_file(os.path.join(OPTI_LOG_DIR, "opti_response.txt"), text)
    return extract_code_block(text)


def function_span(code, function_name):
    lines = code.splitlines(keepends=True)
    start = None
    pattern = re.compile(rf"^def\s+{re.escape(function_name)}\s*\(")
    for idx, line in enumerate(lines):
        if pattern.match(line):
            start = idx
            break
    if start is None:
        return None

    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("def ") or lines[idx].startswith("if __name__"):
            end = idx
            break
    return start, end


def splice_create_function(base_code, generated_code):
    base_span = function_span(base_code, "create_catapult_tcl_script")
    generated_span = function_span(generated_code, "create_catapult_tcl_script")
    if base_span is None or generated_span is None:
        raise RuntimeError("Cannot find create_catapult_tcl_script in base or generated code.")

    base_lines = base_code.splitlines(keepends=True)
    generated_lines = generated_code.splitlines(keepends=True)
    result = (
        base_lines[: base_span[0]]
        + generated_lines[generated_span[0] : generated_span[1]]
        + base_lines[base_span[1] :]
    )
    return "".join(result)


def is_optimization_directive(line):
    stripped = line.strip()
    if not stripped.startswith("directive set"):
        return False
    if "-CLOCKS" in stripped:
        return False
    return True


def normalize_directive_path(line, top_function):
    stripped = line.strip()
    bare_top = f"/{top_function}"
    if re.search(rf"directive\s+set\s+{re.escape(bare_top)}(\s|$)", stripped):
        stripped = stripped.replace(f"directive set {bare_top}", f"directive set {bare_top}/core", 1)
    return stripped


def directive_stage(line):
    upper = line.upper()
    if "ARRAY_INDEX_OPTIMIZATION" in upper:
        return "pre"
    if "DESIGN_GOAL" in upper:
        return "pre"
    return "post"


def directive_needs_manual_value(line):
    upper = line.upper()
    return any(
        key in upper
        for key in ["PIPELINE_INIT_INTERVAL", "UNROLL", "AREA_GOAL"]
    )


def directive_value_prompt(line):
    upper = line.upper()
    if "PIPELINE_INIT_INTERVAL" in upper:
        return "PIPELINE_INIT_INTERVAL"
    if "UNROLL" in upper:
        return "UNROLL"
    if "AREA_GOAL" in upper:
        return "AREA_GOAL"
    return "VALUE"


def replace_directive_numeric_value(line, value):
    return re.sub(r"(-(?:PIPELINE_INIT_INTERVAL|UNROLL|AREA_GOAL)\s+)\S+", rf"\g<1>{value}", line)


def ask_manual_directive_values(directives, assume_defaults=False):
    updated = []
    for directive in directives:
        if not directive_needs_manual_value(directive):
            updated.append(directive)
            continue

        current_match = re.search(r"-(?:PIPELINE_INIT_INTERVAL|UNROLL|AREA_GOAL)\s+(\S+)", directive)
        current_value = current_match.group(1) if current_match else ""
        label = directive_value_prompt(directive)

        if assume_defaults:
            updated.append(directive)
            continue

        prompt = (
            f"[MANUAL] Directive needs a numeric value:\n"
            f"         {directive}\n"
            f"         Enter {label} value"
            f"{f' [{current_value}]' if current_value else ''}: "
        )
        user_value = input(prompt).strip()
        if not user_value:
            user_value = current_value
        if not user_value:
            raise RuntimeError(f"No value provided for {label}: {directive}")
        updated.append(replace_directive_numeric_value(directive, user_value))
    return updated


def sanitize_tcl_directives(code, top_function, assume_defaults=False):
    lines = code.splitlines()
    opt_directives = []
    cleaned = []
    for line in lines:
        if is_optimization_directive(line):
            opt_directives.append(normalize_directive_path(line, top_function))
        else:
            cleaned.append(line)

    selected = []
    for directive in opt_directives:
        if directive not in selected:
            selected.append(directive)
        if len(selected) == 2:
            break

    selected = ask_manual_directive_values(selected, assume_defaults=assume_defaults)

    pre_directives = [d for d in selected if directive_stage(d) == "pre"]
    post_directives = [d for d in selected if directive_stage(d) == "post"]

    result = []
    inserted_pre = False
    inserted_post = False
    for line in cleaned:
        result.append(line)
        stripped = line.strip()
        if not inserted_pre and stripped.startswith("solution file add"):
            result.extend(pre_directives)
            inserted_pre = True
        if not inserted_post and stripped == "go compile":
            result.extend(post_directives)
            inserted_post = True

    return "\n".join(result).rstrip() + "\n"


def fallback_create_function(goal_text):
    goal = goal_text.lower()
    directive = "directive set -DESIGN_GOAL area"
    if "latency" in goal:
        directive = "directive set -DESIGN_GOAL latency"
    elif "power" in goal:
        directive = "directive set -DESIGN_GOAL area"

    return f'''def create_catapult_tcl_script(kernel_path):
    # Path to the TCL script to be generated
    tcl_script_path = '.../cbfs_opti/run_catapult.tcl'
    with open(tcl_script_path, 'w') as f:
        f.write(f"""
solution new -state initial
solution options defaults
solution options set /OnTheFly/VthAttributeType cell_lib
solution file add {{kernel_path}} -type C++
{directive}
go new
go analyze
go compile
solution library add nangate-45nm_beh -- -rtlsyntool OasysRTL -vendor Nangate -technology 045nm
go libraries
directive set -CLOCKS {{{{clk {{{{-CLOCK_PERIOD 2.5 -CLOCK_EDGE rising -CLOCK_UNCERTAINTY 0.0 -CLOCK_HIGH_TIME 1.665 -RESET_SYNC_NAME rst -RESET_ASYNC_NAME arst_n -RESET_KIND sync -RESET_SYNC_ACTIVE high -RESET_ASYNC_ACTIVE low -ENABLE_ACTIVE high}}}}}}}}
go assembly
go architect
go allocate
go extract
flow run /OasysRTL/launch_tool ./rtl.v.or v
quit
""")
        # solution design set Solution -top
# options set Message/ErrorOverride HIER-10 -remove
# options set Message/ErrorOverride ASSERT-1 -remove
# options set Message/ErrorOverride HIER-47 -remove

# flow run /SCVerify/launch_make ./scverify/Verify_rtl_v_msim.mk {{}} SIMTOOL=msim sim
    return tcl_script_path
'''


def fallback_compile_opti(goal_text):
    base_code = read_file(BASE_COMPILE_SCRIPT)
    base_span = function_span(base_code, "create_catapult_tcl_script")
    if base_span is None:
        raise RuntimeError("Cannot find create_catapult_tcl_script in compile.py.")
    base_lines = base_code.splitlines(keepends=True)
    replacement = fallback_create_function(goal_text).splitlines(keepends=True)
    return "".join(base_lines[: base_span[0]] + replacement + base_lines[base_span[1] :])


def generate_compile_opti(goal_text, templates, model, assume_defaults=False):
    base_code = read_file(BASE_COMPILE_SCRIPT)
    _, cpp_code = get_cpp_source()
    top_function = detect_top_function(cpp_code)
    try:
        generated = query_llm_for_compile_opti(goal_text, templates, model)
        compile_opti = splice_create_function(base_code, generated)
    except Exception as exc:
        print(f"[WARN] LLM generation failed; using controlled fallback. Reason: {exc}", flush=True)
        compile_opti = fallback_compile_opti(goal_text)

    compile_opti = sanitize_tcl_directives(compile_opti, top_function, assume_defaults=assume_defaults)
    write_file(GENERATED_COMPILE_SCRIPT, compile_opti)
    return compile_opti


def find_catapult_log():
    candidates = [
        os.path.join(BASE_DIR, "catapult.log"),
        os.path.join(BASE_DIR, "log", "catapult.log"),
        ".../cbfs_opti/catapult.log",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""


def parse_metrics(log_text):
    metrics = {}
    downstream = re.search(r"Downstream synthesis information:.*", log_text)
    if downstream:
        metrics["downstream_summary"] = downstream.group(0)
        for key in ["Area", "MinClkPrd", "Delay", "Slack", "InputDelay", "InputSetup", "R2RDelay", "R2RSetup", "AreaSeq"]:
            match = re.search(rf"{key}=([0-9.+-]+)", downstream.group(0))
            if match:
                metrics[key] = match.group(1)
    exit_status = re.search(r"exit status\s+(-?\d+)", log_text, re.IGNORECASE)
    if exit_status:
        metrics["exit_status"] = exit_status.group(1)
    metrics["result"] = "PASS" if metrics.get("exit_status") == "0" else "UNKNOWN"
    if re.search(r"^#\s*Error:", log_text, re.IGNORECASE | re.MULTILINE):
        metrics["result"] = "FAIL"
    return metrics


def write_metrics(output_txt, metrics, log_path, templates):
    selected = "; ".join(name for name, _, _ in templates[:2])
    lines = [f"selected_templates: {selected}"]
    lines.extend(f"{key}: {value}" for key, value in metrics.items())
    lines.append(f"catapult_log: {log_path}")
    write_file(output_txt, "\n".join(lines) + "\n")


def run_compile_opti(kernel_path, output_txt, templates):
    result = subprocess.run(
        [sys.executable, GENERATED_COMPILE_SCRIPT, kernel_path],
        cwd=BASE_DIR,
        text=True,
        capture_output=True,
        timeout=2100,
        check=False,
    )
    write_file(os.path.join(OPTI_LOG_DIR, "run_compile_opti_stdout.txt"), result.stdout)
    write_file(os.path.join(OPTI_LOG_DIR, "run_compile_opti_stderr.txt"), result.stderr)
    print(result.stdout, end="", flush=True)
    if result.stderr.strip():
        print(result.stderr, file=sys.stderr, flush=True)

    log_path = find_catapult_log()
    copied_log = os.path.join(OPTI_LOG_DIR, "catapult_opti.log")
    if log_path:
        shutil.copyfile(log_path, copied_log)
        log_text = read_file(copied_log)
    else:
        log_text = result.stdout + "\n" + result.stderr
        write_file(copied_log, log_text)

    metrics = parse_metrics(log_text)
    metrics["compile_returncode"] = str(result.returncode)
    write_metrics(output_txt, metrics, copied_log, templates)
    for key in ["result", "exit_status", "Area", "AreaSeq", "MinClkPrd", "Delay", "Slack"]:
        print(f"{key}: {metrics.get(key)}", flush=True)
    return result.returncode, metrics


def parse_args():
    parser = argparse.ArgumentParser(description="Generate compile_opti.py by modifying only create_catapult_tcl_script.")
    parser.add_argument("goal", nargs="*", help="Optimization target: area, power, latency, or free-form text.")
    parser.add_argument("--kernel", default=DEFAULT_KERNEL)
    parser.add_argument("--output", default=os.path.join(OPTI_LOG_DIR, "opti_metrics.txt"))
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--no-run", action="store_true")
    parser.add_argument(
        "--assume-defaults",
        action="store_true",
        help="Do not prompt for numeric directive values; keep values generated by LLM/fallback.",
    )
    return parser.parse_args()


def main():
    os.makedirs(OPTI_LOG_DIR, exist_ok=True)
    args = parse_args()
    goal_text = " ".join(args.goal).strip()
    if not goal_text:
        goal_text = input("Optimization target (area/power/latency): ").strip()
    if not goal_text:
        raise RuntimeError("No optimization target provided.")

    print(f"[INFO] Optimization target: {goal_text}", flush=True)
    templates = retrieve_templates(goal_text, args.top_k)
    generate_compile_opti(goal_text, templates, args.model, assume_defaults=args.assume_defaults)
    print(f"[SAVE] Generated {GENERATED_COMPILE_SCRIPT}", flush=True)

    if args.no_run:
        return

    rc, metrics = run_compile_opti(args.kernel, args.output, templates)
    if rc != 0 or metrics.get("result") == "FAIL" or (metrics.get("exit_status") and metrics.get("exit_status") != "0"):
        print(f"[FAILED] Optimized synthesis failed. See {OPTI_LOG_DIR}.", flush=True)
        sys.exit(1)
    print(f"[DONE] Metrics written to {args.output}", flush=True)


if __name__ == "__main__":
    main()
