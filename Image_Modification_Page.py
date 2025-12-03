"""
Image Modification Page
Simple image editing capabilities for the Image Processing App
"""

import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QSlider, QGroupBox, QGridLayout,
                               QFileDialog, QMessageBox, QSpinBox, QComboBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QImage
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np


class ImageModificationPage(QWidget):
    """
    Image modification page for editing single images.
    Features: Rotate, Flip, Resize, Crop, Brightness, Contrast, Filters
    """
    
    def __init__(self, image_path=None, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_image = None
        self.current_image = None
        self.modified_image = None
        
        # Maximum display size for consistent scaling
        self.max_display_size = (800, 600)
        
        # Modification history for undo
        self.history = []
        self.history_index = -1
        
        self.init_ui()
        
        if image_path:
            self.load_image(image_path)
    
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Controls
        controls_layout = QVBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Image info
        self.info_label = QLabel("No image loaded")
        self.info_label.setStyleSheet("font-size: 14px; padding: 10px;")
        controls_layout.addWidget(self.info_label)
        
        # File operations
        file_group = self.create_file_group()
        controls_layout.addWidget(file_group)
        
        # Transform operations
        transform_group = self.create_transform_group()
        controls_layout.addWidget(transform_group)
        
        # Adjustments
        adjustments_group = self.create_adjustments_group()
        controls_layout.addWidget(adjustments_group)
        
        # Filters
        filters_group = self.create_filters_group()
        controls_layout.addWidget(filters_group)
        
        # Resize/Crop
        resize_group = self.create_resize_group()
        controls_layout.addWidget(resize_group)
        
        # History controls
        history_group = self.create_history_group()
        controls_layout.addWidget(history_group)
        
        # Add stretch to push everything to top
        controls_layout.addStretch()
        
        # Right side - Image display
        image_layout = QVBoxLayout()
        
        # Image display label
        self.image_label = QLabel("Load an image to start editing")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #f5f5f5;
                min-width: 800px;
                min-height: 600px;
            }
        """)
        self.image_label.setScaledContents(False)
        image_layout.addWidget(self.image_label)
        
        # Status label
        self.status_label = QLabel("Ready")
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
    
    def create_file_group(self):
        """Create file operations group"""
        group = QGroupBox("File Operations")
        layout = QVBoxLayout()
        
        save_btn = QPushButton("Save Image")
        save_btn.clicked.connect(self.save_image)
        save_btn.setStyleSheet("padding: 8px; font-size: 12px;")
        layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Original")
        reset_btn.clicked.connect(self.reset_to_original)
        reset_btn.setStyleSheet("padding: 8px; font-size: 12px; background-color: #ff9800; color: white;")
        layout.addWidget(reset_btn)
        
        group.setLayout(layout)
        return group
    
    def create_transform_group(self):
        """Create transform operations group"""
        group = QGroupBox("Transform")
        layout = QGridLayout()
        
        # Rotate buttons
        rotate_left_btn = QPushButton("↶ Rotate Left")
        rotate_left_btn.clicked.connect(lambda: self.rotate_image(-90))
        layout.addWidget(rotate_left_btn, 0, 0)
        
        rotate_right_btn = QPushButton("↷ Rotate Right")
        rotate_right_btn.clicked.connect(lambda: self.rotate_image(90))
        layout.addWidget(rotate_right_btn, 0, 1)
        
        # Flip buttons
        flip_h_btn = QPushButton("⇄ Flip Horizontal")
        flip_h_btn.clicked.connect(self.flip_horizontal)
        layout.addWidget(flip_h_btn, 1, 0)
        
        flip_v_btn = QPushButton("⇅ Flip Vertical")
        flip_v_btn.clicked.connect(self.flip_vertical)
        layout.addWidget(flip_v_btn, 1, 1)
        
        group.setLayout(layout)
        return group
    
    def create_adjustments_group(self):
        """Create image adjustments group"""
        group = QGroupBox("Adjustments")
        layout = QVBoxLayout()
        
        # Brightness
        brightness_label = QLabel("Brightness:")
        brightness_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 13px; 
            color: #2c3e50;
            padding: 5px 0px 2px 0px;
        """)
        layout.addWidget(brightness_label)
        
        brightness_layout = QHBoxLayout()
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.brightness_slider.setTickInterval(25)
        self.brightness_slider.valueChanged.connect(self.update_preview)
        self.brightness_value = QLabel("1.0")
        self.brightness_value.setMinimumWidth(35)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_value)
        layout.addLayout(brightness_layout)
        
        # Contrast
        contrast_label = QLabel("Contrast:")
        contrast_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 13px; 
            color: #2c3e50;
            padding: 8px 0px 2px 0px;
        """)
        layout.addWidget(contrast_label)
        
        contrast_layout = QHBoxLayout()
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.contrast_slider.setTickInterval(25)
        self.contrast_slider.valueChanged.connect(self.update_preview)
        self.contrast_value = QLabel("1.0")
        self.contrast_value.setMinimumWidth(35)
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_value)
        layout.addLayout(contrast_layout)
        
        # Sharpness
        sharpness_label = QLabel("Sharpness:")
        sharpness_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 13px; 
            color: #2c3e50;
            padding: 8px 0px 2px 0px;
        """)
        layout.addWidget(sharpness_label)
        
        sharpness_layout = QHBoxLayout()
        self.sharpness_slider = QSlider(Qt.Orientation.Horizontal)
        self.sharpness_slider.setMinimum(0)
        self.sharpness_slider.setMaximum(200)
        self.sharpness_slider.setValue(100)
        self.sharpness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sharpness_slider.setTickInterval(25)
        self.sharpness_slider.valueChanged.connect(self.update_preview)
        self.sharpness_value = QLabel("1.0")
        self.sharpness_value.setMinimumWidth(35)
        sharpness_layout.addWidget(self.sharpness_slider)
        sharpness_layout.addWidget(self.sharpness_value)
        layout.addLayout(sharpness_layout)
        
        # Apply adjustments button
        apply_btn = QPushButton("Apply Adjustments")
        apply_btn.clicked.connect(self.apply_adjustments)
        apply_btn.setStyleSheet("padding: 8px; background-color: #4CAF50; color: white;")
        layout.addWidget(apply_btn)
        
        group.setLayout(layout)
        return group
    
    def create_filters_group(self):
        """Create filters group"""
        group = QGroupBox("Filters")
        layout = QVBoxLayout()
        
        # Filter selection
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "None",
            "Blur",
            "Sharpen",
            "Edge Enhance",
            "Emboss",
            "Contour",
            "Smooth"
        ])
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        layout.addLayout(filter_layout)
        
        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.clicked.connect(self.apply_filter)
        apply_filter_btn.setStyleSheet("padding: 8px; background-color: #2196F3; color: white;")
        layout.addWidget(apply_filter_btn)
        
        group.setLayout(layout)
        return group
    
    def create_resize_group(self):
        """Create resize/crop group"""
        group = QGroupBox("Resize")
        layout = QVBoxLayout()
        
        # Size inputs
        size_layout = QHBoxLayout()
        
        width_label = QLabel("Width:")
        self.width_spin = QSpinBox()
        self.width_spin.setMinimum(1)
        self.width_spin.setMaximum(10000)
        self.width_spin.setValue(800)
        
        height_label = QLabel("Height:")
        self.height_spin = QSpinBox()
        self.height_spin.setMinimum(1)
        self.height_spin.setMaximum(10000)
        self.height_spin.setValue(600)
        
        size_layout.addWidget(width_label)
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(height_label)
        size_layout.addWidget(self.height_spin)
        layout.addLayout(size_layout)
        
        # Resize button
        resize_btn = QPushButton("Resize Image")
        resize_btn.clicked.connect(self.resize_image)
        resize_btn.setStyleSheet("padding: 8px;")
        layout.addWidget(resize_btn)
        
        group.setLayout(layout)
        return group
    
    def create_history_group(self):
        """Create history/undo group"""
        group = QGroupBox("History")
        layout = QHBoxLayout()
        
        undo_btn = QPushButton("⟲ Undo")
        undo_btn.clicked.connect(self.undo)
        undo_btn.setStyleSheet("padding: 8px;")
        layout.addWidget(undo_btn)
        
        redo_btn = QPushButton("⟳ Redo")
        redo_btn.clicked.connect(self.redo)
        redo_btn.setStyleSheet("padding: 8px;")
        layout.addWidget(redo_btn)
        
        group.setLayout(layout)
        return group
    
    def load_image(self, image_path):
        """Load an image from path"""
        try:
            self.image_path = image_path
            self.original_image = Image.open(image_path).convert('RGB')
            self.current_image = self.original_image.copy()
            
            # Initialize history
            self.history = [self.current_image.copy()]
            self.history_index = 0
            
            # Update size spinboxes
            width, height = self.current_image.size
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)
            
            # Update display
            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText(f"Loaded: {image_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def load_image_dialog(self):
        """Open file dialog to load image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def display_image(self, pil_image):
        """Display PIL image in the label"""
        # Convert PIL image to QPixmap
        img_array = np.array(pil_image)
        height, width, channel = img_array.shape
        bytes_per_line = 3 * width
        q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale to fit max display size while maintaining aspect ratio
        # Use consistent size to prevent image jumping during preview
        from PySide6.QtCore import QSize
        max_size = QSize(self.max_display_size[0], self.max_display_size[1])
        scaled_pixmap = pixmap.scaled(
            max_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
    
    def update_info(self):
        """Update image information display"""
        if self.current_image:
            width, height = self.current_image.size
            mode = self.current_image.mode
            self.info_label.setText(f"Size: {width}x{height} | Mode: {mode}")
    
    def add_to_history(self, image):
        """Add image to history for undo/redo"""
        # Remove any forward history
        self.history = self.history[:self.history_index + 1]
        
        # Add new state
        self.history.append(image.copy())
        self.history_index += 1
        
        # Limit history size
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index -= 1
    
    def rotate_image(self, degrees):
        """Rotate image by specified degrees"""
        if self.current_image is None:
            return
        
        try:
            rotated = self.current_image.rotate(-degrees, expand=True)
            self.current_image = rotated
            self.add_to_history(self.current_image)
            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText(f"Rotated {degrees}°")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rotate: {str(e)}")
    
    def flip_horizontal(self):
        """Flip image horizontally"""
        if self.current_image is None:
            return
        
        try:
            flipped = self.current_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            self.current_image = flipped
            self.add_to_history(self.current_image)
            self.display_image(self.current_image)
            self.status_label.setText("Flipped horizontally")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to flip: {str(e)}")
    
    def flip_vertical(self):
        """Flip image vertically"""
        if self.current_image is None:
            return
        
        try:
            flipped = self.current_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            self.current_image = flipped
            self.add_to_history(self.current_image)
            self.display_image(self.current_image)
            self.status_label.setText("Flipped vertically")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to flip: {str(e)}")
    
    def update_preview(self):
        """Update preview with current adjustment values"""
        if self.current_image is None:
            return
        
        # Update value labels
        brightness_val = self.brightness_slider.value() / 100.0
        contrast_val = self.contrast_slider.value() / 100.0
        sharpness_val = self.sharpness_slider.value() / 100.0
        
        self.brightness_value.setText(f"{brightness_val:.1f}")
        self.contrast_value.setText(f"{contrast_val:.1f}")
        self.sharpness_value.setText(f"{sharpness_val:.1f}")
        
        # Apply preview (without adding to history)
        try:
            preview = self.current_image.copy()
            
            if brightness_val != 1.0:
                enhancer = ImageEnhance.Brightness(preview)
                preview = enhancer.enhance(brightness_val)
            
            if contrast_val != 1.0:
                enhancer = ImageEnhance.Contrast(preview)
                preview = enhancer.enhance(contrast_val)
            
            if sharpness_val != 1.0:
                enhancer = ImageEnhance.Sharpness(preview)
                preview = enhancer.enhance(sharpness_val)
            
            self.display_image(preview)
            self.modified_image = preview
            
        except Exception as e:
            self.status_label.setText(f"Preview error: {str(e)}")
    
    def apply_adjustments(self):
        """Apply current adjustments permanently"""
        if self.modified_image:
            self.current_image = self.modified_image.copy()
            self.add_to_history(self.current_image)
            
            # Reset sliders
            self.brightness_slider.setValue(100)
            self.contrast_slider.setValue(100)
            self.sharpness_slider.setValue(100)
            
            self.status_label.setText("Adjustments applied")
        else:
            self.status_label.setText("No adjustments to apply")
    
    def apply_filter(self):
        """Apply selected filter"""
        if self.current_image is None:
            return
        
        filter_name = self.filter_combo.currentText()
        
        if filter_name == "None":
            # Reset to the image before filters by undoing
            if self.history_index > 0:
                self.undo()
                self.status_label.setText("Filter removed - reverted to previous state")
            else:
                self.status_label.setText("No filter to remove")
            return
        
        try:
            filtered = self.current_image.copy()
            
            if filter_name == "Blur":
                filtered = filtered.filter(ImageFilter.BLUR)
            elif filter_name == "Sharpen":
                filtered = filtered.filter(ImageFilter.SHARPEN)
            elif filter_name == "Edge Enhance":
                filtered = filtered.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_name == "Emboss":
                filtered = filtered.filter(ImageFilter.EMBOSS)
            elif filter_name == "Contour":
                filtered = filtered.filter(ImageFilter.CONTOUR)
            elif filter_name == "Smooth":
                filtered = filtered.filter(ImageFilter.SMOOTH)
            
            self.current_image = filtered
            self.add_to_history(self.current_image)
            self.display_image(self.current_image)
            self.status_label.setText(f"Applied {filter_name} filter")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply filter: {str(e)}")
    
    def resize_image(self):
        """Resize image to specified dimensions"""
        if self.current_image is None:
            return
        
        try:
            new_width = self.width_spin.value()
            new_height = self.height_spin.value()
            
            resized = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.current_image = resized
            self.add_to_history(self.current_image)
            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText(f"Resized to {new_width}x{new_height}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to resize: {str(e)}")
    
    def undo(self):
        """Undo last modification"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText("Undo")
        else:
            self.status_label.setText("Nothing to undo")
    
    def redo(self):
        """Redo last undone modification"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText("Redo")
        else:
            self.status_label.setText("Nothing to redo")
    
    def reset_to_original(self):
        """Reset image to original"""
        if self.original_image:
            reply = QMessageBox.question(
                self,
                "Reset Image",
                "Are you sure you want to reset to the original image?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.current_image = self.original_image.copy()
                self.history = [self.current_image.copy()]
                self.history_index = 0
                
                # Reset all sliders
                self.brightness_slider.setValue(100)
                self.contrast_slider.setValue(100)
                self.sharpness_slider.setValue(100)
                
                self.display_image(self.current_image)
                self.update_info()
                self.status_label.setText("Reset to original")
    
    def save_image(self):
        """Save current image"""
        if self.current_image is None:
            QMessageBox.warning(self, "No Image", "No image to save")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*.*)"
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                self.status_label.setText(f"Saved: {file_path}")
                QMessageBox.information(self, "Success", f"Image saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")
    
    def get_modified_image(self):
        """Return the current modified image"""
        return self.current_image


def main():
    """Test the image modification page standalone"""
    from PySide6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Image Modification Test")
    window.setGeometry(100, 100, 1400, 900)
    mod_page = ImageModificationPage()
    window.setCentralWidget(mod_page)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()