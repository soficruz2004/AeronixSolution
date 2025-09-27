import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QTextEdit, QListWidget, QComboBox, QCheckBox,
                             QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aeronix Solution - Main Application")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height
        
        # Set up central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title label
        title_label = QLabel("Aeronix Solution Dashboard")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create tabs using widgets (simple alternative to QTabWidget)
        self.setup_ui(main_layout)
        
    def setup_ui(self, layout):
        # Button section
        button_layout = QHBoxLayout()
        
        # Buttons for different actions
        self.btn_add = QPushButton("Add Item")
        self.btn_remove = QPushButton("Remove Item")
        self.btn_process = QPushButton("Process Data")
        self.btn_settings = QPushButton("Settings")
        
        # Style buttons
        buttons = [self.btn_add, self.btn_remove, self.btn_process, self.btn_settings]
        for btn in buttons:
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
        
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_remove)
        button_layout.addWidget(self.btn_process)
        button_layout.addWidget(self.btn_settings)
        
        layout.addLayout(button_layout)
        
        # Input section
        input_layout = QHBoxLayout()
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter text here...")
        self.text_input.setFixedHeight(35)
        
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        
        input_layout.addWidget(QLabel("Input:"))
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(QLabel("Options:"))
        input_layout.addWidget(self.combo_box)
        
        layout.addLayout(input_layout)
        
        # List section
        list_layout = QHBoxLayout()
        
        # Left list
        self.left_list = QListWidget()
        self.left_list.addItems(["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"])
        
        # Right list
        self.right_list = QListWidget()
        
        # List buttons
        list_buttons_layout = QVBoxLayout()
        self.btn_move_right = QPushButton(">")
        self.btn_move_left = QPushButton("<")
        
        list_buttons_layout.addWidget(self.btn_move_right)
        list_buttons_layout.addWidget(self.btn_move_left)
        list_buttons_layout.addStretch()
        
        list_layout.addWidget(QLabel("Available Items:"))
        list_layout.addWidget(self.left_list)
        list_layout.addLayout(list_buttons_layout)
        list_layout.addWidget(QLabel("Selected Items:"))
        list_layout.addWidget(self.right_list)
        
        layout.addLayout(list_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Connect signals to slots
        self.connect_signals()
    
    def connect_signals(self):
        """Connect button clicks to methods"""
        self.btn_add.clicked.connect(self.add_item)
        self.btn_remove.clicked.connect(self.remove_item)
        self.btn_process.clicked.connect(self.process_data)
        self.btn_settings.clicked.connect(self.show_settings)
        self.btn_move_right.clicked.connect(self.move_right)
        self.btn_move_left.clicked.connect(self.move_left)
    
    def add_item(self):
        text = self.text_input.text().strip()
        if text:
            self.left_list.addItem(text)
            self.text_input.clear()
            self.status_label.setText(f"Added: {text}")
    
    def remove_item(self):
        current_row = self.left_list.currentRow()
        if current_row >= 0:
            item = self.left_list.takeItem(current_row)
            self.status_label.setText(f"Removed: {item.text()}")
    
    def process_data(self):
        self.status_label.setText("Processing data...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Simulate processing with a timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # Update every 100ms
    
    def update_progress(self):
        current_value = self.progress_bar.value()
        if current_value >= 100:
            self.timer.stop()
            self.progress_bar.setVisible(False)
            self.status_label.setText("Processing complete!")
            QMessageBox.information(self, "Complete", "Data processing finished successfully!")
        else:
            self.progress_bar.setValue(current_value + 5)
    
    def show_settings(self):
        QMessageBox.information(self, "Settings", "Settings dialog would open here")
    
    def move_right(self):
        current_item = self.left_list.currentItem()
        if current_item:
            self.right_list.addItem(current_item.text())
            self.left_list.takeItem(self.left_list.currentRow())
    
    def move_left(self):
        current_item = self.right_list.currentItem()
        if current_item:
            self.left_list.addItem(current_item.text())
            self.right_list.takeItem(self.right_list.currentRow())

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Aeronix Solution")
    app.setApplicationVersion("1.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()