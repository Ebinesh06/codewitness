import ast
from itertools import product

VALUES = [-100, -1, 0, 1, 2, 49, 50, 51, 100, 0.1, 10.005, 99.99, "", "a", "test", [], [1], [1, 2], None]

def _constants(tree):
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, str)) and node.value not in found:
            found.append(node.value)
    return found

def generate_inputs(code: str, function_name: str):
    tree = ast.parse(code)
    function = next((node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name), None)
    if function is None:
        raise ValueError(f"Function '{function_name}' was not found")
    arity = len(function.args.args)
    if arity == 0:
        return [[]]
    values = list(VALUES)
    for value in _constants(tree):
        if value not in values:
            values.append(value)
    if arity == 1:
        return [[value] for value in values]
    common = [-1, 0, 1, 2, 10, 49, 50, 51, 100, 0.1, 10.005, "", "a", [], [1], None]
    return [list(args) for args in product(common, repeat=arity)][:250]
