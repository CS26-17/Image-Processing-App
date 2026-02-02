"""
Results Tab - Display processing results and analysis data
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QSizePolicy, QPushButton, 
                             QTableWidget, QTableWidgetItem, QFileDialog, QHeaderView,
                             QMessageBox, QSplitter, QTextEdit)
from PySide6.QtCore import Qt, QSize, QStandardPaths, QDir
from PySide6.QtGui import QPixmap, QImage, QColor, QBrush

import pandas as pd
import numpy as np
import os


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
        
        # 3. Analysis Results Section
        self.analysis_section = SectionWidget("Analysis Results")
        
        # Create splitter for heatmap and data
        results_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Heatmap display
        heatmap_container = QWidget()
        heatmap_layout = QVBoxLayout(heatmap_container)
        heatmap_title = QLabel("Similarity Heatmap")
        heatmap_title.setStyleSheet("font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        heatmap_layout.addWidget(heatmap_title)
        
        self.heatmap_label = QLabel("No heatmap loaded")
        self.heatmap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heatmap_label.setMinimumSize(400, 300)
        self.heatmap_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #d1d5db;
                border-radius: 8px;
                color: #9ca3af;
                padding: 20px;
            }
        """)
        heatmap_layout.addWidget(self.heatmap_label)
        results_splitter.addWidget(heatmap_container)
        
        # Similarity data table
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_title = QLabel("Similarity Matrix")
        table_title.setStyleSheet("font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        table_layout.addWidget(table_title)
        
        self.similarity_table = QTableWidget()
        self.similarity_table.setMinimumSize(400, 300)
        table_layout.addWidget(self.similarity_table)
        results_splitter.addWidget(table_container)
        
        results_splitter.setSizes([400, 400])
        self.analysis_section.content_layout.addWidget(results_splitter)
        
        # Analysis metrics
        metrics_container = QWidget()
        metrics_layout = QHBoxLayout(metrics_container)
        
        # Left metrics
        left_metrics = QVBoxLayout()
        left_metrics.addWidget(self._create_metric_widget("Similarity Score", "N/A"))
        left_metrics.addWidget(self._create_metric_widget("Processing Time", "N/A"))
        metrics_layout.addLayout(left_metrics)
        
        # Right metrics
        right_metrics = QVBoxLayout()
        right_metrics.addWidget(self._create_metric_widget("Image Size", "N/A"))
        right_metrics.addWidget(self._create_metric_widget("File Format", "N/A"))
        metrics_layout.addLayout(right_metrics)
        
        self.analysis_section.content_layout.addWidget(metrics_container)
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
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    margin-right: 10px;
                }
                QPushButton:hover {
                    background-color: #d1d5db;
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
        
        # Look for CSV files
        csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv')]
        if csv_files:
            csv_path = os.path.join(results_dir, csv_files[0])
            try:
                self.similarity_data = pd.read_csv(csv_path, index_col=0)
                self.display_similarity_table()
                loaded_files.append(f"{csv_files[0]} (similarity data)")
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to load {csv_files[0]}: {str(e)}")
        
        # Look for image files
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        image_files = [f for f in os.listdir(results_dir) 
                      if any(f.lower().endswith(ext) for ext in image_extensions)]
        if image_files:
            img_path = os.path.join(results_dir, image_files[0])
            try:
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    self.heatmap_image = pixmap
                    self.display_heatmap()
                    loaded_files.append(f"{image_files[0]} (heatmap)")
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to load {image_files[0]}: {str(e)}")
        
        if loaded_files:
            self.update_statistics()
            QMessageBox.information(self, "Success", f"Auto-loaded: {', '.join(loaded_files)}")
        else:
            QMessageBox.information(self, "Info", "No results files found in the results directory")
    
    def display_similarity_table(self):
        """Display similarity data in the table widget"""
        if self.similarity_data is None:
            return
        
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
                item = QTableWidgetItem(f"{value:.6f}")
                
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
                font-size: 12px;
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
                font-size: 12px;
            }
        """)
        
        # Make table read-only
        self.similarity_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    
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
        
        # Calculate statistics
        data_values = self.similarity_data.values
        np.fill_diagonal(data_values, np.nan)  # Exclude diagonal (self-similarity)
        
        mean_similarity = np.nanmean(data_values)
        max_similarity = np.nanmax(data_values)
        min_similarity = np.nanmin(data_values)
        std_similarity = np.nanstd(data_values)
        
        # Update statistics display
        stats_text = f"""
<b>Similarity Matrix Statistics:</b><br>
• Mean Similarity: {mean_similarity:.4f}<br>
• Max Similarity: {max_similarity:.4f}<br>
• Min Similarity: {min_similarity:.4f}<br>
• Std Deviation: {std_similarity:.4f}<br>
• Matrix Size: {self.similarity_data.shape[0]} × {self.similarity_data.shape[1]}<br>
• Total Comparisons: {self.similarity_data.shape[0] * self.similarity_data.shape[1]}
        """
        
        self.stats_placeholder.setText(stats_text)
        self.stats_placeholder.setStyleSheet("""
            QLabel {
                color: #374151;
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
        """)
    
    def resizeEvent(self, event):
        """Handle resize events to update heatmap display"""
        super().resizeEvent(event)
        if self.heatmap_image is not None:
            self.display_heatmap()
