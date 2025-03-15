from services.gemini import get_llm_response
from core.graph import generate_indices
import json


def analyze_code_snippet(code_snippet: str):
    prompt = f"""
    SYSTEM: You are an analysis tool that strictly evaluates provided code snippets without making assumptions or predictions about their functionality. Your task is to analyze the given code snippet based solely on its content.

    Analyze the following code snippet: {code_snippet}. 
    Follow this at all time
    1) Ignore comments and any empty function bodies. 
    2) Do not generate or assume any code based on function names or signatures. 
    3) Analyze the code line by line. Identify phases of algorith. 
    4) Analyze time complexity of each phase, also space complexity for each phase

    Phase is a part of an algorithm which is having runtime more than O(1) and taking space more than O(1). Algorithm may have one or more phases.

    There might be nested phases like we are looping through array (Phase 1) and for each array element we are doing some process (Phase 2)

    Time complexity or Space complexity of algorithm should be the one which is dominating the runtime and space. 

    Here is a confusing area where you might think space complexity is O(n) but in reality it is O(1):
     -> Code attempts to store result or indices in an array inside a loop, but code is breaking the loop and there are static number of elements in array.
        At this time you might need to actually analyze the code, and see if actually there can be a case where array can have all n elemets or it will break after
        static number of elements
     -> Storing the frequency of charactors in hashmap. You might think input string has length of n so space complexity is n. but in reality there are just 26 alphabets 
        and maximum 256 distinct charactors in input. So hashmap's space complexity is O(1) as it doesnt grow as input size increases.
    
    Here is a confusing area where you might think Time complexity is O(n) but in reality it is O(1):
    -> Looping through static number of elements. You might think that loop is there so there is time complexity of O(n) but in some cases, loop will have static
       number of iterations regardless of size of input array
    -> Make sure when loop is executing it actually can execute n times in worst case if you are tempted to give O(n) complexity


    Your analysis should include:
    - Time complexity (Domanating)
    - Space complexity (Domanating)
    - A brief explanation (minimum 75 words, maximum 100 words). Should include time and space complexity for all phases.

    If the provided code is empty, invalid, or contains no executable statements, respond with:
    - Time complexity: O(1)
    - Space complexity: O(1)
    - Explanation: "Code is not valid" or "No code to analyze" or "Function body is empty" as appropriate.

    Do not analyze commented code; ignore any comments present in the snippet.

    If the time complexity can include mathematical operators, logarithms, or factorials, return the appropriate notation. For example: O(n^2 + n*log(n) + n!), O(n*m), O(log(n)), O(n!), O(n^2 + n*log(n) + n!), O(m+n), O(n^3), O(m-n). 
    DO NOT RETURN UNSIGNED EQUATIONS, AND DO NOT RETURN LOG WITHOUT BRACKETS AROUND VARIABLES.

    Return the response in JSON format using the following schema:
    {{
        "time_complexity": string,
        "space_complexity": string,
        "explanation": string
    }}
    """
    result = get_llm_response(prompt)
    if result["success"]:
        analysis = create_response_object(result["response"])
        if analysis['success']:
            try:
                indices = generate_indices(analysis["time_complexity"], 10000)    
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
