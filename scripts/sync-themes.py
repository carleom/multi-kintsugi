#!/usr/bin/env python3
"""Generate shared Flared colors; preserve platform-specific mappings and light mode."""

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def dumps(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def render():
    spec = json.loads((ROOT / "palette/flared.json").read_text())
    c = spec["colors"]
    syntax = {k: c[v] for k, v in spec["syntax"].items()}
    md = {k: c[v] for k, v in spec["markdown"].items()}
    feedback = {k: c[v] for k, v in spec["feedback"].items()}
    ansi = [c[name] for name in spec["ansi"]]
    result = {}

    path = "ports/neovim/colors/kintsugi-flared.lua"
    text = (ROOT / path).read_text()
    block = "local c = {\n" + "".join(f'  {k} = "{v}",\n' for k, v in c.items()) + "}"
    text, count = re.subn(r"local c = \{.*?\n\}", lambda _: block, text, count=1, flags=re.S)
    if count != 1:
        raise ValueError("Neovim palette block missing")
    # Generate role assignments too: changing a semantic alias must affect Neovim,
    # not just the chat adapters. Keep styles and language-specific exceptions.
    shared_groups = {
        "syntax": {
            "comment": ["Comment", "@comment"],
            "keyword": ["Statement", "Conditional", "Repeat", "Label", "Keyword", "Exception",
                        "Include", "@keyword", "@keyword.conditional", "@keyword.coroutine",
                        "@keyword.exception", "@keyword.import", "@keyword.repeat",
                        "@keyword.return", "@keyword.directive"],
            "storage": ["StorageClass", "Structure", "Tag", "@keyword.function", "@keyword.modifier",
                        "@keyword.storage", "@keyword.type", "@keyword.storage.javascript",
                        "@keyword.storage.typescript", "@keyword.storage.tsx", "@variable.builtin", "@tag"],
            "function": ["Function", "@function", "@function.call", "@function.method",
                         "@function.method.call", "@lsp.type.function", "@lsp.type.method"],
            "variable": ["Identifier", "@variable", "@variable.parameter", "@property",
                         "@variable.member.typescript", "@variable.member.tsx", "@variable.member.svelte",
                         "@lsp.type.parameter", "@lsp.type.variable", "@lsp.type.property.typescript",
                         "@lsp.type.property.tsx", "@lsp.type.property.svelte"],
            "type": ["@type", "@type.definition", "@lsp.type.class", "@lsp.type.type",
                     "@lsp.type.struct", "@lsp.type.enum", "@lsp.type.interface"],
            "builtin": ["Type", "Typedef", "@type.builtin", "@function.builtin", "@lsp.type.typeParameter"],
            "operator": ["Operator", "@operator", "@operator.typescript", "@operator.tsx",
                         "@operator.svelte", "@keyword.operator", "@punctuation.special"],
            "string": ["String", "@string"],
            "number": ["Number", "Boolean", "Float", "@number", "@boolean", "@constant.builtin"],
            "punctuation": ["Delimiter", "@punctuation", "@punctuation.bracket",
                            "@punctuation.delimiter", "@tag.delimiter"],
            "attribute": ["@attribute"],
        },
        "markdown": {
            "heading": ["@markup.heading", *[f"markdownH{i}" for i in range(1, 7)]],
            "strong": ["@markup.strong", "markdownBold"],
            "link": ["@markup.link", "@markup.link.label", "markdownLinkText"],
            "url": ["@markup.link.url", "markdownUrl"],
            "code": ["@markup.raw", "markdownCode", "markdownCodeBlock"],
            "quote": ["@markup.quote", "markdownBlockquote"],
            "list": ["@markup.list", "markdownListMarker", "markdownOrderedListMarker"],
        },
        "feedback": {
            "error": ["DiagnosticError", "DiagnosticVirtualTextError", "ErrorMsg", "Error", "Debug", "GitSignsDelete", "DiffDelete"],
            "warning": ["DiagnosticWarn", "DiagnosticVirtualTextWarn", "WarningMsg", "GitSignsChange", "DiffChange", "DiffText", "Todo"],
            "success": ["DiagnosticHint", "DiagnosticVirtualTextHint", "MoreMsg", "Question", "GitSignsAdd", "DiffAdd"],
            "info": ["DiagnosticInfo", "DiagnosticVirtualTextInfo"],
        },
    }
    for section, roles in shared_groups.items():
        for role, groups in roles.items():
            for group in groups:
                text, count = re.subn(
                    rf'(hi\("{re.escape(group)}", \{{[^\n]*?fg = c\.)\w+',
                    lambda m: m[1] + spec[section][role], text, count=1,
                )
                if count != 1:
                    raise ValueError(f"Missing Neovim semantic group: {group}")
    text, count = re.subn(
        r"vim\.g\.terminal_color_0 = .*\Z",
        lambda _: "".join(f'vim.g.terminal_color_{i} = c.{name}\n' for i, name in enumerate(spec["ansi"])),
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise ValueError("Neovim terminal palette missing")
    result[path] = text
    for language in ("javascript", "typescript"):
        query = f"after/queries/{language}/highlights.scm"
        result[query] = (ROOT / "ports/neovim" / query).read_text()

    # Keep the established flat theme format, supported by the installed OpenCode.
    # Syntax groups are deliberately coarse; built-ins and storage cannot be split.
    path = ".opencode/themes/kintsugi-flared.json"
    oc = json.loads((ROOT / path).read_text())
    oc["defs"] = dict(c)
    t = oc["theme"]
    roles = {
        "primary": "storage", "secondary": "keyword", "accent": "accent",
        "text": "fg_prose", "textMuted": "fg_muted", "background": "bg_dark",
        "backgroundPanel": "bg_panel", "backgroundElement": "bg_element",
        "border": "border", "borderActive": "accent", "borderSubtle": "border",
        "diffAdded": spec["feedback"]["success"], "diffRemoved": spec["feedback"]["error"], "diffContext": "fg_muted",
        "diffHunkHeader": "fg_muted", "diffHighlightAdded": spec["feedback"]["success"],
        "diffHighlightRemoved": spec["feedback"]["error"], "diffContextBg": "bg",
        "diffLineNumber": "fg_muted",
        "markdownText": spec["markdown"]["text"],
        "markdownHeading": spec["markdown"]["heading"],
        "markdownLink": spec["markdown"]["url"],
        "markdownLinkText": spec["markdown"]["link"],
        "markdownCode": spec["markdown"]["code"],
        "markdownBlockQuote": spec["markdown"]["quote"],
        "markdownEmph": spec["markdown"]["emphasis"],
        "markdownStrong": spec["markdown"]["strong"],
        "markdownHorizontalRule": "border",
        "markdownListItem": spec["markdown"]["list"],
        "markdownListEnumeration": spec["markdown"]["list"],
        "markdownImage": spec["markdown"]["url"],
        "markdownImageText": spec["markdown"]["link"],
        "markdownCodeBlock": spec["markdown"]["code_block"],
    }
    roles.update(spec["feedback"])
    roles.update({"syntax" + k.title(): v for k, v in spec["syntax"].items()
                  if k not in {"storage", "builtin", "attribute"}})
    t.update(roles)
    for key, role, alpha in [
        ("diffAddedBg", "green", "10"), ("diffRemovedBg", "red", "10"),
        ("diffAddedLineNumberBg", "green", "20"), ("diffRemovedLineNumberBg", "red", "20"),
    ]:
        t[key] = feedback["success" if role == "green" else "error"] + alpha
    result[path] = dumps(oc)

    path = "ports/ghostty/kintsugi-flared"
    result[path] = "".join(f"palette = {i}={value}\n" for i, value in enumerate(ansi)) + (
        f'\nbackground = {c["bg_dark"]}\nforeground = {c["fg_prose"]}\n'
        f'cursor-color = {c["cursor"]}\ncursor-text = {c["bg_dark"]}\n'
        f'selection-background = {c["selection"]}\nselection-foreground = {c["fg"]}\n'
    )

    path = "ports/lazygit/kintsugi-flared.yml"
    entries = {
        "activeBorderColor": [c["cursor"], "bold"],
        "inactiveBorderColor": [c["border"]],
        "searchingActiveBorderColor": [c["storage"], "bold"],
        "optionsTextColor": [c["symbol"]],
        "selectedLineBgColor": [c["selection"]],
        "inactiveViewSelectedLineBgColor": [c["selection_inactive"]],
        "cherryPickedCommitFgColor": [c["symbol"]],
        "cherryPickedCommitBgColor": [c["selection_inactive"]],
        "markedBaseCommitFgColor": [c["storage"]],
        "markedBaseCommitBgColor": [c["selection_inactive"]],
        "unstagedChangesColor": [feedback["error"]],
        "defaultFgColor": [c["fg_prose"]],
    }
    result[path] = 'gui:\n  nerdFontsVersion: "3"\n  theme:\n' + "".join(
        f"    {key}:\n" + "".join(f"      - {json.dumps(value)}\n" for value in values)
        for key, values in entries.items()
    ) + f'  authorColors:\n    "*": "{c["syntax"]}"\n  branchColorPatterns:\n    ".*": "{c["storage"]}"\n'

    path = "ports/oh-my-pi/kintsugi-flared.json"
    omp = json.loads((ROOT / path).read_text())
    # Retain the user's renderer/status settings, changing shared roles only.
    omp["vars"].update({
        "background": c["bg_dark"], "editor": c["bg"], "panel": c["bg_panel"],
        "border": c["border"], "foreground": c["fg_prose"], "softText": c["fg_soft"],
        "mutedText": c["fg_muted"], "dimText": c["fg_muted"], "gold": c["storage"],
        "cursor": c["cursor"], "keyword": c["keyword"], "orange": c["operator"],
        "string": c["string"], "number": c["number"], "identifier": c["symbol"],
        "variable": c["syntax"], "punctuation": c["punctuation"], "comment": c["comment"],
        "green": c["green"], "red": c["red"], "yellow": c["yellow"], "blue": c["blue_bright"],
    })
    omp["colors"].update({
        "selectedBg": c["selection"], "syntaxType": "identifier", "mdHeading": "gold",
        "mdLink": "identifier", "mdLinkUrl": "blue", "mdCode": "string", "mdListBullet": "gold",
    })
    for role in ("comment", "keyword", "function", "variable", "string", "number", "type", "operator", "punctuation"):
        omp["colors"]["syntax" + role.title()] = syntax[role]
    for key, role in {"mdHeading": "heading", "mdLink": "link", "mdLinkUrl": "url",
                      "mdCode": "code", "mdCodeBlock": "code_block", "mdQuote": "quote",
                      "mdListBullet": "list"}.items():
        omp["colors"][key] = md[role]
    for key in ("error", "warning", "success"):
        omp["colors"][key] = feedback[key]
    omp["colors"]["toolDiffAdded"] = feedback["success"]
    omp["colors"]["toolDiffRemoved"] = feedback["error"]
    result[path] = dumps(omp)

    path = "ports/obsidian/kintsugi-flared/theme.css"
    text = (ROOT / path).read_text()
    dark, rest = text.split(".theme-light {", 1)
    css = {
        "background-primary": c["bg"], "background-primary-alt": c["bg_highlight"],
        "background-secondary": c["bg_dark"], "background-secondary-alt": c["bg_panel"],
        "background-modifier-border": c["border"], "background-modifier-border-focus": c["cursor"],
        "background-modifier-form-field": c["bg_panel"],
        "background-modifier-form-field-highlighted": c["selection_inactive"],
        "background-modifier-selected": c["selection_inactive"],
        "background-modifier-error": feedback["error"] + "20",
        "background-modifier-error-hover": feedback["error"] + "30",
        "background-modifier-success": feedback["success"] + "20",
        "interactive-normal": c["bg_panel"], "interactive-hover": c["selection_inactive"],
        "interactive-accent": c["cursor"], "interactive-success": feedback["success"],
        "text-on-accent": c["bg_dark"], "text-success": feedback["success"],
        "tag-background": c["selection_inactive"], "tag-background-hover": c["selection"],
        "code-background": c["bg_dark"], "code-border": c["border"],
        "blockquote-border-color": c["cursor"], "blockquote-color": c["fg_muted"],
        "table-header-background": c["bg_panel"], "table-header-background-hover": c["selection_inactive"],
        "table-row-background-hover": c["bg_panel"], "table-border-color": c["border"],
        "hr-color": c["border"], "checkbox-color": c["cursor"],
        "checkbox-marker-color": c["bg_dark"], "caret-color": c["cursor"],
        "scrollbar-bg": c["bg_dark"] + "00", "scrollbar-active-thumb-bg": c["accent"] + "80",
        "text-normal": md["text"], "text-muted": c["fg_muted"], "text-faint": c["fg_muted"],
        "text-accent": c["accent"], "text-accent-hover": c["storage"],
        "text-error": feedback["error"], "text-error-hover": c["red_bright"],
        "text-selection": c["selection"], "text-highlight-bg": c["storage"] + "30",
        "text-highlight-bg-active": c["storage"] + "40", "interactive-accent-hover": c["storage"],
        **{f"h{i}-color": md["heading"] for i in range(1, 7)},
        "heading-formatting": c["symbol"], "link-color": md["link"],
        "link-color-hover": md["url"], "link-external-color": md["link"],
        "link-external-color-hover": md["url"], "tag-color": c["storage"],
        "code-normal": syntax["variable"], "code-comment": syntax["comment"],
        "code-function": syntax["function"], "code-important": syntax["keyword"],
        "code-keyword": syntax["keyword"], "code-operator": syntax["operator"],
        "code-property": syntax["function"], "code-punctuation": syntax["punctuation"],
        "code-string": syntax["string"], "code-tag": c["storage"], "code-value": syntax["number"],
        "callout-title-color": c["storage"], "checkbox-color-hover": c["storage"],
        "bold-color": md["strong"],
    }
    for name, value in css.items():
        pattern = rf"(--{re.escape(name)}:\s*)[^;]+;"
        if re.search(pattern, dark):
            dark = re.sub(pattern, lambda m: m[1] + value + ";", dark)
        else:
            dark = dark.replace(".theme-dark {", f".theme-dark {{\n  --{name}: {value};", 1)
    text = dark + ".theme-light {" + rest
    text = re.sub(
        r"(\.theme-dark \.markdown-rendered :not\(pre\) > code,\n"
        r"\.theme-dark \.cm-inline-code \{\n  color: )[^;]+;",
        lambda m: m[1] + md["code"] + ";", text,
    )
    result[path] = text
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated colors have drifted")
    args = parser.parse_args()
    stale = []
    for name, content in render().items():
        path = ROOT / name
        if path.read_text() != content:
            stale.append(name)
            if not args.check:
                path.write_text(content)
    if stale:
        print(("Out of sync:\n" if args.check else "Updated:\n") + "\n".join(stale))
    else:
        print("All Flared ports are in sync.")
    return int(args.check and bool(stale))


if __name__ == "__main__":
    sys.exit(main())
