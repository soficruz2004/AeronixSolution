import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
from typing import List, Dict, Any, Optional
import threading
from enum import Enum
from AI_model import TestGenerator

# Import your modules
try:
    from parser_but_better import parse_inputs
    from format_output import format_test_output
    import AI_model
    IMPORTS_SUCCESS = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_SUCCESS = False
    
    # Mock classes for testing
    class TestGenerationResult(Enum):
        SUCCESS = "success"
        ERROR = "error"
        NO_DATA = "no_data"
        API_ERROR = "api_error"

    class TestGenerationStatus:
        def __init__(self, result: TestGenerationResult, data: Optional[str] = None, error: Optional[str] = None):
            self.result = result
            self.data = data
            self.error = error

    def parse_inputs(files):
        return {"bom_components": [], "test_points": [], "requirements": {}}
    
    def detect_file_type(path, content):
        return "UNKNOWN"
    
    def get_LORA_test(bom, tp, req):
        return TestGenerationStatus(TestGenerationResult.SUCCESS, "Mock LoRa test result")
    
    def get_arduino_test(bom, tp):
        return TestGenerationStatus(TestGenerationResult.SUCCESS, "Mock Arduino test result")

class TestGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Aeronix Test Generator")
        self.root.geometry("1200x800")
        
        # Data storage
        self.loaded_files = []
        self.parsed_data = {}
        self.current_results = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Aeronix Test Plan Generator", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # File Loading Section
        file_frame = ttk.LabelFrame(main_frame, text="File Management", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Load Files", 
                  command=self.load_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear Files", 
                  command=self.clear_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Parse Files", 
                  command=self.parse_files).pack(side=tk.LEFT, padx=(0, 5))
        
        # File list
        self.file_listbox = tk.Listbox(file_frame, height=6)
        self.file_listbox.pack(fill=tk.X, pady=(0, 5))
        
        # Parsing info
        self.parse_info_label = ttk.Label(file_frame, text="No files parsed")
        self.parse_info_label.pack()
        
        # Test Generation Section
        test_frame = ttk.LabelFrame(main_frame, text="Test Generation", padding="10")
        test_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Generation buttons
        gen_button_frame = ttk.Frame(test_frame)
        gen_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(gen_button_frame, text="Generate LoRa Test", 
                  command=self.generate_lora_test).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(gen_button_frame, text="Generate Arduino Test", 
                  command=self.generate_arduino_test).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(gen_button_frame, text="Export Results", 
                  command=self.export_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(gen_button_frame, text="Create Document", 
                  command=self.create_professional_doc).pack(side=tk.LEFT, padx=(0, 5))
        
        # Results display
        results_notebook = ttk.Notebook(test_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # LoRa results tab
        self.lora_tab = ttk.Frame(results_notebook)
        results_notebook.add(self.lora_tab, text="LoRa Test")
        self.lora_text = scrolledtext.ScrolledText(self.lora_tab, height=15, width=100)
        self.lora_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Arduino results tab
        self.arduino_tab = ttk.Frame(results_notebook)
        results_notebook.add(self.arduino_tab, text="Arduino Test")
        self.arduino_text = scrolledtext.ScrolledText(self.arduino_tab, height=15, width=100)
        self.arduino_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X)
        
        # Show import status
        if not IMPORTS_SUCCESS:
            self.update_status("Warning: Some imports failed - using mock functions")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def load_files(self):
        """Load files for processing"""
        try:
            files = filedialog.askopenfilenames(
                title="Select files to process",
                filetypes=[
                    ("All supported", "*.BomDoc *.SchDoc *.PrjPcb *.PcbDoc *.csv *.txt *.json *.xml *.pdf *.docx *.md *.ipc"),
                    ("Altium BOM", "*.BomDoc"),
                    ("Altium Schematic", "*.SchDoc"),
                    ("Altium Project", "*.PrjPcb"),
                    ("Altium PCB", "*.PcbDoc"),
                    ("CSV files", "*.csv"),
                    ("PDF files", "*.pdf"),
                    ("Word documents", "*.docx"),
                    ("Text files", "*.txt"),
                    ("JSON files", "*.json"),
                    ("XML files", "*.xml"),
                    ("IPC files", "*.ipc"),
                    ("All files", "*.*")
                ]
            )
            
            if files:
                self.loaded_files = list(files)
                self.update_file_list()
                self.update_status(f"Loaded {len(files)} files")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load files: {str(e)}")
            self.update_status("Error loading files")
    
    def clear_files(self):
        """Clear loaded files"""
        self.loaded_files = []
        self.parsed_data = {}
        self.update_file_list()
        self.parse_info_label.config(text="No files parsed")
        self.update_status("Files cleared")
    
    def update_file_list(self):
        """Update the file listbox"""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.loaded_files:
            filename = os.path.basename(file_path)
            self.file_listbox.insert(tk.END, filename)
    
    def parse_files(self):
        """Parse loaded files"""
        if not self.loaded_files:
            messagebox.showwarning("No Files", "Please load files first")
            return
        
        try:
            self.update_status("Parsing files...")
            
            # Prepare files for parsing
            files_for_parsing = []
            for file_path in self.loaded_files:
                try:
                    # Handle different file types
                    file_ext = os.path.splitext(file_path)[1].lower()
                    
                    if file_ext in ['.bomdoc', '.schdoc', '.pcbdoc', '.prjpcb']:
                        # Altium files - binary format, needs special handling
                        files_for_parsing.append({
                            'path': file_path,
                            'content': f"ALTIUM_FILE:{file_ext}",  # Placeholder
                            'type': 'ALTIUM_BINARY'
                        })
                    elif file_ext == '.pdf':
                        # PDF files need special handling
                        files_for_parsing.append({
                            'path': file_path,
                            'content': "PDF_FILE",  # Placeholder
                            'type': 'PDF'
                        })
                    else:
                        # Text-based files
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        files_for_parsing.append({
                            'path': file_path,
                            'content': content,
                            'type': 'TEXT'
                        })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
            
            if files_for_parsing:
                self.parsed_data = parse_inputs(files_for_parsing)
                
                # Update info display
                bom_count = len(self.parsed_data.get('bom_components', []))
                tp_count = len(self.parsed_data.get('test_points', []))
                file_types = self.parsed_data.get('metadata', {}).get('file_types', {})
                
                info_text = f"Parsed: {bom_count} BOM components, {tp_count} test points"
                if file_types:
                    altium_count = sum(1 for ft in file_types.values() if 'ALTIUM' in str(ft))
                    if altium_count > 0:
                        info_text += f", {altium_count} Altium files detected"
                
                self.parse_info_label.config(text=info_text)
                self.update_status("Files parsed successfully")
            else:
                raise ValueError("No files could be read")
                
        except Exception as e:
            messagebox.showerror("Parse Error", f"Failed to parse files: {str(e)}")
            self.update_status("Parse error")
    
    def generate_lora_test(self):
        """Generate LoRa test plan"""
        if not self.parsed_data:
            messagebox.showwarning("No Data", "Please parse files first")
            return
        
        def generate():
            try:
                # Update status on main thread
                self.root.after(0, lambda: self.update_status("Generating LoRa test..."))
                
                bom_components = self.parsed_data.get('bom_components', [])
                test_points = self.parsed_data.get('test_points', [])
                requirements = self.parsed_data.get('requirements', {})
                
                result = TestGenerator.get_LORA_test(bom_components, test_points, requirements)
                
                # Update UI on main thread
                def update_ui():
                    if result:
                        self.current_results['lora'] = result
                        self.lora_text.delete(1.0, tk.END)
                        self.lora_text.insert(1.0, result)
                        self.update_status("LoRa test generated successfully")
                    else:
                        messagebox.showerror("Generation Error", "LoRa test generation failed")
                        self.update_status("LoRa test generation failed")
                
                self.root.after(0, update_ui)
                    
            except Exception as e:
                # Handle errors on main thread
                error_msg = str(e)
                def show_error():
                    messagebox.showerror("Error", f"LoRa test generation error: {error_msg}")
                    self.update_status("LoRa test generation error")
                
                self.root.after(0, show_error)
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()
    
    def generate_arduino_test(self):
        """Generate Arduino test plan"""
        if not self.parsed_data:
            messagebox.showwarning("No Data", "Please parse files first")
            return
        
        def generate():
            try:
                # Update status on main thread
                self.root.after(0, lambda: self.update_status("Generating Arduino test..."))
                
                bom_components = self.parsed_data.get('bom_components', [])
                test_points = self.parsed_data.get('test_points', [])
                
                result = TestGenerator.get_arduino_test(bom_components, test_points)
                
                # Update UI on main thread
                def update_ui():
                    if result:
                        self.current_results['arduino'] = result
                        self.arduino_text.delete(1.0, tk.END)
                        self.arduino_text.insert(1.0, result)
                        self.update_status("Arduino test generated successfully")
                    else:
                        messagebox.showerror("Generation Error", "Arduino test generation failed")
                        self.update_status("Arduino test generation failed")
                
                self.root.after(0, update_ui)
                    
            except Exception as e:
                # Handle errors on main thread
                error_msg = str(e)
                def show_error():
                    messagebox.showerror("Error", f"Arduino test generation error: {error_msg}")
                    self.update_status("Arduino test generation error")
                
                self.root.after(0, show_error)
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()
    
    def export_results(self):
        """Export generated test results"""
        if not self.current_results:
            messagebox.showwarning("No Results", "Please generate some tests first")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                title="Export test results",
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                export_data = {
                    'generated_tests': self.current_results,
                    'parsed_data_summary': {
                        'bom_components': len(self.parsed_data.get('bom_components', [])),
                        'test_points': len(self.parsed_data.get('test_points', [])),
                        'files_processed': len(self.loaded_files)
                    }
                }
                
                with open(filename, 'w') as f:
                    if filename.endswith('.json'):
                        json.dump(export_data, f, indent=2)
                    else:
                        f.write(str(export_data))
                
                self.update_status(f"Results exported to {os.path.basename(filename)}")
                messagebox.showinfo("Export Complete", f"Results exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
            self.update_status("Export failed")
    
    def create_professional_doc(self):
        """Create professional Word document"""
        if not self.current_results:
            messagebox.showwarning("No Results", "Please generate some tests first")
            return
        
        try:
            device_type = "LoRa Car Radio" if 'lora' in self.current_results else "Arduino"
            test_data = self.current_results.get('lora') or self.current_results.get('arduino')
            
            if test_data:
                filename = format_test_output(test_data, device_type)
                self.update_status(f"Professional document created: {os.path.basename(filename)}")
                messagebox.showinfo("Document Created", f"Professional document saved:\n{filename}")
            else:
                messagebox.showerror("Error", "No test data available")
                
        except Exception as e:
            messagebox.showerror("Document Error", f"Failed to create document: {str(e)}")
            self.update_status("Document creation failed")

def main():
    """Main function to run the application"""
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    root = tk.Tk()
    app = TestGeneratorUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application closed by user")

if __name__ == "__main__":
    main()