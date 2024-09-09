from fastapi import APIRouter, HTTPException, Body
from core.analysis import analyze_code_snippet, AnalysisResponse

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(code_snippet: str = Body(..., embed=True)):
    result = analyze_code_snippet(code_snippet)
    
    if result["success"]:
        return result["response"]
    else:
        raise HTTPException(status_code=500, detail=result["error"])