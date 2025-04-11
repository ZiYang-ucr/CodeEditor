from typing import List

def detect_indent(line: str) -> str:
    indent = []
    for char in line:
        if char in (' ', '\t'):
            indent.append(char)
        else:
            break
    return ''.join(indent)

def get_indent_level(lines: List[str], insert_pos: int) -> str:
    if not lines:
        return ''
    if insert_pos < len(lines):
        return detect_indent(lines[insert_pos])
    return detect_indent(lines[-1])

def apply_language_rules(self, lines: list, insert_pos: int, base_indent: str) -> str:
    """
    应用语言特定缩进规则
    :return: 调整后的缩进
    """
    if self.language in ['python', 'java', 'cpp', 'c']:
        if insert_pos > 0:
            prev_line = lines[insert_pos-1].rstrip()
            
            # 通用规则：检测未闭合大括号
            open_brace = prev_line.count('{') - prev_line.count('}')
            if open_brace > 0:
                indent_size = 4 if self.language in ['java', 'cpp', 'c'] else 4
                return base_indent + ' ' * indent_size

            # C/C++ 特殊规则：预处理指令不缩进
            if self.language in ['c', 'cpp'] and prev_line.startswith('#'):
                return ''  # 预处理指令后不缩进

            # Python 特殊规则：冒号结尾增加缩进
            if self.language == 'python' and prev_line.endswith(':'):
                return base_indent + '    '
    return base_indent

def normalize_code_indent(self, code: str, target_indent: str) -> str:
    """去除代码块的公共缩进，并应用目标缩进"""
    lines = code.split('\n')
    # 计算最小缩进
    min_indent = None
    for line in lines:
        stripped_line = line.lstrip(' \t')
        if stripped_line == '':  # 忽略空行
            continue
        indent = line[:len(line)-len(stripped_line)]
        if min_indent is None or len(indent) < len(min_indent):
            min_indent = indent
    min_indent = min_indent or ''
    # 去除公共缩进并应用新缩进
    adjusted = []
    for line in lines:
        if line.startswith(min_indent):
            adjusted_line = target_indent + line[len(min_indent):]
        else:
            adjusted_line = target_indent + line.lstrip()
        adjusted.append(adjusted_line)
    return '\n'.join(adjusted)