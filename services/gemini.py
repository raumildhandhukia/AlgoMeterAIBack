import os
import google.generativeai as genai
from google.generativeai.types import SafetySettingDict
from typing import List, Dict, Union
from google.api_core import exceptions as google_exceptions

# Initialize the Gemini model
try:
    genai.configure(api_key=os.getenv("GENAI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
except Exception as e:
    print(f"Error initializing Gemini model: {str(e)}")
    model = None

def get_llm_response(prompt: str) -> Dict[str, Union[str, bool]]:
    if not model:
        return {"success": False, "error": "Gemini model not initialized"}

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                # "temperature": 0.7,
                # "top_p": 0.95,
                # "top_k": 40,
                "max_output_tokens": 256,
            }
        )
        return {"success": True, "response": response.text}
    except google_exceptions.InvalidArgument as e:
        return {"success": False, "error": f"Invalid argument: {str(e)}"}
    except google_exceptions.ResourceExhausted as e:
        return {"success": False, "error": "API quota exceeded"}
    except google_exceptions.ServiceUnavailable as e:
        return {"success": False, "error": "Gemini service is currently unavailable"}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}
