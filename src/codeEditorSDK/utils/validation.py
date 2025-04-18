from tree_sitter import Parser
from tree_sitter_languages import get_language


class SyntaxValidator:
    def __init__(self, language: str):
        """
        Initialize the syntax validator for a specific language.
        :param language: e.g., 'python', 'java', 'cpp', etc.
        """
        self.language = language
        self.parser = Parser()
        try:
            self.parser.set_language(get_language(language))
        except Exception as e:
            raise RuntimeError(f"Failed to set parser language '{language}': {e}")

    def validate_syntax(self, code: str) -> bool:
        """
        Validate if the code has correct syntax.
        :param code: Code string to validate.
        :return: True if syntax is valid, False otherwise.
        """
        tree = self.parser.parse(bytes(code, "utf8"))
        return not tree.root_node.has_error