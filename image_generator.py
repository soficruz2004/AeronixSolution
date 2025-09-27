import requests
import base64

api_key = "YOUR_API_KEY"
prompt = "A futuristic city at sunset"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json" # Or "image/*" for direct image bytes
}

payload = {
    "prompt": prompt,
    "negative_prompt": "blurry, low quality",
    "width": 512,
    "height": 512
}

response = requests.post("https://api.stability.ai/v1/generation/stable-diffusion-v3/text-to-image", headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    # Process the image data (e.g., decode base64 and save)
    print("Image generated successfully.")
else:
    print(f"Error: {response.status_code} - {response.text}")