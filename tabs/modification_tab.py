"""
Modification Tab - Image modification and editing tools
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class ModificationTab(QWidget):
    """
    Modification tab widget for image editing and modification tools
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the modification tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        mod_label = QLabel("Image Modification Tools")
        mod_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mod_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 20px;")
        layout.addWidget(mod_label)
        
        mod_content = QLabel("Advanced image editing and modification tools.\n\n"
                           "• Filters and effects\n"
                           "• Color adjustment\n"
                           "• Crop and resize\n"
                           "• Batch processing")
        mod_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mod_content.setStyleSheet("font-size: 14px; color: #7f8c8d; margin: 20px;")
        mod_content.setWordWrap(True)
        layout.addWidget(mod_content)
        
        layout.addStretch()
