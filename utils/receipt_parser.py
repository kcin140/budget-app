import os
import base64
import json
from io import BytesIO
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def parse_receipt_image(image_bytes, categories):
    """
    Parse a receipt image using watsonx.ai vision model.
    
    Args:
        image_bytes: Image file bytes
        categories: List of category names for categorization
        
    Returns:
        dict with 'items' key containing list of parsed expenses,
        or 'error' key if parsing failed
    """
    try:
        # Get credentials
        try:
            api_key = st.secrets.get("WATSONX_API_KEY")
            project_id = st.secrets.get("WATSONX_PROJECT_ID")
        except:
            api_key = os.environ.get("WATSONX_API_KEY")
            project_id = os.environ.get("WATSONX_PROJECT_ID")
        
        if not api_key or not project_id:
            return {"error": "Missing Watsonx credentials"}
        
        # Register HEIF opener for HEIC files (iPhone photos)
        try:
            from pillow_heif import register_heif_opener
            register_heif_opener()
        except ImportError:
            pass  # HEIF support not available
        
        # Process image
        image = Image.open(BytesIO(image_bytes))
        
        # Resize if too large (vision models have size limits)
        max_size = 2048
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Import watsonx.ai
        from ibm_watsonx_ai.foundation_models import Model
        
        model_id = "meta-llama/llama-3-2-90b-vision-instruct"
        
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 2000,
            "temperature": 0.1
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
        
        # Construct prompt for vision model
        # Construct prompt for vision model
        prompt_text = f"""Analyze this receipt image and extract ALL line items with their amounts.

For each item purchased, provide:
1. description: Brief description of what was purchased (expand abbreviations if possible, e.g., 'KS' -> 'Kirkland Signature')
2. amount: The price (numeric value only, no $ sign)
3. category: Pick the BEST matching category from this list: [{categories_str}]

Categorization Rules:
- 'HOA', 'Mortgage', 'Utilities', 'Insurance', 'Debt' are for monthly BILLS, not store receipts. DO NOT use them for physical items.
- For food/drink, use 'Grocery', 'Grocery (Costco)', or 'Eating Out'.
- For paper towels, soap, etc., use 'Cleaning Supplies, Toiletries'.
- For vitamins/supplements, use 'Supplemental'.
- If unsure, use 'Misc.' or 'Personal'.

Important:
- Extract EVERY item on the receipt, not just the total
- If multiple items of the same type, list them separately
- Ignore tax, subtotal, and total lines
- Return ONLY a JSON array, no other text

Example format:
[
  {{"description": "Bananas", "amount": 5.99, "category": "Grocery"}},
  {{"description": "Kirkland Signature Towels", "amount": 19.99, "category": "Cleaning Supplies, Toiletries"}}
]

Return the JSON array now:"""

        # For vision models, we need to format the request differently
        # The image is typically sent as a data URL or base64 in the prompt
        image_data_url = f"data:image/jpeg;base64,{img_base64}"
        
        # Try using the generate_text_stream or generate method with image
        # Vision models in watsonx.ai may accept images in different formats
        try:
            # Attempt 1: Try with image URL in prompt (some models support this)
            full_prompt = f"<image>{image_data_url}</image>\n\n{prompt_text}"
            response = model.generate_text(prompt=full_prompt)
        except Exception as e:
            # Attempt 2: Try direct API call if library doesn't support vision
            # This may require using the REST API directly
            import requests
            
            # First, get IAM token
            iam_url = "https://iam.cloud.ibm.com/identity/token"
            iam_headers = {"Content-Type": "application/x-www-form-urlencoded"}
            iam_data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}"
            
            iam_response = requests.post(iam_url, headers=iam_headers, data=iam_data)
            
            if iam_response.status_code != 200:
                return {"error": f"Auth Error: Failed to get IAM token. {iam_response.text}"}
                
            access_token = iam_response.json()["access_token"]
            
            # Use Chat API endpoint for vision models (standard format)
            url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
            
            # Construct chat payload with image
            body = {
                "model_id": model_id,
                "project_id": project_id,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt_text
                            }
                        ]
                    }
                ],
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 2000,
                    "temperature": 0.1
                }
            }
            
            api_response = requests.post(url, headers=headers, json=body)
            
            if api_response.status_code == 200:
                # Chat API response format is different
                response = api_response.json()['choices'][0]['message']['content']
            else:
                return {"error": f"API Error: {api_response.status_code} - {api_response.text}"}
        
        # Try to parse JSON from response
        import re
        
        # Try direct parse
        try:
            items = json.loads(response)
            if isinstance(items, list):
                return {"items": items, "raw": response}
        except:
            pass
        
        # Try to extract JSON array from response
        json_match = re.search(r'\[.*?\]', response, re.DOTALL)
        if json_match:
            try:
                items = json.loads(json_match.group(0))
                return {"items": items}
            except:
                pass
        
        # If parsing failed, return error with raw response
        return {"error": "Failed to parse receipt", "raw": response}
        
    except Exception as e:
        return {"error": f"Error processing receipt: {str(e)}"}
