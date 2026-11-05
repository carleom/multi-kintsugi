; extends

; Core TypeScript queries inherit ecma, not JavaScript's extension file.
(["const" "let" "var" "class" "new" "type" "interface" "enum" "namespace"] @keyword.storage
  (#set! priority 110))

((method_definition
  name: (property_identifier) @keyword.storage)
  (#eq? @keyword.storage "constructor")
  (#set! priority 110))
