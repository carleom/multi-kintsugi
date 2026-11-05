#!/usr/bin/env python3
"""Compare resolved OpenCode/OMP theme slots without launching an agent or changing settings.

This is a semantic swatch comparison, not a simulation of either app's parser.
Open tests/fixtures/flared.ts and flared.md in the apps to check tokenization.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def resolve(data, section, key):
    palette = data["defs" if section == "theme" else "vars"]
    value = data[section][key]
    seen = set()
    while value in palette:
        if value in seen:
            raise ValueError(f"Circular reference: {key}")
        seen.add(value)
        value = palette[value]
    return value


def colored(text, color):
    r, g, b = bytes.fromhex(color.removeprefix("#")[:6])
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


def main():
    oc = json.loads((ROOT / ".opencode/themes/kintsugi-flared.json").read_text())
    omp = json.loads((ROOT / "ports/oh-my-pi/kintsugi-flared.json").read_text())
    spec = json.loads((ROOT / "palette/flared.json").read_text())
    print("Kintsugi Flared · resolved semantic colors (not parser output)")
    print(f'{"Role":<22} {"Reference":<21} {"OpenCode":<21} Oh My Pi')
    samples = [
        ("keyword", "syntaxKeyword", "syntaxKeyword", "syntax", "keyword", "return"),
        ("function", "syntaxFunction", "syntaxFunction", "syntax", "function", "repair()"),
        ("variable", "syntaxVariable", "syntaxVariable", "syntax", "variable", "result"),
        ("string", "syntaxString", "syntaxString", "syntax", "string", '"gold"'),
        ("number", "syntaxNumber", "syntaxNumber", "syntax", "number", "42"),
        ("user type", "syntaxType", "syntaxType", "syntax", "type", "Result"),
        ("operator", "syntaxOperator", "syntaxOperator", "syntax", "operator", "=> +"),
        ("comment", "syntaxComment", "syntaxComment", "syntax", "comment", "// repair"),
        ("heading", "markdownHeading", "mdHeading", "markdown", "heading", "# Heading"),
        ("inline code", "markdownCode", "mdCode", "markdown", "code", "`code`"),
        ("link label", "markdownLinkText", "mdLink", "markdown", "link", "[label]"),
        ("link URL", "markdownLink", "mdLinkUrl", "markdown", "url", "https://…"),
        ("list marker", "markdownListItem", "mdListBullet", "markdown", "list", "- item"),
    ]
    for label, oc_key, omp_key, group, role, sample in samples:
        colors = [spec["colors"][spec[group][role]], resolve(oc, "theme", oc_key), resolve(omp, "colors", omp_key)]
        cells = [colored(f"{sample:<11} {color}", color) for color in colors]
        print(f"{label:<22} " + "  ".join(cells))
    print("\nDeliberate limits: storage/builtin/attribute distinctions require richer syntax slots.")
    print("OMP strong text is bold only; its theme API has no separate strong-color slot.")
    print("Fixtures: tests/fixtures/flared.ts and tests/fixtures/flared.md")


if __name__ == "__main__":
    main()
