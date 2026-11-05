#!/usr/bin/env python3
"""Show Kintsugi Flared swatches and Oh My Pi's real renderer scenarios."""

import json
import os
from pathlib import Path
import subprocess

THEME = Path(__file__).with_name("kintsugi-flared.json")
WIDTH = max(72, min(100, os.get_terminal_size(1).columns)) if os.isatty(1) else 80


def rgb(hex_color: str) -> tuple[int, int, int]:
    return tuple(bytes.fromhex(hex_color.removeprefix("#")))


def swatch(label: str, hex_color: str) -> None:
    r, g, b = rgb(hex_color)
    print(f"  \x1b[48;2;{r};{g};{b}m    \x1b[0m  {label:<19} {hex_color}")


def gallery(*options: str) -> None:
    subprocess.run(["omp", "gallery", f"--width={WIDTH}", *options], check=True)


def main() -> None:
    data = json.loads(THEME.read_text())
    palette = data["vars"]
    colors = data["colors"]
    groups = {
        "Interface / Ghostty": [
            "statusLineBg", "text", "accent", "selectedBg", "border", "mdCodeBlockBorder",
        ],
        "Feedback": ["success", "error", "warning", "toolDiffAdded", "toolDiffRemoved"],
        "Code": [
            "syntaxComment", "syntaxKeyword", "syntaxFunction", "syntaxVariable",
            "syntaxString", "syntaxNumber", "syntaxType", "syntaxOperator",
            "syntaxPunctuation",
        ],
    }
    print("Kintsugi Flared · Oh My Pi palette")
    for title, names in groups.items():
        print(f"\n{title}")
        for name in names:
            value = colors[name]
            swatch(name, palette.get(value, value))

    print("\nActual Oh My Pi renderers (no prompts sent, no configuration changed):")
    gallery("--surface=composer", "--composer=band")
    gallery("--surface=tool", "--tool=context_gauge")
    gallery("--surface=tool", "--tool=edit", "--state=success", "--state=error")
    gallery("--surface=tool", "--tool=bash", "--state=success", "--state=error")
    print("\nThe gallery uses a fixed theme accent; live sessions may use a different")
    print("blue/purple/gold accent derived from their session title.")


if __name__ == "__main__":
    main()
