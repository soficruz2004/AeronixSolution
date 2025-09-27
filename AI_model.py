from typing import Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
global api_key
api_key = os.getenv("API_KEY")
class TestGenerator:
    # Implement user input for these later
    power_tests = {
        "voltage_accuracy": "±5% of nominal",
        "ripple": "<100mV peak-to-peak",
        "load_regulation": "<2% from no-load to full-load",
        "efficiency": ">80% at full load"
    }
    RF_tests = {
        "frequency_response": "≥-137dBm @ SF12",
        "sensitivity": "≥-137dBm @ SF12",
        "signal_to_noise_ratio": "≥30dB",
        "linearity": "≥95%",
        "dynamic_range": "≥100dBm"
    }
    digital_tests = {
        "logic_levels": {"VIH": ">2.0V", "VIL": "<0.8V"},
        "timing": {"setup": ">10ns", "hold": ">5ns"},
        "drive_strength": {"IOH": ">-12mA", "IOL": ">12mA"}
    }
    test_equipment = {}

    def __init__(self, bom_components, test_points, reqs, test_equipment: dict[str,list[str]]):
        self.bom_components = bom_components
        self.test_points = test_points
        self.reqs = reqs
        self.LORA_test = self.get_LORA_test(bom_components, test_points, reqs)
        self.arduino_test = self.get_arduino_test(bom_components, test_points)
        self.test_equipment = test_equipment

    def generate_resp(self,prompt:str,model:str ="deepseek/deepseek-chat-v3.1:free") -> Optional[str|None]:
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

    def get_LORA_test(self,bom_components, test_points,reqs) -> Optional[str|None]:
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
        return self.generate_resp(LORA_pr)

    def get_arduino_test(self,bom_components,test_points) -> Optional[str|None]:
        ard_pr = f"""Generate Arduino Uno test procedure covering:
                1. Power rails (5V ±0.25V, 3.3V ±0.165V)
                2. Digital I/O (D0-D13, PWM capability)
                3. Analog inputs (A0-A5, 10-bit ADC)
                4. USB communication (9600-115200 baud)
                5. Programming interface (bootloader, ICSP)

                Components: {str(bom_components)[:1500]}
                Test Points: {str(test_points)[:548]}
                """
        return self.generate_resp(ard_pr)

    def parse_ai_response(self,response_text: Optional[str|None]) -> Optional[list[Any]|None]:
        test_steps = []
        current_step:dict[str,list[str]] = {}
        match response_text:
            case None:
                return None
            case _: 
                for line in response_text.split('\n'):
                    if line.startswith('- Title:'):
                        if current_step:test_steps.append(current_step)
                        current_step = {'title': [line.split(':', 1)[1].strip()]}
                    elif line.startswith('- Type:'): 
                        current_step['type'] = [line.split(':', 1)[1].strip()]
                    elif line.startswith('- Description:'):
                        current_step['description'] = [line.split(':', 1)[1].strip()]
                    elif line.startswith('- Expected:'):
                        current_step['expected_result'] = [line.split(':', 1)[1].strip()]
                    elif line.startswith('- Equipment:'):
                        current_step['equipment'] = [x.strip() for x in line.split(':', 1)[1].split(',')]
                    elif line.startswith('- Points:'):
                        current_step['test_points'] = [x.strip() for x in line.split(':', 1)[1].split(',')]
                
                if current_step:
                    test_steps.append(current_step)
                
                return test_steps