from datetime import datetime, timezone
from uuid import uuid4

def build_evidence(function_name, properties, corpus, executions, counterexample, verdict, hashes, reproducibility):
    failures = [item for item in executions if not item["comparison"]["equivalent"]]
    return {"verification_id": str(uuid4()), "source_hash": hashes[0], "generated_hash": hashes[1], "function_name": function_name, "test_seed": 0, "tests_generated": len(corpus), "tests_executed": len(executions), "properties": properties, "properties_checked": len(properties), "divergences": len(failures), "failures": failures, "minimal_counterexample": counterexample, "original_result": counterexample.get("original") if counterexample else None, "generated_result": counterexample.get("generated") if counterexample else None, "reproducibility": reproducibility, "execution_environment": {"python": "subprocess", "timeout_seconds": 2}, "timestamp": datetime.now(timezone.utc).isoformat(), "verdict": verdict}
