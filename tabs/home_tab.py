"""
Home Tab - Multi-image upload, display and processing
Layout matches the original Home tab in image_processing_app.py:
- Left side: control panel (info + file operations + processing)
- Right side: large image display and status label
"""

import os
from typing import List, Optional

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QGroupBox, QFileDialog, QSizePolicy,
    QMessageBox
)
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt


class HomeTab(QWidget):
    """
    Home tab widget that supports:
      - Uploading multiple images via file dialog
      - Drag & drop of one or more image files
      - Asking whether to keep or replace previously loaded images
      - Navigating between images (previous / next)
      - Displaying the current image with basic info
      - Sending the current image to the Modification tab
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Reference to the main window (used to access modification_page, tab_widget)
        self.main_window = parent

        # Multi-image state
        self.image_paths: List[str] = []
        self.current_image_path: Optional[str] = None
        self.current_index: Optional[int] = None

        # Enable drag & drop on this widget
        self.setAcceptDrops(True)

        # Base style for the image label (used in several places)
        self.base_image_style = """
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #f5f5f5;
                min-width: 800px;
                min-height: 600px;
                color: #999999;
            }
        """

        self._setup_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        """Create the full Home tab layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ---------------- Left side: Controls ----------------
        controls_layout = QVBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        controls_layout.setSpacing(10)

        # Info label: shows current image name, size, resolution
        self.info_label = QLabel("No image loaded")
        self.info_label.setStyleSheet("font-size: 14px; padding: 10px;")
        self.info_label.setWordWrap(True)
        controls_layout.addWidget(self.info_label)

        # File operations group
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()

        self.upload_button = QPushButton("📁 Upload Images")
        self.upload_button.setStyleSheet("padding: 8px; font-size: 12px;")
        self.upload_button.clicked.connect(self.upload_images)
        file_layout.addWidget(self.upload_button)

        self.clear_button = QPushButton("🗑️ Clear All Images")
        self.clear_button.setStyleSheet("padding: 8px; font-size: 12px;")
        self.clear_button.clicked.connect(self.clear_images)
        file_layout.addWidget(self.clear_button)

        file_group.setLayout(file_layout)
        controls_layout.addWidget(file_group)

        # Navigation group (previous / next)
        nav_group = QGroupBox("Navigation")
        nav_layout = QHBoxLayout()

        self.prev_button = QPushButton("⬅ Previous")
        self.prev_button.setStyleSheet("padding: 6px; font-size: 11px;")
        self.prev_button.clicked.connect(self.show_previous_image)
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next ➡")
        self.next_button.setStyleSheet("padding: 6px; font-size: 11px;")
        self.next_button.clicked.connect(self.show_next_image)
        nav_layout.addWidget(self.next_button)

        nav_group.setLayout(nav_layout)
        controls_layout.addWidget(nav_group)

        # Processing group
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout()

        self.process_button = QPushButton("⚡ Process Current Image")
        self.process_button.setStyleSheet(
            "padding: 8px; font-size: 12px; background-color: #4CAF50; color: white;"
        )
        self.process_button.clicked.connect(self.process_images)
        process_layout.addWidget(self.process_button)

        process_group.setLayout(process_layout)
        controls_layout.addWidget(process_group)

        controls_layout.addStretch()

        # ---------------- Right side: Image + Status ----------------
        image_layout = QVBoxLayout()

        self.image_label = QLabel(
            "Drag & drop images here\nor click the upload button"
        )
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(self.base_image_style)
        self.image_label.setScaledContents(False)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_layout.addWidget(self.image_label)

        self.status_label = QLabel("Ready to process images (0 loaded)")
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
        self.status_label.setWordWrap(True)
        image_layout.addWidget(self.status_label)

        # ---------------- Add to main layout ----------------
        main_layout.addLayout(controls_layout, 1)
        main_layout.addLayout(image_layout, 3)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def is_image_file(self, file_path: str) -> bool:
        """Return True if the path points to a supported image file."""
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        return os.path.isfile(file_path) and file_path.lower().endswith(image_extensions)

    def _update_status_loaded(self, prefix: str = "Ready to process images") -> None:
        """Update the status label based on how many images are loaded."""
        count = len(self.image_paths)
        if count == 0 or self.current_index is None or self.current_image_path is None:
            self.status_label.setText(f"{prefix} (0 loaded)")
        else:
            idx = self.current_index + 1
            file_name = os.path.basename(self.current_image_path)
            self.status_label.setText(
                f"{prefix}: {file_name} | Image {idx}/{count} (total {count})"
            )

    def _show_image_at_index(self, index: int) -> None:
        """
        Display the image at a given index in self.image_paths.
        This updates current_index, current_image_path, the pixmap,
        info label and status label.
        """
        if not self.image_paths:
            return
        if index < 0 or index >= len(self.image_paths):
            return

        self.current_index = index
        self.current_image_path = self.image_paths[index]
        self.display_image(self.current_image_path)
        self._update_status_loaded()

    def _ask_how_to_handle_existing(self, new_paths: List[str]) -> Optional[List[str]]:
        """
        Ask the user whether to replace existing images or keep them and add the new ones.

        Returns the final combined list of image paths, or None if the user cancels.
        """
        if not self.image_paths:
            # No existing images, simply use the new ones
            return new_paths

        box = QMessageBox(self)
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle("Existing images detected")
        box.setText(
            f"You already have {len(self.image_paths)} image(s) loaded.\n"
            "How would you like to handle the new images?"
        )
        box.setInformativeText(
            "Yes: clear old images and only keep the new ones.\n"
            "No: keep old images and add the new ones.\n"
            "Cancel: do not change anything."
        )

        yes_button = box.addButton("Yes, replace old images", QMessageBox.YesRole)
        no_button = box.addButton("No, keep all images", QMessageBox.NoRole)
        cancel_button = box.addButton("Cancel", QMessageBox.RejectRole)

        box.exec()
        clicked = box.clickedButton()

        if clicked is cancel_button:
            # User canceled: do not modify the list
            self._update_status_loaded(prefix="Upload canceled")
            return None

        if clicked is yes_button:
            # Replace existing images
            return new_paths

        # Keep existing images and add new ones (avoid duplicates)
        combined = list(self.image_paths)
        for p in new_paths:
            if p not in combined:
                combined.append(p)
        return combined

    def _handle_new_images(self, new_paths: List[str]) -> None:
        """
        Handle a new set of image paths:
        - If there are already images loaded, ask the user what to do.
        - Then update the list and show the first new image.
        """
        if not new_paths:
            self.status_label.setText(
                "No valid image files selected (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP)."
            )
            return

        final_list = self._ask_how_to_handle_existing(new_paths)
        if final_list is None:
            # User canceled
            return

        self.image_paths = final_list

        # Pick the first newly added image to display
        first_new_index = 0
        if self.current_index is not None and self.image_paths:
            # When appending, we want to show the first of the new images
            # If we replaced, new images start at index 0 anyway
            for i, path in enumerate(self.image_paths):
                if path in new_paths:
                    first_new_index = i
                    break

        self._show_image_at_index(first_new_index)

    # ------------------------------------------------------------------
    # Upload / clear
    # ------------------------------------------------------------------
    def upload_images(self) -> None:
        """Open a file dialog to select and upload one or more images."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Image Files",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp);;All Files (*)"
        )

        if not file_paths:
            return

        valid_paths = [p for p in file_paths if self.is_image_file(p)]
        self._handle_new_images(valid_paths)

    def clear_images(self) -> None:
        """Clear all currently loaded images and reset the UI."""
        self.image_paths = []
        self.current_image_path = None
        self.current_index = None

        self.image_label.clear()
        self.image_label.setText(
            "Drag & drop images here\nor click the upload button"
        )
        self.image_label.setStyleSheet(self.base_image_style)

        self.info_label.setText("No image loaded")
        self._update_status_loaded()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def show_previous_image(self) -> None:
        """Show the previous image in the list, if available."""
        if not self.image_paths or self.current_index is None:
            self.status_label.setText("No images loaded.")
            return

        if self.current_index <= 0:
            self.status_label.setText("This is the first image.")
            return

        self._show_image_at_index(self.current_index - 1)

    def show_next_image(self) -> None:
        """Show the next image in the list, if available."""
        if not self.image_paths or self.current_index is None:
            self.status_label.setText("No images loaded.")
            return

        if self.current_index >= len(self.image_paths) - 1:
            self.status_label.setText("This is the last image.")
            return

        self._show_image_at_index(self.current_index + 1)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def display_image(self, file_path: str) -> None:
        """Display the given image file and update the info label."""
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                self.status_label.setText("Error: unable to load image file.")
                self.image_label.setText(
                    "Drag & drop images here\nor click the upload button"
                )
                self.image_label.setStyleSheet(self.base_image_style)
                return

            # Scale to fit the label while maintaining aspect ratio
            target_size = self.image_label.size()
            if target_size.width() <= 0 or target_size.height() <= 0:
                # Fallback size in case the widget was not laid out yet
                target_size = self.image_label.minimumSizeHint()

            scaled_pixmap = pixmap.scaled(
                target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)

            # Update info: file name, resolution, file size
            file_name = os.path.basename(file_path)
            img_width = pixmap.width()
            img_height = pixmap.height()
            try:
                file_size_kb = os.path.getsize(file_path) / 1024.0
                size_str = f"{file_size_kb:.1f} KB"
            except Exception:
                size_str = "Unknown size"

            self.info_label.setText(
                f"File: {file_name}\n"
                f"Resolution: {img_width} x {img_height}\n"
                f"File Size: {size_str}"
            )

        except Exception as e:
            self.status_label.setText(f"Error loading image: {e}")
            self.image_label.setText(
                "Drag & drop images here\nor click the upload button"
            )
            self.image_label.setStyleSheet(self.base_image_style)

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------
    def process_images(self) -> None:
        """
        Process the current image.
        Behavior matches the original ImageProcessingApp.process_image:
        - Load the current image into the Modification tab
        - Switch to the Modification tab
        """
        if not self.current_image_path:
            self.status_label.setText("Please upload at least one image first.")
            return

        file_name = os.path.basename(self.current_image_path)

        # Access the main window's modification_page if available
        if self.main_window is not None and hasattr(self.main_window, "modification_page"):
            try:
                self.main_window.modification_page.load_image(self.current_image_path)
                if hasattr(self.main_window, "tab_widget"):
                    self.main_window.tab_widget.setCurrentWidget(
                        self.main_window.modification_page
                    )
                self._update_status_loaded(
                    prefix=f"Loaded {file_name} in Modification tab"
                )
            except Exception as e:
                self.status_label.setText(f"Error processing image: {e}")
        else:
            self.status_label.setText(
                "Modification page is not available. Cannot process image."
            )

    # ------------------------------------------------------------------
    # Drag & drop (Qt events)
    # ------------------------------------------------------------------
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Accept the drag if any url is a valid image file."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if self.is_image_file(url.toLocalFile()):
                    event.acceptProposedAction()
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
                    self.image_label.setText("✓ Release to upload image(s)")
                    self.status_label.setText("Ready to drop image(s).")
                    return

    def dragLeaveEvent(self, event) -> None:
        """Reset the visual feedback when the drag leaves the widget."""
        self.image_label.setStyleSheet(self.base_image_style)
        if self.image_paths and self.current_image_path:
            # Keep whatever is currently displayed
            self._update_status_loaded()
        else:
            self.image_label.setText(
                "Drag & drop images here\nor click the upload button"
            )
            self._update_status_loaded()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle dropped files and load all valid images."""
        self.image_label.setStyleSheet(self.base_image_style)
        self.image_label.setText("Loading images...")

        valid_paths: List[str] = []

        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self.is_image_file(file_path):
                    valid_paths.append(file_path)

        self._handle_new_images(valid_paths)
