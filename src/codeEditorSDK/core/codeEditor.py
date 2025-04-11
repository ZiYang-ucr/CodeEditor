from pathlib import Path
from tree_sitter import Parser
from tree_sitter_languages import get_language
from typing import Optional
import os

class CodeFileEditor:
    def __init__(self, language: str):
        """
        初始化文件级代码编辑器
        :param language: 编程语言（支持 python, java, cpp, javascript 等）
        """
        self.language = language
        self.parser = None
        self._init_parser()
        
    def _init_parser(self):
        """初始化语法解析器"""
        try:
            # 新建 Parser 实例
            self.parser = Parser()
            # 使用 get_language 获取语言对象，然后设置到 parser 中
            self.parser.set_language(get_language(self.language))
        except Exception as e:
            raise RuntimeError(f"Parser initialization failed: {str(e)}")
    
    def _validate_syntax(self, code: str) -> bool:
        """验证代码语法有效性"""
        tree = self.parser.parse(bytes(code, "utf8"))
        return not tree.root_node.has_error


    def _detect_indent(self, line: str) -> str:
        """检测行的缩进字符（空格或制表符）"""
        indent = ''
        for char in line:
            if char in (' ', '\t'):
                indent += char
            else:
                break
        return indent

    def _get_indent_level(self, lines: list, insert_pos: int) -> str:
        """
        获取插入位置的缩进基准
        :param lines: 文件所有行
        :param insert_pos: 插入位置索引（从0开始）
        :return: 缩进字符串
        """
        # 默认取插入位置的当前行缩进
        if not lines:
            return ' '
        if insert_pos < len(lines):
            return self._detect_indent(lines[insert_pos])
        
        # 文件末尾则取最后一行缩进
        if lines:
            return self._detect_indent(lines[-1])
        
        return ''  # 空文件无缩进

    def _normalize_code_indent(self, code: str, target_indent: str) -> str:
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
    def _apply_language_rules(self, lines: list, insert_pos: int, base_indent: str) -> str:
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

    def smart_insert(self, file_path: str, code: str) -> Optional[str]:
        """
        智能插入：自动在方法体内部寻找合适的插入点。如果找不到合法插入位置，则返回警告。
        对于不同语言，搜索策略为：
          - Python: 查找第一个 function_definition 的 body（block）
          - Java/C/C++: 查找第一个 method_declaration（或 function_definition）的 body（block）
        :param file_path: 目标文件路径
        :param code: 待插入的代码
        :return: 新文件路径，如果无法插入则返回 None
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
                    # 返回方法体起始行号（行号从0开始）
                    return body.start_point[0] + 1
            for child in node.children:
                result = find_method_body_insert_line(child)
                if result is not None:
                    return result
            return None

        insert_line = find_method_body_insert_line(root)
        if insert_line is None:
            print("未找到合法的插入位置（未检测到方法体）")
            return None

        # 调用 insert 函数直接在该行号插入代码
        try:
            # 因为 insert 接口要求行号从1开始，所以将插入行号加1
            return self.insert(file_path, insert_line + 1, code)
        except SyntaxError as se:
            print(f"插入后语法检查失败: {se}")
            return None

    def insert(self, file_path: str, start_line: int, code: str) -> str:
        path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        normalized_line = max(1, min(start_line, len(lines)+1))
        insert_pos = normalized_line - 1
        
        # 计算基准缩进
        base_indent = self._get_indent_level(lines, insert_pos)
        # 应用语言规则调整缩进
        final_indent = self._apply_language_rules(lines, insert_pos, base_indent)
        # 规范化代码缩进
        normalized_code = self._normalize_code_indent(code, final_indent)
        formatted_code = normalized_code.rstrip('\n') + '\n'  # 确保单一行尾换行
        
        new_lines = lines[:insert_pos] + [formatted_code] + lines[insert_pos:]
        new_content = ''.join(new_lines)
            
        # # 处理多行代码缩进
        # formatted_code = []
        # for i, line in enumerate(code.split('\n')):
        #     # 首行对齐插入位置，后续行使用完整缩进
        #     indent = final_indent if i > 0 else base_indent
        #     formatted_code.append(indent + line)
        
        # new_lines = lines[:insert_pos] + ['\n'.join(formatted_code) + '\n'] + lines[insert_pos:]
        # new_content = ''.join(new_lines)
        
        if not self._validate_syntax(new_content):
            raise SyntaxError("Insertion causes syntax errors")
        
        new_path = path.parent / f"{path.stem}_inserted{path.suffix}"
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return str(new_path)
    def delete(self, file_path: str, start_line: int, end_line: int) -> str:
        """
        删除指定行范围的代码
        :param file_path: 目标文件路径
        :param start_line: 起始行（包含）
        :param end_line: 结束行（包含）
        :return: 新文件路径（原文件名_deleted.ext）
        """
        path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start = max(1, min(start_line, len(lines)))
        end = max(start, min(end_line, len(lines)))
        
        new_lines = lines[:start-1] + lines[end:]
        new_content = ''.join(new_lines)
        
        if not self._validate_syntax(new_content):
            raise SyntaxError("Deletion causes syntax errors")
        
        new_path = path.parent / f"{path.stem}_deleted{path.suffix}"
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return str(new_path)

    def update(self, file_path: str, start_line: int, end_line: int, new_code: str) -> str:
        """
        替换指定行范围的代码（包含自动缩进）
        :param file_path: 目标文件路径
        :param start_line: 起始行（包含）
        :param end_line: 结束行（包含）
        :param new_code: 新的代码内容
        :return: 新文件路径（原文件名_updated.ext）
        """
        path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start = max(1, min(start_line, len(lines)))
        end = max(start, min(end_line, len(lines)))

        insert_pos = start - 1

        # 自动缩进（使用 insert 中的方法）
        base_indent = self._get_indent_level(lines, insert_pos)
        final_indent = self._apply_language_rules(lines, insert_pos, base_indent)

        formatted_code = []
        for i, line in enumerate(new_code.split('\n')):
            indent = final_indent if i > 0 else base_indent
            formatted_code.append(indent + line)

        new_lines = lines[:start-1] + ['\n'.join(formatted_code) + '\n'] + lines[end:]
        new_content = ''.join(new_lines)

        if not self._validate_syntax(new_content):
            raise SyntaxError("Update causes syntax errors")

        new_path = path.parent / f"{path.stem}_updated{path.suffix}"
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return str(new_path)
    def query(self, file_path: str, start_line: int, end_line: int) -> str:
        """
        查询指定行范围的代码
        :param file_path: 目标文件路径
        :param start_line: 起始行（包含）
        :param end_line: 结束行（包含）
        :return: 代码片段字符串
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start = max(1, min(start_line, len(lines)))
        end = max(start, min(end_line, len(lines)))
        
        return ''.join(lines[start-1:end])
