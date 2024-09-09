from services.gemini import get_llm_response
from pydantic import BaseModel
from typing import Dict, Union, Optional
import json

class AnalysisResponse(BaseModel):
    success: bool
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    explanation: Optional[str] = None

def analyze_code_snippet(code_snippet: str) -> Dict[str, Union[AnalysisResponse, str]]:
    prompt = f"""
    Analyze the following code snippet and provide its 
    time complexity (Big O Notation), space complexity (Big O Notation), and a brief explanation (max 100 words).
    Return the response in JSON format using this schema:
    {{
        "time_complexity": string,
        "space_complexity": string,
        "explanation": string
    }}

    Code snippet to analyze:
    {code_snippet}
    """
    
    result = get_llm_response(prompt)
    
    if result["success"]:
        analysis = create_response_object(result["response"])
        if analysis.success:
            return {"success": True, "response": analysis}
        else:
            return {"success": False, "error": "Failed to parse response"}
    else:
        return {"success": False, "error": result["error"]}

def create_response_object(llm_response: str) -> AnalysisResponse:
    try:
        # Parse the LLM response as JSON
        response_dict = json.loads(llm_response)
        
        # Create and return the AnalysisResponse object
        return AnalysisResponse(
            time_complexity=response_dict.get('time_complexity', 'O(1)'),
            space_complexity=response_dict.get('space_complexity', 'O(1)'),
            explanation=response_dict.get('explanation', llm_response),
            success=True
        )
    except json.JSONDecodeError:
        # If JSON parsing fails, return default values
        return AnalysisResponse(
            success=False
        )
