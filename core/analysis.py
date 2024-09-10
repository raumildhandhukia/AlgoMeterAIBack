from services.gemini import get_llm_response
from core.graph import generate_indices
import json


def analyze_code_snippet(code_snippet: str):
    prompt = f"""
    Analyze the following code snippet and provide its 
    time complexity (Big O Notation), space complexity (Big O Notation), and a brief explanation (minimum 75 words, maximum 100 words).
    if time complexity can have any mathematical operators, or log or factorial, you must return the appropriate operator, sign, or log or factorial.
    for example, O(n^2 + n*log(n) + n!), O(n*m), O(log(n)), O(n!), O(n^2 + n*log(n) + n!), O(m+n), O(n^3), O(m-n) 
    DO NOT RETURN UNSIGNED EQUATIONS, DO NOT RETURN LOG WITHOUT BRACKETS AROUND VARIABLE
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
        if analysis['success']:
            try:
                indices = generate_indices(analysis["time_complexity"], 100000)    
            except Exception as e:
                print(e)
                return {"success": True, "response": analysis, "indices": []}
            return {"success": True, "response": analysis, "indices": indices}
        else:
            return {"success": False, "error": "Failed to parse response"}
    else:
        return {"success": False, "error": result["error"]}

def create_response_object(llm_response: str):
    try:
        # Parse the LLM response as JSON
        response_dict = json.loads(llm_response)
        
        return  {
            "time_complexity": response_dict.get('time_complexity', 'O(1)'),
            "space_complexity": response_dict.get('space_complexity', 'O(1)'),
            "explanation": response_dict.get('explanation', llm_response),
            "success": True
        }

    except json.JSONDecodeError:
        # If JSON parsing fails, return default values
        return {"success": False}
