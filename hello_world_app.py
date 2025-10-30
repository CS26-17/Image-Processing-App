import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

class HelloWorldApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello World App")
        self.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.label = QLabel("Click the button to see a greeting!")
        self.label.setStyleSheet("font-size: 16px; margin: 20px;")
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.button = QPushButton("Click Me!")
        self.button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
                min-width: 120px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.button.clicked.connect(self.show_greeting)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
    
    def show_greeting(self):
        self.label.setText("Hello, World!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = HelloWorldApp()
    window.show()
    sys.exit(app.exec_())
