"""
Home Tab - Main image upload and display functionality
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QFrame, QSizePolicy, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt


class HomeTab(QWidget):
    """
    Home tab widget with image upload and display functionality
    Supports drag & drop and file dialog upload
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_images = []
        self.current_image_index = 0
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
        
        # Navigation buttons for multiple images
        self.navigation_layout = QHBoxLayout()

        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 8px 16px;
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.prev_button.clicked.connect(self.previous_image)
        self.prev_button.setEnabled(False)

        self.next_button = QPushButton("Next ▶")
        self.next_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 8px 16px;
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
        background-color: #5a6268;
            }
            QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
            }
        """)
        self.next_button.clicked.connect(self.next_image)
        self.next_button.setEnabled(False)

        self.navigation_layout.addWidget(self.prev_button)
        self.navigation_layout.addStretch()
        self.navigation_layout.addWidget(self.next_button)
        layout.addLayout(self.navigation_layout)
        
        # Button layout with multiple action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Upload Image Button
        self.upload_button = QPushButton("📁 Upload Images")
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
        self.process_button = QPushButton("⚡ Process Images")
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
        self.clear_button = QPushButton("🗑️ Clear All")
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
    
    def upload_multiple_images(self):
        """Open file dialog to select and upload multiple images"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Image Files",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp);;All Files (*)"
        )
        
        if file_paths:
            if self.current_images:
                reply = QMessageBox.question(
                     self,
                     "Add Images",
                     "Do you want to:\n\n• Add to existing images\n• Replace all existing images",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Yes
                 )
            
                if reply == QMessageBox.StandardButton.Yes:
                   self.load_multiple_images(file_paths, clear_existing=False)
                elif reply == QMessageBox.StandardButton.No:
                   self.load_multiple_images(file_paths, clear_existing=True)
            else:
              self.load_multiple_images(file_paths, clear_existing=True)
    
    def load_multiple_images(self, image_paths, clear_existing=False):
        """Load multiple images from file paths
        Args:
        image_paths: List of image file paths to load
        clear_existing: If True, clear existing images before loading new ones
        """
        if clear_existing:
            self.current_images = []
        
        valid_images = []
        
        for file_path in image_paths:
            try:
                existing_paths = [img['path'] for img in self.current_images]
                if file_path in existing_paths:
                    continue
                
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    valid_images.append({
                        'path': file_path,
                        'pixmap': pixmap,
                        'name': os.path.basename(file_path)
                    })
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        if valid_images:
            self.current_images.extend(valid_images)
            if clear_existing or not self.current_images:
                self.current_image_index = 0
            self.display_current_image()
            self.update_navigation_buttons()
            total_count = len(self.current_images)
            new_count = len(valid_images)
            self.status_label.setText(f"Added {new_count} image(s). Total: {total_count} image(s)")
        elif not self.current_images:
            self.status_label.setText("No valid images could be loaded")
    
    def display_current_image(self):
        """Display the current image in the image label"""
        if not self.current_images:
            return
        
        current_image = self.current_images[self.current_image_index]
        
        # Scale image to fit display area while maintaining aspect ratio
        scaled_pixmap = current_image['pixmap'].scaled(
            400, 300, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Display the image
        self.image_label.setPixmap(scaled_pixmap)
        
        # Update status with image info
        if len(self.current_images) > 1:
            self.status_label.setText(f"Image {self.current_image_index + 1}/{len(self.current_images)}: {current_image['name']}")
        else:
            self.status_label.setText(f"Image loaded: {current_image['name']}")
    
    def update_navigation_buttons(self):
        """Update navigation buttons based on current state"""
        has_multiple_images = len(self.current_images) > 1
        self.prev_button.setEnabled(has_multiple_images and self.current_image_index > 0)
        self.next_button.setEnabled(has_multiple_images and self.current_image_index < len(self.current_images) - 1)
    
    def previous_image(self):
        """Display previous image in the list"""
        if self.current_images and self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_current_image()
            self.update_navigation_buttons()
    
    def next_image(self):
        """Display next image in the list"""
        if self.current_images and self.current_image_index < len(self.current_images) - 1:
            self.current_image_index += 1
            self.display_current_image()
            self.update_navigation_buttons()
    
    def clear_all_images(self):
        """Clear all currently loaded images"""
        self.image_label.clear()
        self.image_label.setText("Drag & drop images here\nor click the upload button below")
        self.current_images = []
        self.current_image_index = 0
        self.status_label.setText("Ready to process images")
        self.update_navigation_buttons()
    
    def process_images(self):
        """Process all loaded images (placeholder functionality)"""
        if self.current_images:
            if len(self.current_images) == 1:
                current_image = self.current_images[self.current_image_index]
                self.status_label.setText(f"Processing image: {current_image['name']}")
            else:
                self.status_label.setText(f"Processing {len(self.current_images)} images...")
            # TODO: Add actual image processing logic here
        else:
            self.status_label.setText("Please upload images first")
    
    def handle_drag_enter(self, event: QDragEnterEvent):
        """Handle drag enter event - check if dragged content contains valid image files"""
        if event.mimeData().hasUrls():
            # Check if any of the dragged files are images
            has_valid_image = False
            for url in event.mimeData().urls():
                if self.is_image_file(url.toLocalFile()):
                    has_valid_image = True
                    break
            
            if has_valid_image:
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
                self.image_label.setText("Release to upload images")
                self.status_label.setText("Ready to drop images - Release mouse button")
    
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
        if self.current_images:
            self.display_current_image()
        else:
            self.image_label.setText("Drag & drop images here\nor click the upload button below")
        self.status_label.setText("Ready to process images")
    
    def handle_drop(self, event: QDropEvent):
        """Handle drop event - process dropped image files (multiple)"""
        self.image_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 16px;
                padding: 40px;
                qproperty-wordWrap: true;
            }
        """)
        self.image_label.setText("Processing images...")
        
        # Collect all valid image files
        valid_image_paths = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if self.is_image_file(file_path):
                valid_image_paths.append(file_path)
        
        if valid_image_paths:
            self.load_multiple_images(valid_image_paths, clear_existing=False)
        else:
            # No valid image files found
            self.status_label.setText("Please drop valid image files (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP)")
            self.image_label.setText("Drag & drop images here\nor click the upload button below")
    
    
    def display_image(self, file_path):
        """Display single image (for backward compatibility)"""
        self.load_multiple_images([file_path])
    
    def upload_image(self):
        """Upload single image (for backward compatibility)"""
        self.upload_multiple_images()
    
    def clear_image(self):
        """Clear single image (for backward compatibility)"""
        self.clear_all_images()
    
    def process_image(self):
        """Process single image (for backward compatibility)"""
        self.process_images()