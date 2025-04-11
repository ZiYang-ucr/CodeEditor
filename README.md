# Code Editor SDK

A multi-language source code editing SDK using Tree-sitter. Supports Python, Java, C, C++, JavaScript.

## Features

- Smart code insertion (auto-locates method bodies)
- Syntax-safe deletion, update, query
- Auto-indentation based on language
- Supports Python, Java, C/C++, JavaScript

## Install via GitHub
pip install git https://github.com/ZiYang-ucr/CodeEditor.git

## Example

```python
from code_editor import MultiLangEditorFactory

editor = MultiLangEditorFactory.get_editor("python")
editor.smart_insert("demo.py", 'print("inserted")')