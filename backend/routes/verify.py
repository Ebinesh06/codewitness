from fastapi import APIRouter, HTTPException
from backend.models import VerifyRequest
from backend.verifier.engine import verify

router = APIRouter()

@router.post("/api/verify")
def run_verification(request: VerifyRequest):
    try:
        return verify(request.original_code, request.generated_code, request.function_name, request.intent, request.counterexample_inputs)
    except SyntaxError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid Python: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Verification failed") from exc
