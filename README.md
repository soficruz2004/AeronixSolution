# AeronixSolution
Team solution to Aeronix's 2025 PCB Testing Hackathon

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up API keys in `.env`:
```
OPENROUTER_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
```

3. Run the application:
```bash
python main.py
```

## Features
- Multi-format PCB file parsing (Altium, CSV, Excel, XML)
- AI-powered test procedure generation
- Professional Word document output
- GUI interface for easy operation

## Usage
1. Load PCB files using the GUI
2. Select device type (LoRa/Arduino)
3. Generate test procedures
4. Export to Word document
