import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My First PyQt App")
        self.setGeometry(100, 100, 400, 200)  # x, y, width, height
        
        # Add a label
        self.label = QLabel("Hello PyQt!", self)
        self.label.move(150, 50)
        
        # Add a button
        self.button = QPushButton("Click me!", self)
        self.button.move(150, 100)
        self.button.clicked.connect(self.button_clicked)
    
    def button_clicked(self):
        self.label.setText("Button was clicked!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())