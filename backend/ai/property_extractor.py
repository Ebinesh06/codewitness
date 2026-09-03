import ast

def extract_properties(original_code: str, generated_code: str, intent: str | None = None) -> list[dict]:
    properties = [
        {"id": "P001", "name": "Return value equivalence", "description": "Equivalent inputs should produce equivalent return values.", "priority": "high"},
        {"id": "P002", "name": "Return type preservation", "description": "Equivalent inputs should preserve return types.", "priority": "high"},
        {"id": "P003", "name": "Exception equivalence", "description": "Exceptional inputs should fail in the same observable way.", "priority": "high"},
    ]
    if any(isinstance(node, ast.Compare) for node in ast.walk(ast.parse(original_code))):
        properties.append({"id": "P004", "name": "Boundary behaviour", "description": "Threshold and boundary inputs should remain equivalent.", "priority": "high"})
    if intent:
        properties.append({"id": "P005", "name": "Declared intent", "description": intent, "priority": "medium"})
    return properties
