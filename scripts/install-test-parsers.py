#!/usr/bin/env python3
"""Build pinned JS/TS/TSX test parsers into an isolated runtime, never user config."""

import argparse
from pathlib import Path
import re
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path)
    output = parser.parse_args().runtime.resolve()
    (output / "parser").mkdir(parents=True, exist_ok=True)
    javascript_queries = {}
    with tempfile.TemporaryDirectory(prefix="parser-build-", dir=output) as directory:
        build = Path(directory)
        for repository, version in [("javascript", "v0.23.1"), ("typescript", "v0.23.2")]:
            checkout = build / repository
            subprocess.run([
                "git", "-c", "advice.detachedHead=false", "clone", "--quiet", "--depth=1", "--branch", version,
                f"https://github.com/tree-sitter/tree-sitter-{repository}.git", str(checkout),
            ], check=True)
            languages = ["javascript"] if repository == "javascript" else ["typescript", "tsx"]
            if repository == "javascript":
                javascript_queries = {
                    # Upstream's locals predicate belongs to tree-sitter's CLI,
                    # not Neovim's query API. The fixture tests do not test locals.
                    name: re.sub(r"\s*\(#is-not\? local\)", "", (checkout / "queries" / name).read_text())
                    for name in ("highlights.scm", "highlights-jsx.scm")
                }
            for language in languages:
                source = checkout / "src" if language == "javascript" else checkout / language / "src"
                subprocess.run([
                    "cc", "-shared", "-fPIC", "-O2", "-I", str(source),
                    str(source / "parser.c"), str(source / "scanner.c"),
                    "-o", str(output / "parser" / f"{language}.so"),
                ], check=True)
                queries = output / "queries" / language
                queries.mkdir(parents=True, exist_ok=True)
                if language == "javascript":
                    highlights = javascript_queries["highlights.scm"]
                elif language == "typescript":
                    highlights = "; inherits: javascript\n\n" + (checkout / "queries/highlights.scm").read_text()
                else:
                    highlights = "; inherits: typescript\n\n" + javascript_queries["highlights-jsx.scm"]
                (queries / "highlights.scm").write_text(highlights)
                print(f"Built {language} ({version})", flush=True)


if __name__ == "__main__":
    main()
