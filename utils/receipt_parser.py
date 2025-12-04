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
        prompt_text = f"""Analyze this receipt image and extract ALL information including items, discounts, tax, and total.

Return a JSON object with this structure:
{{
  "items": [
    {{"description": "Item name", "amount": 5.99, "category": "Category"}},
    ...
  ],
  "discounts": [
    {{"description": "Discount description", "amount": -2.50}}
  ],
  "tax": 1.25,
  "total": 15.74
}}

For each item in "items":
1. description: Brief description (expand abbreviations, e.g., 'KS' -> 'Kirkland Signature')
2. amount: Price as positive number (no $ sign)
3. category: Pick BEST match from: [{categories_str}]

Categorization Rules:
- 'Housing', 'Utilities', 'Debt & Savings' are for monthly BILLS only, NOT store items
- Food/drink from stores: use 'Groceries'
- Food/drink from restaurants: use 'Dining Out'
- Cleaning supplies, toiletries, hygiene products: use 'Personal Care'
- Vitamins, supplements, prescriptions: use 'Healthcare'
- Gas, car maintenance, insurance: use 'Transportation'
- If unsure: use 'Miscellaneous'

For "discounts":
- Extract any negative amounts or discounts shown (e.g., "-$2.50 off")
- Amount should be NEGATIVE

For "tax":
- Extract the tax amount (positive number)

For "total":
- Extract the final total amount from the receipt

Important:
- Extract EVERY item, discount, tax, and total
- Items should have positive amounts
- Discounts should have negative amounts
- Return ONLY valid JSON, no other text

Return the JSON object now:"""

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
        parsed_data = None
        try:
            parsed_data = json.loads(response)
        except:
            # Try to extract JSON object from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    parsed_data = json.loads(json_match.group(0))
                except:
                    pass
        
        if not parsed_data:
            return {"error": "Failed to parse receipt", "raw": response}
        
        # Validate structure
        if not isinstance(parsed_data, dict) or 'items' not in parsed_data:
            return {"error": "Invalid receipt data structure", "raw": response}
        
        items = parsed_data.get('items', [])
        discounts = parsed_data.get('discounts', [])
        tax = parsed_data.get('tax', 0)
        receipt_total = parsed_data.get('total', 0)
        
        # Group items by category and sum amounts
        category_totals = {}
        for item in items:
            category = item.get('category', 'Misc.')
            amount = float(item.get('amount', 0))
            
            if category not in category_totals:
                category_totals[category] = {
                    'category': category,
                    'amount': 0,
                    'items': []
                }
            
            category_totals[category]['amount'] += amount
            category_totals[category]['items'].append({
                'description': item.get('description', 'Unknown'),
                'amount': amount
            })
        
        # Apply discounts to the appropriate categories or create a separate entry
        total_discounts = 0
        for discount in discounts:
            discount_amount = float(discount.get('amount', 0))
            total_discounts += discount_amount
        
        # Calculate our total: sum of categories + discounts + tax
        calculated_subtotal = sum(cat['amount'] for cat in category_totals.values())
        calculated_total = calculated_subtotal + total_discounts + tax
        
        # Validate total (allow 1% tolerance for rounding)
        total_diff = abs(calculated_total - receipt_total) if receipt_total > 0 else 0
        total_valid = total_diff < (receipt_total * 0.01) if receipt_total > 0 else True
        
        # Convert category_totals to list
        grouped_items = list(category_totals.values())
        
        return {
            "grouped_items": grouped_items,
            "discounts": discounts,
            "total_discounts": total_discounts,
            "tax": tax,
            "receipt_total": receipt_total,
            "calculated_total": calculated_total,
            "total_valid": total_valid,
            "total_diff": total_diff,
            "raw": response
        }
        
    except Exception as e:
        return {"error": f"Error processing receipt: {str(e)}"}
