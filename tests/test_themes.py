"""Cross-port contracts, checked against the original VS Code Flared syntax."""

import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "palette/flared.json").read_text())
C = SPEC["colors"]


def jsonc(path):
    text = path.read_text()
    text = re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',
                  lambda m: m[0] if m[0].startswith('"') else "", text, flags=re.S)
    return json.loads(text)


def resolve(data, key, palette="defs", roles="theme"):
    value = data[roles][key]
    seen = set()
    while value in data[palette]:
        if value in seen:
            raise AssertionError(f"Circular color reference: {key}")
        seen.add(value)
        value = data[palette][value]
    if not re.fullmatch(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?", value):
        raise AssertionError(f"Unresolved color: {key} = {value}")
    return value.lower()


class ThemeContracts(unittest.TestCase):
    def test_original_vscode_syntax_is_authoritative(self):
        vs = jsonc(ROOT / "themes/Kintsugi-Dark-Flared-color-theme.json")
        tokens = {rule["name"]: rule["settings"] for rule in vs["tokenColors"]}
        mapping = {
            "Keywords": "keyword", "Storage & Bolded Items": "storage",
            "User-defined names (Functions, Classes, etc)": "symbol",
            "Default Text, Variables, Properties": "syntax", "String": "string",
            "Primitive Literals (Numbers, Booleans, etc)": "number", "Operator": "operator",
            "Comment": "comment", "Punctuation": "punctuation",
            "Compiler Metadata & Attributes (Annotations, Lifetimes, Decorators)": "attribute",
            "Markdown: Titles & Bold Text": "storage", "Markdown: Raw Code": "string",
        }
        for name, color in mapping.items():
            with self.subTest(role=name):
                self.assertEqual(tokens[name]["foreground"].lower(), C[color].lower())

    def test_opencode_and_omp_syntax(self):
        oc = json.loads((ROOT / ".opencode/themes/kintsugi-flared.json").read_text())
        omp = json.loads((ROOT / "ports/oh-my-pi/kintsugi-flared.json").read_text())
        for role, color in SPEC["syntax"].items():
            if role in {"storage", "builtin", "attribute"}:
                continue  # These renderers expose no separate slot.
            key = "syntax" + role.title()
            for data, palette, roles in [(oc, "defs", "theme"), (omp, "vars", "colors")]:
                with self.subTest(app=roles, role=role):
                    self.assertEqual(resolve(data, key, palette, roles), C[color].lower())
        for data, palette, roles in [(oc, "defs", "theme"), (omp, "vars", "colors")]:
            for key in data[roles]:
                resolve(data, key, palette, roles)

    def test_markdown_hierarchy(self):
        oc = json.loads((ROOT / ".opencode/themes/kintsugi-flared.json").read_text())
        for key, role in {"markdownHeading": "heading", "markdownStrong": "strong",
                          "markdownCode": "code", "markdownLinkText": "link",
                          "markdownLink": "url", "markdownListItem": "list",
                          "markdownListEnumeration": "list", "markdownEmph": "emphasis"}.items():
            self.assertEqual(resolve(oc, key), C[SPEC["markdown"][role]].lower())
        css = (ROOT / "ports/obsidian/kintsugi-flared/theme.css").read_text()
        dark, light = css.split(".theme-light {", 1)
        for i in range(1, 7):
            self.assertIn(f'--h{i}-color: {C["storage"]};', dark)
        self.assertIn(f'--bold-color: {C["storage"]};', dark)
        self.assertIn("--bold-color: #9a7820;", light)
        self.assertNotIn("--bold-color:", css.split("body {", 1)[1].split("}", 1)[0])

    def test_terminal_palette_matches_vscode(self):
        vs = jsonc(ROOT / "themes/Kintsugi-Dark-Flared-color-theme.json")["colors"]
        ghostty = (ROOT / "ports/ghostty/kintsugi-flared").read_text()
        colors = dict(re.findall(r"palette = (\d+)=(#[0-9a-fA-F]+)", ghostty))
        names = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]
        names += ["Bright" + name for name in names]
        self.assertEqual(len(colors), 16)
        for i, name in enumerate(names):
            self.assertEqual(colors[str(i)].lower(), vs["terminal.ansi" + name].lower())
        self.assertIn(f'foreground = {C["fg_prose"]}', ghostty)

    def test_generation_is_idempotent_and_catches_drift(self):
        module_spec = importlib.util.spec_from_file_location("sync_themes", ROOT / "scripts/sync-themes.py")
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        expected = module.render()
        for name, content in expected.items():
            with self.subTest(port=name):
                self.assertEqual((ROOT / name).read_text(), content, "Run python3 scripts/sync-themes.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "palette").mkdir()
            shutil.copyfile(ROOT / "palette/flared.json", root / "palette/flared.json")
            for name, content in expected.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            for language in ("javascript", "typescript"):
                source = f"ports/neovim/after/queries/{language}/highlights.scm"
                target = root / source
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / source, target)
            module.ROOT = root
            self.assertEqual(module.render(), expected)
            # A real shared color edit must update every adapter, not just one app.
            changed = json.loads((root / "palette/flared.json").read_text())
            changed["colors"]["symbol"] = "#abcdef"
            (root / "palette/flared.json").write_text(json.dumps(changed))
            generated = module.render()
            for name in expected:
                if "ghostty" not in name and not name.endswith(".scm"):
                    self.assertNotEqual(generated[name], expected[name], name)
            changed["syntax"]["function"] = "string"
            changed["markdown"]["heading"] = "keyword"
            changed["feedback"]["error"] = "magenta"
            changed["colors"]["bg_dark"] = "#121110"
            (root / "palette/flared.json").write_text(json.dumps(changed))
            generated = module.render()
            self.assertIn('hi("@function", { fg = c.string })', generated["ports/neovim/colors/kintsugi-flared.lua"])
            self.assertIn('hi("@markup.heading", { fg = c.keyword, bold = true })', generated["ports/neovim/colors/kintsugi-flared.lua"])
            self.assertIn('hi("DiagnosticVirtualTextError", { fg = c.magenta,', generated["ports/neovim/colors/kintsugi-flared.lua"])
            self.assertIn('hi("DiffDelete", { fg = c.magenta,', generated["ports/neovim/colors/kintsugi-flared.lua"])
            self.assertEqual(resolve(json.loads(generated[".opencode/themes/kintsugi-flared.json"]), "diffRemoved"), C["magenta"].lower())
            self.assertEqual(resolve(json.loads(generated["ports/oh-my-pi/kintsugi-flared.json"]), "toolDiffRemoved", "vars", "colors"), C["magenta"].lower())
            css = generated["ports/obsidian/kintsugi-flared/theme.css"]
            self.assertIn("--background-secondary: #121110;", css)
            self.assertIn("--code-background: #121110;", css)

    @unittest.skipUnless(shutil.which("nvim"), "Neovim is not installed")
    def test_neovim_resolved_highlights(self):
        groups = {
            "@keyword": "keyword", "@keyword.storage.typescript": "storage", "@keyword.type": "storage",
            "@function": "symbol", "@constructor": "symbol", "@constant": "symbol",
            "@constant.builtin": "number", "@type": "symbol", "@type.builtin": "operator",
            "@string": "string", "@number": "number", "@variable": "syntax",
            "@markup.heading": "storage", "@markup.strong": "storage",
            "@markup.link.label": "symbol", "@markup.link.url": "blue_bright",
            "@markup.list": "storage", "markdownBold": "storage", "markdownCode": "string",
            "DiagnosticError": "red", "DiagnosticWarn": "yellow", "DiagnosticInfo": "blue_bright",
        }
        lua = "local out={}; for _,g in ipairs(" + "{" + ",".join(json.dumps(g) for g in groups) + "}" + ") do out[g]=vim.api.nvim_get_hl(0,{name=g,link=false}) end; io.write(vim.json.encode(out))"
        result = subprocess.run([
            "nvim", "--headless", "-u", "NONE", "-i", "NONE", "-n",
            "--cmd", f"lua vim.opt.rtp:prepend([=[{ROOT}]=])",
            "-c", "colorscheme kintsugi-flared", "-c", "lua " + lua, "-c", "qa!",
        ], capture_output=True, text=True, timeout=15, check=True)
        actual = json.loads(result.stdout)
        for group, color in groups.items():
            with self.subTest(group=group):
                self.assertEqual(actual[group]["fg"], int(C[color][1:], 16))
        self.assertTrue(actual["@keyword"]["bold"])
        self.assertTrue(actual["@markup.strong"]["bold"])

    @unittest.skipUnless(shutil.which("nvim"), "Neovim is not installed")
    def test_js_ts_tsx_fixtures_use_bundled_declaration_overrides(self):
        lua = '''
local lang = LANG
local ok, loaded = pcall(vim.treesitter.language.add, lang)
if not ok or loaded == false then io.write("NO_PARSER"); return end
local acquired, p = pcall(vim.treesitter.get_parser, 0, lang)
if not acquired or p == nil then io.write("NO_PARSER"); return end
local tree = p:parse()[1]
local q = vim.treesitter.query.get(lang, "highlights")
local out = {}
for id, node, metadata in q:iter_captures(tree:root(), 0) do
  if q.captures[id] == "keyword.storage" then
    table.insert(out, vim.treesitter.get_node_text(node, 0))
  end
end
io.write(vim.json.encode(out))
'''
        for language in ("javascript", "typescript", "tsx"):
            with self.subTest(language=language):
                runtime = ROOT / "ports/neovim"
                setup = f"lua vim.opt.rtp:prepend([=[{runtime}]=]); vim.opt.rtp:append([=[{runtime / 'after'}]=])"
                if os.getenv("KINTSUGI_PARSER_RUNTIME"):
                    setup += f"; vim.opt.rtp:prepend([=[{os.environ['KINTSUGI_PARSER_RUNTIME']}]=])"
                fixture = "flared.js" if language == "javascript" else "flared.ts"
                with tempfile.TemporaryDirectory() as isolated:
                    env = os.environ.copy()
                    for kind in ("CONFIG", "DATA", "STATE", "CACHE"):
                        env[f"XDG_{kind}_HOME"] = str(Path(isolated) / kind.lower())
                    result = subprocess.run([
                        "nvim", "--headless", "-u", "NONE", "-i", "NONE", "-n",
                        "--cmd", setup, str(ROOT / "tests/fixtures" / fixture),
                        "-c", "lua " + lua.replace("LANG", json.dumps(language)), "-c", "qa!",
                    ], capture_output=True, text=True, timeout=15, check=True, env=env)
                if result.stdout == "NO_PARSER":
                    if os.getenv("KINTSUGI_REQUIRE_PARSERS"):
                        self.fail(f"Required parser unavailable: {language}")
                    self.skipTest("Build isolated parsers with scripts/install-test-parsers.py to run fixture checks")
                self.assertTrue(result.stdout, result.stderr)
                actual = json.loads(result.stdout)
                keywords = ["const", "class", "constructor", "new"]
                if language != "javascript":
                    keywords.append("type")
                for keyword in keywords:
                    self.assertIn(keyword, actual)


if __name__ == "__main__":
    unittest.main()
