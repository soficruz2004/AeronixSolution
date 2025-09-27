"""Test data for unit tests"""

# Sample BOM CSV content
SAMPLE_BOM_CSV = """Designator,Part Number,Footprint,Quantity,Description,Value
U1,STM32F103CBT6,LQFP48,1,Microcontroller,STM32F103CBT6
U2,SX1276,QFN28,1,LoRa Transceiver,SX1276
R1,10K,0603,1,Resistor,10K
R2,1K,0603,2,Resistor,1K
C1,100nF,0603,1,Capacitor,100nF
C2,22pF,0603,2,Capacitor,22pF
L1,10uH,0805,1,Inductor,10uH
X1,32MHz,HC49,1,Crystal,32MHz"""

# Sample test points data
SAMPLE_TESTPOINTS = """TP1 VCC 10.5 20.3 0
TP2 GND 15.2 25.1 0
TP3 RESET 8.7 12.4 90
TP4 UART_TX 22.1 18.9 0
TP5 UART_RX 24.3 18.9 0
TP6 SPI_CLK 30.5 15.2 0"""

# Sample XML BOM
SAMPLE_XML_BOM = """<?xml version="1.0" encoding="UTF-8"?>
<bom>
    <component designator="U1" partnumber="STM32F103" footprint="LQFP48" quantity="1">
        <description>Microcontroller</description>
        <value>STM32F103</value>
    </component>
    <component designator="R1" partnumber="10K" footprint="0603" quantity="1">
        <description>Resistor</description>
        <value>10K</value>
    </component>
</bom>"""

# Sample requirements text
SAMPLE_REQUIREMENTS = """
# Functional Requirements
- Device shall operate on 3.3V power supply
- LoRa communication range minimum 1km
- UART interface for configuration

# Performance Requirements  
- Power consumption < 100mA active
- Sleep current < 10uA
- Boot time < 2 seconds

# Environmental Requirements
- Operating temperature: -40°C to +85°C
- Storage temperature: -55°C to +125°C
- Humidity: 0-95% non-condensing
"""

# Expected test results
EXPECTED_LORA_TEST = """
1. Title: Power Supply Validation
2. Type: Power
3. Description: Verify 3.3V rail within ±5% tolerance
4. Expected: 3.135V to 3.465V
5. Equipment: Digital multimeter, power supply
6. Points: TP1 (VCC), TP2 (GND)

1. Title: LoRa RF Performance
2. Type: RF
3. Description: Measure sensitivity at SF12
4. Expected: ≥-137dBm sensitivity
5. Equipment: Vector network analyzer, RF generator
6. Points: ANT1, RF_OUT
"""

# Mock API responses
MOCK_API_RESPONSES = {
    "lora_test": EXPECTED_LORA_TEST,
    "arduino_test": """
1. Title: Power Rail Test
2. Type: Power  
3. Description: Verify 5V and 3.3V rails
4. Expected: 5V±0.25V, 3.3V±0.165V
5. Equipment: Multimeter
6. Points: VCC, 3V3, GND
"""
}

# Test file paths
TEST_FILES = {
    "bom_csv": "test_bom.csv",
    "testpoints": "test_points.txt", 
    "requirements": "requirements.txt",
    "altium_bom": "test.BomDoc",
    "altium_sch": "test.SchDoc"
}