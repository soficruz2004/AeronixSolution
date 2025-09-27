from typing import Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
global api_key
api_key = os.getenv("API_KEY")

def generate_resp(prompt:str,model:str ="deepseek/deepseek-chat-v3.1:free") -> Optional[str|None]:
    client = OpenAI(api_key=api_key,base_url = "https://openrouter.ai/api/v1")
    repsonse = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        stream = False
    )
    return repsonse.choices[0].message.content

def get_LORA_test(bom_components, test_points,reqs) -> Optional[str|None]:
    LORA_pr = f"""You are an expert RF test engineer. Generate a comprehensive test procedure for a LoRa train communication radio.
                COMPONENTS:
                {str(bom_components)[:1348]}
                TEST POINTS:
                {str(test_points)[:350]}
                REQUIREMENTS:
                {str(reqs)[:350]}
                Generate test steps covering:
                1. Power supply validation (±5% tolerance)
                2. RF performance (sensitivity -137dBm @ SF12)
                3. LoRa protocol compliance
                4. Environmental testing (-40°C to +70°C)
                5. Train integration (CAN bus, emergency protocols)

                Format each test as:
                1. Title: [Test Name]
                2. Type: [Power/RF/Digital/Protocol]
                3. Description: [Detailed procedure]
                4. Expected: [Pass criteria]
                5. Equipment: [Required tools]
                6. Points: [Test points to probe]
                """
    return generate_resp(LORA_pr)

def get_arduino_test(bom_components,test_points) -> Optional[str|None]:
    ard_pr = f"""Generate Arduino Uno test procedure covering:
            1. Power rails (5V ±0.25V, 3.3V ±0.165V)
            2. Digital I/O (D0-D13, PWM capability)
            3. Analog inputs (A0-A5, 10-bit ADC)
            4. USB communication (9600-115200 baud)
            5. Programming interface (bootloader, ICSP)

            Components: {str(bom_components)[:1500]}
            Test Points: {str(test_points)[:548]}
            """
