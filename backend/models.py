from pydantic import BaseModel

class VerifyRequest(BaseModel):
    original_code: str
    generated_code: str
    function_name: str
    intent: str | None = None
    counterexample_inputs: list | None = None
