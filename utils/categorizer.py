import os
import json
from ibm_watsonx_ai.foundation_models import Model
from dotenv import load_dotenv

load_dotenv()

def categorize_expense(text: str, categories: list):
    """
    Uses IBM watsonx.ai to extract:
    - amount
    - vendor
    - category
    - notes
    Returns a dict with standardized keys.
    """
    api_key = os.environ.get("WATSONX_API_KEY")
    project_id = os.environ.get("WATSONX_PROJECT_ID")
    
    if not api_key or not project_id:
        return {"error": "Missing Watsonx credentials"}

    model_id = "meta-llama/llama-3-3-70b-instruct"
    
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 200,
        "temperature": 0.1,
        "repetition_penalty": 1.0
    }

    model = Model(
        model_id=model_id,
        params=parameters,
        credentials={
            "url": "https://us-south.ml.cloud.ibm.com",
            "apikey": api_key
        },
        project_id=project_id
    )

    categories_str = ", ".join(categories)
    
    prompt = f"""You are an expense parsing assistant. Extract expense information from the input text and return ONLY a JSON array.

Input: "{text}"

Extract ALL expenses mentioned. For each expense, extract:
- amount: numeric value only
- vendor: store/merchant name
- category: pick the BEST match from [{categories_str}]
- notes: any additional details

If there are multiple expenses, return an array. If only one expense, still return an array with one item.

Return ONLY this JSON format with no other text:
[{{"amount": 0, "vendor": "Store Name", "category": "Category Name", "notes": "Any notes"}}]"""

    generated_response = model.generate_text(prompt=prompt)
    
    try:
        # Try to find JSON in the response
        import re
        
        # First try direct parse
        try:
            result = json.loads(generated_response)
            # Ensure it's an array
            if isinstance(result, dict):
                result = [result]
            return {"expenses": result}
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```', generated_response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
            if isinstance(result, dict):
                result = [result]
            return {"expenses": result}
        
        # Try to find any JSON array in the response
        json_match = re.search(r'\[.*?"amount".*?\]', generated_response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            return {"expenses": result}
        
        # Try to find a single JSON object
        json_match = re.search(r'\{[^{}]*"amount"[^{}]*\}', generated_response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            return {"expenses": [result]}
            
        # If all else fails, return error with raw response
        print(f"Failed to parse JSON: {generated_response}")
        return {"error": "Failed to parse AI response", "raw": generated_response}
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {generated_response}")
        return {"error": f"Parsing error: {str(e)}", "raw": generated_response}
