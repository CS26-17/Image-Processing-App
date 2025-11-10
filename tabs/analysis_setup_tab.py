"""
Analysis Setup Tab - Configure analysis parameters and settings
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class AnalysisSetupTab(QWidget):
    """
    Analysis Setup tab widget for configuring analysis parameters
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the analysis setup tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        analysis_label = QLabel("Analysis Configuration")
        analysis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analysis_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 20px;")
        layout.addWidget(analysis_label)
        
        analysis_content = QLabel("Configure analysis parameters and settings.\n\n"
                                "• Algorithm selection\n"
                                "• Parameter tuning\n"
                                "• Output format\n"
                                "• Automation settings")
        analysis_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analysis_content.setStyleSheet("font-size: 14px; color: #7f8c8d; margin: 20px;")
        analysis_content.setWordWrap(True)
        layout.addWidget(analysis_content)
        
        layout.addStretch()
