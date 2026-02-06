# 3. Running on Docker Container:

# 	Open Docker Desktop and make sure your Docker engine is running
# 	In the terminal cd into the Image-Processing-App and run:
# 		docker build --no-cache -t image-analysis-cnn Docker/

# 	You can test the container in the terminal by running: 
# 	docker run --rm -v "C:\Image-Processing-App\testing_images\grey_images:/data" 
# 	-v "C:\Image-Processing-App\results:/app/output" image-analysis-cnn --model vgg16 
# 	--folder /data --name test_run

# 	Once that is working you can use the GUI to run the analysis

# 	Result files currently go to the image directory that was chosen for analysis

"""
Analysis Setup Tab - Configure analysis parameters and settings
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QButtonGroup, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtCore import QProcess
import os

class AnalysisSetupTab(QWidget):
    """
    Analysis Setup tab widget for configuring analysis parameters
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_folder = ""
        self.selected_model = None
        self.process = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the analysis setup tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        analysis_label = QLabel("Analysis Configuration")
        analysis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analysis_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 20px;")
        layout.addWidget(analysis_label)
        
        # Create main analysis layout
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        
        # Model selection section
        model_layout = QHBoxLayout()
        model_label = QLabel("Select Model:")
        model_label.setStyleSheet("font-size: 14px; margin-right: 10px;")
        
        #Model choice buttons
        self.vg_button = QPushButton("VGG16")
        self.res_button = QPushButton("ResNet50")
        for btn in (self.vg_button, self.res_button):
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
        button_group = QButtonGroup(self)
        button_group.setExclusive(True)
        button_group.addButton(self.vg_button)
        button_group.addButton(self.res_button)
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
        model_layout.addWidget(self.vg_button)
        model_layout.addWidget(self.res_button)
        model_layout.addWidget(doc1_btn)
        model_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        analysis_layout.addLayout(model_layout)

        #choose folder
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Select Image Folder")
        self.folder_button = QPushButton("Browse...")
        self.folder_button.setStyleSheet("""
          QPushButton{
            font-size: 14px;
            background-color: #8888ff;
            padding: 8px 18px;
            color: white;
            border-radius: 6px;                             
          }
          QPushButton:hover{
            background-color: #5555ff;
          }
        """)
        self.folder_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_button)
        folder_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        analysis_layout.addLayout(folder_layout)
        #Setting up user file name choice input field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name for result files: ")
        name_label.setStyleSheet("font-size: 14px; margin-right: 10px;")
        self.name_input = QLineEdit()
        self.name_input.setFixedWidth(200)
        self.name_input.setPlaceholderText("ex: Experiment1")
        self.name_input.setStyleSheet("""
          QLineEdit{
            font-size: 14px;
            border: 2px solid black;
            padding: 3px;
          }""")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        name_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
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
        
        name_layout.addWidget(doc2_btn)
        name_widget = QWidget()
        name_widget.setLayout(name_layout)
        analysis_layout.addWidget(name_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        apply_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.setStyleSheet("""QPushButton{
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
        self.apply_button.clicked.connect(self.on_apply)
        apply_layout.addWidget(self.apply_button)
        apply_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
       
        analysis_layout.addLayout(apply_layout)
        analysis_widget.setObjectName("analysis_widget")

        #status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #333333; margin-top: 15px;")
        analysis_layout.addWidget(self.status_label)
        
        # Add the analysis widget to the main layout
        layout.addWidget(analysis_widget)
        layout.addStretch()
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.selected_folder = folder
            self.status_label.setText(f"Selected folder: {folder}")

    def on_apply(self):
        #checking that user has added their input
        if not self.selected_folder:
            self.status_label.setText("Please select and image folder")
            return
        if not (self.vg_button.isChecked() or self.res_button.isChecked()):
            self.status_label.setText("Please select model")
            return
        model = "vgg16" if self.vg_button.isChecked() else "resnet50"
        name = self.name_input.text().strip()
        if not name:
            self.status_label.setText("Please enter a result name")
            return
        self.status_label.setText("Running analysis...")

        #starting docker container to run the analysis
        self.process = QProcess(self)
        self.process.finished.connect(self.on_analysis_finished)
        # self.process.readyReadStandardError.connect(self.on_analysis_error)
        self.process.start(
            # exe_path,
            # [
            #     "--model", model,
            #     "--folder", self.selected_folder,
            #     "--name", name
            # ]
             "docker",
             [
                 "run",
                 "--rm",
                 "-v", f"{self.selected_folder}:/data:ro",
                 "-v", f"{self.selected_folder}/results:/output",
                 "-e", "OUTPUT_DIR=/output",
                 "image-analysis-cnn",
                 "--model", model,
                 "--folder", "/data",
                 "--name", name
            ]
        )

    #successful analysis message
    def on_analysis_finished(self):
        self.status_label.setText("Anlaysis complete! Results saved to folder")
      