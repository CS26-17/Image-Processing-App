import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QTabWidget
from PyQt5.QtCore import Qt

class HelloWorldApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello World App")
        self.setGeometry(100, 100, 400, 300)
        
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        
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
        
        results_widget = QWidget()
        documentation_widget = QWidget()
        modification_widget = QWidget()
        analysis_setup_widget = QWidget()
        
        self.tab_widget.addTab(home_widget, "Home")
        self.tab_widget.addTab(results_widget, "Results")
        self.tab_widget.addTab(documentation_widget, "Documentation")
        self.tab_widget.addTab(modification_widget, "Modification")
        self.tab_widget.addTab(analysis_setup_widget, "Analysis Set up")
    
    def show_greeting(self):
        self.label.setText("Hello, World!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = HelloWorldApp()
    window.show()
    sys.exit(app.exec_())
