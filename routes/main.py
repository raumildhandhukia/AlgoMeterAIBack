from fastapi import APIRouter, HTTPException, Body, Request
from core.analysis import analyze_code_snippet
from core.user import store_user_analysis

router = APIRouter()

@router.post("/analyze")
def analyze(request: Request, code_snippet: str = Body(..., embed=True)):
    result = analyze_code_snippet(code_snippet)
    
    if result["success"]:
        # Store user data asynchronously
        store_user_analysis(request, code_snippet, result["response"])
        return result["response"]
    else:
        raise HTTPException(status_code=500, detail=result["error"])