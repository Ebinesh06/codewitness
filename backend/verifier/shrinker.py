from .comparator import compare
from .executor import execute


def shrink(code_original: str, code_generated: str, function_name: str, inputs: list, timeout: float = 2.0) -> dict:
    current = list(inputs)
    candidates = [[0], [1], [-1], [50], [10], [10.005], [""], ["a"], [[]], [[1]], [None]] if len(current) == 1 else [[0] * len(current), [1] * len(current), [-1] * len(current)]
    for candidate in candidates:
        left = execute(code_original, function_name, candidate, timeout)
        right = execute(code_generated, function_name, candidate, timeout)
        if not compare(left, right)["equivalent"]:
            current = candidate
            break
    return {"inputs": current, "original": execute(code_original, function_name, current, timeout), "generated": execute(code_generated, function_name, current, timeout)}
