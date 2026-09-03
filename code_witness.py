from backend.verifier.engine import verify

CASES = {
    "boundary": ("demo/boundary_original.py", "demo/boundary_generated.py", "is_eligible"),
    "rounding": ("demo/rounding_original.py", "demo/rounding_generated.py", "calculate_discount"),
    "empty": ("demo/null_original.py", "demo/null_generated.py", "get_first"),
    "equivalent": ("demo/equivalent_original.py", "demo/equivalent_generated.py", "add"),
}

if __name__ == "__main__":
    for name, (original, generated, function) in CASES.items():
        with open(original, encoding="utf-8") as source_file:
            original_code = source_file.read()
        with open(generated, encoding="utf-8") as source_file:
            generated_code = source_file.read()
        result = verify(original_code, generated_code, function)
        print(f"{name}: {result['verdict']['status']} ({result['metrics']['tests_executed']} tests, {result['metrics']['divergences']} divergences)")
        if result.get("counterexample"):
            print(f"  counterexample={result['counterexample']['inputs']}")
