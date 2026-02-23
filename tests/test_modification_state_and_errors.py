"""
Purpose:
- Validate state correctness for edit history and filter workflow, not just happy-path output.
- Validate error-path robustness for load/save operations.

Method:
- Build a synthetic non-uniform image so transforms/filters produce observable pixel changes.
- Use pixel-level numpy assertions to verify exact image state transitions.
- Use monkeypatch to isolate dialog and I/O failures and assert safe behavior under exceptions.
"""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image
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
    """Create a non-uniform image so transform/filter behavior is easy to assert."""
    img_path = tmp_path / "pattern.png"
    arr = np.zeros((32, 32, 3), dtype=np.uint8)
    arr[..., 0] = np.arange(32, dtype=np.uint8)[None, :] * 8
    arr[..., 1] = np.arange(32, dtype=np.uint8)[:, None] * 8
    arr[::2, ::2, 2] = 255
    Image.fromarray(arr, mode="RGB").save(img_path)
    return img_path


@pytest.fixture
def page(qtbot):
    w = ImageModificationPage()
    qtbot.addWidget(w)
    w.show()
    return w


def test_history_undo_redo_branch_and_history_cap(page, tmp_path: Path):
    # Verify undo/redo branch behavior and 50-entry history cap.
    image_path = _create_pattern_png(tmp_path)
    page.load_image(str(image_path))
    original = page.original_image.copy()

    page.rotate_image(90)
    rotated = page.get_modified_image().copy()
    page.flip_horizontal()
    flipped = page.get_modified_image().copy()

    page.undo()
    _assert_images_close(page.get_modified_image(), rotated)

    # A new operation after undo should clear redo branch.
    page.rotate_image(-90)
    page.redo()
    assert page.status_label.text() == "Nothing to redo"
    assert not np.array_equal(np.asarray(page.get_modified_image()), np.asarray(flipped))

    # History should cap at 50 entries.
    for _ in range(60):
        page.rotate_image(90)
    assert len(page.history) == 50
    assert page.history_index == 49
    assert page.get_modified_image() is not None
    assert page.original_image is not None
    _assert_images_close(page.original_image, original)


def test_filter_none_reverts_to_prefilter_and_prefilter_resets(page, tmp_path: Path):
    # Verify "None" reverts to pre-filter state and permanent ops clear pre-filter cache.
    image_path = _create_pattern_png(tmp_path)
    page.load_image(str(image_path))
    base = page.get_modified_image().copy()

    page.filter_combo.setCurrentText("Box Blur")
    page.box_blur_spin.setValue(3)
    page.apply_filter()
    blurred = page.get_modified_image().copy()
    assert not np.array_equal(np.asarray(base), np.asarray(blurred))
    assert page.pre_filter_image is not None

    page.filter_combo.setCurrentText("None")
    page.apply_filter()
    _assert_images_close(page.get_modified_image(), base)

    # Permanent operations should clear pre_filter_image state.
    page.filter_combo.setCurrentText("Box Blur")
    page.apply_filter()
    assert page.pre_filter_image is not None
    page.rotate_image(90)
    assert page.pre_filter_image is None


def test_load_and_save_error_paths(page, tmp_path: Path, monkeypatch):
    # Verify warning/critical paths for save-without-image, bad load, and save failure.
    warning_calls = []
    critical_calls = []

    def fake_warning(*args, **kwargs):
        warning_calls.append((args, kwargs))
        return modification_module.QMessageBox.StandardButton.Ok

    def fake_critical(*args, **kwargs):
        critical_calls.append((args, kwargs))
        return modification_module.QMessageBox.StandardButton.Ok

    monkeypatch.setattr(modification_module.QMessageBox, "warning", fake_warning)
    monkeypatch.setattr(modification_module.QMessageBox, "critical", fake_critical)

    # Save without image.
    page.save_image()
    assert len(warning_calls) == 1

    # Load invalid image path.
    page.load_image(str(tmp_path / "does_not_exist.png"))
    assert len(critical_calls) == 1
    assert page.current_image is None

    # Save error after valid load.
    valid_path = _create_pattern_png(tmp_path)
    page.load_image(str(valid_path))
    assert page.current_image is not None

    output_path = tmp_path / "output.png"
    monkeypatch.setattr(
        modification_module.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(output_path), "PNG Files (*.png)"),
    )

    def fake_save(*args, **kwargs):
        raise OSError("simulated save failure")

    monkeypatch.setattr(Image.Image, "save", fake_save, raising=False)
    page.save_image()
    assert len(critical_calls) == 2
