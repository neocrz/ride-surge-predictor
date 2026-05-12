import ollama
# client = ollama.Client(host='https://3d76-136-118-20-127.ngrok-free.app')
client = ollama.Client()
def process_with_llm(image_path):
    """Sends image to LLM and returns the raw string response."""
    
    prompt = """
    Get the information from this image and return a json.
    you will only insert ride_id elements that are visible and in this set ("uber_x", "uber_moto", "comfort", "bag"). you will return inside a codeblock.
    you will check the price to fill price and you will check the number in the same line as "mins away" to fill wait_time_minutes
    example: ```json[
    {
        "ride_id": "uber_x", 
        "price": 0.00,
        "wait_time_minutes": 0
    },
    {
        "ride_id": "uber_moto",
        "price": 0.00,
        "wait_time_minutes": 0
    }
    ]
    ```
    IMPORTANT: Do NOT include trailing commas in your JSON output.
    """
    try:
        response = client.chat(
            model='qwen3.5:2b',
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }],
        )
        return response['message']['content']
    except Exception as e:
        print(f"| LLM Processing Error on {image_path}: {e}")
        return None