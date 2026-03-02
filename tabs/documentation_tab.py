"""
Documentation Tab - Application documentation and user guide
"""

import os
import shutil
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextBrowser, QPushButton, QFrame, QSplitter,
                             QListWidget, QFileDialog, QMessageBox, QLineEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class DocumentationTab(QWidget):
    """
    Documentation tab widget for displaying user guide and documentation
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_documentation_content()
    
    def setup_ui(self):
        """Setup the documentation tab UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)
        
        # Create splitter for navigation and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(6)
        
        # Left side - Navigation
        self.nav_frame = QFrame()
        self.nav_frame.setMaximumWidth(300)
        self.nav_frame.setMinimumWidth(250)
        self.nav_frame.setStyleSheet("""
            QFrame {
                background-color: #f7f9fc;
                border: 1px solid #d8e1eb;
                border-radius: 8px;
            }
        """)
        
        nav_layout = QVBoxLayout(self.nav_frame)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(8)
        
        # Navigation header
        nav_header = QLabel("Documentation Center")
        nav_header.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        nav_header.setStyleSheet(
            "color: #102a43; padding: 10px 8px 6px 8px; border: none;"
        )
        nav_header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        nav_layout.addWidget(nav_header)

        self.nav_subtitle = QLabel("Browse guides and reference material")
        self.nav_subtitle.setStyleSheet("color: #486581; font-size: 12px; padding: 0 8px 8px 8px;")
        nav_layout.addWidget(self.nav_subtitle)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search sections...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #bcccdc;
                border-radius: 6px;
                padding: 8px 10px;
                color: #102a43;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #2f80ed;
            }
        """)
        self.search_input.textChanged.connect(self.filter_navigation)
        nav_layout.addWidget(self.search_input)
        
        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                font-size: 13px;
                color: #102a43;
                outline: 0;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 6px;
                margin: 1px 0;
                color: #102a43;
            }
            QListWidget::item:selected {
                background-color: #2f80ed;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #eaf2ff;
                color: #102a43;
            }
        """)
        
        # Add navigation items
        self.nav_items = [
            "Getting Started",
            "Image Upload Guide",
            "Image Modification",
            "Image Analysis",
            "Results Interpretation",
            "Troubleshooting",
            "Keyboard Shortcuts",
            "API Reference",
        ]
        
        for item in self.nav_items:
            self.nav_list.addItem(item)
        
        self.nav_list.currentRowChanged.connect(self.on_nav_changed)
        nav_layout.addWidget(self.nav_list)
        
        # User manual download button (supports PDF/Word selection)
        pdf_button = QPushButton("📥 Download User Manual")
        pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        pdf_button.clicked.connect(self.download_user_manual)
        nav_layout.addWidget(pdf_button)
        
        nav_layout.addStretch()
        
        # Right side - Content
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: #fdfefe;
                border: 1px solid #d8e1eb;
                border-radius: 8px;
            }
        """)
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(14, 12, 14, 12)
        content_layout.setSpacing(10)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)

        self.section_path_label = QLabel("Documentation")
        self.section_path_label.setStyleSheet("color: #627d98; font-size: 12px;")
        header_layout.addWidget(self.section_path_label)

        self.section_title_label = QLabel("Getting Started")
        self.section_title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.section_title_label.setStyleSheet("color: #102a43;")
        header_layout.addWidget(self.section_title_label)
        content_layout.addLayout(header_layout)
        
        # Content browser
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        self.content_browser.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: 1px solid #d8e1eb;
                border-radius: 8px;
                padding: 24px;
                font-size: 15px;
                line-height: 1.7;
                color: #102a43;
            }
            QTextBrowser h1 {
                color: #102a43;
                font-size: 24px;
                margin-bottom: 14px;
            }
            QTextBrowser h2 {
                color: #243b53;
                font-size: 20px;
                margin-top: 22px;
                margin-bottom: 12px;
            }
            QTextBrowser h3 {
                color: #334e68;
                font-size: 16px;
                margin-top: 16px;
                margin-bottom: 10px;
            }
            QTextBrowser p {
                margin-bottom: 12px;
                color: #102a43;
            }
            QTextBrowser ul, QTextBrowser ol {
                margin: 8px 0px 10px 20px;
                color: #102a43;
            }
            QTextBrowser li {
                margin-bottom: 6px;
                color: #102a43;
            }
            QTextBrowser code {
                background-color: #eaf2ff;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New';
                color: #243b53;
            }
            QTextBrowser pre {
                background-color: #f7f9fc;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #2f80ed;
                margin: 15px 0px;
                font-family: 'Courier New';
                white-space: pre-wrap;
                color: #102a43;
            }
            QTextBrowser table {
                color: #102a43;
            }
            QTextBrowser th, QTextBrowser td {
                color: #102a43;
            }
        """)
        self.content_browser.setMinimumWidth(650)
        self.content_browser.setMaximumWidth(940)
        
        browser_row = QHBoxLayout()
        browser_row.addStretch()
        browser_row.addWidget(self.content_browser, stretch=1)
        browser_row.addStretch()
        content_layout.addLayout(browser_row, stretch=1)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.go_previous_section)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f4f8;
                color: #102a43;
                border: 1px solid #bcccdc;
                border-radius: 6px;
                padding: 7px 12px;
            }
            QPushButton:hover {
                background-color: #d9e2ec;
            }
        """)
        controls_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.go_next_section)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #2f80ed;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1f6cd0;
            }
        """)
        controls_layout.addWidget(self.next_button)
        controls_layout.addStretch()

        top_button = QPushButton("Back to Top")
        top_button.clicked.connect(self.scroll_to_top)
        top_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #334e68;
                border: 1px solid #bcccdc;
                border-radius: 6px;
                padding: 7px 12px;
            }
            QPushButton:hover {
                background-color: #f0f4f8;
            }
        """)
        controls_layout.addWidget(top_button)
        content_layout.addLayout(controls_layout)
        
        # Add frames to splitter
        splitter.addWidget(self.nav_frame)
        splitter.addWidget(self.content_frame)
        splitter.setSizes([270, 780])  # Initial sizes
        
        main_layout.addWidget(splitter)
    
    def load_documentation_content(self):
        """Load all documentation content"""
        self.docs_content = {
            0: self.get_getting_started_content(),
            1: self.get_image_upload_content(),
            2: self.get_image_modification_content(),
            3: self.get_image_analysis_content(),
            4: self.get_results_interpretation_content(),
            5: self.get_troubleshooting_content(),
            6: self.get_keyboard_shortcuts_content(),
            7: self.get_api_reference_content()
        }
        
        # Show first section by default
        self.nav_list.setCurrentRow(0)
        self.on_nav_changed(0)
    
    def on_nav_changed(self, row):
        """Handle navigation item selection"""
        if row >= 0 and row < len(self.docs_content):
            self.content_browser.setHtml(self.docs_content[row])
            self.section_title_label.setText(self.nav_items[row])
            self.section_path_label.setText(f"Documentation > {self.nav_items[row]}")
            self.prev_button.setEnabled(self._has_visible_before(row))
            self.next_button.setEnabled(self._has_visible_after(row))

    def filter_navigation(self, text):
        """Filter visible sections based on search text."""
        query = text.strip().lower()
        first_visible = None

        for idx in range(self.nav_list.count()):
            item = self.nav_list.item(idx)
            is_match = query in item.text().lower()
            item.setHidden(not is_match)
            if is_match and first_visible is None:
                first_visible = idx

        current_item = self.nav_list.currentItem()
        if current_item and current_item.isHidden():
            if first_visible is not None:
                self.nav_list.setCurrentRow(first_visible)
            else:
                self.section_title_label.setText("No section found")
                self.section_path_label.setText("Documentation")
                self.content_browser.setHtml(
                    "<h2>No matching section</h2><p>Try a different search keyword.</p>"
                )
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
        elif self.nav_list.currentRow() >= 0:
            row = self.nav_list.currentRow()
            self.prev_button.setEnabled(self._has_visible_before(row))
            self.next_button.setEnabled(self._has_visible_after(row))

    def go_previous_section(self):
        """Go to previous visible section."""
        current_row = self.nav_list.currentRow()
        for row in range(current_row - 1, -1, -1):
            if not self.nav_list.item(row).isHidden():
                self.nav_list.setCurrentRow(row)
                return

    def go_next_section(self):
        """Go to next visible section."""
        current_row = self.nav_list.currentRow()
        for row in range(current_row + 1, self.nav_list.count()):
            if not self.nav_list.item(row).isHidden():
                self.nav_list.setCurrentRow(row)
                return

    def scroll_to_top(self):
        """Scroll documentation content to top."""
        self.content_browser.verticalScrollBar().setValue(0)

    def _has_visible_before(self, row):
        for idx in range(row - 1, -1, -1):
            if not self.nav_list.item(idx).isHidden():
                return True
        return False

    def _has_visible_after(self, row):
        for idx in range(row + 1, self.nav_list.count()):
            if not self.nav_list.item(idx).isHidden():
                return True
        return False
    
    def download_user_manual(self):
        """Download user manual from the project root with PDF/Word choice."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # Locate candidates by type.
        manual_files = {"pdf": [], "word": []}
        candidate_names = [
            "Image-Processing-App User Manual.pdf",
            "Image-Processing-App User Manual 26.docx.pdf",
            "Image-Processing-App User Manual 26.docx",
            "Image-Processing-App User Manual.docx",
            "Image-Processing-App User Manual.doc",
        ]

        for name in candidate_names:
            path = os.path.join(project_root, name)
            if not os.path.isfile(path):
                continue
            lower_name = name.lower()
            if lower_name.endswith(".pdf"):
                manual_files["pdf"].append(path)
            elif lower_name.endswith((".docx", ".doc")):
                manual_files["word"].append(path)

        # Fallback: find any file in root that looks like a user manual.
        if not manual_files["pdf"] or not manual_files["word"]:
            for entry in os.listdir(project_root):
                path = os.path.join(project_root, entry)
                if not os.path.isfile(path):
                    continue
                lower_entry = entry.lower()
                if "user manual" not in lower_entry:
                    continue
                if lower_entry.endswith(".pdf") and path not in manual_files["pdf"]:
                    manual_files["pdf"].append(path)
                elif lower_entry.endswith((".docx", ".doc")) and path not in manual_files["word"]:
                    manual_files["word"].append(path)

        has_pdf = bool(manual_files["pdf"])
        has_word = bool(manual_files["word"])
        if not has_pdf and not has_word:
            QMessageBox.warning(
                self,
                "Manual Not Found",
                "Could not find a user manual (PDF/Word) file in the project root folder.",
            )
            return

        # Let user choose preferred format when both are available.
        selected_type = "pdf" if has_pdf else "word"
        if has_pdf and has_word:
            choice_box = QMessageBox(self)
            choice_box.setWindowTitle("Choose File Format")
            choice_box.setText("Please choose a format for the user manual download:")
            pdf_btn = choice_box.addButton("PDF", QMessageBox.ButtonRole.AcceptRole)
            word_btn = choice_box.addButton("Word", QMessageBox.ButtonRole.AcceptRole)
            choice_box.addButton(QMessageBox.StandardButton.Cancel)
            choice_box.exec()

            clicked = choice_box.clickedButton()
            if clicked is None or clicked == choice_box.button(QMessageBox.StandardButton.Cancel):
                return
            selected_type = "pdf" if clicked == pdf_btn else "word"

        manual_path = manual_files[selected_type][0]
        default_name = os.path.basename(manual_path)
        if selected_type == "pdf":
            file_filter = "PDF Files (*.pdf);;All Files (*)"
        else:
            file_filter = "Word Documents (*.docx *.doc);;All Files (*)"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save User Manual",
            default_name,
            file_filter,
        )

        if not save_path:
            return

        try:
            shutil.copy2(manual_path, save_path)
            QMessageBox.information(
                self,
                "Download Complete",
                f"User manual saved to:\n{save_path}",
            )
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Download Failed",
                f"Failed to save user manual:\n{exc}",
            )
    
    # Documentation content methods
    def get_getting_started_content(self):
        return """
        <h1>🚀 Getting Started</h1>
        
        <h2>Welcome to Image Processing App</h2>
        <p>This application is designed for psychology researchers to analyze and modify images for visual perception studies.</p>
        
        <h2>System Requirements</h2>
        <ul>
            <li><strong>Operating System:</strong> Windows 10/11 or macOS 10.14+</li>
            <li><strong>RAM:</strong> 8GB minimum, 16GB recommended</li>
            <li><strong>Storage:</strong> 500MB free space</li>
            <li><strong>Python:</strong> 3.8 or higher (included in installation)</li>
        </ul>
        
        <h2>Installation Guide</h2>
        <ol>
            <li>Download the installation package for your operating system</li>
            <li>Run the installer and follow the on-screen instructions</li>
            <li>Launch the application from your Start Menu or Applications folder</li>
        </ol>
        
        <h2>Basic Workflow</h2>
        <p>Follow these steps for a typical research session:</p>
        <ol>
            <li><strong>Upload Images:</strong> Use the Home tab to upload your stimulus images</li>
            <li><strong>Modify Images:</strong> Use the Modification tab to adjust image properties if needed</li>
            <li><strong>Analyze:</strong> Configure and run analysis in the Analysis Setup tab</li>
            <li><strong>Interpret Results:</strong> View and export results in the Results tab</li>
        </ol>
        
        <h2>Need Help?</h2>
        <p>If you encounter any issues:</p>
        <ul>
            <li>Check the <strong>Troubleshooting</strong> section</li>
            <li>Contact technical support at: support@psychresearch.edu</li>
            <li>Refer to the research methodology guide provided by your department</li>
        </ul>
        """
    
    def get_image_upload_content(self):
        return """
        <h1>🖼️ Image Upload Guide</h1>
        
        <h2>Supported Formats</h2>
        <ul>
            <li><strong>JPEG/JPG:</strong> Recommended for photographs</li>
            <li><strong>PNG:</strong> Recommended for images with transparency</li>
            <li><strong>GIF:</strong> Supported for static images</li>
            <li><strong>BMP:</strong> Basic bitmap format</li>
        </ul>
        
        <h2>Upload Methods</h2>
        
        <h3>Drag & Drop</h3>
        <p>Simply drag image files from your file explorer and drop them onto the Home tab.</p>
        <pre>1. Open your file explorer
2. Select one or multiple images
3. Drag them to the dashed upload area
4. Release to upload</pre>
        
        <h3>File Browser</h3>
        <p>Use the "Browse Images" button to select files through a dialog.</p>
        
        <h3>Batch Upload</h3>
        <p>For large datasets:</p>
        <ul>
            <li>Select multiple files (Ctrl+Click or Shift+Click)</li>
            <li>Upload entire folders by dragging the folder</li>
            <li>Use consistent naming conventions for easier organization</li>
        </ul>
        
        <h2>Best Practices</h2>
        <ul>
            <li><strong>Image Size:</strong> Recommended 500x500 to 2000x2000 pixels</li>
            <li><strong>File Size:</strong> Keep under 5MB per image for optimal performance</li>
            <li><strong>Naming:</strong> Use descriptive names (e.g., "stimulus_high_complexity_01.jpg")</li>
            <li><strong>Organization:</strong> Group related images in separate upload sessions</li>
        </ul>
        
        <h2>Troubleshooting Upload Issues</h2>
        <ul>
            <li><strong>Format not supported:</strong> Convert images to JPEG or PNG</li>
            <li><strong>File too large:</strong> Resize images before upload</li>
            <li><strong>Upload fails:</strong> Check file permissions and available disk space</li>
        </ul>
        """
    
    def get_image_modification_content(self):
        return """
        <h1>✏️ Image Modification</h1>
        
        <h2>Basic Adjustments</h2>
        
        <h3>Brightness & Contrast</h3>
        <p>Adjust these parameters to control visual perception variables:</p>
        <ul>
            <li><strong>Brightness:</strong> Overall light intensity (-100 to +100)</li>
            <li><strong>Contrast:</strong> Difference between dark and light areas (-100 to +100)</li>
            <li><strong>Saturation:</strong> Color intensity (0 to 200%)</li>
        </ul>
        
        <h3>Crop & Resize</h3>
        <p>Modify image dimensions for experimental consistency:</p>
        <ul>
            <li>Select specific regions of interest</li>
            <li>Standardize image sizes across stimuli</li>
            <li>Maintain aspect ratios for natural appearance</li>
        </ul>
        
        <h2>Research-Specific Modifications</h2>
        
        <h3>Visual Complexity Manipulation</h3>
        <p>Create stimulus sets with controlled complexity levels:</p>
        <ul>
            <li>Adjust detail density</li>
            <li>Control color variety</li>
            <li>Modify pattern regularity</li>
        </ul>
        
        <h3>Batch Processing</h3>
        <p>Apply the same modification to multiple images:</p>
        <pre>1. Select multiple images in the Modification tab
2. Choose your adjustment parameters
3. Apply to all selected images
4. Save modified versions with new filenames</pre>
        
        <h2>Experimental Design Tips</h2>
        <ul>
            <li>Keep a log of all modifications for reproducibility</li>
            <li>Save original images separately from modified versions</li>
            <li>Use consistent modification parameters across experimental conditions</li>
            <li>Validate that modifications don't introduce unintended artifacts</li>
        </ul>
        """
    
    def get_image_analysis_content(self):
        return """
        <h1>🔍 Image Analysis</h1>
        
        <h2>CNN-Based Similarity Analysis</h2>
        <p>Our application uses Convolutional Neural Networks (CNNs) to analyze image relationships.</p>
        
        <h3>Similarity Scores</h3>
        <p>Pairwise similarity comparisons generate scores from 0 to 1:</p>
        <ul>
            <li><strong>0.0:</strong> Completely dissimilar</li>
            <li><strong>0.5:</strong> Moderately similar</li>
            <li><strong>1.0:</strong> Identical or very similar</li>
        </ul>
        
        <h3>Analysis Configuration</h3>
        <p>Configure your analysis in the Analysis Setup tab:</p>
        <ol>
            <li>Select the CNN model (VGG16, ResNet50, or custom)</li>
            <li>Choose analysis type (pairwise similarity, complexity assessment)</li>
            <li>Set output parameters (confidence thresholds, visualization options)</li>
            <li>Run analysis and monitor progress</li>
        </ol>
        
        <h2>Complexity Metrics</h2>
        <p>Additional image characteristics analyzed:</p>
        <ul>
            <li><strong>Visual Clutter:</strong> Density of visual elements</li>
            <li><strong>Color Distribution:</strong> Color variety and distribution</li>
            <li><strong>Edge Density:</strong> Amount of detail and texture</li>
            <li><strong>Symmetry:</strong> Bilateral and rotational symmetry</li>
        </ul>
        
        <h2>Interpretation Guidelines</h2>
        <ul>
            <li>Similarity scores are relative within your image set</li>
            <li>Consider the research context when interpreting scores</li>
            <li>Use multiple metrics for comprehensive understanding</li>
            <li>Compare with human perception validation when possible</li>
        </ul>
        """
    
    def get_results_interpretation_content(self):
        return """
        <h1>📊 Results Interpretation</h1>
        
        <h2>Similarity Matrix</h2>
        <p>The similarity matrix shows pairwise comparisons between all images in your set.</p>
        
        <h3>Reading the Matrix</h3>
        <ul>
            <li><strong>Diagonal:</strong> Self-comparisons (always 1.0)</li>
            <li><strong>Upper/Lower triangles:</strong> Mirror image pairs</li>
            <li><strong>Color coding:</strong> Heatmap indicates similarity strength</li>
        </ul>
        
        <h3>Interactive Features</h3>
        <ul>
            <li><strong>Hover:</strong> See exact similarity scores</li>
            <li><strong>Click:</strong> View detailed pairwise comparison</li>
            <li><strong>Zoom:</strong> Focus on specific matrix regions</li>
        </ul>
        
        <h2>Export Options</h2>
        
        <h3>CSV Export</h3>
        <p>Export similarity matrices for statistical analysis:</p>
        <pre>Image1,Image2,Image3
Image1,1.00,0.75,0.32
Image2,0.75,1.00,0.28
Image3,0.32,0.28,1.00</pre>
        
        <h3>Visualization Export</h3>
        <ul>
            <li><strong>High-resolution heatmaps:</strong> For publications and presentations</li>
            <li><strong>Scatter plots:</strong> For dimensionality reduction views</li>
            <li><strong>Cluster diagrams:</strong> For group structure visualization</li>
        </ul>
        
        <h2>Research Applications</h2>
        
        <h3>Stimulus Set Validation</h3>
        <p>Ensure your image sets have appropriate characteristics:</p>
        <ul>
            <li>Verify intended similarity relationships</li>
            <li>Identify outlier images</li>
            <li>Confirm experimental condition separation</li>
        </ul>
        
        <h3>Exploratory Analysis</h3>
        <p>Discover unexpected patterns in your stimuli:</p>
        <ul>
            <li>Cluster analysis of image groups</li>
            <li>Dimensionality reduction for pattern discovery</li>
            <li>Correlation with behavioral data</li>
        </ul>
        """
    
    def get_troubleshooting_content(self):
        return """
        <h1>❓ Troubleshooting Guide</h1>
        
        <h2>Common Issues and Solutions</h2>
        
        <h3>Application Won't Start</h3>
        <ul>
            <li><strong>Issue:</strong> Application fails to launch</li>
            <li><strong>Solution:</strong> Reinstall the application and ensure all dependencies are installed</li>
            <li><strong>Prevention:</strong> Keep your operating system updated</li>
        </ul>
        
        <h3>Image Upload Problems</h3>
        <ul>
            <li><strong>Issue:</strong> Images not uploading</li>
            <li><strong>Solution:</strong> Check file format and size restrictions</li>
            <li><strong>Prevention:</strong> Use supported formats (JPEG, PNG) under 5MB</li>
        </ul>
        
        <h3>Slow Performance</h3>
        <ul>
            <li><strong>Issue:</strong> Application runs slowly, especially with large image sets</li>
            <li><strong>Solution:</strong> Close other applications, increase system RAM if possible</li>
            <li><strong>Prevention:</strong> Work with smaller image batches, use optimized image sizes</li>
        </ul>
        
        <h3>Analysis Errors</h3>
        <ul>
            <li><strong>Issue:</strong> CNN analysis fails or produces errors</li>
            <li><strong>Solution:</strong> Check that images are properly loaded and formatted</li>
            <li><strong>Prevention:</strong> Validate images before analysis, ensure consistent image dimensions</li>
        </ul>
        
        <h2>Performance Optimization</h2>
        
        <h3>System Settings</h3>
        <ul>
            <li>Close unnecessary applications during analysis</li>
            <li>Ensure adequate free disk space (minimum 2GB)</li>
            <li>Update graphics drivers for better performance</li>
        </ul>
        
        <h3>Workflow Optimization</h3>
        <ul>
            <li>Process images in smaller batches</li>
            <li>Use lower resolution for exploratory analysis</li>
            <li>Save and reload projects instead of re-analyzing</li>
        </ul>
        
        <h2>Getting Technical Support</h2>
        <p>If problems persist, contact technical support with the following information:</p>
        <ul>
            <li>Application version number</li>
            <li>Operating system and version</li>
            <li>Detailed description of the issue</li>
            <li>Error messages (screenshot if possible)</li>
            <li>Steps to reproduce the problem</li>
        </ul>
        """
    
    def get_keyboard_shortcuts_content(self):
        return """
        <h1>⌨️ Keyboard Shortcuts</h1>
        
        <h2>Global Shortcuts</h2>
        <table border="1" style="border-collapse: collapse; width: 100%; margin: 15px 0;">
            <tr style="background-color: #f8f9fa;">
                <th style="padding: 10px; text-align: left;">Action</th>
                <th style="padding: 10px; text-align: left;">Shortcut</th>
                <th style="padding: 10px; text-align: left;">Description</th>
            </tr>
            <tr>
                <td style="padding: 8px;">New Project</td>
                <td style="padding: 8px;"><code>Ctrl+N</code></td>
                <td style="padding: 8px;">Start a new research project</td>
            </tr>
            <tr>
                <td style="padding: 8px;">Open Project</td>
                <td style="padding: 8px;"><code>Ctrl+O</code></td>
                <td style="padding: 8px;">Load existing project</td>
            </tr>
            <tr>
                <td style="padding: 8px;">Save Project</td>
                <td style="padding: 8px;"><code>Ctrl+S</code></td>
                <td style="padding: 8px;">Save current project</td>
            </tr>
            <tr>
                <td style="padding: 8px;">Upload Images</td>
                <td style="padding: 8px;"><code>Ctrl+U</code></td>
                <td style="padding: 8px;">Open image upload dialog</td>
            </tr>
            <tr>
                <td style="padding: 8px;">Run Analysis</td>
                <td style="padding: 8px;"><code>F5</code></td>
                <td style="padding: 8px;">Start image analysis</td>
            </tr>
            <tr>
                <td style="padding: 8px;">Export Results</td>
                <td style="padding: 8px;"><code>Ctrl+E</code></td>
                <td style="padding: 8px;">Export current results</td>
            </tr>
        </table>
        
        <h2>Navigation Shortcuts</h2>
        <table border="1" style="border-collapse: collapse; width: 100%; margin: 15px 0;">
            <tr style="background-color: #f8f9fa;">
                <th style="padding: 10px; text-align: left;">Action</th>
                <th style="padding: 10px; text-align: left;">Shortcut</th>
            </tr>
            <tr>
                <td style="padding: 8px;">Home Tab</td>
                <td style="padding: 8px;"><code>Ctrl+1</code></td>
            </tr>
            <tr>
                <td style="padding: 8px;">Modification Tab</td>
                <td style="padding: 8px;"><code>Ctrl+2</code></td>
            </tr>
            <tr>
                <td style="padding: 8px;">Analysis Tab</td>
                <td style="padding: 8px;"><code>Ctrl+3</code></td>
            </tr>
            <tr>
                <td style="padding: 8px;">Results Tab</td>
                <td style="padding: 8px;"><code>Ctrl+4</code></td>
            </tr>
            <tr>
                <td style="padding: 8px;">Documentation Tab</td>
                <td style="padding: 8px;"><code>Ctrl+5</code></td>
            </tr>
        </table>
        
        <h2>Image Viewing Shortcuts</h2>
        <ul>
            <li><code>+</code> / <code>-</code>: Zoom in/out</li>
            <li><code>Space</code>: Reset zoom</li>
            <li><code>Arrow Keys</code>: Navigate between images</li>
            <li><code>Delete</code>: Remove selected image</li>
        </ul>
        
        <h2>Accessibility Features</h2>
        <ul>
            <li>All functions accessible via keyboard</li>
            <li>High contrast mode available in settings</li>
            <li>Screen reader compatible text descriptions</li>
            <li>Adjustable font sizes in documentation</li>
        </ul>
        """
    
    def get_api_reference_content(self):
        return """
        <h1>🔧 API Reference</h1>
        
        <h2>Overview</h2>
        <p>The Image Processing App provides programmatic access to analysis functions for advanced users and integration with other research tools.</p>
        
        <h2>Core Functions</h2>
        
        <h3>Image Analysis API</h3>
        <pre>from image_processing import ImageAnalyzer

# Initialize analyzer
analyzer = ImageAnalyzer(model='vgg16')

# Analyze image set
results = analyzer.analyze_images(
    image_paths=['image1.jpg', 'image2.jpg', 'image3.jpg'],
    analysis_type='similarity',
    output_format='matrix'
)

# Get similarity matrix
similarity_matrix = results.get_similarity_matrix()</pre>
        
        <h3>Batch Processing</h3>
        <pre># Process multiple image sets
batch_results = analyzer.batch_analyze(
    image_sets=[set1, set2, set3],
    parallel_processing=True,
    save_intermediate=True
)</pre>
        
        <h2>Data Structures</h2>
        
        <h3>Similarity Matrix</h3>
        <p>Numpy array with pairwise similarity scores:</p>
        <pre>[[1.00, 0.75, 0.32],
 [0.75, 1.00, 0.28], 
 [0.32, 0.28, 1.00]]</pre>
        
        <h3>Analysis Results</h3>
        <pre>class AnalysisResults:
    similarity_matrix: np.ndarray
    complexity_scores: dict
    processing_time: float
    confidence_scores: np.ndarray
    visualization_data: dict</pre>
        
        <h2>Integration Examples</h2>
        
        <h3>Python Script Integration</h3>
        <pre># Custom analysis pipeline
import image_processing as ip

# Load your stimulus set
images = ip.load_images('stimulus_set/')

# Custom analysis configuration
config = {
    'model': 'resnet50',
    'metrics': ['similarity', 'complexity', 'color_distribution'],
    'normalization': 'zscore'
}

results = ip.analyze_with_config(images, config)</pre>
        
        <h3>R Integration</h3>
        <pre># Use the reticulate package in R
library(reticulate)

ip <- import("image_processing")
results <- ip$analyze_images(image_paths, analysis_type="similarity")

# Convert to R data frame
similarity_df <- as.data.frame(results$get_similarity_matrix())</pre>
        
        <h2>Advanced Usage</h2>
        <p>For researchers with programming experience, the API supports:</p>
        <ul>
            <li>Custom model integration</li>
            <li>Extended metric development</li>
            <li>Real-time analysis during experiments</li>
            <li>Integration with eye-tracking data</li>
        </ul>
        """
