import sys
# Import pandas/numpy before PySide6 to prevent shibokensupport from
# intercepting the six.moves import chain (known PySide6 + six conflict).
import pandas
import numpy
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QLabel, QTabWidget, QComboBox
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
        self.themes = {
            "Light": {
                "window_bg": "#f5f5f5",
                "pane_bg": "#ffffff",
                "surface_bg": "#ffffff",
                "surface_alt": "#E1E1E1",
                "surface_hover": "#d0d0d0",
                "border": "#C2C7CB",
                "text": "#1f2933",
                "accent": "#2196F3",
                "accent_text": "#ffffff",
            },
            "Dark": {
                "window_bg": "#1f242b",
                "pane_bg": "#262d35",
                "surface_bg": "#2d3640",
                "surface_alt": "#37414d",
                "surface_hover": "#465261",
                "border": "#4f5b68",
                "text": "#f3f6f8",
                "accent": "#4DA3FF",
                "accent_text": "#0f1720",
            },
            "Forest": {
                "window_bg": "#eef4ee",
                "pane_bg": "#fbfdf9",
                "surface_bg": "#f8fbf4",
                "surface_alt": "#dbe7d8",
                "surface_hover": "#c8d8c5",
                "border": "#a8baa5",
                "text": "#203126",
                "accent": "#5A8F55",
                "accent_text": "#ffffff",
            },
        }
        self.current_theme = "Light"

        # Central tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setMovable(True)
        self.setCentralWidget(self.tab_widget)

        # Set up all tabs
        self.setup_home_tab()
        self.setup_other_tabs()
        self.apply_theme(self.current_theme)

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

        # Theme Tab
        self.theme_tab = QWidget()
        theme_layout = QVBoxLayout(self.theme_tab)
        theme_layout.setContentsMargins(40, 40, 40, 40)
        theme_layout.setSpacing(16)

        theme_title = QLabel("Choose a color theme")
        theme_title.setStyleSheet("font-size: 22px; font-weight: 700;")

        theme_description = QLabel(
            "Select a preset theme to update the interface colors."
        )
        theme_description.setWordWrap(True)

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(self.themes.keys())
        self.theme_selector.setCurrentText(self.current_theme)
        self.theme_selector.currentTextChanged.connect(self.apply_theme)
        self.theme_selector.setMaximumWidth(260)

        theme_layout.addWidget(theme_title)
        theme_layout.addWidget(theme_description)
        theme_layout.addWidget(self.theme_selector, alignment=Qt.AlignLeft)
        theme_layout.addStretch()

        self.tab_widget.addTab(self.theme_tab, "Theme")

    def _on_analysis_complete(self, output_dir):
        self.results_tab.load_from_directory(output_dir)
        self.tab_widget.setCurrentWidget(self.results_tab)

    def apply_theme(self, theme_name: str) -> None:
        """Apply one of the preset application themes."""
        theme = self.themes.get(theme_name, self.themes["Light"])
        self.current_theme = theme_name if theme_name in self.themes else "Light"
        self.setStyleSheet(self._build_stylesheet(theme))

    def _build_stylesheet(self, theme: dict) -> str:
        """Build the application stylesheet from a small set of theme colors."""
        return f"""
            QMainWindow {{
                background-color: {theme["window_bg"]};
                color: {theme["text"]};
            }}
            QWidget {{
                color: {theme["text"]};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme["border"]};
                background-color: {theme["pane_bg"]};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {theme["surface_alt"]};
                border: 1px solid {theme["border"]};
                color: {theme["text"]};
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {theme["accent"]};
                color: {theme["accent_text"]};
            }}
            QTabBar::tab:hover {{
                background-color: {theme["surface_hover"]};
            }}
            QLabel {{
                color: {theme["text"]};
            }}
            QComboBox,
            QLineEdit,
            QTextEdit,
            QListWidget,
            QPlainTextEdit {{
                background-color: {theme["surface_bg"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                padding: 6px 8px;
            }}
            QPushButton {{
                background-color: {theme["accent"]};
                color: {theme["accent_text"]};
                border: 1px solid {theme["accent"]};
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
            }}
        """


def main() -> None:
    """Entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = ImageProcessingApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
