"""
Additional regression-focused tests for ImageModificationPage.

Covers:
1) stale preview state around apply_adjustments
2) reset_to_original Yes/No branches
3) resize behavior across all interpolation modes
4) filter branch coverage and non-stacking behavior
"""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageFilter

import Image_Modification_Page as modification_module
from Image_Modification_Page import ImageModificationPage


def _assert_images_close(a: Image.Image, b: Image.Image, *, max_abs_diff: int = 0):
    assert a.size == b.size
    assert a.mode == b.mode

    aa = np.asarray(a)
    bb = np.asarray(b)

    if max_abs_diff == 0:
        assert np.array_equal(aa, bb)
    else:
        diff = np.abs(aa.astype(np.int16) - bb.astype(np.int16))
        assert int(diff.max()) <= max_abs_diff


def _create_pattern_png(tmp_path: Path) -> Path:
    """Create a non-uniform image so all operations produce observable changes."""
    img_path = tmp_path / "pattern_for_additional_tests.png"
    arr = np.zeros((32, 32, 3), dtype=np.uint8)
    arr[..., 0] = np.arange(32, dtype=np.uint8)[None, :] * 8
    arr[..., 1] = np.arange(32, dtype=np.uint8)[:, None] * 8
    arr[::2, ::2, 2] = 255
    Image.fromarray(arr, mode="RGB").save(img_path)
    return img_path


def _apply_expected_custom_filter(base: Image.Image, filter_name: str, page: ImageModificationPage) -> Image.Image:
    """Mirror the production filter logic so we can assert exact output per branch."""
    if filter_name == "Box Blur":
        return base.filter(ImageFilter.BoxBlur(page.box_blur_spin.value()))

    if filter_name == "Gaussian Blur":
        return base.filter(ImageFilter.GaussianBlur(page.gaussian_blur_spin.value()))

    if filter_name == "Sharpen":
        factor = page.sharpen_spin.value()
        out = base.copy()
        for _ in range(int(factor)):
            out = out.filter(ImageFilter.SHARPEN)
        if factor % 1.0 > 0:
            temp = out.filter(ImageFilter.SHARPEN)
            out = Image.blend(out, temp, factor % 1.0)
        return out

    if filter_name == "Edge Enhance":
        factor = page.edge_spin.value()
        out = base.copy()
        for _ in range(int(factor)):
            out = out.filter(ImageFilter.EDGE_ENHANCE)
        if factor % 1.0 > 0:
            temp = out.filter(ImageFilter.EDGE_ENHANCE)
            out = Image.blend(out, temp, factor % 1.0)
        return out

    if filter_name == "Emboss":
        return base.filter(ImageFilter.EMBOSS)

    if filter_name == "Contour":
        return base.filter(ImageFilter.CONTOUR)

    if filter_name == "Smooth":
        return base.filter(ImageFilter.SMOOTH)

    if filter_name == "Find Edges":
        return base.filter(ImageFilter.FIND_EDGES)

    raise ValueError(f"Unexpected filter name: {filter_name}")


@pytest.fixture
def page(qtbot):
    w = ImageModificationPage()
    qtbot.addWidget(w)
    w.show()
    return w


def test_apply_adjustments_ignores_stale_preview_after_rotate(page, tmp_path: Path):
    # Build a pending preview state.
    image_path = _create_pattern_png(tmp_path)
    page.load_image(str(image_path))
    page.brightness_slider.setValue(130)
    page.update_preview()
    assert page.modified_image is not None

    # Perform a permanent operation afterwards.
    page.rotate_image(90)
    rotated = page.get_modified_image().copy()
    history_len_after_rotate = len(page.history)

    # Applying adjustments now should not overwrite with an old preview from pre-rotate state.
    page.apply_adjustments()

    _assert_images_close(page.get_modified_image(), rotated)
    assert len(page.history) == history_len_after_rotate


def test_reset_to_original_respects_confirmation_and_resets_state(page, tmp_path: Path, monkeypatch):
    image_path = _create_pattern_png(tmp_path)
    page.load_image(str(image_path))

    # Create a modified state first.
    page.rotate_image(90)
    modified = page.get_modified_image().copy()
    assert page.history_index == 1

    # If user chooses No, nothing should change.
    monkeypatch.setattr(
        modification_module.QMessageBox,
        "question",
        lambda *args, **kwargs: modification_module.QMessageBox.StandardButton.No,
    )
    page.reset_to_original()
    _assert_images_close(page.get_modified_image(), modified)
    assert page.history_index == 1

    # If user chooses Yes, image and state should be fully reset.
    monkeypatch.setattr(
        modification_module.QMessageBox,
        "question",
        lambda *args, **kwargs: modification_module.QMessageBox.StandardButton.Yes,
    )
    page.reset_to_original()

    _assert_images_close(page.get_modified_image(), page.original_image)
    assert len(page.history) == 1
    assert page.history_index == 0
    assert page.brightness_slider.value() == 100
    assert page.contrast_slider.value() == 100
    assert page.sharpness_slider.value() == 100
    assert page.pre_filter_image is None


def test_resize_all_interpolation_modes_match_pil_and_support_undo_redo(page, tmp_path: Path):
    image_path = _create_pattern_png(tmp_path)

    interpolation_map = {
        "Lanczos": Image.Resampling.LANCZOS,
        "Bicubic": Image.Resampling.BICUBIC,
        "Bilinear": Image.Resampling.BILINEAR,
        "Nearest": Image.Resampling.NEAREST,
    }

    for method_name, resampling in interpolation_map.items():
        # Reload every iteration to keep each interpolation check independent.
        page.load_image(str(image_path))
        base = page.original_image.copy()

        new_size = (base.size[0] + 11, base.size[1] + 7)
        page.width_spin.setValue(new_size[0])
        page.height_spin.setValue(new_size[1])
        page.interpolation_combo.setCurrentText(method_name)

        page.resize_image()

        expected = base.resize(new_size, resampling)
        _assert_images_close(page.get_modified_image(), expected)
        assert page.get_modified_image().size == new_size
        assert len(page.history) == 2
        assert page.history_index == 1
        assert page.pre_filter_image is None

        # Verify history integration of resize state transitions.
        page.undo()
        assert page.get_modified_image().size == base.size
        page.redo()
        assert page.get_modified_image().size == new_size


def test_all_filter_branches_apply_from_prefilter_base_and_match_expected(page, tmp_path: Path):
    image_path = _create_pattern_png(tmp_path)

    filters = [
        "Box Blur",
        "Gaussian Blur",
        "Sharpen",
        "Edge Enhance",
        "Emboss",
        "Contour",
        "Smooth",
        "Find Edges",
    ]

    for name in filters:
        # Reload each time so assertions are isolated to one filter branch.
        page.load_image(str(image_path))
        base = page.original_image.copy()

        # Use non-default values for parameterized filters to exercise parameter paths.
        if name == "Box Blur":
            page.box_blur_spin.setValue(3)
        elif name == "Gaussian Blur":
            page.gaussian_blur_spin.setValue(4)
        elif name == "Sharpen":
            page.sharpen_spin.setValue(2.3)
        elif name == "Edge Enhance":
            page.edge_spin.setValue(2.4)

        page.filter_combo.setCurrentText(name)
        page.apply_filter()

        first_result = page.get_modified_image().copy()
        _assert_images_close(page.pre_filter_image, base)

        expected_first = _apply_expected_custom_filter(base, name, page)
        _assert_images_close(first_result, expected_first, max_abs_diff=1)

        # Apply the same filter again with a changed parameter (when available).
        # Result should still be computed from pre_filter_image, not stacked result.
        if name == "Box Blur":
            page.box_blur_spin.setValue(6)
        elif name == "Gaussian Blur":
            page.gaussian_blur_spin.setValue(2)
        elif name == "Sharpen":
            page.sharpen_spin.setValue(1.7)
        elif name == "Edge Enhance":
            page.edge_spin.setValue(3.1)

        page.apply_filter()
        second_result = page.get_modified_image().copy()

        _assert_images_close(page.pre_filter_image, base)
        expected_second = _apply_expected_custom_filter(base, name, page)
        _assert_images_close(second_result, expected_second, max_abs_diff=1)
