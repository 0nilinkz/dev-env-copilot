"""
Development Environment MCP Server

A Model Context Protocol server for intelligent environment detection
and cross-platform development command assistance.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

try:
    from .server import EnvironmentMCPServer, main
    __all__ = ["EnvironmentMCPServer", "main"]
except ImportError:
    # Handle case where server module is not yet available
    __all__ = []
