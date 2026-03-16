import os

def pytest_configure():
    if os.environ.get("CI"):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
