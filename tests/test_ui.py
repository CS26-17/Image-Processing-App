import os

import pytest
from PIL import Image
from PySide6.QtCore import Qt

from image_processing_app import ImageProcessingApp


def _create_temp_png(tmp_path):
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (32, 32), color=(255, 0, 0))
    img.save(img_path)
    return str(img_path)


@pytest.fixture
def window(qtbot):
    w = ImageProcessingApp()
    qtbot.addWidget(w)
    w.show()
    return w


def test_window_constructs_and_has_tabs(window):
    assert window.tab_widget is not None
    assert window.tab_widget.count() >= 4

    titles = [window.tab_widget.tabText(i) for i in range(window.tab_widget.count())]

    assert any("Home" in t for t in titles)
    assert any("Results" in t for t in titles)
    assert any("Documentation" in t for t in titles)
    assert any("Modification" in t for t in titles)


def test_home_tab_buttons_exist(window):
    assert window.upload_button is not None
    assert window.clear_button is not None
    assert window.process_button is not None


def test_process_image_without_upload_sets_status(window, qtbot):
    window.clear_image()

    qtbot.mouseClick(window.process_button, Qt.MouseButton.LeftButton)

    assert "upload" in window.status_label.text().lower()


def test_process_image_after_loading_temp_image_switches_to_modification(window, qtbot, tmp_path):
    img_path = _create_temp_png(tmp_path)

    window.display_image(img_path)
    assert window.current_image_path == img_path

    qtbot.mouseClick(window.process_button, Qt.MouseButton.LeftButton)

    assert window.tab_widget.currentWidget() == window.modification_page
    assert window.modification_page.current_image is not None


def test_clear_image_resets_state(window):
    window.clear_image()

    assert window.current_image_path is None
    assert "no image" in window.info_label.text().lower()
