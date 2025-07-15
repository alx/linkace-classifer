"""
LinkAce Classifier Package

A Python package for automatically classifying URLs using LinkAce API and AI.
"""

__version__ = "1.0.0"
__author__ = "LinkAce Classifier Team"
__description__ = "AI-powered URL classification for LinkAce"

# Package-level imports for convenience
from .core.config import ClassifierConfig, ConfigManager
from .core.utils import log_message

__all__ = [
    "ClassifierConfig",
    "ConfigManager", 
    "log_message",
    "__version__",
]