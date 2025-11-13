"""
Tabs package for Image Processing App
Contains modular tab implementations
"""

from .home_tab import HomeTab
from .results_tab import ResultsTab
from .documentation_tab import DocumentationTab
from .modification_tab import ModificationTab
from .analysis_setup_tab import AnalysisSetupTab

__all__ = [
    'HomeTab',
    'ResultsTab',
    'DocumentationTab',
    'ModificationTab',
    'AnalysisSetupTab'
]
