"""
Results Tab - Display processing results and analysis data
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class ResultsTab(QWidget):
    """
    Results tab widget for displaying processing results
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the results tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        results_label = QLabel("Processing Results")
        results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 20px;")
        layout.addWidget(results_label)
        
        results_content = QLabel("Processing results and analysis data will be displayed here.\n\n"
                               "• Image statistics\n"
                               "• Processing history\n"
                               "• Export options\n"
                               "• Comparison views")
        results_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_content.setStyleSheet("font-size: 14px; color: #7f8c8d; margin: 20px;")
        results_content.setWordWrap(True)
        layout.addWidget(results_content)
        
        layout.addStretch()
