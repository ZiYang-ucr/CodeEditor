from pathlib import Path
from tree_sitter import Parser
from tree_sitter_languages import get_language
from codeEditorSDK.utils.indent import IndentHelper
from codeEditorSDK.utils.validation import SyntaxValidator
from typing import Optional

import os

class CodeFileEditor:
    def __init__(self, language: str):
        """
        Initialize a file-level code editor.
        :param language: Programming language (supported: python, java, cpp, javascript, etc.)
        """
        self.language = language
        self.parser = None
        self.indent_helper = IndentHelper(language)
        self.validator = SyntaxValidator(language)
        self._init_parser()


        
    def _init_parser(self):
        """Initialize the syntax parser"""
        try:
            # create instance of Parser
            self.parser = Parser()
            # use get_language to get the language parser
            self.parser.set_language(get_language(self.language))
        except Exception as e:
            raise RuntimeError(f"Parser initialization failed: {str(e)}")   

    def _apply_language_rules(self, lines: list, insert_pos: int, base_indent: str) -> str:
        """
        Apply language-specific indentation rules.
        :return: Adjusted indentation
        """
        if self.language in ['python', 'java', 'cpp', 'c']:
            if insert_pos > 0:
                prev_line = lines[insert_pos-1].rstrip()
                
                # general rule: detect unclosed braces
                open_brace = prev_line.count('{') - prev_line.count('}')
                if open_brace > 0:
                    indent_size = 4 if self.language in ['java', 'cpp', 'c'] else 4
                    return base_indent + ' ' * indent_size

                # C/C++ special rule: do not indent after preprocessor directives
                if self.language in ['c', 'cpp'] and prev_line.startswith('#'):
                    return ''  # preprocessor directives do not require indentation

                # Pytonh special rule: increase indent after a colon
                if self.language == 'python' and prev_line.endswith(':'):
                    return base_indent + '    '
        return base_indent

    def smart_insert(self, file_path: str, code: str) -> Optional[str]:
        """
        Smart insert: automatically find a legal insertion point inside a method body.
        If no legal insertion point is found, a warning is returned.
        For different languages, the search strategy is:
          - Python: locate the body of the first function_definition
          - Java/C/C++: locate the body of the first method_declaration or function_definition
        :param file_path: Target file path
        :param code: Code to be inserted
        :return: New file path, or None if insertion fails
        """
        path = Path(file_path)
        source_code = path.read_text(encoding="utf-8")
        tree = self.parser.parse(bytes(source_code, "utf8"))
        root = tree.root_node
        lines = source_code.splitlines()
        
        def find_method_body_insert_line(node):
            if self.language == "python":
                target_type = "function_definition"
                body_type = "block"
            elif self.language in ["java", "cpp", "c"]:
                target_type = "method_declaration" if self.language == "java" else "function_definition"
                body_type = "block"
            else:
                return None

            if node.type == target_type:
                body = node.child_by_field_name("body")
                if body and body.type == body_type:
                    # return body.startPoint + 1
                    return body.start_point[0] + 1
            for child in node.children:
                result = find_method_body_insert_line(child)
                if result is not None:
                    return result
            return None

        insert_line = find_method_body_insert_line(root)
        if insert_line is None:
            print("not find a legal insertion point")
            return None

        # use the insert method to insert the code
        try:
            # because the insert method will check the syntax, so we can use it to check the syntax
            return self.insert(file_path, insert_line + 1, code)
        except SyntaxError as se:
            print(f"Insertion failed due to syntax error: {se}")
            return None

    def insert(self, file_path: str, start_line: int, code: str) -> str:
        path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        normalized_line = max(1, min(start_line, len(lines)+1))
        insert_pos = normalized_line - 1
        
        # cacuate base indent
        base_indent = self.indent_helper.get_indent_level(lines, insert_pos)
        # apply langugage rules
        final_indent = self.indent_helper.apply_language_rules(lines, insert_pos, base_indent)
        # normalize code indent
        normalized_code = self.indent_helper.normalize_code_indent(code, final_indent)
        formatted_code = normalized_code.rstrip('\n') + '\n'  # insure the last line is \n
        
        new_lines = lines[:insert_pos] + [formatted_code] + lines[insert_pos:]
        new_content = ''.join(new_lines)
            
        if not self.validator.validate_syntax(new_content):
            raise SyntaxError("Insertion causes syntax errors")
        
        new_path = path.parent / f"{path.stem}_inserted{path.suffix}"
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return str(new_path)
    def delete(self, file_path: str, start_line: int, end_line: int) -> str:
        """
        Delete code in a specified line range.
        :param file_path: Target file path
        :param start_line: Start line (inclusive)
        :param end_line: End line (inclusive)
        :return: New file path (original name + _deleted suffix)
        """
        path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start = max(1, min(start_line, len(lines)))
        end = max(start, min(end_line, len(lines)))
        
        new_lines = lines[:start-1] + lines[end:]
        new_content = ''.join(new_lines)
        
        if not self.validator.validate_syntax(new_content):
            raise SyntaxError("Deletion causes syntax errors")
        
        new_path = path.parent / f"{path.stem}_deleted{path.suffix}"
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return str(new_path)

    def update(self, file_path: str, start_line: int, end_line: int, new_code: str) -> str:
        """
        Replace code in a specified line range (with automatic indentation).
        :param file_path: Target file path
        :param start_line: Start line (inclusive)
        :param end_line: End line (inclusive)
        :param new_code: New code content
        :return: New file path (original name + _updated suffix)
        """
        path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start = max(1, min(start_line, len(lines)))
        end = max(start, min(end_line, len(lines)))

        insert_pos = start - 1

        base_indent = self.indent_helper.get_indent_level(lines, insert_pos)
        final_indent = self.indent_helper.apply_language_rules(lines, insert_pos, base_indent)

        formatted_code = []
        for i, line in enumerate(new_code.split('\n')):
            indent = final_indent if i > 0 else base_indent
            formatted_code.append(indent + line)

        new_lines = lines[:start-1] + ['\n'.join(formatted_code) + '\n'] + lines[end:]
        new_content = ''.join(new_lines)

        if not self.validator.validate_syntax(new_content):
            raise SyntaxError("Update causes syntax errors")

        new_path = path.parent / f"{path.stem}_updated{path.suffix}"
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return str(new_path)
    def query(self, file_path: str, start_line: int, end_line: int) -> str:
        """
        Query code in a specified line range.
        :param file_path: Target file path
        :param start_line: Start line (inclusive)
        :param end_line: End line (inclusive)
        :return: Code snippet as a string
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start = max(1, min(start_line, len(lines)))
        end = max(start, min(end_line, len(lines)))
        
        return ''.join(lines[start-1:end])
