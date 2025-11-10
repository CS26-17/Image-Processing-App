"""
Home Tab - Main image upload and display functionality
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QFrame, QSizePolicy, QPushButton, QFileDialog)
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt


class HomeTab(QWidget):
    """
    Home tab widget with image upload and display functionality
    Supports drag & drop and file dialog upload
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the home tab UI with image upload and display functionality"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Application title
        title_label = QLabel("Image Processing Application")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 20px;
                padding: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Instructions label
        instructions_label = QLabel("Upload an image to get started with processing")
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(instructions_label)
        
        # Image display area with styled frame
        image_frame = QFrame()
        image_frame.setFrameStyle(QFrame.Box)
        image_frame.setStyleSheet("""
            QFrame {
                border: 3px dashed #bdc3c7;
                border-radius: 10px;
                background-color: #fafafa;
                min-height: 300px;
            }
        """)
        image_layout = QVBoxLayout(image_frame)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 16px;
                padding: 40px;
                qproperty-wordWrap: true;
            }
        """)
        self.image_label.setText("Drag & drop an image here\nor click the upload button below")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_layout.addWidget(self.image_label)
        
        layout.addWidget(image_frame)
        
        # Status label to show current state
        self.status_label = QLabel("Ready to process images")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #34495e;
                margin: 10px;
                padding: 12px;
                background-color: #e8f4fd;
                border-radius: 6px;
                border: 1px solid #b3d9ff;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Button layout with multiple action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Upload Image Button
        self.upload_button = QPushButton("📁 Upload Image")
        self.upload_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.upload_button.clicked.connect(self.upload_image)
        
        # Process Image Button
        self.process_button = QPushButton("⚡ Process Image")
        self.process_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a6ebd;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.process_button.clicked.connect(self.process_image)
        
        # Clear Button
        self.clear_button = QPushButton("🗑️ Clear Image")
        self.clear_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 6px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #d17a00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.clear_button.clicked.connect(self.clear_image)
        
        # Add buttons to layout
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.clear_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
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
                self.image_label.setText("Drag & drop an image here\nor click the upload button below")
                return
            
            # Scale image to fit display area while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                400, 300, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Display the image
            self.image_label.setPixmap(scaled_pixmap)
            self.current_image_path = file_path
            file_name = os.path.basename(file_path)
            self.status_label.setText(f"Image loaded successfully: {file_name}")
            
        except Exception as e:
            self.status_label.setText(f"Error loading image: {str(e)}")
            self.image_label.setText("Drag & drop an image here\nor click the upload button below")
    
    def clear_image(self):
        """Clear the currently displayed image"""
        self.image_label.clear()
        self.image_label.setText("Drag & drop an image here\nor click the upload button below")
        self.current_image_path = None
        self.status_label.setText("Ready to process images")
    
    def process_image(self):
        """Process the current image (placeholder functionality)"""
        if self.current_image_path:
            file_name = os.path.basename(self.current_image_path)
            self.status_label.setText(f"Processing image: {file_name}")
            # TODO: Add actual image processing logic here
        else:
            self.status_label.setText("Please upload an image first")
    
    def handle_drag_enter(self, event: QDragEnterEvent):
        """Handle drag enter event - check if dragged content is valid image file"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and self.is_image_file(urls[0].toLocalFile()):
                event.acceptProposedAction()
                # Visual feedback for valid drag
                self.image_label.setStyleSheet("""
                    QLabel {
                        color: #4CAF50;
                        font-size: 16px;
                        padding: 40px;
                        qproperty-wordWrap: true;
                    }
                """)
                self.image_label.setText("Release to upload image")
                self.status_label.setText("Ready to drop image - Release mouse button")
    
    def handle_drag_leave(self):
        """Handle drag leave event - reset visual feedback"""
        self.image_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 16px;
                padding: 40px;
                qproperty-wordWrap: true;
            }
        """)
        self.image_label.setText("Drag & drop an image here\nor click the upload button below")
        self.status_label.setText("Ready to process images")
    
    def handle_drop(self, event: QDropEvent):
        """Handle drop event - process dropped image files"""
        self.image_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 16px;
                padding: 40px;
                qproperty-wordWrap: true;
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
            self.image_label.setText("Drag & drop an image here\nor click the upload button below")
