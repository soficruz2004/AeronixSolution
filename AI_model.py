from typing import Any
from openai import OpenAI

def generate_test_plan(data: dict[Any,Any],model:str,api_key:str):
    client = OpenAI(api_key=api_key,base_url = "https://api.deepseek.com")
    structured_data = str(data)
    prompt = f""" You are an expert.Please build a plan using {structured_data}. """
    repsonse = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        stream = False
    )
    return repsonse.choices[0].message.content
