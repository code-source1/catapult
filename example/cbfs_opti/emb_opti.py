import argparse
import os
import re
import sys


DEFAULT_TOP_K = 5
TARGET_ALIASES = {
    "area": "large area",
    "large area": "large area",
    "power": "high power",
    "high power": "high power",
    "latency": "large latency",
    "large latency": "large latency",
}


def warn(message):
    print(f"[emb_opti.py] {message}", file=sys.stderr)


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as exc:
        warn(f"Cannot read {path}: {exc}")
        return ""


def tokenize(text):
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]+|\d+", text.lower()))


def normalize_targets(query):
    lowered = query.lower()
    targets = []
    for key, normalized in TARGET_ALIASES.items():
        if key in lowered and normalized not in targets:
            targets.append(normalized)
    return targets


def target_bonus(targets, text):
    target_line = ""
    for line in text.splitlines()[:5]:
        if line.lower().startswith("optimization targets:"):
            target_line = line.lower()
            break
    score = 0.0
    for target in targets:
        if target in target_line:
            score += 2.0
        else:
            score -= 0.35
    return score


def design_goal_priority(query, name):
    lowered_query = query.lower()
    lowered_name = name.lower()
    if "design_goal_area" in lowered_name and ("area" in lowered_query or "large area" in lowered_query):
        return 0.6
    if "design_goal_latency" in lowered_name and ("latency" in lowered_query or "large latency" in lowered_query):
        return 0.6
    return 0.0


def keyword_similarity(query, text):
    query_tokens = tokenize(query)
    text_tokens = tokenize(text)
    if not query_tokens or not text_tokens:
        return 0.0
    overlap = len(query_tokens & text_tokens)
    query_coverage = overlap / len(query_tokens)
    jaccard = overlap / len(query_tokens | text_tokens)
    return 0.75 * query_coverage + 0.25 * jaccard


def iter_templates(optimization_dir):
    for name in sorted(os.listdir(optimization_dir)):
        if name.lower().endswith(".txt"):
            path = os.path.join(optimization_dir, name)
            if os.path.isfile(path):
                yield name, path


def retrieve(query, optimization_dir, top_k):
    targets = normalize_targets(query)
    results = []
    for name, path in iter_templates(optimization_dir):
        content = read_file(path).strip()
        if not content:
            continue
        searchable = f"{name}\n{content}"
        score = (
            keyword_similarity(query, searchable)
            + target_bonus(targets, searchable)
            + design_goal_priority(query, name)
        )
        results.append((name, score))
    results.sort(key=lambda item: item[1], reverse=True)
    return results[:top_k]


def parse_args():
    parser = argparse.ArgumentParser(description="Fast retrieval for Catapult HLS optimization templates.")
    parser.add_argument("query", help="User optimization request, e.g. 'large area' or 'high power latency'.")
    parser.add_argument("optimization_dir", help="Directory containing optimization .txt templates.")
    parser.add_argument("top_k", nargs="?", type=int, default=DEFAULT_TOP_K)
    return parser.parse_args()


def main():
    args = parse_args()
    if not os.path.isdir(args.optimization_dir):
        warn(f"Optimization library does not exist: {args.optimization_dir}")
        sys.exit(1)

    matches = retrieve(args.query, args.optimization_dir, max(1, args.top_k))
    if not matches:
        warn("No optimization templates found.")
        sys.exit(1)

    for name, score in matches:
        print(f"{name},{score:.6f}")


if __name__ == "__main__":
    main()
