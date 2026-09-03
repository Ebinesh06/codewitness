import json
import os
import subprocess
import sys
import tempfile
import time


def execute(code: str, function_name: str, inputs: list, timeout: float = 2.0) -> dict:
    # Submitted code runs in a short-lived subprocess; this is not a production-grade security sandbox.
    runner = '''import contextlib, io, json, sys\ntry:\n    namespace = {}\n    exec(compile(sys.stdin.read(), "submitted.py", "exec"), namespace)\n    args = json.loads(sys.argv[2])\n    output = io.StringIO()\n    error = None\n    with contextlib.redirect_stdout(output):\n        try:\n            value = namespace[sys.argv[1]](*args)\n        except Exception as exc:\n            error = {"type": type(exc).__name__, "message": str(exc)}\n    print(json.dumps({"value": None if error else value, "type": None if error else type(value).__name__, "exception": error, "stdout": output.getvalue()}))\nexcept Exception as exc:\n    print(json.dumps({"value": None, "type": None, "exception": {"type": type(exc).__name__, "message": str(exc)}, "stdout": ""}))\n'''
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="code-witness-") as directory:
        runner_path = os.path.join(directory, "runner.py")
        with open(runner_path, "w", encoding="utf-8") as file:
            file.write(runner)
        try:
            completed = subprocess.run([sys.executable, runner_path, function_name, json.dumps(inputs)], input=code, text=True, capture_output=True, timeout=timeout, cwd=directory, env={"PATH": os.environ.get("PATH", "")})
            output_lines = completed.stdout.strip().splitlines()
            if not output_lines:
                return {"value": None, "type": None, "exception": {"type": "ExecutionError", "message": completed.stderr or "No execution result returned"}, "stdout": "", "stderr": completed.stderr, "duration_ms": round((time.perf_counter() - started) * 1000, 3)}
            payload = json.loads(output_lines[-1])
            payload["stderr"] = completed.stderr
            payload["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
            return payload
        except subprocess.TimeoutExpired:
            return {"value": None, "type": None, "exception": {"type": "TimeoutError", "message": "Execution exceeded timeout"}, "stdout": "", "stderr": "", "duration_ms": round((time.perf_counter() - started) * 1000, 3)}
