# Aeronix Test Generator v1.0.0

## Overview
Professional PCB test plan generator using AI and advanced parsing.

## Features
- Multi-format file parsing (Altium, CSV, Excel, PDF)
- AI-powered test generation
- Professional Word document output
- Vector database for test plan similarity
- Comprehensive GUI interface

## Installation

### Option 1: Standalone Executable
1. Download `AeronixTestGenerator.exe`
2. Run the executable
3. No additional setup required

### Option 2: Python Installation
1. Extract `AeronixTestGenerator_v1.0.0.zip`
2. Run `install.sh` (Linux/Mac) or `install.bat` (Windows)
3. Run `python UI.py`

### Option 3: Docker
```bash
docker build -t aeronix-test-generator .
docker run -p 8080:8080 aeronix-test-generator
```

## Usage
1. Launch the application
2. Load PCB files (BOM, schematics, test points)
3. Parse the files
4. Generate test plans (LoRa or Arduino)
5. Export professional documents

## Requirements
- Python 3.8+
- OpenRouter API key (for AI generation)
- Pinecone API key (for vector database)

## Configuration
Create `.env` file with:
```
API_KEY=your_openrouter_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-east4-gcp
```

## Support
For issues and support, contact the development team.

## License
© 2025 Aeronix Solutions
