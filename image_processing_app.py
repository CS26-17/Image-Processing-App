import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QLabel, QTabWidget
)
from PySide6.QtCore import Qt

from tabs.Image_Modification_Page import ImageModificationPage
from tabs.results_tab import ResultsTab
from tabs.documentation_tab import DocumentationTab
from tabs.home_tab import HomeTab
from tabs.analysis_setup_tab import AnalysisSetupTab


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

        # Set up all tabs
        self.setup_home_tab()
        self.setup_other_tabs()

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

        # Documentation Tab
        self.docs_tab = DocumentationTab(parent=self)
        self.tab_widget.addTab(self.docs_tab, "📚 Documentation")

        # Modification Tab
        self.modification_page = ImageModificationPage(parent=self)
        self.tab_widget.addTab(self.modification_page, "🛠️ Modification")

        # Analysis Setup Tab (simple placeholder, as before)
        self.analysis_setup_tab = AnalysisSetupTab()
        self.tab_widget.addTab(self.analysis_setup_tab, "⚙️ Analysis Setup")


def main() -> None:
    """Entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = ImageProcessingApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
