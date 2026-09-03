def make_verdict(divergences: int, execution_error: bool = False) -> dict:
    if execution_error:
        return {"status": "EXECUTION_ERROR", "message": "One or more artefacts could not be executed."}
    if divergences:
        return {"status": "DIVERGENCE_DETECTED", "message": "Behavioural divergence detected within the tested verification scope."}
    return {"status": "VERIFIED_WITHIN_SCOPE", "message": "No behavioural violations were detected within the tested verification scope."}
