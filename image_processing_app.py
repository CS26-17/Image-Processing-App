import sys
# Import pandas/numpy before PySide6 to prevent shibokensupport from
# intercepting the six.moves import chain (known PySide6 + six conflict).
import pandas
import numpy
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QTabBar
)

from tabs.Image_Modification_Page import ImageModificationPage
from tabs.results_tab import ResultsTab
from tabs.documentation_tab import DocumentationTab
from tabs.home_tab import HomeTab
from tabs.analysis_setup_tab import AnalysisSetupTab


class NoWheelTabBar(QTabBar):
    """Prevent mouse-wheel scrolling from changing the active tab."""

    def wheelEvent(self, event):
        event.ignore()



class ImageProcessingApp(QMainWindow):
    """
    Main application window for the Image Processing App.

    The Home tab UI and functionality are fully implemented in tabs.home_tab.HomeTab.
    This window is responsible for:
      - Creating tabs
      - Providing the modification_page and tab_widget references
        that HomeTab uses when processing images.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processing App")
        self.setGeometry(100, 100, 1400, 900)

        # Central tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(NoWheelTabBar())
        self.tab_widget.setMovable(True)
        self.setCentralWidget(self.tab_widget)

        # Set up all tabs
        self.setup_home_tab()
        self.setup_other_tabs()
        self.apply_default_styles()

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------
    def setup_home_tab(self) -> None:
        """Create and add the Upload tab."""
        self.home_tab = HomeTab(parent=self)
        self.tab_widget.addTab(self.home_tab, "Upload")

    def setup_other_tabs(self) -> None:
        """Create and add the remaining tabs in pipeline order."""
        # Edit tab stays next to Upload by default.
        self.modification_page = ImageModificationPage(parent=self)
        self.tab_widget.addTab(self.modification_page, "Edit")

        # Analyze Tab
        self.analysis_setup_tab = AnalysisSetupTab()
        self.tab_widget.addTab(self.analysis_setup_tab, "Analyze")
        self.analysis_setup_tab.analysis_complete.connect(self._on_analysis_complete)

        # Results Tab
        self.results_tab = ResultsTab()
        self.tab_widget.addTab(self.results_tab, "Results")

        # Help Tab
        self.docs_tab = DocumentationTab(parent=self)
        self.tab_widget.addTab(self.docs_tab, "Help")

    def _on_analysis_complete(self, output_dir):
        self.results_tab.load_from_directory(output_dir)
        self.tab_widget.setCurrentWidget(self.results_tab)

    def apply_default_styles(self) -> None:
        """Apply a light, slightly richer default application palette."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f6f8fb;
            }
            QWidget {
                color: #243447;
            }
            QTabWidget::pane {
                border: 1px solid #d8e2ef;
                background-color: #fcfdff;
                border-radius: 6px;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #eaf0f7;
                border: 1px solid #d3deea;
                color: #425466;
                padding: 9px 20px;
                margin-right: 3px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #fcfdff;
                color: #1f3b5b;
                border-bottom-color: #fcfdff;
            }
            QTabBar::tab:hover {
                background-color: #dde8f5;
                color: #1f3b5b;
            }
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #dbe4ee;
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px 10px 10px 10px;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #355070;
                background-color: #ffffff;
            }
            QLineEdit,
            QComboBox,
            QSpinBox,
            QTextEdit,
            QPlainTextEdit,
            QListWidget {
                background-color: #ffffff;
                color: #243447;
                border: 1px solid #cfd9e6;
                border-radius: 6px;
                padding: 6px 8px;
            }
            QLineEdit:focus,
            QComboBox:focus,
            QSpinBox:focus,
            QTextEdit:focus,
            QPlainTextEdit:focus,
            QListWidget:focus {
                border: 1px solid #7aa7d9;
            }
            QPushButton {
                background-color: #edf4fb;
                color: #24405f;
                border: 1px solid #c8d7e8;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #dfeaf7;
                border-color: #b4c9df;
            }
            QPushButton:pressed {
                background-color: #d4e2f1;
            }
        """)


def main() -> None:
    """Entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = ImageProcessingApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
