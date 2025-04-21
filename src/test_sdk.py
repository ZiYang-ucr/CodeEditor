import sys
import os
from codeEditorSDK.core.EditBuilder import EditBuilder

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
        start_line=4,  
        end_line=6,
        new_code="""
result = a * b
print("Multiplying instead of adding")
return result
""".strip()
    )
print(f"Generate files: {new_file}")

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
print(f"case4: insert switch statements success: {case4}")
print(f"complete success: {result}")




## Test for swpping operators in Python 
op_swapped = py_editor.swap_operator('demo2.py', '==', '!=')
print(f"swpped all file success: path is : {op_swapped}")

op_swapped = py_editor.swap_operator('demo2.py', '==', '!=',func="loop_and_sum")
print(f"swpped func success: path is : {op_swapped}")

## Test for renaming variables in Python
# renamed = py_editor.rename_var('demo2.py', 'a', 'e')
renamed = py_editor.rename_var('demo2.py','a', 'new_var',func="nested_loop")
renamed = py_editor.rename_var('demo2.py','a', 'new_var')
renamed = py_editor.rename_var('demo2.py','n', 'new_var',func="loop_and_sum",include_param = True)


output = py_editor.change_type(file_path='demo2.py', from_type='float',to_type='double')

##include_param only used for function parameters, not for all file
output = py_editor.change_type(file_path='demo2.py', from_type='float',to_type='double',func='compute_area',include_param=True)


# output = py_editor.unroll_loop(file_path='demo2.py', func='loop_and_sum')

output = py_editor.swap_condition_operator(file_path='demo2.py', old_op='*',new_op='/')


# begin chained edit operations, no need to call apply() after each operation
builder = EditBuilder(py_editor, file_path='demo2.py')

# chained operations
builder.rename_var(old_name='radius', new_name='r', func='compute_area')\
       .change_type(from_type='float', to_type='double', func='compute_area')\
       .operator_swap(old='*', new='-', func='compute_area')\
       .condition_operator_swap(old_op='>', new_op='<=', func='compute_area')\
       .insert_code("print('Debug insert')")\
       .insert_code_lines(9, "print('Area check')")\
       .update_lines(12, 12, new_code="print('I just updated this line ')")\
       .apply()


# builder = EditBuilder(py_editor, file_path="demo2.py")
# builder.insert_code_lines(4,"print('simple zi  yang line')")\
#        .insert_code(
#            code="print('I just inserted a line')"
#        )\
#     .apply()

# builder.insert_code(code="print('I just inserted a line')").apply()

# py_editor.smart_insert(
#     file_path="demo2.py",
#     code="print('simple line')")
    