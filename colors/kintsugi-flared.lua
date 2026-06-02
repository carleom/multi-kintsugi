local source = debug.getinfo(1, "S").source:sub(2)
local root = vim.fn.fnamemodify(source, ":h:h")

dofile(root .. "/ports/neovim/colors/kintsugi-flared.lua")
