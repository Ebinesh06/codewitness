def compare(original: dict, generated: dict) -> dict:
    same = (original.get("value") == generated.get("value") and original.get("type") == generated.get("type") and original.get("exception") == generated.get("exception") and original.get("stdout") == generated.get("stdout") and original.get("stderr") == generated.get("stderr"))
    return {"equivalent": same, "difference": None if same else "Observable return, exception, type, or stdout differs."}
