import sys
# Import pandas/numpy before PySide6 to prevent shibokensupport from
# intercepting the six.moves import chain (known PySide6 + six conflict).
import pandas
import numpy
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QLabel, QTabWidget
)
from PySide6.QtCore import Qt, QSignalBlocker

from tabs.Image_Modification_Page import ImageModificationPage
from tabs.results_tab import ResultsTab
from tabs.documentation_tab import DocumentationTab
from tabs.home_tab import HomeTab
from tabs.analysis_setup_tab import AnalysisSetupTab


class DocumentationWindow(QMainWindow):
    """Standalone window for the documentation browser."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Documentation")
        self.setGeometry(180, 140, 1280, 860)
        self.docs_tab = DocumentationTab(parent=self)
        self.setCentralWidget(self.docs_tab)


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

        # Global application styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #C2C7CB;
                background-color: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #E1E1E1;
                border: 1px solid #C4C4C3;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
        """)

        # Central tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.documentation_window = DocumentationWindow()
        self.documentation_tab_index = -1
        self.last_main_tab_index = 0

        # Set up all tabs
        self.setup_home_tab()
        self.setup_other_tabs()
        self.tab_widget.currentChanged.connect(self.handle_tab_change)

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------
    def setup_home_tab(self) -> None:
        """Create and add the Home tab using HomeTab."""
        self.home_tab = HomeTab(parent=self)
        self.tab_widget.addTab(self.home_tab, "🏠 Home")

    def setup_other_tabs(self) -> None:
        """Create and add the remaining tabs."""
        # Results Tab
        self.results_tab = ResultsTab()
        self.tab_widget.addTab(self.results_tab, "📊 Results")

        # Documentation launcher tab
        self.docs_launcher_tab = QWidget()
        self.documentation_tab_index = self.tab_widget.addTab(
            self.docs_launcher_tab,
            "📚 Documentation",
        )

        # Modification Tab
        self.modification_page = ImageModificationPage(parent=self)
        self.tab_widget.addTab(self.modification_page, "🛠️ Modification")

        # Analysis Setup Tab (simple placeholder, as before)
        self.analysis_setup_tab = AnalysisSetupTab()
        self.tab_widget.addTab(self.analysis_setup_tab, "⚙️ Analysis Setup")

        # When analysis finishes, load results and switch to Results tab
        self.analysis_setup_tab.analysis_complete.connect(self._on_analysis_complete)

    def handle_tab_change(self, index: int) -> None:
        """Open documentation in a standalone window when its tab is clicked."""
        if index == self.documentation_tab_index:
            self.open_documentation_window()
            fallback_index = self.last_main_tab_index
            if fallback_index == self.documentation_tab_index or fallback_index < 0:
                fallback_index = 0

            blocker = QSignalBlocker(self.tab_widget)
            self.tab_widget.setCurrentIndex(fallback_index)
            del blocker
            return

        self.last_main_tab_index = index

    def open_documentation_window(self) -> None:
        """Show the documentation window and bring it to the front."""
        self.documentation_window.show()
        self.documentation_window.raise_()
        self.documentation_window.activateWindow()

    def _on_analysis_complete(self, output_dir):
        self.results_tab.load_from_directory(output_dir)
        self.tab_widget.setCurrentWidget(self.results_tab)


def main() -> None:
    """Entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = ImageProcessingApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
