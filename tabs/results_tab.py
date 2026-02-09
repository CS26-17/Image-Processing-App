"""
Results Tab - Display processing results and analysis data
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QSizePolicy, QPushButton,
                             QTableWidget, QTableWidgetItem, QFileDialog, QHeaderView,
                             QMessageBox, QSplitter, QTextEdit, QComboBox, QSpinBox,
                             QGroupBox, QGridLayout, QTabWidget)
from PySide6.QtCore import Qt, QSize, QStandardPaths, QDir
from PySide6.QtGui import QPixmap, QImage, QColor, QBrush, QFont

import pandas as pd
import numpy as np
import os
import re


class SectionWidget(QFrame):
    """Reusable section widget with title and content"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # Content container
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.content)


class ResultsTab(QWidget):
    """
    Results tab widget for displaying processing results
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.similarity_data = None
        self.heatmap_image = None
        self.object_groups = {}  # Store object groupings
        self.current_filter_obj1 = None
        self.current_filter_obj2 = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the results tab UI"""
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Container widget for scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(15)
        
        # File loading section
        file_section = SectionWidget("Load Results")
        file_layout = QHBoxLayout()
        
        btn_load_csv = QPushButton("Load Similarity CSV")
        btn_load_csv.clicked.connect(self.load_similarity_csv)
        
        btn_load_heatmap = QPushButton("Load Heatmap Image")
        btn_load_heatmap.clicked.connect(self.load_heatmap_image)
        
        btn_auto_load = QPushButton("Auto-Load from Results Folder")
        btn_auto_load.clicked.connect(self.auto_load_results)
        
        for btn in [btn_load_csv, btn_load_heatmap, btn_auto_load]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    margin-right: 10px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            file_layout.addWidget(btn)
        
        file_section.content_layout.addLayout(file_layout)
        scroll_layout.addWidget(file_section)
        
        # 1. Image Display Section
        self.image_section = SectionWidget("Image Preview")
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 2px dashed #d1d5db;
                border-radius: 8px;
                color: #9ca3af;
                font-style: italic;
                padding: 20px;
            }
        """)
        self.image_section.content_layout.addWidget(self.image_label)
        scroll_layout.addWidget(self.image_section)
        
        # 2. Image Statistics Section
        self.stats_section = SectionWidget("Image Statistics")
        self.stats_placeholder = QLabel("Image statistics will be displayed here")
        self.stats_placeholder.setStyleSheet("color: #6b7280; font-style: italic;")
        self.stats_section.content_layout.addWidget(self.stats_placeholder)
        scroll_layout.addWidget(self.stats_section)
        
        # 3. Analysis Results Section - Using tabs for organization
        self.analysis_section = SectionWidget("Analysis Results")

        # Create tab widget for different views
        self.results_tabs = QTabWidget()
        self.results_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                color: #374151;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #1f2937;
                border-bottom: 2px solid #3b82f6;
            }
            QLabel {
                color: #374151;
            }
            QComboBox {
                color: #1f2937;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView {
                color: #1f2937;
                background-color: white;
                selection-background-color: #3b82f6;
                selection-color: white;
            }
            QSpinBox {
                color: #1f2937;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QTableWidget {
                color: #1f2937;
                background-color: white;
                gridline-color: #e5e7eb;
            }
        """)

        # Tab 1: Heatmap View
        heatmap_tab = QWidget()
        heatmap_tab_layout = QVBoxLayout(heatmap_tab)
        self.heatmap_label = QLabel("No heatmap loaded")
        self.heatmap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heatmap_label.setMinimumSize(600, 400)
        self.heatmap_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #d1d5db;
                border-radius: 8px;
                color: #9ca3af;
                padding: 20px;
            }
        """)
        heatmap_tab_layout.addWidget(self.heatmap_label)
        self.results_tabs.addTab(heatmap_tab, "Heatmap")

        # Tab 2: Full Matrix View
        matrix_tab = QWidget()
        matrix_tab_layout = QVBoxLayout(matrix_tab)

        # Matrix info label
        self.matrix_info_label = QLabel("Load a similarity CSV to view the matrix")
        self.matrix_info_label.setStyleSheet("color: #6b7280; font-style: italic; margin-bottom: 10px;")
        matrix_tab_layout.addWidget(self.matrix_info_label)

        self.similarity_table = QTableWidget()
        self.similarity_table.setMinimumSize(600, 400)
        matrix_tab_layout.addWidget(self.similarity_table)
        self.results_tabs.addTab(matrix_tab, "Full Matrix")

        # Tab 3: Filtered View - Compare specific objects
        filter_tab = QWidget()
        filter_tab_layout = QVBoxLayout(filter_tab)

        # Filter controls
        filter_controls = QWidget()
        filter_controls_layout = QHBoxLayout(filter_controls)
        filter_controls_layout.setContentsMargins(0, 0, 0, 10)

        label_style = "color: #374151; font-weight: bold;"

        obj1_label = QLabel("Object 1:")
        obj1_label.setStyleSheet(label_style)
        filter_controls_layout.addWidget(obj1_label)
        self.filter_obj1_combo = QComboBox()
        self.filter_obj1_combo.setMinimumWidth(150)
        self.filter_obj1_combo.currentTextChanged.connect(self.apply_filter)
        filter_controls_layout.addWidget(self.filter_obj1_combo)

        obj2_label = QLabel("Object 2:")
        obj2_label.setStyleSheet(label_style)
        filter_controls_layout.addWidget(obj2_label)
        self.filter_obj2_combo = QComboBox()
        self.filter_obj2_combo.setMinimumWidth(150)
        self.filter_obj2_combo.currentTextChanged.connect(self.apply_filter)
        filter_controls_layout.addWidget(self.filter_obj2_combo)

        btn_reset_filter = QPushButton("Reset")
        btn_reset_filter.clicked.connect(self.reset_filter)
        btn_reset_filter.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        filter_controls_layout.addWidget(btn_reset_filter)
        filter_controls_layout.addStretch()

        filter_tab_layout.addWidget(filter_controls)

        self.filtered_table = QTableWidget()
        self.filtered_table.setMinimumSize(600, 350)
        filter_tab_layout.addWidget(self.filtered_table)

        # Filtered stats
        self.filtered_stats_label = QLabel("")
        self.filtered_stats_label.setStyleSheet("""
            QLabel {
                color: #374151;
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 4px;
                padding: 8px;
                margin-top: 10px;
            }
        """)
        filter_tab_layout.addWidget(self.filtered_stats_label)

        self.results_tabs.addTab(filter_tab, "Compare Objects")

        # Tab 4: Object Summary - Per-object statistics
        summary_tab = QWidget()
        summary_tab_layout = QVBoxLayout(summary_tab)

        self.summary_table = QTableWidget()
        self.summary_table.setMinimumSize(600, 400)
        summary_tab_layout.addWidget(self.summary_table)

        self.results_tabs.addTab(summary_tab, "Object Summary")

        # Tab 5: Top Matches - Show highest/lowest similarity pairs
        matches_tab = QWidget()
        matches_tab_layout = QVBoxLayout(matches_tab)

        matches_controls = QWidget()
        matches_controls_layout = QHBoxLayout(matches_controls)
        matches_controls_layout.setContentsMargins(0, 0, 0, 10)

        show_top_label = QLabel("Show top:")
        show_top_label.setStyleSheet("color: #374151; font-weight: bold;")
        matches_controls_layout.addWidget(show_top_label)
        self.top_n_spinner = QSpinBox()
        self.top_n_spinner.setRange(10, 100)
        self.top_n_spinner.setValue(20)
        self.top_n_spinner.valueChanged.connect(self.update_top_matches)
        matches_controls_layout.addWidget(self.top_n_spinner)

        self.match_type_combo = QComboBox()
        self.match_type_combo.addItems(["Most Similar", "Least Similar", "Cross-Object Similar"])
        self.match_type_combo.currentTextChanged.connect(self.update_top_matches)
        matches_controls_layout.addWidget(self.match_type_combo)

        matches_controls_layout.addStretch()
        matches_tab_layout.addWidget(matches_controls)

        self.matches_table = QTableWidget()
        self.matches_table.setMinimumSize(600, 350)
        matches_tab_layout.addWidget(self.matches_table)

        self.results_tabs.addTab(matches_tab, "Top Matches")

        self.analysis_section.content_layout.addWidget(self.results_tabs)
        scroll_layout.addWidget(self.analysis_section)
        
        # 4. Comparison Section
        self.comparison_section = SectionWidget("Image Comparison")
        comparison_container = QWidget()
        comparison_layout = QHBoxLayout(comparison_container)
        
        # Before/After comparison placeholders
        before = self._create_comparison_box("Original")
        after = self._create_comparison_box("Processed")
        
        comparison_layout.addWidget(before)
        comparison_layout.addWidget(after)
        
        self.comparison_section.content_layout.addWidget(comparison_container)
        scroll_layout.addWidget(self.comparison_section)
        
        # 5. Export Section
        self.export_section = SectionWidget("Export Options")
        
        # Export buttons
        button_layout = QHBoxLayout()
        
        btn_export_png = QPushButton("Export as PNG")
        btn_export_jpg = QPushButton("Export as JPG")
        btn_export_pdf = QPushButton("Export as PDF")
        btn_export_csv = QPushButton("Export Data (CSV)")
        
        # Style buttons
        for btn in [btn_export_png, btn_export_jpg, btn_export_pdf, btn_export_csv]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e5e7eb;
                    color: #374151;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    margin-right: 10px;
                }
                QPushButton:hover {
                    background-color: #d1d5db;
                    color: #1f2937;
                }
            """)
            button_layout.addWidget(btn)
        
        self.export_section.content_layout.addLayout(button_layout)
        scroll_layout.addWidget(self.export_section)
        
        # Add stretch to push content to top
        scroll_layout.addStretch()
        
        # Set up scroll area
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
    
    def _create_metric_widget(self, name, value):
        """Helper to create a metric display widget"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        
        name_label = QLabel(name)
        name_label.setStyleSheet("color: #6b7280; font-size: 13px;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #111827;
            }
        """)
        
        layout.addWidget(name_label)
        layout.addWidget(value_label)
        
        return container
    
    def _create_comparison_box(self, title):
        """Helper to create a comparison box"""
        container = QWidget()
        layout = QVBoxLayout(container)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #4b5563;
                margin-bottom: 5px;
            }
        """)
        
        image_box = QLabel("No image")
        image_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_box.setMinimumSize(200, 150)
        image_box.setStyleSheet("""
            QLabel {
                background-color: #f3f4f6;
                border: 1px dashed #d1d5db;
                border-radius: 6px;
                color: #9ca3af;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(image_box)
        
        return container
    
    def load_similarity_csv(self):
        """Load similarity data from CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Similarity CSV", 
            "", 
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                self.similarity_data = pd.read_csv(file_path, index_col=0)
                self.display_similarity_table()
                self.update_statistics()
                QMessageBox.information(self, "Success", f"Loaded similarity data from {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV file: {str(e)}")
    
    def load_heatmap_image(self):
        """Load heatmap image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Heatmap Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        
        if file_path:
            try:
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    self.heatmap_image = pixmap
                    self.display_heatmap()
                    QMessageBox.information(self, "Success", f"Loaded heatmap from {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Warning", "Could not load image file")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def auto_load_results(self):
        """Automatically load results from the results folder"""
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

        if not os.path.exists(results_dir):
            QMessageBox.warning(self, "Warning", f"Results directory not found: {results_dir}")
            return

        loaded_files = []
        all_files = os.listdir(results_dir)

        # Look for similarity CSV files - prefer files with 'similarity' in the name
        csv_files = [f for f in all_files if f.endswith('.csv')]
        similarity_csvs = [f for f in csv_files if 'similarity' in f.lower()]
        target_csv = similarity_csvs[0] if similarity_csvs else (csv_files[0] if csv_files else None)

        if target_csv:
            csv_path = os.path.join(results_dir, target_csv)
            try:
                self.similarity_data = pd.read_csv(csv_path, index_col=0)
                self.display_similarity_table()
                loaded_files.append(f"{target_csv} (similarity data)")
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to load {target_csv}: {str(e)}")

        # Look for heatmap image files - prefer files with 'heatmap' in the name
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        image_files = [f for f in all_files
                      if any(f.lower().endswith(ext) for ext in image_extensions)]
        heatmap_images = [f for f in image_files if 'heatmap' in f.lower()]
        target_image = heatmap_images[0] if heatmap_images else (image_files[0] if image_files else None)

        if target_image:
            img_path = os.path.join(results_dir, target_image)
            try:
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    self.heatmap_image = pixmap
                    self.display_heatmap()
                    loaded_files.append(f"{target_image} (heatmap)")
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to load {target_image}: {str(e)}")

        if loaded_files:
            self.update_statistics()
            QMessageBox.information(self, "Success", f"Auto-loaded:\n" + "\n".join(f"  - {f}" for f in loaded_files))
        else:
            QMessageBox.information(self, "Info", "No results files found in the results directory")
    
    def display_similarity_table(self):
        """Display similarity data in the table widget"""
        if self.similarity_data is None:
            return

        # Update matrix info label
        num_images = len(self.similarity_data)
        self.matrix_info_label.setText(
            f"Matrix size: {num_images} x {num_images} | "
            f"Total comparisons: {num_images * num_images:,} | "
            f"Unique pairs: {num_images * (num_images - 1) // 2:,}"
        )
        self.matrix_info_label.setStyleSheet("""
            QLabel {
                color: #374151;
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 4px;
                padding: 8px;
                margin-bottom: 10px;
            }
        """)

        # Set table dimensions
        self.similarity_table.setRowCount(len(self.similarity_data))
        self.similarity_table.setColumnCount(len(self.similarity_data.columns))

        # Set headers
        self.similarity_table.setHorizontalHeaderLabels(list(self.similarity_data.columns))
        self.similarity_table.setVerticalHeaderLabels(list(self.similarity_data.index))

        # Fill table with data
        for i, row_name in enumerate(self.similarity_data.index):
            for j, col_name in enumerate(self.similarity_data.columns):
                value = self.similarity_data.iloc[i, j]
                item = QTableWidgetItem(f"{value:.4f}")

                # Color code based on similarity value
                if isinstance(value, (int, float)):
                    if value >= 0.8:
                        item.setBackground(QBrush(QColor(144, 238, 144)))  # Light green
                    elif value >= 0.6:
                        item.setBackground(QBrush(QColor(255, 255, 224)))  # Light yellow
                    elif value >= 0.4:
                        item.setBackground(QBrush(QColor(255, 218, 185)))  # Light orange
                    else:
                        item.setBackground(QBrush(QColor(255, 182, 193)))  # Light red

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QBrush(QColor(0, 0, 0)))  # Black text
                self.similarity_table.setItem(i, j, item)

        # Adjust column widths
        header = self.similarity_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Style headers to ensure proper text visibility
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                padding: 5px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        # Style vertical headers (row labels)
        vertical_header = self.similarity_table.verticalHeader()
        vertical_header.setStyleSheet("""
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                padding: 5px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        # Make table read-only
        self.similarity_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Extract object groups and populate filters
        self.extract_object_groups()

        # Update all analysis views
        self.update_object_summary()
        self.update_top_matches()
        self.apply_filter()
    
    def display_heatmap(self):
        """Display the heatmap image"""
        if self.heatmap_image is None:
            return
        
        # Scale image to fit while maintaining aspect ratio
        scaled_pixmap = self.heatmap_image.scaled(
            self.heatmap_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.heatmap_label.setPixmap(scaled_pixmap)
        self.heatmap_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 5px;
            }
        """)
    
    def update_statistics(self):
        """Update the statistics section with data from similarity matrix"""
        if self.similarity_data is None:
            return

        # Calculate overall statistics
        data_values = self.similarity_data.values.copy()
        np.fill_diagonal(data_values, np.nan)  # Exclude diagonal (self-similarity)

        mean_similarity = np.nanmean(data_values)
        max_similarity = np.nanmax(data_values)
        min_similarity = np.nanmin(data_values)
        std_similarity = np.nanstd(data_values)

        # Calculate intra vs inter object statistics if object groups exist
        intra_stats = ""
        inter_stats = ""
        if self.object_groups:
            intra_values = []
            inter_values = []

            for obj_key, images in self.object_groups.items():
                # Intra-object comparisons
                for i, img1 in enumerate(images):
                    for j, img2 in enumerate(images):
                        if i < j:
                            intra_values.append(self.similarity_data.loc[img1, img2])

            # Inter-object comparisons
            obj_keys = list(self.object_groups.keys())
            for i, obj1 in enumerate(obj_keys):
                for j, obj2 in enumerate(obj_keys):
                    if i < j:
                        for img1 in self.object_groups[obj1]:
                            for img2 in self.object_groups[obj2]:
                                inter_values.append(self.similarity_data.loc[img1, img2])

            if intra_values:
                intra_mean = np.mean(intra_values)
                intra_std = np.std(intra_values)
                intra_stats = f"""
<br><b>Intra-Object (same object views):</b><br>
• Mean: {intra_mean:.4f} | Std: {intra_std:.4f}<br>
• Count: {len(intra_values):,} pairs"""

            if inter_values:
                inter_mean = np.mean(inter_values)
                inter_std = np.std(inter_values)
                inter_stats = f"""
<br><b>Inter-Object (different objects):</b><br>
• Mean: {inter_mean:.4f} | Std: {inter_std:.4f}<br>
• Count: {len(inter_values):,} pairs"""

        num_objects = len(self.object_groups) if self.object_groups else "N/A"

        # Update statistics display
        stats_text = f"""
<b>Overall Similarity Statistics:</b><br>
• Mean: {mean_similarity:.4f} | Std: {std_similarity:.4f}<br>
• Range: [{min_similarity:.4f}, {max_similarity:.4f}]<br>
• Matrix Size: {self.similarity_data.shape[0]} × {self.similarity_data.shape[1]}<br>
• Unique Pairs: {self.similarity_data.shape[0] * (self.similarity_data.shape[0] - 1) // 2:,}<br>
• Objects Detected: {num_objects}
{intra_stats}
{inter_stats}
        """

        self.stats_placeholder.setText(stats_text)
        self.stats_placeholder.setStyleSheet("""
            QLabel {
                color: #374151;
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
    
    def extract_object_groups(self):
        """Extract object groupings from image filenames"""
        if self.similarity_data is None:
            return

        self.object_groups = {}
        pattern = re.compile(r'grey_obj(\d+)[a-l]\.jpg')

        for name in self.similarity_data.index:
            match = pattern.match(name)
            if match:
                obj_num = match.group(1)
                obj_key = f"Object {obj_num}"
                if obj_key not in self.object_groups:
                    self.object_groups[obj_key] = []
                self.object_groups[obj_key].append(name)

        # Update filter dropdowns
        self.filter_obj1_combo.clear()
        self.filter_obj2_combo.clear()

        self.filter_obj1_combo.addItem("All Objects")
        self.filter_obj2_combo.addItem("All Objects")

        for obj_key in sorted(self.object_groups.keys(), key=lambda x: int(x.split()[1])):
            self.filter_obj1_combo.addItem(obj_key)
            self.filter_obj2_combo.addItem(obj_key)

    def apply_filter(self):
        """Apply object filter to show subset of similarity matrix"""
        if self.similarity_data is None:
            return

        obj1 = self.filter_obj1_combo.currentText()
        obj2 = self.filter_obj2_combo.currentText()

        if obj1 == "All Objects" and obj2 == "All Objects":
            filtered_data = self.similarity_data
        else:
            rows = self.object_groups.get(obj1, list(self.similarity_data.index)) if obj1 != "All Objects" else list(self.similarity_data.index)
            cols = self.object_groups.get(obj2, list(self.similarity_data.columns)) if obj2 != "All Objects" else list(self.similarity_data.columns)
            filtered_data = self.similarity_data.loc[rows, cols]

        self.display_filtered_table(filtered_data)
        self.update_filtered_stats(filtered_data, obj1, obj2)

    def reset_filter(self):
        """Reset filters to show all data"""
        self.filter_obj1_combo.setCurrentIndex(0)
        self.filter_obj2_combo.setCurrentIndex(0)

    def display_filtered_table(self, data):
        """Display filtered data in the filtered table"""
        self.filtered_table.setRowCount(len(data))
        self.filtered_table.setColumnCount(len(data.columns))

        self.filtered_table.setHorizontalHeaderLabels(list(data.columns))
        self.filtered_table.setVerticalHeaderLabels(list(data.index))

        for i, row_name in enumerate(data.index):
            for j, col_name in enumerate(data.columns):
                value = data.iloc[i, j]
                item = QTableWidgetItem(f"{value:.4f}")

                # Color code
                if isinstance(value, (int, float)):
                    if value >= 0.8:
                        item.setBackground(QBrush(QColor(144, 238, 144)))
                    elif value >= 0.6:
                        item.setBackground(QBrush(QColor(255, 255, 224)))
                    elif value >= 0.4:
                        item.setBackground(QBrush(QColor(255, 218, 185)))
                    else:
                        item.setBackground(QBrush(QColor(255, 182, 193)))

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QBrush(QColor(0, 0, 0)))
                self.filtered_table.setItem(i, j, item)

        self.filtered_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.filtered_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Style headers for filtered table
        for header in [self.filtered_table.horizontalHeader(), self.filtered_table.verticalHeader()]:
            header.setStyleSheet("""
                QHeaderView::section {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    padding: 5px;
                    border: 1px solid #e0e0e0;
                    font-weight: bold;
                }
            """)

    def update_filtered_stats(self, data, obj1, obj2):
        """Update statistics for filtered data"""
        values = data.values.flatten()

        # Remove self-comparisons (1.0 values on diagonal if same object)
        if obj1 == obj2 and obj1 != "All Objects":
            mask = ~np.eye(len(data), dtype=bool).flatten()
            values = values[mask]

        if len(values) == 0:
            self.filtered_stats_label.setText("No data to display")
            return

        mean_val = np.mean(values)
        max_val = np.max(values)
        min_val = np.min(values)
        std_val = np.std(values)

        comparison_text = f"{obj1} vs {obj2}" if obj1 != "All Objects" or obj2 != "All Objects" else "All Objects"

        self.filtered_stats_label.setText(
            f"<b>{comparison_text}</b> | "
            f"Mean: {mean_val:.4f} | Max: {max_val:.4f} | Min: {min_val:.4f} | Std: {std_val:.4f} | "
            f"Comparisons: {len(values)}"
        )

    def update_object_summary(self):
        """Create summary table showing per-object statistics"""
        if self.similarity_data is None or not self.object_groups:
            return

        objects = sorted(self.object_groups.keys(), key=lambda x: int(x.split()[1]))

        # Set up table: Objects as both rows and columns, showing mean similarity
        self.summary_table.setRowCount(len(objects))
        self.summary_table.setColumnCount(len(objects) + 3)  # +3 for intra-object stats

        headers = objects + ["Intra-Mean", "Intra-Min", "Intra-Max"]
        self.summary_table.setHorizontalHeaderLabels(headers)
        self.summary_table.setVerticalHeaderLabels(objects)

        for i, obj1 in enumerate(objects):
            rows = self.object_groups[obj1]

            # Intra-object statistics
            intra_data = self.similarity_data.loc[rows, rows].values
            np.fill_diagonal(intra_data, np.nan)
            intra_mean = np.nanmean(intra_data)
            intra_min = np.nanmin(intra_data)
            intra_max = np.nanmax(intra_data)

            for j, obj2 in enumerate(objects):
                cols = self.object_groups[obj2]
                subset = self.similarity_data.loc[rows, cols].values

                if i == j:
                    np.fill_diagonal(subset, np.nan)

                mean_val = np.nanmean(subset)
                item = QTableWidgetItem(f"{mean_val:.4f}")

                # Color code - intra-object should be high, inter-object lower
                if i == j:
                    item.setBackground(QBrush(QColor(173, 216, 230)))  # Light blue for same object
                elif mean_val >= 0.6:
                    item.setBackground(QBrush(QColor(255, 255, 224)))  # Yellow for high cross-obj
                elif mean_val >= 0.4:
                    item.setBackground(QBrush(QColor(255, 218, 185)))
                else:
                    item.setBackground(QBrush(QColor(144, 238, 144)))  # Green for low cross-obj (good discrimination)

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QBrush(QColor(0, 0, 0)))
                self.summary_table.setItem(i, j, item)

            # Add intra-object stats
            for k, val in enumerate([intra_mean, intra_min, intra_max]):
                item = QTableWidgetItem(f"{val:.4f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(QBrush(QColor(240, 248, 255)))
                item.setForeground(QBrush(QColor(0, 0, 0)))
                self.summary_table.setItem(i, len(objects) + k, item)

        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Style headers
        for header in [self.summary_table.horizontalHeader(), self.summary_table.verticalHeader()]:
            header.setStyleSheet("""
                QHeaderView::section {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    padding: 5px;
                    border: 1px solid #e0e0e0;
                    font-weight: bold;
                }
            """)

    def update_top_matches(self):
        """Update the top matches table based on current selection"""
        if self.similarity_data is None:
            return

        n = self.top_n_spinner.value()
        match_type = self.match_type_combo.currentText()

        # Get all pairs
        pairs = []
        for i, row in enumerate(self.similarity_data.index):
            for j, col in enumerate(self.similarity_data.columns):
                if i < j:  # Only upper triangle (avoid duplicates and self-comparison)
                    pairs.append({
                        'Image 1': row,
                        'Image 2': col,
                        'Similarity': self.similarity_data.iloc[i, j],
                        'Same Object': self._same_object(row, col)
                    })

        df_pairs = pd.DataFrame(pairs)

        if match_type == "Most Similar":
            df_pairs = df_pairs.nlargest(n, 'Similarity')
        elif match_type == "Least Similar":
            df_pairs = df_pairs.nsmallest(n, 'Similarity')
        elif match_type == "Cross-Object Similar":
            # Most similar pairs from different objects
            cross_obj = df_pairs[~df_pairs['Same Object']]
            df_pairs = cross_obj.nlargest(n, 'Similarity')

        # Display in table
        self.matches_table.setRowCount(len(df_pairs))
        self.matches_table.setColumnCount(4)
        self.matches_table.setHorizontalHeaderLabels(['Image 1', 'Image 2', 'Similarity', 'Same Object'])

        for i, (_, row) in enumerate(df_pairs.iterrows()):
            img1_item = QTableWidgetItem(row['Image 1'])
            img1_item.setForeground(QBrush(QColor(0, 0, 0)))
            self.matches_table.setItem(i, 0, img1_item)

            img2_item = QTableWidgetItem(row['Image 2'])
            img2_item.setForeground(QBrush(QColor(0, 0, 0)))
            self.matches_table.setItem(i, 1, img2_item)

            sim_item = QTableWidgetItem(f"{row['Similarity']:.4f}")
            sim_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Color code similarity
            if row['Similarity'] >= 0.8:
                sim_item.setBackground(QBrush(QColor(144, 238, 144)))
            elif row['Similarity'] >= 0.6:
                sim_item.setBackground(QBrush(QColor(255, 255, 224)))
            elif row['Similarity'] >= 0.4:
                sim_item.setBackground(QBrush(QColor(255, 218, 185)))
            else:
                sim_item.setBackground(QBrush(QColor(255, 182, 193)))
            sim_item.setForeground(QBrush(QColor(0, 0, 0)))

            self.matches_table.setItem(i, 2, sim_item)

            same_obj_item = QTableWidgetItem("Yes" if row['Same Object'] else "No")
            same_obj_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if row['Same Object']:
                same_obj_item.setBackground(QBrush(QColor(173, 216, 230)))
            same_obj_item.setForeground(QBrush(QColor(0, 0, 0)))
            self.matches_table.setItem(i, 3, same_obj_item)

        self.matches_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.matches_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Style headers for matches table
        self.matches_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                padding: 5px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)

    def _same_object(self, img1, img2):
        """Check if two images are from the same object"""
        pattern = re.compile(r'grey_obj(\d+)[a-l]\.jpg')
        match1 = pattern.match(img1)
        match2 = pattern.match(img2)
        if match1 and match2:
            return match1.group(1) == match2.group(1)
        return False

    def resizeEvent(self, event):
        """Handle resize events to update heatmap display"""
        super().resizeEvent(event)
        if self.heatmap_image is not None:
            self.display_heatmap()
