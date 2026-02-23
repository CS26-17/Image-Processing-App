"""
Analysis Setup Tab - Configure analysis parameters and settings
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QLineEdit, QComboBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


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
        
        # Create main analysis layout
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        
        # Model selection section
        model_layout = QHBoxLayout()
        model_label = QLabel("Select Model:")
        model_label.setStyleSheet("font-size: 14px; margin-right: 10px;")
        
        vg_button = QPushButton("VGG16")
        res_button = QPushButton("ResNet50")
        for btn in (vg_button, res_button):
            btn.setCheckable(True)
            btn.setStyleSheet("""QPushButton{
                                font-size: 15px; 
                                border: none; 
                                border-radius: 6px;
                                background-color: #52ba59; 
                                padding: 12px 24px;
                                color: white;
                              }
                              QPushButton:hover{
                                background-color: #45a84c;
                              }
                              QPushButton:checked{
                                background-color: #24752a; 
                              }
                              """)
        button_group = QButtonGroup()
        button_group.setExclusive(True)
        button_group.addButton(vg_button)
        button_group.addButton(res_button)
        #Documentation button
        doc1_btn = QPushButton("?")
        doc1_btn.setFixedSize(20, 20)
        doc1_btn.setStyleSheet("""
            QPushButton{
               font-size: 15px;
               border: 2px solid blue;
               border-radius: 10px;
               color: blue;            
            }
            QPushButton:hover{
               border: 2px solid #6971f5;
               color: #6971f5;            
            }                    
        """)
        doc1_btn.setToolTip("Choose which CNN model you want to do the comparisons on your \n images." \
        " Both models are built on PyTorch and are trained on ImageNet data.")
        #adding widget to the page
        model_layout.addWidget(model_label)
        model_layout.addWidget(vg_button)
        model_layout.addWidget(res_button)
        model_layout.addWidget(doc1_btn)
        model_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        analysis_layout.addLayout(model_layout)

        #Setting up user file name choice input field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name for result files: ")
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter name for files. . .")
        name_input.setFixedWidth(200)
        name_input.setStyleSheet("""
                                QLineEdit{
                                    font-size: 14px;
                                    border: 2px solid black;
                                 }

                                """)
        #Documentation button
        doc2_btn = QPushButton("?")
        doc2_btn.setFixedSize(20, 20)
        doc2_btn.setStyleSheet("""
            QPushButton{
               font-size: 15px;
               border: 2px solid blue;
               border-radius: 10px;
               color: blue;            
            }
            QPushButton:hover{
               border: 2px solid #6971f5;
               color: #6971f5;            
            }                   
        """)
        doc2_btn.setToolTip("Enter the name that you want all of your analysis" \
        "result files to use. \n Files will include the raw data as a csv file, a heatmap \n" \
        " image, and more")
       #adding file name input to the page
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_input)
        name_layout.addWidget(doc2_btn)
        name_widget = QWidget()
        name_widget.setLayout(name_layout)
        analysis_layout.addWidget(name_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        apply_layout = QHBoxLayout()
        apply_button = QPushButton("Apply")
        apply_button.setStyleSheet("""QPushButton{
                                font-size: 15px; 
                                border: none; 
                                border-radius: 6px;
                                background-color: #202af5; 
                                padding: 12px 24px;
                                color: white;
                              }
                              QPushButton:hover{
                                background-color: #040ed1;
                              }
                              QPushButton:checked{
                                background-color: #010885; 
                              }
                              """)
        apply_layout.addWidget(apply_button)
        apply_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
       
        analysis_layout.addLayout(apply_layout)
        analysis_widget.setObjectName("analysis_widget")
        
        # Add the analysis widget to the main layout
        layout.addWidget(analysis_widget)
        layout.addStretch()
