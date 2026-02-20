import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageEnhance, ImageFilter

from Image_Modification_Page import ImageModificationPage

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _image_paths() -> list[Path]:
    root = _repo_root() / "testing_images"
    candidates = [root / "Images", root / "grey_images"]

    paths: list[Path] = []
    for folder in candidates:
        if folder.is_dir():
            paths.extend(sorted(folder.glob("*.jpg")))
            paths.extend(sorted(folder.glob("*.jpeg")))
            paths.extend(sorted(folder.glob("*.png")))

    run_all = os.environ.get("ALL_TEST_IMAGES", "").strip() not in ("", "0", "false", "False")
    if run_all:
        return paths

    per_folder_limit = 3
    limited: list[Path] = []
    for folder in candidates:
        if folder.is_dir():
            folder_paths = [p for p in paths if p.parent == folder]
            limited.extend(folder_paths[:per_folder_limit])

    return limited


TEST_IMAGE_PATHS = _image_paths()


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


@pytest.fixture
def page(qtbot):
    w = ImageModificationPage()
    qtbot.addWidget(w)
    w.show()
    return w


@pytest.mark.parametrize("image_path", TEST_IMAGE_PATHS, ids=lambda p: str(p.name))
def test_load_image_sets_current_image(page, image_path: Path):
    page.load_image(str(image_path))

    assert page.current_image is not None
    assert page.original_image is not None
    assert page.current_image.size == page.original_image.size


@pytest.mark.parametrize("image_path", TEST_IMAGE_PATHS, ids=lambda p: str(p.name))
def test_rotate_90_matches_pil(page, image_path: Path):
    page.load_image(str(image_path))
    original = page.original_image.copy()

    page.rotate_image(90)

    expected = original.rotate(-90, expand=True)
    actual = page.get_modified_image()

    _assert_images_close(actual, expected)


@pytest.mark.parametrize("image_path", TEST_IMAGE_PATHS, ids=lambda p: str(p.name))
def test_flip_horizontal_matches_pil(page, image_path: Path):
    page.load_image(str(image_path))
    original = page.original_image.copy()

    page.flip_horizontal()

    expected = original.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    actual = page.get_modified_image()

    _assert_images_close(actual, expected)


@pytest.mark.parametrize("image_path", TEST_IMAGE_PATHS, ids=lambda p: str(p.name))
def test_brightness_adjustment_matches_pil(page, image_path: Path):
    page.load_image(str(image_path))
    original = page.original_image.copy()

    page.brightness_slider.setValue(120)
    page.update_preview()
    page.apply_adjustments()

    expected = ImageEnhance.Brightness(original).enhance(1.2)
    actual = page.get_modified_image()

    _assert_images_close(actual, expected, max_abs_diff=1)


@pytest.mark.parametrize("image_path", TEST_IMAGE_PATHS, ids=lambda p: str(p.name))
def test_blur_filter_matches_pil(page, image_path: Path):
    page.load_image(str(image_path))
    original = page.original_image.copy()

    page.filter_combo.setCurrentText("Box Blur")
    page.apply_filter()

    expected = original.filter(ImageFilter.BoxBlur(2))
    actual = page.get_modified_image()

    _assert_images_close(actual, expected)
