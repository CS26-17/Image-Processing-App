"""
Analysis Setup Tab - Configure analysis parameters and settings
"""
 
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QButtonGroup, QFileDialog)
from PySide6.QtCore import Qt, Signal
from PySide6.QtCore import QProcess, QProcessEnvironment
from PySide6.QtWidgets import QProgressBar
import os
import sys
 
class AnalysisSetupTab(QWidget):
    """
    Analysis Setup tab widget for configuring analysis parameters
    """

    analysis_complete = Signal(str)  # emits output_dir path on success

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_folder = ""
        self.selected_model = None
        self.process = None
        self._stderr_buffer = []
        self.setup_ui()
    
    def get_project_root(self):
        """
        Returns the project root directory.
        """
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 
    def get_python_executable(self):
        """
        Returns the path to the venv Python interpreter in the project root.
        Falls back to sys.executable and surfaces a warning in the status label
        so it is obvious when the venv is not being used.
        """
        project_root = self.get_project_root()
 
        if sys.platform == "win32":
            venv_python = os.path.join(project_root, ".venv", "Scripts", "python.exe")
        else:
            venv_python = os.path.join(project_root, ".venv", "bin", "python")
 
        if os.path.isfile(venv_python):
            return venv_python
 
        # Venv not found - warn the user so they know why packages may be missing
        self.status_label.setText(
            f"Warning: .venv not found in {project_root}. "
            "Run the launch script first to create it."
        )
        return sys.executable
 
    def get_script_path(self):
        """
        Returns the absolute path to run_models.py (project root).
        """
        project_root = self.get_project_root()
        script = os.path.join(project_root, "run_models.py")
        if not os.path.isfile(script):
            raise FileNotFoundError(
                f"run_models.py not found at: {script}\n"
                "Make sure run_models.py is in the project root folder."
            )
        return script
 
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
        
        # Model choice buttons
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
 
        # Documentation button
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
        doc1_btn.setToolTip("Choose which CNN model you want to do the comparisons on your \n images."
                            " Both models are built on PyTorch and are trained on ImageNet data.")
 
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.vg_button)
        model_layout.addWidget(self.res_button)
        model_layout.addWidget(doc1_btn)
        model_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        analysis_layout.addLayout(model_layout)
 
        # Choose folder
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
 
        # Result file name input
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
 
        # Documentation button
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
        doc2_btn.setToolTip("Enter the name that you want all of your analysis"
                            "result files to use. \n Files will include the raw data as a csv file, a heatmap \n"
                            " image, and more")
        name_layout.addWidget(doc2_btn)
        name_widget = QWidget()
        name_widget.setLayout(name_layout)
        analysis_layout.addWidget(name_widget, alignment=Qt.AlignmentFlag.AlignHCenter)
 
        # Apply button
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
 
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #333333; margin-top: 15px;")
        analysis_layout.addWidget(self.status_label)
 
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        analysis_layout.addWidget(self.progress_bar)
        
        layout.addWidget(analysis_widget)
        layout.addStretch()
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.selected_folder = folder
            self.status_label.setText(f"Selected folder: {folder}")
 
    def on_apply(self):
        # Validate inputs
        if not self.selected_folder:
            self.status_label.setText("Please select and image folder")
            return
        if not (self.vg_button.isChecked() or self.res_button.isChecked()):
            self.status_label.setText("Please select model")
            return
        if not (self.vg_button.isChecked() or self.res_button.isChecked()):
            self.status_label.setText("Please select a model")
            return
        model = "vgg16" if self.vg_button.isChecked() else "resnet50"
        name = self.name_input.text().strip()
        if not name:
            self.status_label.setText("Please enter a result name")
            return
 
        # Results go into a "results" subfolder inside the chosen image folder
        self.output_dir = os.path.join(self.selected_folder, "results")
        output_dir = self.output_dir
        os.makedirs(output_dir, exist_ok=True)
 
        self.status_label.setText("Running analysis...")
        self.apply_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self._stderr_buffer = []
 
        # Run run_models.py with the venv Python interpreter
        python = self.get_python_executable()
        try:
            script = self.get_script_path()
        except FileNotFoundError as e:
            self.apply_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.status_label.setText(str(e))
            return
 
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.finished.connect(self.on_analysis_finished)
 
        env = QProcessEnvironment.systemEnvironment()
        env.insert("OUTPUT_DIR", output_dir)
        self.process.setProcessEnvironment(env)
 
        self.process.start(
            python,
            [
                script,
                "--model", model,
                "--folder", self.selected_folder,
                "--name", name,
            ]
        )
 
    def handle_output(self):
        data = self.process.readAllStandardOutput().data().decode()
        for line in data.splitlines():
            if line.startswith("PROGRESS:"):
                try:
                    value = int(line.split(":")[1])
                    self.progress_bar.setValue(value)
                except ValueError:
                    pass
 
    def handle_error(self):
        """Buffer stderr - tqdm and torchvision write harmless progress to stderr.
        We only surface it in the UI if the process actually fails."""
        err = self.process.readAllStandardError().data().decode().strip()
        if err:
            self._stderr_buffer.append(err)
 
    def on_analysis_finished(self, exit_code, exit_status):
        self.apply_button.setEnabled(True)
        if exit_code == 0:
            self.progress_bar.setValue(100)
            self.status_label.setText("Analysis complete! Results saved to folder.")
            self.analysis_complete.emit(self.output_dir)
        else:
            self.progress_bar.setVisible(False)
            # Show the last meaningful stderr line (filter out tqdm noise)
            error_detail = ""
            if self._stderr_buffer:
                meaningful = [
                    ln for ln in "\n".join(self._stderr_buffer).splitlines()
                    if ln.strip() and "\r" not in ln and "%|" not in ln
                ]
                if meaningful:
                    error_detail = meaningful[-1]
            if error_detail:
                self.status_label.setText(f"Analysis failed: {error_detail}")
            else:
                self.status_label.setText(
                    f"Analysis failed (exit code {exit_code}). "
                    "Check that your image folder contains supported images."
                )
      