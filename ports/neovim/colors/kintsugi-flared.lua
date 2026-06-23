vim.cmd("highlight clear")

if vim.fn.exists("syntax_on") == 1 then
  vim.cmd("syntax reset")
end

vim.g.colors_name = "kintsugi-flared"
vim.o.termguicolors = true

local c = {
  bg = "#161618",
  bg_dark = "#131314",
  bg_panel = "#20201f",
  bg_element = "#292928",
  bg_highlight = "#1d1d1c",
  border = "#2a2a28",
  fg = "#dddddd",
  fg_soft = "#c9c4b8",
  fg_muted = "#75715e",
  syntax = "#BCAC8F",
  comment = "#5f5f5f",
  punctuation = "#7f7b66",
  keyword = "#D66848",
  storage = "#DBAD49",
  operator = "#E08542",
  string = "#cc7f66",
  number = "#DB9833",
  symbol = "#798283",
  attribute = "#678E87",
  pointer = "#EBA96C",
  accent = "#b8943a",
  cursor = "#d4a943",
  blue = "#6c7a8a",
  blue_bright = "#8fa3b3",
  cyan = "#6ac6f2",
  green = "#a3be8c",
  red = "#b38f8f",
  yellow = "#ebcb8b",
  magenta = "#b3a3d3",
}

local function hi(group, opts)
  vim.api.nvim_set_hl(0, group, opts)
end

hi("Normal", { fg = c.fg, bg = c.bg })
hi("NormalFloat", { fg = c.fg_soft, bg = c.bg_panel })
hi("FloatBorder", { fg = c.border, bg = c.bg_panel })
hi("ColorColumn", { bg = c.bg_panel })
hi("Cursor", { fg = c.bg_dark, bg = c.cursor })
hi("CursorLine", { bg = c.bg_highlight })
hi("CursorLineNr", { fg = c.storage, bold = true })
hi("LineNr", { fg = "#444444" })
hi("SignColumn", { bg = c.bg })
hi("Folded", { fg = c.fg_muted, bg = "#1f1f1f" })
hi("VertSplit", { fg = c.border })
hi("WinSeparator", { fg = c.border })
hi("StatusLine", { fg = c.fg_soft, bg = c.bg_dark })
hi("StatusLineNC", { fg = c.fg_muted, bg = c.bg_dark })
hi("Pmenu", { fg = c.fg_soft, bg = c.bg_panel })
hi("PmenuSel", { fg = c.fg, bg = "#393b31" })
hi("PmenuSbar", { bg = c.bg_element })
hi("PmenuThumb", { bg = c.fg_muted })
hi("Visual", { fg = c.fg, bg = "#2a3035" })
hi("Search", { fg = c.fg, bg = "#303740" })
hi("IncSearch", { fg = c.bg_dark, bg = c.yellow })
hi("MatchParen", { fg = c.fg, bg = "#353d45" })
hi("Directory", { fg = c.storage })
hi("ErrorMsg", { fg = c.red })
hi("WarningMsg", { fg = c.yellow })
hi("MoreMsg", { fg = c.green })
hi("Question", { fg = c.green })
hi("NonText", { fg = c.comment })
hi("SpecialKey", { fg = c.comment })
hi("Whitespace", { fg = "#30302e" })

hi("Comment", { fg = c.comment })
hi("Constant", { fg = c.number })
hi("String", { fg = c.string })
hi("Character", { fg = c.symbol })
hi("Number", { fg = c.number })
hi("Boolean", { fg = c.number })
hi("Float", { fg = c.number })
hi("Identifier", { fg = c.syntax })
hi("Function", { fg = c.symbol })
hi("Statement", { fg = c.keyword, bold = true })
hi("Conditional", { fg = c.keyword, bold = true })
hi("Repeat", { fg = c.keyword, bold = true })
hi("Label", { fg = c.keyword, bold = true })
hi("Operator", { fg = c.operator })
hi("Keyword", { fg = c.keyword, bold = true })
hi("Exception", { fg = c.keyword, bold = true })
hi("PreProc", { fg = c.symbol })
hi("Include", { fg = c.keyword, bold = true })
hi("Define", { fg = c.symbol })
hi("Macro", { fg = c.symbol })
hi("PreCondit", { fg = c.symbol })
hi("Type", { fg = c.operator })
hi("StorageClass", { fg = c.storage, bold = true })
hi("Structure", { fg = c.storage, bold = true })
hi("Typedef", { fg = c.operator })
hi("Special", { fg = c.pointer })
hi("SpecialChar", { fg = c.symbol })
hi("Tag", { fg = c.storage, bold = true })
hi("Delimiter", { fg = c.punctuation })
hi("Debug", { fg = c.red })
hi("Underlined", { fg = c.blue_bright, underline = true })
hi("Ignore", { fg = c.fg_muted })
hi("Error", { fg = c.red })
hi("Todo", { fg = c.yellow, bg = c.bg_panel, bold = true })

hi("DiagnosticError", { fg = c.red })
hi("DiagnosticWarn", { fg = c.yellow })
hi("DiagnosticInfo", { fg = c.blue_bright })
hi("DiagnosticHint", { fg = c.green })
hi("DiagnosticVirtualTextError", { fg = c.red, bg = "#2b2525" })
hi("DiagnosticVirtualTextWarn", { fg = c.yellow, bg = "#302b20" })
hi("DiagnosticVirtualTextInfo", { fg = c.blue_bright, bg = "#25282c" })
hi("DiagnosticVirtualTextHint", { fg = c.green, bg = "#293028" })

hi("DiffAdd", { fg = c.green, bg = "#20241f" })
hi("DiffChange", { fg = c.yellow, bg = "#25231d" })
hi("DiffDelete", { fg = c.red, bg = "#231f20" })
hi("DiffText", { fg = c.yellow, bg = "#302b20" })

hi("GitSignsAdd", { fg = c.green, bg = c.bg })
hi("GitSignsChange", { fg = c.yellow, bg = c.bg })
hi("GitSignsDelete", { fg = c.red, bg = c.bg })

hi("TreesitterContext", { bg = c.bg_panel })
hi("@comment", { fg = c.comment })
hi("@punctuation", { fg = c.punctuation })
hi("@punctuation.bracket", { fg = c.punctuation })
hi("@punctuation.delimiter", { fg = c.punctuation })
hi("@keyword", { fg = c.keyword, bold = true })
hi("@keyword.conditional", { fg = c.keyword, bold = true })
hi("@keyword.coroutine", { fg = c.keyword, bold = true })
hi("@keyword.exception", { fg = c.keyword, bold = true })
hi("@keyword.function", { fg = c.storage, bold = true })
hi("@keyword.import", { fg = c.keyword, bold = true })
hi("@keyword.modifier", { fg = c.storage, bold = true })
hi("@keyword.operator", { fg = c.operator })
hi("@keyword.repeat", { fg = c.keyword, bold = true })
hi("@keyword.return", { fg = c.keyword, bold = true })
hi("@keyword.storage", { fg = c.storage, bold = true })
hi("@keyword.storage.javascript", { fg = c.storage, bold = true })
hi("@keyword.storage.typescript", { fg = c.storage, bold = true })
hi("@keyword.storage.tsx", { fg = c.storage, bold = true })
hi("@operator", { fg = c.operator })
hi("@string", { fg = c.string })
hi("@string.escape", { fg = c.symbol })
hi("@number", { fg = c.number })
hi("@boolean", { fg = c.number })
hi("@constant", { fg = c.number })
hi("@constant.builtin", { fg = c.number })
hi("@function", { fg = c.symbol })
hi("@function.builtin", { fg = c.operator })
hi("@function.call", { fg = c.symbol })
hi("@function.method", { fg = c.symbol })
hi("@function.method.call", { fg = c.symbol })
hi("@constructor", { fg = c.storage, bold = true })
hi("@variable", { fg = c.syntax })
hi("@variable.builtin", { fg = c.storage, bold = true })
hi("@variable.member", { fg = c.symbol })
hi("@variable.parameter", { fg = c.syntax })
hi("@property", { fg = c.syntax })
hi("@module", { fg = c.symbol })
hi("@namespace", { fg = c.symbol })
hi("@type", { fg = c.symbol })
hi("@type.builtin", { fg = c.operator })
hi("@type.definition", { fg = c.symbol })
hi("@tag", { fg = c.storage, bold = true })
hi("@tag.attribute", { fg = c.symbol })
hi("@tag.delimiter", { fg = c.punctuation })
hi("@attribute", { fg = c.attribute })
hi("@keyword.directive", { fg = c.keyword, bold = true })
hi("@markup.heading", { fg = c.storage, bold = true })
hi("@markup.link", { fg = c.symbol })
hi("@markup.raw", { fg = c.string })

hi("@lsp.type.class", { fg = c.symbol })
hi("@lsp.type.enum", { fg = c.symbol })
hi("@lsp.type.enumMember", { fg = c.number })
hi("@lsp.type.function", { fg = c.symbol })
hi("@lsp.type.interface", { fg = c.symbol })
hi("@lsp.type.method", { fg = c.symbol })
hi("@lsp.type.namespace", { fg = c.symbol })
hi("@lsp.type.parameter", { fg = c.syntax })
hi("@lsp.type.property", { fg = c.symbol })
hi("@lsp.type.struct", { fg = c.symbol })
hi("@lsp.type.type", { fg = c.symbol })
hi("@lsp.type.typeParameter", { fg = c.operator })
hi("@lsp.type.variable", { fg = c.syntax })
hi("@lsp.typemod.property.declaration", { fg = c.syntax })
hi("@lsp.typemod.property.declaration.typescript", { fg = c.syntax })
hi("@lsp.typemod.property.declaration.svelte", { fg = c.syntax })

hi("@field", { fg = c.symbol })
hi("@parameter", { fg = c.syntax })
hi("@namespace", { fg = c.symbol })
hi("@symbol", { fg = c.symbol })

hi("NeoTreeDirectoryIcon", { fg = c.storage })
hi("NeoTreeDirectoryName", { fg = c.storage, bold = true })
hi("NeoTreeFileName", { fg = c.fg_soft })
hi("NeoTreeFileNameOpened", { fg = c.fg, bold = true })
hi("NvimTreeFolderIcon", { fg = c.storage })
hi("NvimTreeFolderName", { fg = c.storage, bold = true })
hi("NvimTreeFileIcon", { fg = c.fg_soft })
hi("NvimTreeNormal", { fg = c.fg_soft, bg = c.bg_dark })

vim.g.terminal_color_0 = c.bg_dark
vim.g.terminal_color_1 = c.red
vim.g.terminal_color_2 = c.green
vim.g.terminal_color_3 = c.yellow
vim.g.terminal_color_4 = c.blue
vim.g.terminal_color_5 = c.magenta
vim.g.terminal_color_6 = c.cyan
vim.g.terminal_color_7 = c.fg
vim.g.terminal_color_8 = "#444444"
vim.g.terminal_color_9 = "#d9a6a6"
vim.g.terminal_color_10 = "#c3de9c"
vim.g.terminal_color_11 = "#fbe4a8"
vim.g.terminal_color_12 = c.blue_bright
vim.g.terminal_color_13 = "#d3a3d3"
vim.g.terminal_color_14 = "#8ac6f2"
vim.g.terminal_color_15 = "#ffffff"
