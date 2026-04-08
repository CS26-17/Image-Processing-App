"""
Analysis Setup Tab - Configure analysis parameters and settings
"""
 
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QLineEdit, QButtonGroup, QFileDialog,
                               QFrame, QProgressBar, QToolTip)
from PySide6.QtCore import Qt, Signal, QPoint, QProcess, QProcessEnvironment
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
 
    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _make_info_button(self, text: str) -> QPushButton:
        """
        Return a circular '?' button that shows a tooltip popup on click
        positioned just below the button.
        """
        btn = QPushButton("?")
        btn.setFixedSize(22, 22)
        btn.setStyleSheet("""
            QPushButton { font-size: 13px; border: 2px solid #3b82f6;
                          border-radius: 11px; color: #3b82f6; background: white; }
            QPushButton:hover { border-color: #2563eb; color: #2563eb; }
        """)
        # Capture text in a default-arg lambda so each button keeps its own message
        btn.clicked.connect(
            lambda checked=False, msg=text, b=btn:
                QToolTip.showText(
                    b.mapToGlobal(QPoint(0, b.height() + 4)),
                    msg,
                    b
                )
        )
        return btn

    def setup_ui(self):
        """Setup the analysis setup tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ── Page title ────────────────────────────────────────────────
        title_label = QLabel("Analysis Configuration")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 6px;"
        )
        layout.addWidget(title_label)

        # ── Card helper style (shared by all section frames) ──────────
        CARD_STYLE = """
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """
        SECTION_TITLE_STYLE = (
            "font-size: 14px; font-weight: bold; color: #2c3e50;"
            "border-bottom: 1px solid #e0e0e0; padding-bottom: 4px; margin-bottom: 4px;"
        )

        # ── Model selection card ──────────────────────────────────────
        model_card = QFrame()
        model_card.setStyleSheet(CARD_STYLE)
        model_card_layout = QVBoxLayout(model_card)
        model_card_layout.setContentsMargins(18, 14, 18, 14)
        model_card_layout.setSpacing(10)

        model_title = QLabel("Select Model")
        model_title.setStyleSheet(SECTION_TITLE_STYLE)
        model_card_layout.addWidget(model_title)

        model_row = QHBoxLayout()
        model_row.setSpacing(10)

        self.vg_button = QPushButton("VGG16")
        self.res_button = QPushButton("ResNet50")
        MODEL_BTN_STYLE = """
            QPushButton {
                font-size: 14px;
                border: 2px solid #52ba59;
                border-radius: 6px;
                background-color: white;
                padding: 10px 28px;
                color: #2c7a30;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #edfaee;
            }
            QPushButton:checked {
                background-color: #52ba59;
                color: white;
                border-color: #24752a;
            }
        """
        for btn in (self.vg_button, self.res_button):
            btn.setCheckable(True)
            btn.setStyleSheet(MODEL_BTN_STYLE)

        button_group = QButtonGroup(self)
        button_group.setExclusive(True)
        button_group.addButton(self.vg_button)
        button_group.addButton(self.res_button)

        doc1_btn = self._make_info_button(
            "VGG16 and ResNet50 are deep learning models trained on ImageNet.\n\n"
            "VGG16 is simpler and works well for general image comparison.\n\n"
            "ResNet50 is more advanced and tends to produce more accurate similarity\n"
            "scores, especially for complex or visually similar images.\n\n"
            "If you are unsure, ResNet50 is the recommended choice."
        )

        model_row.addStretch()
        model_row.addWidget(self.vg_button)
        model_row.addWidget(self.res_button)
        model_row.addWidget(doc1_btn)
        model_row.addStretch()
        model_card_layout.addLayout(model_row)
        layout.addWidget(model_card)

        # ── Image folder card ─────────────────────────────────────────
        folder_card = QFrame()
        folder_card.setStyleSheet(CARD_STYLE)
        folder_card_layout = QVBoxLayout(folder_card)
        folder_card_layout.setContentsMargins(18, 14, 18, 14)
        folder_card_layout.setSpacing(10)

        folder_title = QLabel("Image Folder")
        folder_title.setStyleSheet(SECTION_TITLE_STYLE)
        folder_card_layout.addWidget(folder_title)

        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)

        self.folder_button = QPushButton("Browse…")
        self.folder_button.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                background-color: #7c3aed;
                padding: 8px 20px;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #6d28d9; }
        """)
        self.folder_button.clicked.connect(self.browse_folder)

        doc_folder_btn = self._make_info_button(
            "Select the folder containing the images you want to analyse.\n\n"
            "All supported image files (JPG, PNG, BMP, TIFF, WEBP) inside\n"
            "the folder will be included in the analysis.\n\n"
            "If you arrived here via the 'Analyse Images' button on the Upload\n"
            "tab, your uploaded images are already pre-filled here and you do\n"
            "not need to browse."
        )

        # Label shown when images are pre-loaded from the Upload tab
        self.upload_source_label = QLabel("")
        self.upload_source_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #166534;
                background-color: #dcfce7;
                border: 1px solid #86efac;
                border-radius: 5px;
                padding: 5px 10px;
            }
        """)
        self.upload_source_label.setVisible(False)

        folder_row.addStretch()
        folder_row.addWidget(self.folder_button)
        folder_row.addWidget(doc_folder_btn)
        folder_row.addWidget(self.upload_source_label)
        folder_row.addStretch()
        folder_card_layout.addLayout(folder_row)
        layout.addWidget(folder_card)

        # ── Result name card ──────────────────────────────────────────
        name_card = QFrame()
        name_card.setStyleSheet(CARD_STYLE)
        name_card_layout = QVBoxLayout(name_card)
        name_card_layout.setContentsMargins(18, 14, 18, 14)
        name_card_layout.setSpacing(10)

        name_title = QLabel("Result File Name")
        name_title.setStyleSheet(SECTION_TITLE_STYLE)
        name_card_layout.addWidget(name_title)

        name_row = QHBoxLayout()
        name_row.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setFixedWidth(220)
        self.name_input.setPlaceholderText("e.g. Experiment1")
        self.name_input.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 6px 10px;
                background: white;
                color: #1f2937;
            }
            QLineEdit:focus { border-color: #3b82f6; }
        """)

        doc2_btn = self._make_info_button(
            "Choose a name that will be used for all output files from this run.\n\n"
            "The analysis will generate:\n"
            "  • A CSV file containing the full similarity score matrix\n"
            "  • A heatmap image visualising those scores\n"
            "  • Any additional result files produced by the model\n\n"
            "Example: entering 'Trial1' produces 'Trial1_similarity.csv', etc."
        )

        name_row.addStretch()
        name_row.addWidget(self.name_input)
        name_row.addWidget(doc2_btn)
        name_row.addStretch()
        name_card_layout.addLayout(name_row)
        layout.addWidget(name_card)

        # ── Run button ────────────────────────────────────────────────
        run_row = QHBoxLayout()
        self.apply_button = QPushButton("▶  Run Analysis")
        self.apply_button.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                background-color: #2563eb;
                padding: 13px 40px;
                color: white;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton:disabled { background-color: #93c5fd; }
        """)
        self.apply_button.clicked.connect(self.on_apply)
        run_row.addStretch()
        run_row.addWidget(self.apply_button)
        run_row.addStretch()
        layout.addLayout(run_row)

        # ── Status label ──────────────────────────────────────────────
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(
            "font-size: 13px; color: #374151; margin-top: 4px;"
        )
        layout.addWidget(self.status_label)

        # ── Progress bar ──────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #f3f4f6;
                height: 16px;
                text-align: center;
                color: #1f2937;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)

        layout.addStretch()
    
    def set_folder(self, folder: str) -> None:
        """
        Called by HomeTab.go_to_analysis() to pre-fill the folder with the
        images that were loaded on the Upload tab.
        Shows a green badge next to the Browse button so the user knows
        the images come from the Upload tab.
        """
        self.selected_folder = folder
        n = len([
            f for f in os.listdir(folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'))
        ])
        self.upload_source_label.setText(f"✓ Using {n} image(s) from Upload tab")
        self.upload_source_label.setVisible(True)
        self.status_label.setText("")

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.selected_folder = folder
            # Hide the upload-source badge — user chose a different folder manually
            self.upload_source_label.setVisible(False)
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