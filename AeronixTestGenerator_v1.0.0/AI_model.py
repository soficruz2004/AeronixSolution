from typing import Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
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
    @staticmethod
    def generate_resp(prompt:str,model:str ="x-ai/grok-4-fast:free") -> Optional[str|None]:
        import time
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return completion.choices[0].message.content
                
            except Exception as e:
                error_str = str(e)
                print(f"API Error (attempt {attempt + 1}): {error_str}")
                
                if "401" in error_str or "unauthorized" in error_str.lower():
                    print("❌ API Key expired/invalid. Solutions:")
                    print("1. Get new key: https://openrouter.ai/keys")
                    print("2. Check account credits")
                    return None
                elif "429" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Rate limited. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                elif "quota" in error_str.lower():
                    print("❌ Quota exceeded. Add credits to OpenRouter.")
                    return None
                
                if attempt == max_retries - 1:
                    return None
        
        return None
    @staticmethod
    def get_LORA_test(bom_components, test_points,reqs) -> Optional[str|None]:
        LORA_pr = f"""You are an expert RF test engineer. Generate a comprehensive test procedure for a LoRa train communication radio.
                    Do not add formatting, ONLY provide a clear and concise response with NO preceeding acknowledgement.
                    COMPONENTS:
                    {bom_components}
                    TEST POINTS:
                    {test_points}
                    REQUIREMENTS:
                    {reqs}
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
        return TestGenerator.generate_resp(LORA_pr)
    @staticmethod
    def get_arduino_test(bom_components,test_points) -> Optional[str|None]:
        ard_pr = f"""Generate Arduino Uno test procedure covering:
                Do not add formatting, ONLY provide a clear and concise response with NO preceeding acknowledgement.
                1. Power rails (5V ±0.25V, 3.3V ±0.165V)
                2. Digital I/O (D0-D13, PWM capability)
                3. Analog inputs (A0-A5, 10-bit ADC)
                4. USB communication (9600-115200 baud)
                5. Programming interface (bootloader, ICSP)

                Components: {bom_components}
                Test Points: {test_points}
                """
        return TestGenerator.generate_resp(ard_pr)

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
    def build_test_context(self,data):
        context = {
            'component_count': len(data['bom_components']),
            'critical_components': [c for c in data['bom_components'] 
                                if c.test_priority == 'HIGH'],
            'test_point_count': len(data['test_points']),
            'power_components': [c for c in data['bom_components'] 
                                if 'POWER' in c.part_number.upper()],
            'rf_components': [c for c in data['bom_components'] 
                            if any(rf in c.part_number.upper() 
                                for rf in ['RF', 'LORA', 'ANTENNA'])]
        }
        return context
    def optimize_prompt(self,data):
        # Critical items only
        critical_components = [c for c in data['bom_components'] 
                            if c.test_priority == 'HIGH'][:10]
        
        # Summarize test points by type
        test_point_summary = {
            'power': len([tp for tp in data['test_points'] 
                        if 'VCC' in tp.net_name or 'GND' in tp.net_name]),
            'signal': len(data['test_points']) - 
                    len([tp for tp in data['test_points'] 
                        if 'VCC' in tp.net_name or 'GND' in tp.net_name])
        }
        
        return {
            'critical_components': critical_components,
            'test_point_summary': test_point_summary
        }