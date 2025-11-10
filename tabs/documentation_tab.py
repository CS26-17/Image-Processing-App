"""
Documentation Tab - Application documentation and user guide
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class DocumentationTab(QWidget):
    """
    Documentation tab widget for displaying user guide and documentation
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the documentation tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        docs_label = QLabel("Application Documentation")
        docs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        docs_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 20px;")
        layout.addWidget(docs_label)
        
        docs_content = QLabel("User guide and application documentation.\n\n"
                            "• How to use features\n"
                            "• Troubleshooting guide\n"
                            "• Keyboard shortcuts\n"
                            "• API documentation")
        docs_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        docs_content.setStyleSheet("font-size: 14px; color: #7f8c8d; margin: 20px;")
        docs_content.setWordWrap(True)
        layout.addWidget(docs_content)
        
        layout.addStretch()
