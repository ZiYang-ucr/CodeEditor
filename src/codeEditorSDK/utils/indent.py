from typing import List


class IndentHelper:
    def __init__(self, language: str):
        self.language = language

    def detect_indent(self, line: str) -> str:
        indent = []
        for char in line:
            if char in (' ', '\t'):
                indent.append(char)
            else:
                break
        return ''.join(indent)

    def get_indent_level(self, lines: List[str], insert_pos: int) -> str:
        if not lines:
            return ''
        if insert_pos < len(lines):
            return self.detect_indent(lines[insert_pos])
        return self.detect_indent(lines[-1])

    def apply_language_rules(self, lines: List[str], insert_pos: int, base_indent: str) -> str:
        """
        Apply language-specific indentation rules.
        :return: adjusted indentation
        """
        if self.language in ['python', 'java', 'cpp', 'c']:
            if insert_pos > 0:
                prev_line = lines[insert_pos - 1].rstrip()

                # Common rule: detect unclosed braces
                open_brace = prev_line.count('{') - prev_line.count('}')
                if open_brace > 0:
                    indent_size = 4
                    return base_indent + ' ' * indent_size

                # C/C++: do not indent after preprocessor directives
                if self.language in ['c', 'cpp'] and prev_line.startswith('#'):
                    return ''

                # Python: increase indent after colon
                if self.language == 'python' and prev_line.endswith(':'):
                    return base_indent + '    '
        return base_indent

    def normalize_code_indent(self, code: str, target_indent: str) -> str:
        """
        Remove common indentation from the code block and apply the target indentation.
        """
        lines = code.split('\n')
        min_indent = None
        for line in lines:
            stripped_line = line.lstrip(' \t')
            if stripped_line == '':
                continue
            indent = line[:len(line) - len(stripped_line)]
            if min_indent is None or len(indent) < len(min_indent):
                min_indent = indent
        min_indent = min_indent or ''
        adjusted = []
        for line in lines:
            if line.startswith(min_indent):
                adjusted_line = target_indent + line[len(min_indent):]
            else:
                adjusted_line = target_indent + line.lstrip()
            adjusted.append(adjusted_line)
        return '\n'.join(adjusted)