"""
Analysis Setup Tab - Configure analysis parameters and settings
"""
 
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QLineEdit, QButtonGroup, QFileDialog,
                               QFrame, QProgressBar, QToolTip)
from PySide6.QtCore import Qt, Signal, QPoint, QTimer
import multiprocessing
import os
 
class AnalysisSetupTab(QWidget):
    """
    Analysis Setup tab widget for configuring analysis parameters
    """

    analysis_complete = Signal(str)  # emits output_dir path on success

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_folder = ""
        self.selected_model = None
        self._worker_process = None
        self._progress_queue = None
        self._poll_timer = None
        self.setup_ui()
    
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
        btn.setObjectName("infoButton")
        btn.setStyleSheet("""
            QPushButton#infoButton {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #3b82f6;
                border-radius: 11px;
                color: #1e3a5f;
                background: white;
                padding: 0px;
            }
            QPushButton#infoButton:hover { background: #eff6ff; }
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
            "All supported image files (JPG, JPEG, GIF, PNG) inside\n"
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
            self.status_label.setText("Please select an image folder")
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
        os.makedirs(self.output_dir, exist_ok=True)

        self.status_label.setText("Running analysis...")
        self.apply_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Lazy import so torch doesn't load until analysis actually runs
        from run_models import run_cnn_analysis_worker

        self._progress_queue = multiprocessing.Queue()
        self._worker_process = multiprocessing.Process(
            target=run_cnn_analysis_worker,
            args=(model, self.selected_folder, name, self.output_dir, self._progress_queue),
            daemon=True,
        )
        self._worker_process.start()

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_queue)
        self._poll_timer.start(100)  # check for updates every 100 ms

    def _poll_queue(self):
        """Drain the inter-process queue and update UI accordingly."""
        import queue as _queue
        try:
            while True:
                msg_type, value = self._progress_queue.get_nowait()
                if msg_type == "PROGRESS":
                    self.progress_bar.setValue(value)
                elif msg_type == "DONE":
                    self._finish_analysis(success=True, detail=value)
                    return
                elif msg_type == "ERROR":
                    self._finish_analysis(success=False, detail=value)
                    return
        except _queue.Empty:
            pass

        # Guard against the worker dying without sending a message
        if self._worker_process and not self._worker_process.is_alive():
            self._finish_analysis(success=False, detail="Worker process exited unexpectedly.")

    def _finish_analysis(self, success: bool, detail: str):
        self._poll_timer.stop()
        self.apply_button.setEnabled(True)
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("Analysis complete! Results saved to folder.")
            self.analysis_complete.emit(detail)
        else:
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Analysis failed: {detail}")