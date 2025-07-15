"""
API clients for external services

Contains clients for LinkAce API and Ollama server integration.
"""

from .linkace import LinkAceClient
from .ollama import OllamaClient

__all__ = [
    "LinkAceClient", 
    "OllamaClient",
]