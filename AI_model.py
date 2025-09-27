from typing import Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
global api_key
api_key = os.getenv("API_KEY")

def generate_test_plan(data: dict[Any,Any],model:str ="deepseek/deepseek-chat-v3.1:free") -> Optional[str|None]:
    client = OpenAI(api_key=api_key,base_url = "https://openrouter.ai/api/v1")
    structured_data = str(data)
    prompt = f""" You are an expert in PCB testing and design. Please build a study plan using {structured_data}."""
    repsonse = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        stream = False
    )
    return repsonse.choices[0].message.content