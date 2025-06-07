#!/usr/bin/env python3
"""
Unit tests for the MCP server functionality.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dev_environment_mcp.server import EnvironmentDetector, CommandSyntaxProvider


def test_environment_detector_creation():
    """Test that the EnvironmentDetector can be created."""
    detector = EnvironmentDetector()
    assert detector is not None


def test_command_syntax_provider_creation():
    """Test that the CommandSyntaxProvider can be created."""
    detector = EnvironmentDetector()
    env_info = detector.detect_environment()
    helper = CommandSyntaxProvider(env_info)
    assert helper is not None


def test_detect_environment():
    """Test that environment detection works."""
    detector = EnvironmentDetector()
    env_info = detector.detect_environment()
    
    assert env_info is not None
    assert hasattr(env_info, 'os_type')
    assert hasattr(env_info, 'shell')
    assert hasattr(env_info, 'python_cmd')
    assert env_info.os_type in ['windows', 'linux', 'darwin']


def test_command_syntax_provider():
    """Test that command syntax provider works."""
    detector = EnvironmentDetector()
    env_info = detector.detect_environment()
    helper = CommandSyntaxProvider(env_info)
    
    result = helper.get_command_syntax("list_files")
    assert isinstance(result, dict)
    assert len(result) > 0


def test_command_syntax_provider_with_options():
    """Test that command syntax provider works with options."""
    detector = EnvironmentDetector()
    env_info = detector.detect_environment()
    helper = CommandSyntaxProvider(env_info)
    
    options = {"path": "test_dir"}
    result = helper.get_command_syntax("create_directory", options)
    assert isinstance(result, dict)
    assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__])
