"""
Quick test to verify PyQt6 is installed and working correctly
"""

import sys

print("Testing PyQt6 installation...\n")

# Test 1: Import QtCore
print("Test 1: Importing QtCore...", end=" ")
try:
    from PyQt6 import QtCore
    print("✓ SUCCESS")
except ImportError as e:
    print(f"✗ FAILED: {e}")
    print("\nRun fix_pyqt6.bat to fix this issue.")
    sys.exit(1)

# Test 2: Import QtWidgets
print("Test 2: Importing QtWidgets...", end=" ")
try:
    from PyQt6 import QtWidgets
    print("✓ SUCCESS")
except ImportError as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 3: Create QApplication
print("Test 3: Creating QApplication...", end=" ")
try:
    app = QtWidgets.QApplication(sys.argv)
    print("✓ SUCCESS")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 4: Create widgets
print("Test 4: Creating QLabel...", end=" ")
try:
    label = QtWidgets.QLabel("Test")
    print("✓ SUCCESS")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 5: Create QMainWindow
print("Test 5: Creating QMainWindow...", end=" ")
try:
    window = QtWidgets.QMainWindow()
    print("✓ SUCCESS")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# All tests passed
print("\n" + "="*50)
print("✓✓✓ ALL TESTS PASSED!")
print("="*50)
print("\nPyQt6 is installed correctly and ready to use.")
print("You can now run your application:")
print("  python image_modification_page.py")
print("  python demo_gallery_app.py")
print("  python image_difference_app.py")
