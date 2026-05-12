import json
import re

def extract_json_from_response(content):
    """Extracts and validates JSON from the LLM's raw text response."""
    if not content:
        return None
    
    # Look for the JSON block inside markdown formatting
    match = re.search(r'```json\s*(\[.*?\])\s*```', content, re.DOTALL)
    if match:
        json_str = match.group(1)
        
        # SAFETY NET: Remove any accidental trailing commas before parsing
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*\]', ']', json_str)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"| JSON Parse Error: {e}\nRaw String: {json_str}")
            return None
            
    print("| No JSON code block found in LLM response.")
    return None