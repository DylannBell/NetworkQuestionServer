from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins

def run_restricted_python(code_to_run):
    # Run python code using RestrictedPython

    code_to_run = '''def compute(number): return (number*7)'''
    result = {}

    code = compile_restricted(code_to_run, '<string>', 'exec')
    exec(code, safe_builtins, result)

    # Run code with test case of 7
    output = (result['compute'](7))
    print(output)

    print("Error in attempting to run the code.")
    output = 0

    return output

run_restricted_python("nothing")