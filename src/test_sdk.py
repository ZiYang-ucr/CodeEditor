import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from codeEditorSDK.factories import MultiLangEditorFactory

py_editor = MultiLangEditorFactory.get_editor('python')


new_file = py_editor.insert(
    file_path='demo.py',
    start_line=3,
    code='if x > 0: print("Positive")'
)
case2 = py_editor.insert('demo.py', 5, '''
if x < 0:
    print("Negative")
    x = -x
''')


case3 = py_editor.insert('demo.py', 1, '''
def debug_info(msg):
    print(f"[DEBUG] {msg}")
''')
# new_file = py_editor.delete(
#     file_path='demo.py',
#     start_line=3,
#     end_line=20
# )

new_file = py_editor.update(
        file_path="demo.py",
        start_line=4,  # 替换 def add(a, b) 的内容
        end_line=6,
        new_code="""
result = a * b
print("Multiplying instead of adding")
return result
""".strip()
    )
print(f"生成文件: {new_file}")

java_editor = MultiLangEditorFactory.get_editor('Java')

new_file2 = java_editor.insert(
    file_path="Helloworld.java",
    start_line=3,
    code='Integer a = 5;'
)

case4 = java_editor.insert(file_path='HelloWorld.java', start_line=6, code='''
switch(day) {
    case 1: System.out.println("Monday"); break;
    case 2: System.out.println("Tuesday"); break;
    default: System.out.println("Other day");
}
''')
result = java_editor.smart_insert(
    file_path="HelloWorld.java",
    code='''
switch(day) {
    case 1: System.out.println("Monday"); break;
    case 2: System.out.println("Tuesday"); break;
    default: System.out.println("Other day");
}
'''
)
print(f"case4: 插入 switch 语句成功: {case4}")
print(f"生成文件: {result}")
