"""
Results Tab - Display processing results and analysis data
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QSizePolicy, QPushButton)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage


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
        
        # Heatmap placeholder
        heatmap_container = QWidget()
        heatmap_layout = QVBoxLayout(heatmap_container)
        heatmap_label = QLabel("Heatmap visualization will be shown here")
        heatmap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heatmap_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff0000, stop:0.5 #ffff00, stop:1 #00ff00);
                color: #000000;
                padding: 40px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
        """)
        heatmap_layout.addWidget(heatmap_label)
        self.analysis_section.content_layout.addWidget(heatmap_container)
        
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
