import ast

from .comparator import compare
from .evidence import build_evidence
from .executor import execute
from .hashing import source_hash
from .shrinker import shrink
from .test_generator import generate_inputs
from .verdict import make_verdict
from backend.ai.property_extractor import extract_properties


def verify(original_code: str, generated_code: str, function_name: str, intent: str | None = None, rerun_inputs: list | None = None) -> dict:
    original_tree = ast.parse(original_code)
    generated_tree = ast.parse(generated_code)
    for tree, label in ((original_tree, "Original"), (generated_tree, "Generated")):
        if not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name for node in tree.body):
            raise ValueError(f"{label} function '{function_name}' was not found")
    corpus = [rerun_inputs] if rerun_inputs is not None else generate_inputs(original_code, function_name)
    properties = extract_properties(original_code, generated_code, intent)
    executions = []
    for inputs in corpus:
        original = execute(original_code, function_name, inputs)
        generated = execute(generated_code, function_name, inputs)
        executions.append({"inputs": inputs, "original": original, "generated": generated, "comparison": compare(original, generated)})
    failures = [item for item in executions if not item["comparison"]["equivalent"]]
    counterexample = None
    if failures and rerun_inputs is None:
        counterexample = shrink(original_code, generated_code, function_name, failures[0]["inputs"])
    if failures and rerun_inputs is not None:
        counterexample = {"inputs": failures[0]["inputs"], "original": failures[0]["original"], "generated": failures[0]["generated"]}
    execution_error = any((item[side].get("exception") or {}).get("type") == "TimeoutError" for item in executions for side in ("original", "generated"))
    verdict = make_verdict(len(failures), execution_error)
    reproducibility = {"requested": rerun_inputs is not None, "reproduced": bool(rerun_inputs is not None and failures)}
    evidence = build_evidence(function_name, properties, corpus, executions, counterexample, verdict, (source_hash(original_code), source_hash(generated_code)), reproducibility)
    return {"verdict": verdict, "metrics": {"tests_generated": len(corpus), "tests_executed": len(executions), "divergences": len(failures), "execution_time_ms": round(sum(item["original"]["duration_ms"] + item["generated"]["duration_ms"] for item in executions), 3)}, "properties": properties, "counterexample": counterexample, "reproduced": reproducibility["reproduced"], "executions": executions, "evidence": evidence}
