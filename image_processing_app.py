import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt

from tabs import (HomeTab, ResultsTab, DocumentationTab, 
                  ModificationTab, AnalysisSetupTab)

class ImageProcessingApp(QMainWindow):
    """
    Main application window for Image Processing App
    Supports drag & drop and image upload functionality
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processing App")
        self.setGeometry(100, 100, 800, 600)  # Increased window size for better layout
        
        # Enable drag and drop functionality
        self.setAcceptDrops(True)
        
        # Set application-wide styles
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
        
        # Initialize tab widget as central widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Setup all tabs
        self.setup_tabs()
    
    def setup_tabs(self):
        """Setup all application tabs using modular tab classes"""
        # Create and add Home tab
        self.home_tab = HomeTab(self)
        self.tab_widget.addTab(self.home_tab, "🏠 Home")
        
        # Create and add Results tab
        self.results_tab = ResultsTab(self)
        self.tab_widget.addTab(self.results_tab, "📊 Results")
        
        # Create and add Documentation tab
        self.docs_tab = DocumentationTab(self)
        self.tab_widget.addTab(self.docs_tab, "📚 Documentation")
        
        # Create and add Modification tab
        self.mod_tab = ModificationTab(self)
        self.tab_widget.addTab(self.mod_tab, "🛠️ Modification")
        
        # Create and add Analysis Setup tab
        self.analysis_tab = AnalysisSetupTab(self)
        self.tab_widget.addTab(self.analysis_tab, "⚙️ Analysis Setup")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event - delegate to home tab"""
        self.home_tab.handle_drag_enter(event)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event - delegate to home tab"""
        self.home_tab.handle_drag_leave()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event - delegate to home tab"""
        self.home_tab.handle_drop(event)


def main():
    """Main function to start the application"""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = ImageProcessingApp()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
