import time
from pathlib import Path
from typing import List

import pytest
from PIL import Image

from Image_Modification_Page import ImageModificationPage


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _get_test_images() -> List[Path]:
    """Get all available test images"""
    root = _repo_root() / "testing_images"
    candidates = [root / "Images", root / "grey_images"]

    paths: list[Path] = []
    for folder in candidates:
        if folder.is_dir():
            paths.extend(sorted(folder.glob("*.jpg")))
            paths.extend(sorted(folder.glob("*.jpeg")))
            paths.extend(sorted(folder.glob("*.png")))

    return paths


@pytest.fixture
def page(qtbot):
    """Create a fresh ImageModificationPage instance"""
    w = ImageModificationPage()
    qtbot.addWidget(w)
    w.show()
    return w


class TestBulkImageLoading:
    """Test loading multiple images sequentially"""

    def test_load_10_images_sequential(self, page, qtbot):
        """Load 10 images one after another and measure time"""
        test_images = _get_test_images()
        
        if len(test_images) < 10:
            pytest.skip(f"Need at least 10 test images, found {len(test_images)}")
        
        images_to_load = test_images[:10]
        
        start_time = time.perf_counter()
        
        for img_path in images_to_load:
            page.load_image(str(img_path))
            assert page.current_image is not None, f"Failed to load {img_path.name}"
            assert page.original_image is not None
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        avg_time = elapsed / len(images_to_load)
        
        print(f"\n✓ Loaded {len(images_to_load)} images in {elapsed:.3f}s")
        print(f"  Average time per image: {avg_time:.3f}s")
        
        assert elapsed < 30, f"Loading {len(images_to_load)} images took too long: {elapsed:.2f}s"

    def test_load_25_images_sequential(self, page, qtbot):
        """Load 25 images one after another and measure time"""
        test_images = _get_test_images()
        
        if len(test_images) < 25:
            pytest.skip(f"Need at least 25 test images, found {len(test_images)}")
        
        images_to_load = test_images[:25]
        
        start_time = time.perf_counter()
        
        for img_path in images_to_load:
            page.load_image(str(img_path))
            assert page.current_image is not None
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        avg_time = elapsed / len(images_to_load)
        
        print(f"\n✓ Loaded {len(images_to_load)} images in {elapsed:.3f}s")
        print(f"  Average time per image: {avg_time:.3f}s")
        
        assert elapsed < 75, f"Loading {len(images_to_load)} images took too long: {elapsed:.2f}s"

    def test_load_all_available_images(self, page, qtbot):
        """Load all available test images and measure performance"""
        test_images = _get_test_images()
        
        if len(test_images) < 1:
            pytest.skip("No test images found")
        
        start_time = time.perf_counter()
        
        for img_path in test_images:
            page.load_image(str(img_path))
            assert page.current_image is not None
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        avg_time = elapsed / len(test_images)
        
        print(f"\n✓ Loaded all {len(test_images)} test images in {elapsed:.3f}s")
        print(f"  Average time per image: {avg_time:.3f}s")
        
        assert elapsed < 10 * len(test_images), "Loading took unreasonably long"


class TestBulkImageOperations:
    """Test performing operations on multiple images"""

    def test_rotate_multiple_images(self, page, qtbot):
        """Rotate 10 images and measure time"""
        test_images = _get_test_images()
        
        if len(test_images) < 10:
            pytest.skip(f"Need at least 10 test images, found {len(test_images)}")
        
        images_to_process = test_images[:10]
        
        start_time = time.perf_counter()
        
        for img_path in images_to_process:
            page.load_image(str(img_path))
            page.rotate_image(90)
            assert page.current_image is not None
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        avg_time = elapsed / len(images_to_process)
        
        print(f"\n✓ Rotated {len(images_to_process)} images in {elapsed:.3f}s")
        print(f"  Average time per image: {avg_time:.3f}s")

    def test_apply_filter_to_multiple_images(self, page, qtbot):
        """Apply blur filter to multiple images and measure time"""
        test_images = _get_test_images()
        
        if len(test_images) < 10:
            pytest.skip(f"Need at least 10 test images, found {len(test_images)}")
        
        images_to_process = test_images[:10]
        
        start_time = time.perf_counter()
        
        for img_path in images_to_process:
            page.load_image(str(img_path))
            page.filter_combo.setCurrentText("Blur")
            page.apply_filter()
            assert page.current_image is not None
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        avg_time = elapsed / len(images_to_process)
        
        print(f"\n✓ Applied filter to {len(images_to_process)} images in {elapsed:.3f}s")
        print(f"  Average time per image: {avg_time:.3f}s")

    def test_brightness_adjustment_multiple_images(self, page, qtbot):
        """Adjust brightness on multiple images and measure time"""
        test_images = _get_test_images()
        
        if len(test_images) < 10:
            pytest.skip(f"Need at least 10 test images, found {len(test_images)}")
        
        images_to_process = test_images[:10]
        
        start_time = time.perf_counter()
        
        for img_path in images_to_process:
            page.load_image(str(img_path))
            page.brightness_slider.setValue(150)
            page.update_preview()
            page.apply_adjustments()
            assert page.current_image is not None
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        avg_time = elapsed / len(images_to_process)
        
        print(f"\n✓ Adjusted brightness on {len(images_to_process)} images in {elapsed:.3f}s")
        print(f"  Average time per image: {avg_time:.3f}s")

    def test_complex_operation_chain_multiple_images(self, page, qtbot):
        """Perform multiple operations on each image and measure time"""
        test_images = _get_test_images()
        
        if len(test_images) < 5:
            pytest.skip(f"Need at least 5 test images, found {len(test_images)}")
        
        images_to_process = test_images[:5]
        
        start_time = time.perf_counter()
        
        for img_path in images_to_process:
            page.load_image(str(img_path))
            
            # Rotate
            page.rotate_image(90)
            
            # Flip
            page.flip_horizontal()
            
            # Adjust brightness
            page.brightness_slider.setValue(120)
            page.update_preview()
            page.apply_adjustments()
            
            # Apply filter
            page.filter_combo.setCurrentText("Sharpen")
            page.apply_filter()
            
            assert page.current_image is not None
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        avg_time = elapsed / len(images_to_process)
        
        print(f"\n✓ Applied 4 operations to {len(images_to_process)} images in {elapsed:.3f}s")
        print(f"  Average time per image: {avg_time:.3f}s")


class TestMemoryHandling:
    """Test memory handling with many images"""

    def test_rapid_image_switching(self, page, qtbot):
        """Rapidly switch between images to test memory cleanup"""
        test_images = _get_test_images()
        
        if len(test_images) < 20:
            pytest.skip(f"Need at least 20 test images, found {len(test_images)}")
        
        images_to_load = test_images[:20]
        
        start_time = time.perf_counter()
        
        # Load each image rapidly
        for img_path in images_to_load:
            page.load_image(str(img_path))
            assert page.current_image is not None
        
        # Load them again in reverse order to test cleanup
        for img_path in reversed(images_to_load):
            page.load_image(str(img_path))
            assert page.current_image is not None
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        total_loads = len(images_to_load) * 2
        avg_time = elapsed / total_loads
        
        print(f"\n✓ Loaded {total_loads} images (rapid switching) in {elapsed:.3f}s")
        print(f"  Average time per load: {avg_time:.3f}s")

    def test_large_image_handling(self, page, qtbot):
        """Test handling of larger images"""
        test_images = _get_test_images()
        
        if len(test_images) < 1:
            pytest.skip("No test images found")
        
        # Find the largest image
        largest_img = None
        largest_size = 0
        
        for img_path in test_images:
            with Image.open(img_path) as img:
                size = img.width * img.height
                if size > largest_size:
                    largest_size = size
                    largest_img = img_path
        
        if largest_img is None:
            pytest.skip("Could not find any images")
        
        start_time = time.perf_counter()
        
        # Load the largest image multiple times
        for _ in range(5):
            page.load_image(str(largest_img))
            page.rotate_image(90)
            page.apply_filter()
            assert page.current_image is not None
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        print(f"\n✓ Processed largest image ({largest_size:,} pixels) 5 times in {elapsed:.3f}s")
        print(f"  Average time per operation set: {elapsed/5:.3f}s")


class TestStressScenarios:
    """Stress test scenarios"""

    def test_undo_redo_stress(self, page, qtbot):
        """Perform many operations and test undo/redo performance"""
        test_images = _get_test_images()
        
        if len(test_images) < 1:
            pytest.skip("No test images found")
        
        page.load_image(str(test_images[0]))
        
        start_time = time.perf_counter()
        
        # Perform 20 operations
        for i in range(20):
            if i % 4 == 0:
                page.rotate_image(90)
            elif i % 4 == 1:
                page.flip_horizontal()
            elif i % 4 == 2:
                page.brightness_slider.setValue(100 + (i * 5))
                page.update_preview()
                page.apply_adjustments()
            else:
                page.filter_combo.setCurrentText("Blur")
                page.apply_filter()
        
        # Undo all operations
        for _ in range(20):
            page.undo()
        
        # Redo all operations
        for _ in range(20):
            page.redo()
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        print(f"\n✓ Performed 20 operations + 20 undos + 20 redos in {elapsed:.3f}s")
        print(f"  Total operations: 60")
        print(f"  Average time per operation: {elapsed/60:.4f}s")
