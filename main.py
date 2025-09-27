"""
Aeronix PCB Test Generator - Main Entry Point
Team solution to Aeronix's 2025 PCB Testing Hackathon
"""

import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    try:
        import openai
    except ImportError:
        missing.append("openai")
    
    try:
        import openpyxl
    except ImportError:
        missing.append("openpyxl")
    
    try:
        from docx import Document
    except ImportError:
        missing.append("python-docx")
    
    if missing:
        print("Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    return True

def main():
    """Main entry point"""
    print("Aeronix PCB Test Generator")
    print("=" * 40)
    
    if not check_dependencies():
        sys.exit(1)
    
    try:
        from UI import TestGeneratorUI
        import tkinter as tk
        
        root = tk.Tk()
        app = TestGeneratorUI(root)
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()