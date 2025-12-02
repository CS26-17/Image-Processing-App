import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                               QWidget, QLabel, QTabWidget, QFileDialog, QHBoxLayout,
                               QFrame, QSizePolicy, QGroupBox)
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt, QMimeData
from tabs.Image_Modification_Page import ImageModificationPage
from tabs.results_tab import ResultsTab
from tabs.documentation_tab import DocumentationTab

class ImageProcessingApp(QMainWindow):
    """
    Main application window for Image Processing App
    Supports drag & drop and image upload functionality
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processing App")
        self.setGeometry(100, 100, 1400, 900)  # Larger window size for better layout
        
        # Enable drag and drop functionality
        self.setAcceptDrops(True)
        
        # Set application-wide styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #C2C7CB;
                background-color: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #E1E1E1;
                border: 1px solid #C4C4C3;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
        """)
        
        # Initialize tab widget as central widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Store current image path
        self.current_image_path = None
        
        # Setup all tabs
        self.setup_home_tab()
        self.setup_other_tabs()
    
    def setup_home_tab(self):
        """Setup the home tab with image upload and display functionality"""
        home_widget = QWidget()
        main_layout = QHBoxLayout(home_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Left side - Control panel
        controls_layout = QVBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        controls_layout.setSpacing(10)
        
        # Image info label
        self.info_label = QLabel("No image loaded")
        self.info_label.setStyleSheet("font-size: 14px; padding: 10px;")
        controls_layout.addWidget(self.info_label)
        
        # File operations group
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        
        self.upload_button = QPushButton("📁 Upload Image")
        self.upload_button.setStyleSheet("padding: 8px; font-size: 12px;")
        self.upload_button.clicked.connect(self.upload_image)
        file_layout.addWidget(self.upload_button)
        
        self.clear_button = QPushButton("🗑️ Clear Image")
        self.clear_button.setStyleSheet("padding: 8px; font-size: 12px;")
        self.clear_button.clicked.connect(self.clear_image)
        file_layout.addWidget(self.clear_button)
        
        file_group.setLayout(file_layout)
        controls_layout.addWidget(file_group)
        
        # Processing group
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout()
        
        self.process_button = QPushButton("⚡ Process Image")
        self.process_button.setStyleSheet("padding: 8px; font-size: 12px; background-color: #4CAF50; color: white;")
        self.process_button.clicked.connect(self.process_image)
        process_layout.addWidget(self.process_button)
        
        process_group.setLayout(process_layout)
        controls_layout.addWidget(process_group)
        
        controls_layout.addStretch()
        
        # Right side - Image display
        image_layout = QVBoxLayout()
        
        self.image_label = QLabel("Drag & drop an image here\nor click the upload button")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #f5f5f5;
                min-width: 800px;
                min-height: 600px;
                color: #999999;
            }
        """)
        self.image_label.setScaledContents(False)
        image_layout.addWidget(self.image_label)
        
        # Status label
        self.status_label = QLabel("Ready to process images")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #e3f2fd;
                border: 1px solid #90caf9;
                border-radius: 4px;
                font-size: 12px;
                color: #1976d2;
            }
        """)
        image_layout.addWidget(self.status_label)
        
        # Add layouts to main layout
        main_layout.addLayout(controls_layout, 1)
        main_layout.addLayout(image_layout, 3)
        
        # Add home tab to tab widget
        self.tab_widget.addTab(home_widget, "🏠 Home")
    
    def setup_other_tabs(self):
        """Setup placeholder tabs for future functionality"""
        
        # Results Tab
        self.results_tab = ResultsTab()
        self.tab_widget.addTab(self.results_tab, "📊 Results")
        
        # Documentation Tab - use the real DocumentationTab
        self.docs_tab = DocumentationTab(parent=self) 
        self.tab_widget.addTab(self.docs_tab, "📚 Documentation")
        
        # Modification Tab - Actual image modification page
        self.modification_page = ImageModificationPage(parent=self)
        self.tab_widget.addTab(self.modification_page, "🛠️ Modification")
        
        # Analysis Setup Tab
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        analysis_layout.setContentsMargins(30, 30, 30, 30)
        
        analysis_label = QLabel("Analysis Configuration")
        analysis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analysis_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 20px;")
        analysis_layout.addWidget(analysis_label)
        
        analysis_content = QLabel("Configure analysis parameters and settings.\n\n"
                                "• Algorithm selection\n"
                                "• Parameter tuning\n"
                                "• Output format\n"
                                "• Automation settings")
        analysis_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analysis_content.setStyleSheet("font-size: 14px; color: #7f8c8d; margin: 20px;")
        analysis_content.setWordWrap(True)
        analysis_layout.addWidget(analysis_content)
        
        analysis_layout.addStretch()
        self.tab_widget.addTab(analysis_widget, "⚙️ Analysis Setup")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event - check if dragged content is valid image file"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and self.is_image_file(urls[0].toLocalFile()):
                event.acceptProposedAction()
                # Visual feedback for valid drag
                self.image_label.setStyleSheet("""
                    QLabel {
                        border: 2px dashed #4CAF50;
                        border-radius: 10px;
                        background-color: #e8f5e9;
                        min-width: 800px;
                        min-height: 600px;
                        color: #4CAF50;
                        font-weight: bold;
                    }
                """)
                self.image_label.setText("✓ Release to upload image")
                self.status_label.setText("Ready to drop image")
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event - reset visual feedback"""
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #f5f5f5;
                min-width: 800px;
                min-height: 600px;
                color: #999999;
            }
        """)
        self.image_label.setText("Drag & drop an image here\nor click the upload button")
        self.status_label.setText("Ready to process images")
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event - process dropped image files"""
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #f5f5f5;
                min-width: 800px;
                min-height: 600px;
                color: #999999;
            }
        """)
        self.image_label.setText("Processing image...")
        
        # Process all dropped URLs
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if self.is_image_file(file_path):
                self.display_image(file_path)
                break  # Only process first valid image
        else:
            # No valid image files found
            self.status_label.setText("Please drop a valid image file (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP)")
            self.image_label.setText("Drag & drop an image here\nor click the upload button")
    
    def is_image_file(self, file_path):
        """Check if file is a supported image format"""
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        return os.path.isfile(file_path) and file_path.lower().endswith(image_extensions)
    
    def upload_image(self):
        """Open file dialog to select and upload image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp);;All Files (*)"
        )
        
        if file_path:
            self.display_image(file_path)
    
    def display_image(self, file_path):
        """Display the selected image in the image label"""
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                self.status_label.setText("Error: Unable to load image file")
                self.image_label.setText("Drag & drop an image here\nor click the upload button")
                return
            
            # Scale image to fit display area while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Display the image
            self.image_label.setPixmap(scaled_pixmap)
            self.current_image_path = file_path
            file_name = os.path.basename(file_path)
            
            # Update info label with image details
            img_width = pixmap.width()
            img_height = pixmap.height()
            file_size = os.path.getsize(file_path) / 1024  # KB
            self.info_label.setText(f"File: {file_name}\nSize: {img_width}x{img_height}\nFile Size: {file_size:.1f} KB")
            
            self.status_label.setText(f"Image loaded successfully: {file_name}")
            
        except Exception as e:
            self.status_label.setText(f"Error loading image: {str(e)}")
            self.image_label.setText("Drag & drop an image here\nor click the upload button")
    
    def clear_image(self):
        """Clear the currently displayed image"""
        self.image_label.clear()
        self.image_label.setText("Drag & drop an image here\nor click the upload button")
        self.current_image_path = None
        self.info_label.setText("No image loaded")
        self.status_label.setText("Ready to process images")
    
    def process_image(self):
        """Process the current image - load it in modification tab"""
        if self.current_image_path:
            file_name = os.path.basename(self.current_image_path)
            # Load the image in the modification page
            self.modification_page.load_image(self.current_image_path)
            # Switch to the modification tab
            self.tab_widget.setCurrentWidget(self.modification_page)
            self.status_label.setText(f"Loaded {file_name} in Modification tab")
        else:
            self.status_label.setText("Please upload an image first")


def main():
    """Main function to start the application"""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = ImageProcessingApp()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
