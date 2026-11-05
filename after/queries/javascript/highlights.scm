; extends

; Keep declaration keywords separate from control flow, as in VS Code Flared.
(["const" "let" "var" "class" "new"] @keyword.storage
  (#set! priority 110))

((method_definition
  name: (property_identifier) @keyword.storage)
  (#eq? @keyword.storage "constructor")
  (#set! priority 110))
