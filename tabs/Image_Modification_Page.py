"""
Image Modification Page
Simple image editing capabilities for the Image Processing App
"""

import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QSlider, QGroupBox, QGridLayout,
                               QFileDialog, QMessageBox, QSpinBox, QComboBox, QDoubleSpinBox,
                               QScrollArea)
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
        
        # Track state before filter application
        self.pre_filter_image = None
        
        # Custom filter parameters
        self.blur_radius = 2
        self.gaussian_blur_radius = 2
        self.sharpen_factor = 1.0
        self.edge_enhance_factor = 1.0
        
        self.init_ui()
        
        if image_path:
            self.load_image(image_path)
    
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Controls (with scroll area)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMinimumWidth(350)
        scroll_area.setMaximumWidth(450)
        scroll_area.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: white; color: black;")
        controls_layout = QVBoxLayout(scroll_widget)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Image info (hidden but kept for update_info method)
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 14px; padding: 10px;")
        self.info_label.hide()
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
        
        scroll_area.setWidget(scroll_widget)
        
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
            }
        """)
        self.image_label.setScaledContents(False)
        self.image_label.setMinimumSize(400, 300)
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
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(image_layout, 1)
    
    def show_info_dialog(self, title, message):
        """Show information dialog with documentation"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def create_file_group(self):
        """Create file operations group"""
        group = QGroupBox("File Operations")
        layout = QVBoxLayout()
        
        # Add title with info button
        header_layout = QHBoxLayout()
        title_label = QLabel("File Operations")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        info_btn = QPushButton("ℹ️")
        info_btn.setMaximumWidth(30)
        info_btn.setStyleSheet("font-size: 14px; padding: 2px; background-color: transparent; border: none;")
        info_btn.clicked.connect(lambda: self.show_info_dialog(
            "File Operations",
            "<b>File Operations</b><br><br>"
            "<b>Save Image:</b> Save the current modified image to disk<br><br>"
            "<b>Reset to Original:</b> Discard all changes and restore the original image"
        ))
        header_layout.addWidget(info_btn)
        layout.addLayout(header_layout)
        
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
        layout = QVBoxLayout()
        
        # Add title with info button
        header_layout = QHBoxLayout()
        title_label = QLabel("Transform Operations")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        info_btn = QPushButton("ℹ️")
        info_btn.setMaximumWidth(30)
        info_btn.setStyleSheet("font-size: 14px; padding: 2px; background-color: transparent; border: none;")
        info_btn.clicked.connect(lambda: self.show_info_dialog(
            "Transform Operations",
            "<b>Transform Operations</b><br><br>"
            "<b>Rotate:</b> Rotate the image clockwise or counter-clockwise<br>"
            "• Use preset buttons for 90° rotations<br>"
            "• Or enter a custom angle (0-360 degrees)<br><br>"
            "<b>Flip:</b> Mirror the image horizontally or vertically<br>"
            "• Horizontal: Left ↔ Right<br>"
            "• Vertical: Top ↔ Bottom"
        ))
        header_layout.addWidget(info_btn)
        layout.addLayout(header_layout)
        
        # Grid for buttons
        button_grid = QGridLayout()
        
        # Rotate buttons
        rotate_left_btn = QPushButton("↶ Rotate Left 90°")
        rotate_left_btn.clicked.connect(lambda: self.rotate_image(-90))
        button_grid.addWidget(rotate_left_btn, 0, 0)
        
        rotate_right_btn = QPushButton("↷ Rotate Right 90°")
        rotate_right_btn.clicked.connect(lambda: self.rotate_image(90))
        button_grid.addWidget(rotate_right_btn, 0, 1)
        
        layout.addLayout(button_grid)
        
        # Custom rotation angle
        custom_rotate_layout = QHBoxLayout()
        custom_rotate_label = QLabel("Custom Angle:")
        self.rotation_angle_spin = QDoubleSpinBox()
        self.rotation_angle_spin.setMinimum(-360)
        self.rotation_angle_spin.setMaximum(360)
        self.rotation_angle_spin.setValue(45)
        self.rotation_angle_spin.setSuffix("°")
        self.rotation_angle_spin.setToolTip("Enter custom rotation angle in degrees")
        custom_rotate_btn = QPushButton("Rotate")
        custom_rotate_btn.clicked.connect(lambda: self.rotate_image(self.rotation_angle_spin.value()))
        custom_rotate_layout.addWidget(custom_rotate_label)
        custom_rotate_layout.addWidget(self.rotation_angle_spin)
        custom_rotate_layout.addWidget(custom_rotate_btn)
        layout.addLayout(custom_rotate_layout)
        
        # Flip buttons
        flip_grid = QGridLayout()
        flip_h_btn = QPushButton("⇄ Flip Horizontal")
        flip_h_btn.clicked.connect(self.flip_horizontal)
        flip_grid.addWidget(flip_h_btn, 0, 0)
        
        flip_v_btn = QPushButton("⇅ Flip Vertical")
        flip_v_btn.clicked.connect(self.flip_vertical)
        flip_grid.addWidget(flip_v_btn, 0, 1)
        layout.addLayout(flip_grid)
        
        group.setLayout(layout)
        return group
    
    def create_adjustments_group(self):
        """Create image adjustments group"""
        group = QGroupBox("Adjustments")
        layout = QVBoxLayout()
        
        # Add title with info button
        header_layout = QHBoxLayout()
        title_label = QLabel("Adjustments")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        info_btn = QPushButton("ℹ️")
        info_btn.setMaximumWidth(30)
        info_btn.setStyleSheet("font-size: 14px; padding: 2px; background-color: transparent; border: none;")
        info_btn.clicked.connect(lambda: self.show_info_dialog(
            "Image Adjustments",
            "<b>Image Adjustments</b><br><br>"
            "<b>Brightness:</b> Control the overall lightness/darkness<br>"
            "• 0.0 = Black, 1.0 = Original, 2.0 = Double brightness<br><br>"
            "<b>Contrast:</b> Control the difference between light and dark<br>"
            "• 0.0 = Gray, 1.0 = Original, 2.0 = Enhanced contrast<br><br>"
            "<b>Sharpness:</b> Control edge definition and detail<br>"
            "• 0.0 = Blurred, 1.0 = Original, 2.0 = Enhanced sharpness<br><br>"
            "<i>Adjustments are previewed in real-time. Click 'Apply Adjustments' to make them permanent.</i>"
        ))
        header_layout.addWidget(info_btn)
        layout.addLayout(header_layout)
        
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
        
        # Add title with info button
        header_layout = QHBoxLayout()
        title_label = QLabel("Filters")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        info_btn = QPushButton("ℹ️")
        info_btn.setMaximumWidth(30)
        info_btn.setStyleSheet("font-size: 14px; padding: 2px; background-color: transparent; border: none;")
        info_btn.clicked.connect(lambda: self.show_info_dialog(
            "Filters",
            "<b>Image Filters</b><br><br>"
            "<b>Box Blur:</b> Simple blur with adjustable radius (1-10 pixels)<br><br>"
            "<b>Gaussian Blur:</b> Smooth blur with adjustable radius (1-20 pixels)<br><br>"
            "<b>Sharpen:</b> Enhance edges with adjustable factor (0.5-3.0)<br><br>"
            "<b>Edge Enhance:</b> Emphasize edges with adjustable factor (1.0-5.0)<br><br>"
            "<b>Emboss:</b> Create a 3D raised effect<br><br>"
            "<b>Contour:</b> Detect and highlight edges<br><br>"
            "<b>Smooth:</b> Reduce noise and soften image<br><br>"
            "<b>Find Edges:</b> Detect all edges in the image<br><br>"
            "<i>Tip: Parameters are preserved so you can apply the same filter repeatedly with consistent results.</i>"
        ))
        header_layout.addWidget(info_btn)
        layout.addLayout(header_layout)
        
        # Filter selection with inline parameters
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "None",
            "Box Blur",
            "Gaussian Blur",
            "Sharpen",
            "Edge Enhance",
            "Emboss",
            "Contour",
            "Smooth",
            "Find Edges"
        ])
        self.filter_combo.currentTextChanged.connect(self.update_filter_params_visibility)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        
        # Box Blur parameters (inline)
        self.box_blur_label = QLabel("Radius:")
        self.box_blur_spin = QSpinBox()
        self.box_blur_spin.setMinimum(1)
        self.box_blur_spin.setMaximum(10)
        self.box_blur_spin.setValue(2)
        self.box_blur_spin.setToolTip("Blur radius in pixels (1-10)")
        filter_layout.addWidget(self.box_blur_label)
        filter_layout.addWidget(self.box_blur_spin)
        
        # Gaussian Blur parameters (inline)
        self.gaussian_blur_label = QLabel("Radius:")
        self.gaussian_blur_spin = QSpinBox()
        self.gaussian_blur_spin.setMinimum(1)
        self.gaussian_blur_spin.setMaximum(20)
        self.gaussian_blur_spin.setValue(2)
        self.gaussian_blur_spin.setToolTip("Gaussian blur radius in pixels (1-20)")
        filter_layout.addWidget(self.gaussian_blur_label)
        filter_layout.addWidget(self.gaussian_blur_spin)
        
        # Sharpen parameters (inline)
        self.sharpen_label = QLabel("Factor:")
        self.sharpen_spin = QDoubleSpinBox()
        self.sharpen_spin.setMinimum(0.5)
        self.sharpen_spin.setMaximum(3.0)
        self.sharpen_spin.setValue(1.0)
        self.sharpen_spin.setSingleStep(0.1)
        self.sharpen_spin.setToolTip("Sharpen factor (0.5-3.0, 1.0=normal)")
        filter_layout.addWidget(self.sharpen_label)
        filter_layout.addWidget(self.sharpen_spin)
        
        # Edge Enhance parameters (inline)
        self.edge_label = QLabel("Factor:")
        self.edge_spin = QDoubleSpinBox()
        self.edge_spin.setMinimum(1.0)
        self.edge_spin.setMaximum(5.0)
        self.edge_spin.setValue(1.0)
        self.edge_spin.setSingleStep(0.1)
        self.edge_spin.setToolTip("Edge enhancement factor (1.0-5.0)")
        filter_layout.addWidget(self.edge_label)
        filter_layout.addWidget(self.edge_spin)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Initially hide all parameter widgets
        self.update_filter_params_visibility("None")
        
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
        
        # Add title with info button
        header_layout = QHBoxLayout()
        title_label = QLabel("Resize")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        info_btn = QPushButton("ℹ️")
        info_btn.setMaximumWidth(30)
        info_btn.setStyleSheet("font-size: 14px; padding: 2px; background-color: transparent; border: none;")
        info_btn.clicked.connect(lambda: self.show_info_dialog(
            "Resize",
            "<b>Resize Image</b><br><br>"
            "Change the dimensions of your image.<br><br>"
            "<b>Interpolation Methods:</b><br>"
            "• <b>Lanczos:</b> Highest quality, best for downscaling (recommended)<br>"
            "• <b>Bicubic:</b> High quality, smooth results<br>"
            "• <b>Bilinear:</b> Good quality, faster processing<br>"
            "• <b>Nearest:</b> Fastest, preserves hard edges (pixel art)<br><br>"
            "<i>Tip: Use Lanczos for photographs, Nearest for pixel art.</i>"
        ))
        header_layout.addWidget(info_btn)
        layout.addLayout(header_layout)
        
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
    
    def update_filter_params_visibility(self, filter_name):
        """Show/hide filter parameters based on selected filter"""
        # Hide all parameter widgets
        self.box_blur_label.hide()
        self.box_blur_spin.hide()
        self.gaussian_blur_label.hide()
        self.gaussian_blur_spin.hide()
        self.sharpen_label.hide()
        self.sharpen_spin.hide()
        self.edge_label.hide()
        self.edge_spin.hide()
        
        # Show relevant parameter widgets
        if filter_name == "Box Blur":
            self.box_blur_label.show()
            self.box_blur_spin.show()
        elif filter_name == "Gaussian Blur":
            self.gaussian_blur_label.show()
            self.gaussian_blur_spin.show()
        elif filter_name == "Sharpen":
            self.sharpen_label.show()
            self.sharpen_spin.show()
        elif filter_name == "Edge Enhance":
            self.edge_label.show()
            self.edge_spin.show()

    def create_history_group(self):
        """Create history/undo group"""
        group = QGroupBox("History")
        layout = QVBoxLayout()
        
        # Add title with info button
        header_layout = QHBoxLayout()
        title_label = QLabel("History")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        info_btn = QPushButton("ℹ️")
        info_btn.setMaximumWidth(30)
        info_btn.setStyleSheet("font-size: 14px; padding: 2px; background-color: transparent; border: none;")
        info_btn.clicked.connect(lambda: self.show_info_dialog(
            "History",
            "<b>History Controls</b><br><br>"
            "<b>Undo:</b> Revert the last modification<br><br>"
            "<b>Redo:</b> Reapply a previously undone modification<br><br>"
            "<i>Up to 50 operations are stored in history.</i>"
        ))
        header_layout.addWidget(info_btn)
        layout.addLayout(header_layout)
        
        # Section title
        section_title = QLabel("Undo and Redo")
        section_title.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50;")
        layout.addWidget(section_title)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        undo_btn = QPushButton("⟲ Undo")
        undo_btn.clicked.connect(self.undo)
        undo_btn.setStyleSheet("padding: 8px;")
        buttons_layout.addWidget(undo_btn)
        
        redo_btn = QPushButton("⟳ Redo")
        redo_btn.clicked.connect(self.redo)
        redo_btn.setStyleSheet("padding: 8px;")
        buttons_layout.addWidget(redo_btn)
        
        layout.addLayout(buttons_layout)
        
        group.setLayout(layout)
        return group
    
    def load_image(self, image_path):
        """Load an image from path"""
        try:
            self.image_path = image_path
            self.original_image = Image.open(image_path).convert('RGB')
            self.current_image = self.original_image.copy()
            
            # Reset pre-filter state
            self.pre_filter_image = None
            
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
            # Use expand=True to prevent cropping, resample for quality, fillcolor for corners
            rotated = self.current_image.rotate(
                -degrees, 
                resample=Image.Resampling.BICUBIC,
                expand=True, 
                fillcolor=(255, 255, 255)
            )
            self.current_image = rotated
            self.add_to_history(self.current_image)
            # Reset pre-filter state after permanent change
            self.pre_filter_image = None
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
            # Reset pre-filter state after permanent change
            self.pre_filter_image = None
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
            # Reset pre-filter state after permanent change
            self.pre_filter_image = None
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
            # Reset pre-filter state after permanent change
            self.pre_filter_image = None
            
            # Reset sliders
            self.brightness_slider.setValue(100)
            self.contrast_slider.setValue(100)
            self.sharpness_slider.setValue(100)
            
            self.status_label.setText("Adjustments applied")
        else:
            self.status_label.setText("No adjustments to apply")
    
    def apply_filter(self):
        """Apply selected filter with custom parameters"""
        if self.current_image is None:
            return
        
        filter_name = self.filter_combo.currentText()
        
        if filter_name == "None":
            # Revert to pre-filter state if it exists
            if self.pre_filter_image is not None:
                self.current_image = self.pre_filter_image.copy()
                self.display_image(self.current_image)
                self.status_label.setText("Filter removed - reverted to original state")
            else:
                self.status_label.setText("No filter to remove")
            return
        
        try:
            # Save the pre-filter state if not already saved
            if self.pre_filter_image is None:
                self.pre_filter_image = self.current_image.copy()
            
            # Always start from the pre-filter state to avoid stacking
            filtered = self.pre_filter_image.copy()
            
            if filter_name == "Box Blur":
                radius = self.box_blur_spin.value()
                filtered = filtered.filter(ImageFilter.BoxBlur(radius))
                self.status_label.setText(f"Applied Box Blur (radius={radius})")
            elif filter_name == "Gaussian Blur":
                radius = self.gaussian_blur_spin.value()
                filtered = filtered.filter(ImageFilter.GaussianBlur(radius))
                self.status_label.setText(f"Applied Gaussian Blur (radius={radius})")
            elif filter_name == "Sharpen":
                factor = self.sharpen_spin.value()
                # Apply sharpening multiple times based on factor
                for _ in range(int(factor)):
                    filtered = filtered.filter(ImageFilter.SHARPEN)
                if factor % 1.0 > 0:
                    # Blend for fractional factors
                    temp = filtered.filter(ImageFilter.SHARPEN)
                    filtered = Image.blend(filtered, temp, factor % 1.0)
                self.status_label.setText(f"Applied Sharpen (factor={factor:.1f})")
            elif filter_name == "Edge Enhance":
                factor = self.edge_spin.value()
                for _ in range(int(factor)):
                    filtered = filtered.filter(ImageFilter.EDGE_ENHANCE)
                if factor % 1.0 > 0:
                    temp = filtered.filter(ImageFilter.EDGE_ENHANCE)
                    filtered = Image.blend(filtered, temp, factor % 1.0)
                self.status_label.setText(f"Applied Edge Enhance (factor={factor:.1f})")
            elif filter_name == "Emboss":
                filtered = filtered.filter(ImageFilter.EMBOSS)
                self.status_label.setText("Applied Emboss filter")
            elif filter_name == "Contour":
                filtered = filtered.filter(ImageFilter.CONTOUR)
                self.status_label.setText("Applied Contour filter")
            elif filter_name == "Smooth":
                filtered = filtered.filter(ImageFilter.SMOOTH)
                self.status_label.setText("Applied Smooth filter")
            elif filter_name == "Find Edges":
                filtered = filtered.filter(ImageFilter.FIND_EDGES)
                self.status_label.setText("Applied Find Edges filter")
            
            # Update current image but don't save to pre_filter_image
            # (so next filter still starts from the same base)
            self.current_image = filtered
            self.display_image(self.current_image)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply filter: {str(e)}")
    
    def resize_image(self):
        """Resize image to specified dimensions"""
        if self.current_image is None:
            return
        
        try:
            new_width = self.width_spin.value()
            new_height = self.height_spin.value()
            
            # Use Lanczos interpolation (highest quality)
            resized = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.current_image = resized
            self.add_to_history(self.current_image)
            # Reset pre-filter state after permanent change
            self.pre_filter_image = None
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
            # Reset pre-filter state after undo
            self.pre_filter_image = None
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
            # Reset pre-filter state after redo
            self.pre_filter_image = None
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
                
                # Reset pre-filter state
                self.pre_filter_image = None
                
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