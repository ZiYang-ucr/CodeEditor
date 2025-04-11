from tree_sitter import Parser

def validate_syntax(parser: Parser, code: str) -> bool:
    tree = parser.parse(bytes(code, "utf8"))
    return not tree.root_node.has_error