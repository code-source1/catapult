import argparse
import os
import re
import sys


DEFAULT_TOP_K = 3


def warn(message):
    print(f"[emb.py] {message}", file=sys.stderr)


def extract_text_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            return file.read()
    except Exception as exc:
        warn(f"Cannot read {file_path}: {exc}")
        return ""


def iter_library_files(library_dir):
    for root, _, files in os.walk(library_dir):
        for file_name in sorted(files):
            if file_name.lower().endswith(".txt"):
                file_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(file_path, library_dir)
                yield rel_path, file_path


def tokenize(text):
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]+|\d+", text.lower()))


def keyword_similarity(query_text, doc_text):
    query_tokens = tokenize(query_text)
    doc_tokens = tokenize(doc_text)
    if not query_tokens or not doc_tokens:
        return 0.0
    overlap = len(query_tokens & doc_tokens)
    query_coverage = overlap / len(query_tokens)
    jaccard = overlap / len(query_tokens | doc_tokens)
    return 0.8 * query_coverage + 0.2 * jaccard


def retrieve_matches(query_text, library_dir, top_k):
    doc_names = []
    doc_texts = []
    for rel_path, file_path in iter_library_files(library_dir):
        file_text = extract_text_from_file(file_path).strip()
        if not file_text:
            continue
        doc_names.append(rel_path)
        # Include the template file name because names such as pointer/DA/recur are useful signals.
        doc_texts.append(f"{rel_path}\n{file_text}")

    if not doc_texts:
        return []

    scored = [
        (name, keyword_similarity(query_text, text))
        for name, text in zip(doc_names, doc_texts)
    ]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:top_k]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Retrieve the most relevant HLS repair templates for a compiler error."
    )
    parser.add_argument("error_message", help="Compiler error text used as the RAG query.")
    parser.add_argument("library_dir", help="Directory containing .txt repair templates.")
    parser.add_argument(
        "top_k",
        nargs="?",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"Number of templates to return. Defaults to {DEFAULT_TOP_K}.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    error_message = args.error_message.strip()
    library_dir = args.library_dir
    top_k = max(1, args.top_k)

    if not error_message:
        warn("Empty compiler error query; no templates retrieved.")
        sys.exit(1)

    if not os.path.isdir(library_dir):
        warn(f"Library directory does not exist: {library_dir}")
        sys.exit(1)

    matches = retrieve_matches(error_message, library_dir, top_k)
    if not matches:
        warn(f"No non-empty .txt templates found in: {library_dir}")
        sys.exit(1)

    for file_name, similarity in matches:
        print(f"{file_name},{similarity:.6f}")


if __name__ == "__main__":
    main()
