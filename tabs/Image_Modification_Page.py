"""
Image Modification Page
Image editing with multi-image navigation, filter parameters, and aspect-ratio lock.
"""

import sys
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QSlider, QGroupBox, QGridLayout,
                               QFileDialog, QMessageBox, QSpinBox, QComboBox,
                               QCheckBox, QStackedWidget, QScrollArea, QDialog,
                               QTextBrowser, QDialogButtonBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np


class ImageModificationPage(QWidget):
    """
    Image modification page supporting multiple images, filter parameters,
    aspect-ratio-locked resizing, and Apply-to-All batch editing.
    """

    def __init__(self, image_path=None, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_image = None
        self.current_image = None
        self.modified_image = None

        self.max_display_size = (800, 600)
        self.history = []
        self.history_index = -1

        self.pre_filter_image = None
        self.active_filter = None
        self.adjustment_base = None
        self.pre_filter_adjustment_base = None

        # Multi-image support
        self.image_paths = []
        self.current_index = 0
        self.image_states = {}       # path -> saved state dict

        # Operation log for Apply-to-All (records committed operations)
        self._applied_ops = []

        # Guard against recursive spinbox updates (aspect ratio lock)
        self._updating_spinbox = False

        self.init_ui()

        if image_path:
            self.set_images([image_path])

    # ------------------------------------------------------------------ #
    # Help dialogs
    # ------------------------------------------------------------------ #

    def _make_help_btn(self, title, html):
        """Return a small '?' button that opens a help dialog when clicked."""
        btn = QPushButton("?")
        btn.setFixedSize(22, 22)
        btn.setStyleSheet(
            "QPushButton { border: 1px solid #aaa; border-radius: 11px;"
            " font-weight: bold; color: #555; background: #f0f0f0; }"
            " QPushButton:hover { background: #dde; color: #000; }"
        )
        btn.setToolTip("Show help")
        btn.clicked.connect(lambda: self._show_help_dialog(title, html))
        return btn

    def _show_help_dialog(self, title, html):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(520, 420)
        layout = QVBoxLayout(dlg)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setHtml(html)
        browser.setStyleSheet("font-size: 13px; padding: 6px;")
        layout.addWidget(browser)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btns.rejected.connect(dlg.accept)
        layout.addWidget(btns)
        dlg.exec()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Left panel inside a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedWidth(310)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: white; }
            QScrollArea > QWidget > QWidget { background-color: white; }
        """)

        controls_widget = QWidget()
        controls_widget.setStyleSheet("background-color: white; color: black;")
        cl = QVBoxLayout(controls_widget)
        cl.setAlignment(Qt.AlignmentFlag.AlignTop)
        cl.setSpacing(6)

        cl.addWidget(self.create_navigation_group())

        self.info_label = QLabel("No image loaded")
        self.info_label.setStyleSheet("font-size: 14px; padding: 10px;")
        cl.addWidget(self.info_label)

        cl.addWidget(self.create_file_group())
        cl.addWidget(self.create_transform_group())
        cl.addWidget(self.create_adjustments_group())
        cl.addWidget(self.create_filters_group())
        cl.addWidget(self.create_resize_group())
        cl.addWidget(self.create_history_group())
        cl.addStretch()

        scroll.setWidget(controls_widget)

        # Right panel — image display
        image_layout = QVBoxLayout()

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

        main_layout.addWidget(scroll)
        main_layout.addLayout(image_layout, 1)

    _APPLY_ALL_HELP = """
        <h3>Apply Edits to All Images</h3>
        <p>This button replays every <b>committed</b> operation from the current image
        onto all other images in the session, starting from each image's original.</p>
        <p><b>What counts as a committed operation?</b></p>
        <ul>
          <li>Clicking <i>Apply Adjustments</i> (brightness / contrast / sharpness)</li>
          <li>Clicking <i>Apply Filter</i></li>
          <li>Rotate Left / Rotate Right</li>
          <li>Flip Horizontal / Flip Vertical</li>
          <li>Resize Image</li>
        </ul>
        <p>Moving a slider without clicking <i>Apply Adjustments</i> is a live preview
        only and is <b>not</b> recorded.</p>
        <p>After applying, navigate to each image to review and save individually.</p>
    """

    def create_navigation_group(self):
        group = QGroupBox("Image Navigation")
        layout = QVBoxLayout()
        layout.setSpacing(6)

        nav_row = QHBoxLayout()

        self.prev_img_btn = QPushButton("← Prev")
        self.prev_img_btn.clicked.connect(self.show_previous_image)
        self.prev_img_btn.setEnabled(False)

        self.nav_label = QLabel("No images")
        self.nav_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.nav_label.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.next_img_btn = QPushButton("Next →")
        self.next_img_btn.clicked.connect(self.show_next_image)
        self.next_img_btn.setEnabled(False)

        nav_row.addWidget(self.prev_img_btn)
        nav_row.addWidget(self.nav_label, 1)
        nav_row.addWidget(self.next_img_btn)
        layout.addLayout(nav_row)

        apply_row = QHBoxLayout()
        self.apply_all_btn = QPushButton("Apply Edits to All Images")
        self.apply_all_btn.clicked.connect(self.apply_to_all)
        self.apply_all_btn.setStyleSheet(
            "padding: 7px; background-color: #9c27b0; color: white; font-size: 12px;"
        )
        self.apply_all_btn.setEnabled(False)
        apply_row.addWidget(self.apply_all_btn)
        apply_row.addWidget(self._make_help_btn("Apply to All", self._APPLY_ALL_HELP))
        layout.addLayout(apply_row)

        group.setLayout(layout)
        return group

    def create_file_group(self):
        group = QGroupBox("File Operations")
        layout = QVBoxLayout()

        save_btn = QPushButton("Save Image(s)")
        save_btn.clicked.connect(self.save_image)
        save_btn.setStyleSheet("padding: 8px; font-size: 12px;")
        layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset to Original")
        reset_btn.clicked.connect(self.reset_to_original)
        reset_btn.setStyleSheet(
            "padding: 8px; font-size: 12px; background-color: #ff9800; color: white;"
        )
        layout.addWidget(reset_btn)

        group.setLayout(layout)
        return group

    _TRANSFORM_HELP = """
        <h3>Transform</h3>
        <ul>
          <li><b>Rotate Left / Right</b> — Rotates the image 90 degrees.
              The canvas expands to fit the rotated result so no content is clipped.</li>
          <li><b>Flip Horizontal</b> — Mirrors the image left-to-right.</li>
          <li><b>Flip Vertical</b> — Mirrors the image top-to-bottom.</li>
        </ul>
        <p>Each transform is committed immediately and added to the operation log
        (used by <i>Apply Edits to All Images</i>).</p>
    """

    def create_transform_group(self):
        group = QGroupBox("Transform")
        layout = QGridLayout()

        help_row = QHBoxLayout()
        help_row.addStretch()
        help_row.addWidget(self._make_help_btn("Transform", self._TRANSFORM_HELP))
        layout.addLayout(help_row, 0, 0, 1, 2)

        rotate_left_btn = QPushButton("↶ Rotate Left")
        rotate_left_btn.clicked.connect(lambda: self.rotate_image(-90))
        layout.addWidget(rotate_left_btn, 1, 0)

        rotate_right_btn = QPushButton("↷ Rotate Right")
        rotate_right_btn.clicked.connect(lambda: self.rotate_image(90))
        layout.addWidget(rotate_right_btn, 1, 1)

        flip_h_btn = QPushButton("⇄ Flip Horizontal")
        flip_h_btn.clicked.connect(self.flip_horizontal)
        layout.addWidget(flip_h_btn, 2, 0)

        flip_v_btn = QPushButton("⇅ Flip Vertical")
        flip_v_btn.clicked.connect(self.flip_vertical)
        layout.addWidget(flip_v_btn, 2, 1)

        group.setLayout(layout)
        return group

    _ADJUSTMENTS_HELP = """
        <h3>Brightness / Contrast / Sharpness</h3>
        <p>All sliders range from <b>0 to 2</b>, with <b>1.0 (center) = original image</b>.</p>
        <ul>
          <li><b>Brightness</b> — Scales overall pixel luminance.
              0 = completely black, 1 = unchanged, 2 = twice as bright.</li>
          <li><b>Contrast</b> — Controls the difference between dark and light regions.
              0 = flat solid grey, 1 = unchanged, 2 = high contrast.</li>
          <li><b>Sharpness</b> — Adjusts edge definition.
              0 = fully blurred, 1 = unchanged, 2 = strongly sharpened.</li>
        </ul>
        <p>Moving a slider shows a <b>live preview</b> without changing the image.
        Click <i>Apply Adjustments</i> to commit the changes permanently.
        The sliders stay in place after applying — moving any slider back to 1.0
        always returns to the base image.</p>
    """

    def create_adjustments_group(self):
        group = QGroupBox("Adjustments")
        layout = QVBoxLayout()

        help_row = QHBoxLayout()
        help_row.addStretch()
        help_row.addWidget(self._make_help_btn("Adjustments", self._ADJUSTMENTS_HELP))
        layout.addLayout(help_row)

        def add_slider(label_text, top_pad="5px"):
            lbl = QLabel(label_text)
            lbl.setStyleSheet(
                f"font-weight: bold; font-size: 13px; color: #2c3e50;"
                f" padding: {top_pad} 0px 2px 0px;"
            )
            layout.addWidget(lbl)
            row = QHBoxLayout()
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(200)
            slider.setValue(100)
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(25)
            val_lbl = QLabel("1.0")
            val_lbl.setMinimumWidth(35)
            row.addWidget(slider)
            row.addWidget(val_lbl)
            layout.addLayout(row)
            return slider, val_lbl

        self.brightness_slider, self.brightness_value = add_slider("Brightness:")
        self.contrast_slider, self.contrast_value = add_slider("Contrast:", "8px")
        self.sharpness_slider, self.sharpness_value = add_slider("Sharpness:", "8px")

        for s in (self.brightness_slider, self.contrast_slider, self.sharpness_slider):
            s.valueChanged.connect(self.update_preview)

        apply_btn = QPushButton("Apply Adjustments")
        apply_btn.clicked.connect(self.apply_adjustments)
        apply_btn.setStyleSheet("padding: 8px; background-color: #4CAF50; color: white;")
        layout.addWidget(apply_btn)

        group.setLayout(layout)
        return group

    _FILTERS_HELP = """
        <h3>Filters</h3>
        <p>Filters are <b>non-stacking</b>: switching to a different filter always
        re-applies to the pre-filter image, so filters never pile on top of each other.
        Select <i>None</i> to remove the current filter.</p>

        <h4>Blur</h4>
        <ul>
          <li><b>Gaussian Blur</b> — Smooth, natural-looking blur using a Gaussian kernel.
              <i>Radius</i>: area of influence (higher = softer).</li>
          <li><b>Box Blur</b> — Simple average blur, slightly less smooth than Gaussian.
              <i>Radius</i>: neighbourhood size.</li>
          <li><b>Blur</b> — Fixed lightweight blur with no parameters.</li>
          <li><b>Motion Blur</b> — Horizontal streak effect simulating camera motion.
              <i>Kernel Size</i>: length of the blur trail (must be odd).</li>
          <li><b>Median</b> — Reduces noise while preserving edges by replacing each pixel
              with the median of its neighbours.
              <i>Size</i>: neighbourhood size (must be odd).</li>
        </ul>

        <h4>Sharpening</h4>
        <ul>
          <li><b>Sharpen</b> — Increases edge contrast using a fixed kernel.</li>
          <li><b>Unsharp Mask</b> — Precise sharpening.
              <i>Radius</i>: area, <i>Percent</i>: strength (higher = more sharpening),
              <i>Threshold</i>: minimum edge contrast to sharpen (higher = fewer edges affected).</li>
        </ul>

        <h4>Edge &amp; Texture</h4>
        <ul>
          <li><b>Edge Enhance / Edge Enhance More</b> — Subtly or strongly highlights edges.</li>
          <li><b>Find Edges</b> — Detects all edges, outputs them on a black background.</li>
          <li><b>Emboss</b> — Gives a 3-D raised or sunken relief appearance.</li>
          <li><b>Contour</b> — Traces the boundaries of distinct regions.</li>
        </ul>

        <h4>Smoothing &amp; Detail</h4>
        <ul>
          <li><b>Detail</b> — Enhances fine texture detail.</li>
          <li><b>Smooth / Smooth More</b> — Reduces fine-grained noise while preserving
              larger structures.</li>
        </ul>
    """

    def create_filters_group(self):
        group = QGroupBox("Filters")
        layout = QVBoxLayout()
        layout.setSpacing(6)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "None", "Gaussian Blur", "Box Blur", "Motion Blur", "Median",
            "Blur", "Sharpen", "Unsharp Mask", "Edge Enhance", "Edge Enhance More",
            "Find Edges", "Emboss", "Contour", "Detail", "Smooth", "Smooth More",
        ])
        self.filter_combo.currentTextChanged.connect(self._update_filter_params_ui)
        filter_row.addWidget(self.filter_combo)
        filter_row.addWidget(self._make_help_btn("Filters", self._FILTERS_HELP))
        layout.addLayout(filter_row)

        # Filter parameter panels (shown only for filters that have params)
        self.filter_params_stack = QStackedWidget()
        self.filter_params_stack.setFixedHeight(0)   # hidden until a param filter is chosen

        # Page 0 — no params
        self.filter_params_stack.addWidget(QWidget())

        # Page 1 — radius  (Gaussian Blur, Box Blur)
        p1 = QWidget()
        p1l = QHBoxLayout(p1)
        p1l.setContentsMargins(0, 4, 0, 4)
        p1l.addWidget(QLabel("Radius:"))
        self.blur_radius_spin = QSpinBox()
        self.blur_radius_spin.setRange(1, 50)
        self.blur_radius_spin.setValue(2)
        p1l.addWidget(self.blur_radius_spin)
        p1l.addStretch()
        self.filter_params_stack.addWidget(p1)

        # Page 2 — kernel size  (Motion Blur)
        p2 = QWidget()
        p2l = QHBoxLayout(p2)
        p2l.setContentsMargins(0, 4, 0, 4)
        p2l.addWidget(QLabel("Kernel Size:"))
        self.motion_kernel_spin = QSpinBox()
        self.motion_kernel_spin.setRange(3, 99)
        self.motion_kernel_spin.setSingleStep(2)
        self.motion_kernel_spin.setValue(15)
        p2l.addWidget(self.motion_kernel_spin)
        p2l.addStretch()
        self.filter_params_stack.addWidget(p2)

        # Page 3 — size  (Median)
        p3 = QWidget()
        p3l = QHBoxLayout(p3)
        p3l.setContentsMargins(0, 4, 0, 4)
        p3l.addWidget(QLabel("Size (odd):"))
        self.median_size_spin = QSpinBox()
        self.median_size_spin.setRange(3, 21)
        self.median_size_spin.setSingleStep(2)
        self.median_size_spin.setValue(3)
        p3l.addWidget(self.median_size_spin)
        p3l.addStretch()
        self.filter_params_stack.addWidget(p3)

        # Page 4 — Unsharp Mask
        p4 = QWidget()
        p4l = QGridLayout(p4)
        p4l.setContentsMargins(0, 4, 0, 4)
        p4l.addWidget(QLabel("Radius:"), 0, 0)
        self.unsharp_radius_spin = QSpinBox()
        self.unsharp_radius_spin.setRange(1, 20)
        self.unsharp_radius_spin.setValue(2)
        p4l.addWidget(self.unsharp_radius_spin, 0, 1)
        p4l.addWidget(QLabel("Percent:"), 0, 2)
        self.unsharp_percent_spin = QSpinBox()
        self.unsharp_percent_spin.setRange(50, 500)
        self.unsharp_percent_spin.setSingleStep(10)
        self.unsharp_percent_spin.setValue(150)
        p4l.addWidget(self.unsharp_percent_spin, 0, 3)
        p4l.addWidget(QLabel("Threshold:"), 1, 0)
        self.unsharp_threshold_spin = QSpinBox()
        self.unsharp_threshold_spin.setRange(0, 10)
        self.unsharp_threshold_spin.setValue(3)
        p4l.addWidget(self.unsharp_threshold_spin, 1, 1)
        self.filter_params_stack.addWidget(p4)

        layout.addWidget(self.filter_params_stack)

        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.clicked.connect(self.apply_filter)
        apply_filter_btn.setStyleSheet(
            "padding: 8px; background-color: #2196F3; color: white;"
        )
        layout.addWidget(apply_filter_btn)

        group.setLayout(layout)
        return group

    def _update_filter_params_ui(self, filter_name):
        page_map = {
            "Gaussian Blur": 1, "Box Blur": 1,
            "Motion Blur": 2,
            "Median": 3,
            "Unsharp Mask": 4,
        }
        idx = page_map.get(filter_name, 0)
        self.filter_params_stack.setCurrentIndex(idx)
        self.filter_params_stack.setFixedHeight(0 if idx == 0 else 62)

    _RESIZE_HELP = """
        <h3>Resize</h3>
        <p>Enter the desired pixel dimensions and click <i>Resize Image</i>.</p>
        <h4>Lock aspect ratio</h4>
        <p>When checked, changing the width automatically updates the height (and
        vice versa) so the image keeps its <b>original proportions</b>.
        The ratio is always calculated from the <b>original loaded image</b>,
        not the current edited size — so it stays consistent even after cropping
        or prior resizes.</p>
        <p>Resize is committed immediately and added to the operation log.</p>
    """

    def create_resize_group(self):
        group = QGroupBox("Resize")
        layout = QVBoxLayout()

        help_row = QHBoxLayout()
        help_row.addStretch()
        help_row.addWidget(self._make_help_btn("Resize", self._RESIZE_HELP))
        layout.addLayout(help_row)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("W:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(800)
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("H:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(600)
        size_layout.addWidget(self.height_spin)
        layout.addLayout(size_layout)

        self.lock_ratio_check = QCheckBox("Lock aspect ratio")
        self.lock_ratio_check.setToolTip(
            "Automatically adjust the other dimension to preserve the original proportions"
        )
        layout.addWidget(self.lock_ratio_check)

        self.width_spin.valueChanged.connect(self._on_width_changed)
        self.height_spin.valueChanged.connect(self._on_height_changed)

        resize_btn = QPushButton("Resize Image")
        resize_btn.clicked.connect(self.resize_image)
        resize_btn.setStyleSheet("padding: 8px;")
        layout.addWidget(resize_btn)

        group.setLayout(layout)
        return group

    def create_history_group(self):
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

    # ------------------------------------------------------------------ #
    # Multi-image navigation
    # ------------------------------------------------------------------ #

    def set_images(self, paths, start_index=0):
        """Load a list of image paths and navigate to start_index."""
        self.image_paths = list(paths)
        self.image_states = {}
        idx = min(start_index, len(paths) - 1) if paths else 0
        self._navigate_to(idx)

    def show_previous_image(self):
        self._save_current_state()
        self._navigate_to(self.current_index - 1)

    def show_next_image(self):
        self._save_current_state()
        self._navigate_to(self.current_index + 1)

    def _navigate_to(self, index):
        if not self.image_paths or index < 0 or index >= len(self.image_paths):
            return
        self.current_index = index
        self._update_navigation_ui()
        path = self.image_paths[index]
        if path in self.image_states:
            self._restore_state(path)
        else:
            self.load_image(path)

    def _save_current_state(self):
        """Persist the editing state of the currently displayed image."""
        if not self.image_paths or self.current_image is None:
            return
        path = self.image_paths[self.current_index]
        self.image_states[path] = {
            'original_image': self.original_image.copy() if self.original_image else None,
            'current_image': self.current_image.copy(),
            'adjustment_base': self.adjustment_base.copy() if self.adjustment_base else None,
            'pre_filter_image': self.pre_filter_image.copy() if self.pre_filter_image else None,
            'pre_filter_adjustment_base': (
                self.pre_filter_adjustment_base.copy()
                if self.pre_filter_adjustment_base else None
            ),
            'active_filter': self.active_filter,
            'modified_image': self.modified_image.copy() if self.modified_image else None,
            'history': [h.copy() for h in self.history],
            'history_index': self.history_index,
            'brightness': self.brightness_slider.value(),
            'contrast': self.contrast_slider.value(),
            'sharpness': self.sharpness_slider.value(),
            'filter_name': self.filter_combo.currentText(),
            'applied_ops': list(self._applied_ops),
        }

    def _restore_state(self, path):
        """Restore a previously saved editing state."""
        s = self.image_states[path]
        self.image_path = path
        self.original_image = s['original_image']
        self.current_image = s['current_image']
        self.adjustment_base = s['adjustment_base']
        self.pre_filter_image = s['pre_filter_image']
        self.pre_filter_adjustment_base = s['pre_filter_adjustment_base']
        self.active_filter = s['active_filter']
        self.modified_image = s['modified_image']
        self.history = s['history']
        self.history_index = s['history_index']
        self._applied_ops = s['applied_ops']

        # Block all sliders together, set values, then unblock — this moves
        # the handles to the correct positions without firing intermediate previews.
        for slider in (self.brightness_slider, self.contrast_slider, self.sharpness_slider):
            slider.blockSignals(True)
        self.brightness_slider.setValue(s['brightness'])
        self.contrast_slider.setValue(s['contrast'])
        self.sharpness_slider.setValue(s['sharpness'])
        for slider in (self.brightness_slider, self.contrast_slider, self.sharpness_slider):
            slider.blockSignals(False)

        # Manually sync the value labels (blockSignals prevented update_preview from running)
        self.brightness_value.setText(f"{s['brightness'] / 100.0:.1f}")
        self.contrast_value.setText(f"{s['contrast'] / 100.0:.1f}")
        self.sharpness_value.setText(f"{s['sharpness'] / 100.0:.1f}")

        self.filter_combo.blockSignals(True)
        self.filter_combo.setCurrentText(s['filter_name'])
        self.filter_combo.blockSignals(False)

        if self.current_image:
            w, h = self.current_image.size
            self._updating_spinbox = True
            self.width_spin.setValue(w)
            self.height_spin.setValue(h)
            self._updating_spinbox = False

        # update_preview renders adjustment_base + current slider values, which
        # gives the correct display and keeps slider positions meaningful.
        self.update_preview()
        self.update_info()
        self.status_label.setText(f"Restored: {path.split('/')[-1]}")

    def _update_navigation_ui(self):
        total = len(self.image_paths)
        if total == 0:
            self.nav_label.setText("No images")
            self.prev_img_btn.setEnabled(False)
            self.next_img_btn.setEnabled(False)
            self.apply_all_btn.setEnabled(False)
        else:
            name = self.image_paths[self.current_index].split('/')[-1]
            self.nav_label.setText(f"{self.current_index + 1} / {total}  —  {name}")
            self.prev_img_btn.setEnabled(self.current_index > 0)
            self.next_img_btn.setEnabled(self.current_index < total - 1)
            self.apply_all_btn.setEnabled(total > 1)

    # ------------------------------------------------------------------ #
    # Apply to All
    # ------------------------------------------------------------------ #

    def apply_to_all(self):
        """Apply the current image's transforms and slider adjustments to all other images."""
        if len(self.image_paths) <= 1:
            self.status_label.setText("Only one image — nothing to apply to.")
            return

        # Transform ops (rotate/flip/filter/resize) must be committed via their buttons.
        # Slider adjustments use the CURRENT slider values so the user does not need
        # to click "Apply Adjustments" separately before clicking this button.
        transform_ops = [op for op in self._applied_ops if op[0] != "adjust"]
        b = self.brightness_slider.value() / 100.0
        c = self.contrast_slider.value() / 100.0
        s = self.sharpness_slider.value() / 100.0
        has_sliders = (b != 1.0 or c != 1.0 or s != 1.0)

        if not transform_ops and not has_sliders:
            self.status_label.setText(
                "No edits to apply. Rotate/flip/apply a filter, or move the adjustment sliders first."
            )
            return

        errors = []
        for i, path in enumerate(self.image_paths):
            if i == self.current_index:
                continue
            try:
                original = Image.open(path).convert('RGB')
                # Apply committed transforms, producing the pre-adjustment base.
                adj_base = self._replay_ops(original, transform_ops)
                # Apply current slider values on top to get the final result.
                result = adj_base.copy()
                if b != 1.0:
                    result = ImageEnhance.Brightness(result).enhance(b)
                if c != 1.0:
                    result = ImageEnhance.Contrast(result).enhance(c)
                if s != 1.0:
                    result = ImageEnhance.Sharpness(result).enhance(s)

                stored_ops = list(transform_ops)
                if has_sliders:
                    stored_ops.append(("adjust", b, c, s))

                self.image_states[path] = {
                    'original_image': original,
                    'current_image': result,
                    'adjustment_base': adj_base,
                    'pre_filter_image': None,
                    'pre_filter_adjustment_base': None,
                    'active_filter': None,
                    'modified_image': None,
                    'history': [result.copy()],
                    'history_index': 0,
                    'brightness': int(b * 100),
                    'contrast': int(c * 100),
                    'sharpness': int(s * 100),
                    'filter_name': 'None',
                    'applied_ops': stored_ops,
                }
            except Exception as e:
                errors.append(f"{path.split('/')[-1]}: {e}")

        if errors:
            self.status_label.setText(f"Errors on: {'; '.join(errors)}")
        else:
            count = len(self.image_paths) - 1
            self.status_label.setText(f"Applied edits to {count} other image(s).")

    def _replay_ops(self, img, ops):
        """Replay a list of recorded operations on a PIL image."""
        img = img.copy()
        for op in ops:
            kind = op[0]
            if kind == "rotate":
                img = img.rotate(-op[1], expand=True)
            elif kind == "flip_h":
                img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            elif kind == "flip_v":
                img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            elif kind == "filter":
                img = self._apply_pil_filter(img, op[1], op[2])
            elif kind == "adjust":
                b, c, s = op[1], op[2], op[3]
                if b != 1.0:
                    img = ImageEnhance.Brightness(img).enhance(b)
                if c != 1.0:
                    img = ImageEnhance.Contrast(img).enhance(c)
                if s != 1.0:
                    img = ImageEnhance.Sharpness(img).enhance(s)
            elif kind == "resize":
                img = img.resize((op[1], op[2]), Image.Resampling.LANCZOS)
        return img

    # ------------------------------------------------------------------ #
    # Image loading
    # ------------------------------------------------------------------ #

    def load_image(self, image_path):
        """Load a fresh image from disk."""
        try:
            self.image_path = image_path
            self.original_image = Image.open(image_path).convert('RGB')
            self.current_image = self.original_image.copy()
            self.adjustment_base = self.original_image.copy()
            self.pre_filter_adjustment_base = None
            self.pre_filter_image = None
            self.active_filter = None
            self.modified_image = None
            self._applied_ops = []

            self.history = [self.current_image.copy()]
            self.history_index = 0

            width, height = self.current_image.size
            self._updating_spinbox = True
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)
            self._updating_spinbox = False

            for slider in (self.brightness_slider, self.contrast_slider, self.sharpness_slider):
                slider.blockSignals(True)
                slider.setValue(100)
                slider.blockSignals(False)

            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText(f"Loaded: {image_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")

    # ------------------------------------------------------------------ #
    # Display helpers
    # ------------------------------------------------------------------ #

    def display_image(self, pil_image):
        img_array = np.array(pil_image)
        height, width, _ = img_array.shape
        bytes_per_line = 3 * width
        q_image = QImage(
            img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(q_image)
        max_size = QSize(self.max_display_size[0], self.max_display_size[1])
        scaled = pixmap.scaled(
            max_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)

    def update_info(self):
        if self.current_image:
            w, h = self.current_image.size
            self.info_label.setText(f"Size: {w}x{h} | Mode: {self.current_image.mode}")

    def add_to_history(self, image):
        self.history = self.history[:self.history_index + 1]
        self.history.append(image.copy())
        self.history_index += 1
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index -= 1

    # ------------------------------------------------------------------ #
    # Aspect-ratio lock helpers
    # ------------------------------------------------------------------ #

    def _original_aspect_ratio(self):
        if self.original_image:
            w, h = self.original_image.size
            return w / h if h else None
        return None

    def _on_width_changed(self, value):
        if self._updating_spinbox:
            return
        if self.lock_ratio_check.isChecked():
            ratio = self._original_aspect_ratio()
            if ratio:
                self._updating_spinbox = True
                self.height_spin.setValue(max(1, round(value / ratio)))
                self._updating_spinbox = False

    def _on_height_changed(self, value):
        if self._updating_spinbox:
            return
        if self.lock_ratio_check.isChecked():
            ratio = self._original_aspect_ratio()
            if ratio:
                self._updating_spinbox = True
                self.width_spin.setValue(max(1, round(value * ratio)))
                self._updating_spinbox = False

    # ------------------------------------------------------------------ #
    # Transform operations
    # ------------------------------------------------------------------ #

    def rotate_image(self, degrees):
        if self.current_image is None:
            return
        try:
            self.current_image = self.current_image.rotate(-degrees, expand=True)
            self.adjustment_base = self.adjustment_base.rotate(-degrees, expand=True)
            self.add_to_history(self.current_image)
            self._applied_ops.append(("rotate", degrees))
            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText(f"Rotated {degrees}°")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rotate: {str(e)}")

    def flip_horizontal(self):
        if self.current_image is None:
            return
        try:
            self.current_image = self.current_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            self.adjustment_base = self.adjustment_base.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            self.add_to_history(self.current_image)
            self._applied_ops.append(("flip_h",))
            self.display_image(self.current_image)
            self.status_label.setText("Flipped horizontally")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to flip: {str(e)}")

    def flip_vertical(self):
        if self.current_image is None:
            return
        try:
            self.current_image = self.current_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            self.adjustment_base = self.adjustment_base.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            self.add_to_history(self.current_image)
            self._applied_ops.append(("flip_v",))
            self.display_image(self.current_image)
            self.status_label.setText("Flipped vertically")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to flip: {str(e)}")

    # ------------------------------------------------------------------ #
    # Adjustment sliders
    # ------------------------------------------------------------------ #

    def update_preview(self):
        """Live preview — always computes from adjustment_base so middle = base photo."""
        if self.current_image is None or self.adjustment_base is None:
            return

        b = self.brightness_slider.value() / 100.0
        c = self.contrast_slider.value() / 100.0
        s = self.sharpness_slider.value() / 100.0

        self.brightness_value.setText(f"{b:.1f}")
        self.contrast_value.setText(f"{c:.1f}")
        self.sharpness_value.setText(f"{s:.1f}")

        try:
            preview = self.adjustment_base.copy()
            if b != 1.0:
                preview = ImageEnhance.Brightness(preview).enhance(b)
            if c != 1.0:
                preview = ImageEnhance.Contrast(preview).enhance(c)
            if s != 1.0:
                preview = ImageEnhance.Sharpness(preview).enhance(s)
            self.display_image(preview)
            self.modified_image = preview
        except Exception as e:
            self.status_label.setText(f"Preview error: {str(e)}")

    def apply_adjustments(self):
        """Commit slider values to current_image. Sliders stay in place."""
        if self.modified_image:
            self.current_image = self.modified_image.copy()
            self.add_to_history(self.current_image)
            b = self.brightness_slider.value() / 100.0
            c = self.contrast_slider.value() / 100.0
            s = self.sharpness_slider.value() / 100.0
            self._applied_ops.append(("adjust", b, c, s))
            self.status_label.setText("Adjustments applied")
        else:
            self.status_label.setText("No adjustments to apply")

    # ------------------------------------------------------------------ #
    # Filters
    # ------------------------------------------------------------------ #

    def _get_current_filter_params(self, filter_name=None):
        if filter_name is None:
            filter_name = self.filter_combo.currentText()
        if filter_name in ("Gaussian Blur", "Box Blur"):
            return {"radius": self.blur_radius_spin.value()}
        if filter_name == "Motion Blur":
            return {"kernel_size": self.motion_kernel_spin.value()}
        if filter_name == "Median":
            return {"size": self.median_size_spin.value()}
        if filter_name == "Unsharp Mask":
            return {
                "radius": self.unsharp_radius_spin.value(),
                "percent": self.unsharp_percent_spin.value(),
                "threshold": self.unsharp_threshold_spin.value(),
            }
        return {}

    def _apply_pil_filter(self, image, filter_name, params=None):
        if params is None:
            params = self._get_current_filter_params(filter_name)
        filtered = image.copy()
        if filter_name == "Gaussian Blur":
            filtered = filtered.filter(ImageFilter.GaussianBlur(radius=params.get("radius", 2)))
        elif filter_name == "Box Blur":
            filtered = filtered.filter(ImageFilter.BoxBlur(radius=params.get("radius", 2)))
        elif filter_name == "Motion Blur":
            arr = np.array(filtered, dtype=np.float32)
            ks = params.get("kernel_size", 15)
            kernel = np.ones(ks) / ks
            for ch in range(arr.shape[2]):
                for row in range(arr.shape[0]):
                    arr[row, :, ch] = np.convolve(arr[row, :, ch], kernel, mode='same')
            filtered = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
        elif filter_name == "Median":
            filtered = filtered.filter(ImageFilter.MedianFilter(size=params.get("size", 3)))
        elif filter_name == "Blur":
            filtered = filtered.filter(ImageFilter.BLUR)
        elif filter_name == "Sharpen":
            filtered = filtered.filter(ImageFilter.SHARPEN)
        elif filter_name == "Unsharp Mask":
            filtered = filtered.filter(ImageFilter.UnsharpMask(
                radius=params.get("radius", 2),
                percent=params.get("percent", 150),
                threshold=params.get("threshold", 3),
            ))
        elif filter_name == "Edge Enhance":
            filtered = filtered.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_name == "Edge Enhance More":
            filtered = filtered.filter(ImageFilter.EDGE_ENHANCE_MORE)
        elif filter_name == "Find Edges":
            filtered = filtered.filter(ImageFilter.FIND_EDGES)
        elif filter_name == "Emboss":
            filtered = filtered.filter(ImageFilter.EMBOSS)
        elif filter_name == "Contour":
            filtered = filtered.filter(ImageFilter.CONTOUR)
        elif filter_name == "Detail":
            filtered = filtered.filter(ImageFilter.DETAIL)
        elif filter_name == "Smooth":
            filtered = filtered.filter(ImageFilter.SMOOTH)
        elif filter_name == "Smooth More":
            filtered = filtered.filter(ImageFilter.SMOOTH_MORE)
        return filtered

    def apply_filter(self):
        """Apply selected filter (non-stacking — always applies from the pre-filter base)."""
        if self.current_image is None:
            return

        filter_name = self.filter_combo.currentText()

        if filter_name == "None":
            if self.pre_filter_image is not None:
                self.current_image = self.pre_filter_image.copy()
                self.pre_filter_image = None
                if self.pre_filter_adjustment_base is not None:
                    self.adjustment_base = self.pre_filter_adjustment_base.copy()
                    self.pre_filter_adjustment_base = None
                self.active_filter = None
                self.add_to_history(self.current_image)
                self.display_image(self.current_image)
                self.status_label.setText("Filter removed")
            else:
                self.status_label.setText("No filter to remove")
            return

        try:
            if self.pre_filter_image is None:
                self.pre_filter_image = self.current_image.copy()
            if self.pre_filter_adjustment_base is None:
                self.pre_filter_adjustment_base = self.adjustment_base.copy()

            params = self._get_current_filter_params(filter_name)
            self.current_image = self._apply_pil_filter(self.pre_filter_image, filter_name, params)
            self.adjustment_base = self._apply_pil_filter(
                self.pre_filter_adjustment_base, filter_name, params
            )
            self.active_filter = filter_name
            self.add_to_history(self.current_image)
            self._applied_ops.append(("filter", filter_name, params))
            self.display_image(self.current_image)
            self.status_label.setText(f"Applied {filter_name} filter")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply filter: {str(e)}")

    # ------------------------------------------------------------------ #
    # Resize
    # ------------------------------------------------------------------ #

    def resize_image(self):
        if self.current_image is None:
            return
        try:
            new_w = self.width_spin.value()
            new_h = self.height_spin.value()
            self.current_image = self.current_image.resize(
                (new_w, new_h), Image.Resampling.LANCZOS
            )
            self.adjustment_base = self.adjustment_base.resize(
                (new_w, new_h), Image.Resampling.LANCZOS
            )
            self.add_to_history(self.current_image)
            self._applied_ops.append(("resize", new_w, new_h))
            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText(f"Resized to {new_w}x{new_h}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to resize: {str(e)}")

    # ------------------------------------------------------------------ #
    # History — undo / redo
    # ------------------------------------------------------------------ #

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.adjustment_base = self.current_image.copy()
            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText("Undo")
        else:
            self.status_label.setText("Nothing to undo")

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.adjustment_base = self.current_image.copy()
            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText("Redo")
        else:
            self.status_label.setText("Nothing to redo")

    # ------------------------------------------------------------------ #
    # Reset & Save
    # ------------------------------------------------------------------ #

    def reset_to_original(self):
        if not self.original_image:
            return
        reply = QMessageBox.question(
            self, "Reset Image",
            "Reset to the original image? All edits will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.current_image = self.original_image.copy()
            self.adjustment_base = self.original_image.copy()
            self.pre_filter_adjustment_base = None
            self.pre_filter_image = None
            self.active_filter = None
            self.modified_image = None
            self._applied_ops = []
            self.history = [self.current_image.copy()]
            self.history_index = 0

            for slider in (self.brightness_slider, self.contrast_slider, self.sharpness_slider):
                slider.setValue(100)

            w, h = self.current_image.size
            self._updating_spinbox = True
            self.width_spin.setValue(w)
            self.height_spin.setValue(h)
            self._updating_spinbox = False

            self.display_image(self.current_image)
            self.update_info()
            self.status_label.setText("Reset to original")

    def save_image(self):
        if self.current_image is None:
            QMessageBox.warning(self, "No Image", "No image to save")
            return

        # Count how many images have been modified (current + others in image_states)
        other_modified = [
            p for p in self.image_paths
            if p != self.image_paths[self.current_index] and p in self.image_states
        ]

        if not other_modified:
            # Only one image in play — use the simple single-file save dialog
            self._save_single()
            return

        # Multiple modified images — ask what to save
        box = QMessageBox(self)
        box.setWindowTitle("Save Image(s)")
        box.setText(
            f"You have {1 + len(other_modified)} modified image(s).\n"
            "What would you like to save?"
        )
        current_btn = box.addButton("Save current image only", QMessageBox.ActionRole)
        all_btn = box.addButton(
            f"Save all {1 + len(other_modified)} modified images to a folder",
            QMessageBox.ActionRole,
        )
        box.addButton("Cancel", QMessageBox.RejectRole)
        box.exec()
        clicked = box.clickedButton()

        if clicked is current_btn:
            self._save_single()
        elif clicked is all_btn:
            self._save_all(other_modified)

    def _save_single(self):
        """Save the currently displayed image via a file-save dialog."""
        img_to_save = self.modified_image if self.modified_image else self.current_image
        default_name = os.path.basename(self.image_path) if self.image_path else ""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", default_name,
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*.*)",
        )
        if file_path:
            try:
                img_to_save.save(file_path)
                self.status_label.setText(f"Saved: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")

    def _save_all(self, other_modified_paths):
        """Save all modified images (current + others) to a chosen folder."""
        folder = QFileDialog.getExistingDirectory(self, "Choose folder to save images")
        if not folder:
            return

        # First save the current image (include any uncommitted slider preview)
        # Then save each other modified image from its stored state.
        to_save = []

        # Current image
        img = self.modified_image if self.modified_image else self.current_image
        to_save.append((self.image_paths[self.current_index], img))

        # Other modified images
        for path in other_modified_paths:
            state = self.image_states[path]
            img = state['modified_image'] if state['modified_image'] else state['current_image']
            to_save.append((path, img))

        errors = []
        saved = []
        for src_path, img in to_save:
            filename = os.path.basename(src_path)
            dest = os.path.join(folder, filename)
            try:
                img.save(dest)
                saved.append(filename)
            except Exception as e:
                errors.append(f"{filename}: {e}")

        if errors:
            self.status_label.setText(f"Saved {len(saved)}, errors: {'; '.join(errors)}")
            QMessageBox.warning(
                self, "Partial Save",
                f"Saved {len(saved)} image(s).\nErrors:\n" + "\n".join(errors),
            )
        else:
            self.status_label.setText(f"Saved {len(saved)} image(s) to {folder}")
            QMessageBox.information(
                self, "Saved",
                f"Saved {len(saved)} image(s) to:\n{folder}",
            )

    def get_modified_image(self):
        return self.current_image


def main():
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
