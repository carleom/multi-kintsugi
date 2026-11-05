# Flared's cross-app contract

`flared.json` owns the shared colors and semantic roles. The original
[`Kintsugi-Dark-Flared-color-theme.json`](../themes/Kintsugi-Dark-Flared-color-theme.json)
is the reference for syntax, not the terminal's sixteen ANSI slots. Tests compare
the contract with that original so the ports cannot silently redefine Flared.

## Stable meanings

| Role | Color | Meaning |
| --- | --- | --- |
| Keyword | `#D66848` | Control flow and language keywords |
| Storage | `#DBAD49` | Declarations, `this`/`self`, markup tags |
| Symbol | `#798283` | User-defined functions, classes, types, named constants |
| Variable | `#BCAC8F` | Ordinary identifiers; language-specific property exceptions |
| Built-in/support | `#E08542` | Built-in types/functions and generic library support |
| String | `#cc7f66` | Strings and Markdown inline code |
| Number | `#DB9833` | Numbers, booleans and built-in literals |
| Attribute | `#678E87` | Decorators, annotations and compiler metadata |
| Heading/strong | `#DBAD49` | Markdown hierarchy, not language control flow |
| Feedback | red/amber/green/blue | Error/warning/success/information, respectively |

Rendered link labels use symbol gray; visible URLs use muted blue. Italics
retain their surrounding text color. Markdown list markers use heading gold.
These are deliberate rendered-Markdown conventions where the original editor
theme does not define a complete role independently.

## Deliberate differences

- **Editor versus prose:** editable code keeps the original `#161618` editor
  background and `#dddddd` default foreground. Chat/prose and terminal defaults
  use warm `#d4c7ad` text on `#131314`. This changes surface hierarchy, not syntax.
- **ANSI is not syntax:** all sixteen ANSI colors match the original VS Code
  terminal palette. A terminal cannot decide that red means a keyword or that
  yellow means a declaration. Truecolor applications own their syntax colors.
- **Selection:** terminal/prose selection uses opaque warm `#4a4030`. Editor
  selection keeps the original cool overlay approximation. This is intentional.
- **Coarse tokenizers:** OpenCode and Oh My Pi expose only nine syntax colors.
  Their general `type` slot uses user-type gray. They cannot separately express
  gold storage keywords, orange built-in types or teal annotations. No palette
  can fix a parser assigning a token to a different category.
- **Highlight engines:** VS Code uses TextMate here (`semanticHighlighting` is
  off); Neovim combines Tree-sitter with LSP semantic highlights. The Neovim
  adapter keeps language-specific property overrides, rather than pretending
  every capture has an exact TextMate equivalent.
  Bundled JS/TS declaration queries keep `const`, `class`, `new` and related
  declarations gold instead of relying on upstream generic keyword captures.
- **Bold and code blocks:** OpenCode can color strong text gold. Oh My Pi can
  make it bold but offers no separate strong-color token. Unclassified code-block
  text uses soft text in chat renderers; classified tokens use syntax colors.
- **Light mode:** this contract is for Dark Flared. Obsidian's existing light
  palette is retained, with its own dark-enough bold color instead of inheriting
  a pale dark-mode value. The other VS Code variants are not recolored.

## Maintaining and comparing

```sh
python3 scripts/sync-themes.py
python3 scripts/sync-themes.py --check
python3 -m unittest discover -s tests -v
python3 scripts/preview-themes.py
```

The synchronizer updates shared palette sections and mappings in the existing
adapters; it preserves app-specific Neovim groups, OMP renderer/status settings
and Obsidian light-mode CSS. The OpenCode adapter retains the established flat
`defs`/`theme` compatibility format used by this installation.

The Neovim plugin installs its query extensions automatically. For a standalone
installation, copy **both** `ports/neovim/colors` and `ports/neovim/after` into
your Neovim configuration (merge directories; do not replace your configuration).
CI builds pinned JavaScript, TypeScript and TSX parsers and their upstream base
queries, then requires fixture tests in isolated XDG directories rather than
depending on installed user plugins. To reproduce that isolated setup:

```sh
python3 scripts/install-test-parsers.py /path/to/temporary-runtime
KINTSUGI_PARSER_RUNTIME=/path/to/temporary-runtime KINTSUGI_REQUIRE_PARSERS=1 python3 -m unittest discover -s tests -v
```

For parser comparisons, open [`flared.ts`](../tests/fixtures/flared.ts) and
[`flared.md`](../tests/fixtures/flared.md) in each app. The preview resolves the
actual adapter files; it is a swatch/role check, not a claim to reproduce an app's
syntax parser or font rasterizer. Neovim tests additionally load the real
colorscheme and inspect resolved highlight groups.

Rex imports a **copy** of the Ghostty theme, not a live link. Re-import after
changing the file. Keep **Force theme palette for text** off for truecolor
applications; use matching contrast and color-space settings when comparing.
Font family, fallback metrics, ligatures and glyph overlap are separate from
this color contract.
