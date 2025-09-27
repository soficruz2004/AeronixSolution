#!/usr/bin/env python3
"""Deployment package creator for Aeronix Test Generator"""

import os
import shutil
import zipfile
import subprocess
import sys
from datetime import datetime

class DeploymentPackager:
    def __init__(self):
        self.project_name = "AeronixTestGenerator"
        self.version = "1.0.0"
        self.build_dir = "build"
        self.dist_dir = "dist"
        
    def create_executable(self):
        """Create standalone executable using PyInstaller"""
        print("Creating standalone executable...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                         check=True, capture_output=True)
            spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['UI.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('UF_Hackathon', 'UF_Hackathon'),
        ('output', 'output'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'sentence_transformers',
        'pinecone',
        'openai',
        'docx',
        'openpyxl',
        'PyPDF2'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.project_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
            
            with open(f"{self.project_name}.spec", "w") as f:
                f.write(spec_content)
            cmd = [sys.executable, "-m", "PyInstaller", "--clean", f"{self.project_name}.spec"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Executable created successfully")
                return True
            else:
                print(f"PyInstaller failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Executable creation failed: {e}")
            return False
    
    def create_docker_image(self):
        """Create Docker container"""
        print("Creating Docker container...")
        
        dockerfile_content = f'''
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create output directory
RUN mkdir -p output

# Expose port for web interface (if needed)
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["python", "UI.py"]
'''
        
        try:
            # Write Dockerfile
            with open("Dockerfile", "w") as f:
                f.write(dockerfile_content)
            
            # Create .dockerignore
            dockerignore_content = '''
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
.env.local
.venv/
venv/
'''
            
            with open(".dockerignore", "w") as f:
                f.write(dockerignore_content)
            
            print("Docker files created")
            print("To build: docker build -t aeronix-test-generator .")
            print("To run: docker run -p 8080:8080 aeronix-test-generator")
            return True
            
        except Exception as e:
            print(f"Docker setup failed: {e}")
            return False
    
    def create_installer_package(self):
        """Create installation package"""
        print("Creating installation package...")
        
        try:
            package_dir = f"{self.project_name}_v{self.version}"
            if os.path.exists(package_dir):
                shutil.rmtree(package_dir)
            os.makedirs(package_dir)
            
            files_to_copy = [
                "UI.py",
                "AI_model.py", 
                "parser_but_better.py",
                "format_output.py",
                "vector_db",
                "requirements.txt",
                ".env",
                "README.md"
            ]
            
            for file in files_to_copy:
                if os.path.exists(file):
                    if os.path.isdir(file):
                        shutil.copytree(file, os.path.join(package_dir, file))
                    else:
                        shutil.copy2(file, package_dir)
            
            dirs_to_copy = ["UF_Hackathon", "output"]
            for dir_name in dirs_to_copy:
                if os.path.exists(dir_name):
                    shutil.copytree(dir_name, os.path.join(package_dir, dir_name))
            
            install_script = f'''#!/bin/bash
# Aeronix Test Generator Installation Script

echo "Installing Aeronix Test Generator v{self.version}"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ -z "$python_version" ]]; then
    echo "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python $python_version found"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Create desktop shortcut (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cat > ~/Desktop/AeronixTestGenerator.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Aeronix Test Generator
Comment=PCB Test Plan Generator
Exec=python3 $(pwd)/UI.py
Icon=applications-engineering
Terminal=false
Categories=Development;Engineering;
EOF
    chmod +x ~/Desktop/AeronixTestGenerator.desktop
    echo "Desktop shortcut created"
fi

echo "Installation complete!"
echo "Run: python3 UI.py"
'''
            
            with open(os.path.join(package_dir, "install.sh"), "w") as f:
                f.write(install_script)
            
            # Create Windows batch file
            windows_script = f'''@echo off
echo Installing Aeronix Test Generator v{self.version}

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt

echo Installation complete!
echo Run: python UI.py
pause
'''
            
            with open(os.path.join(package_dir, "install.bat"), "w") as f:
                f.write(windows_script)
            
            # Create ZIP package
            zip_filename = f"{package_dir}.zip"
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(package_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, package_dir)
                        zipf.write(file_path, arcname)
            
            print(f"✅ Installation package created: {zip_filename}")
            return zip_filename
            
        except Exception as e:
            print(f"❌ Package creation failed: {e}")
            return None
    
    def create_documentation(self):
        """Create deployment documentation"""
        print("📚 Creating documentation...")
        
        readme_content = f'''# Aeronix Test Generator v{self.version}

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
1. Download `{self.project_name}.exe`
2. Run the executable
3. No additional setup required

### Option 2: Python Installation
1. Extract `{self.project_name}_v{self.version}.zip`
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
© {datetime.now().year} Aeronix Solutions
'''
        
        try:
            with open("README.md", "w") as f:
                f.write(readme_content)
            
            print("Documentation created")
            return True
            
        except Exception as e:
            print(f"Documentation creation failed: {e}")
            return False

def main():
    """Main deployment function"""
    print("AERONIX TEST GENERATOR DEPLOYMENT")
    print("="*50)
    
    packager = DeploymentPackager()
    packager.create_documentation()
    package_file = packager.create_installer_package()
    packager.create_docker_image()
    
    print("\nDeployment Options Created:")
    print("1. Installation package (ZIP)")
    print("2. Docker container setup")
    print("3. Documentation")
    
    create_exe = input("\nCreate standalone executable? (y/n): ").lower() == 'y'
    if create_exe:
        packager.create_executable()
    
    print("\n Deployment package ready!")
    print(f"Package: {package_file}")
    print("Docker: Use Dockerfile")
    print("Docs: README.md")

if __name__ == "__main__":
    main()