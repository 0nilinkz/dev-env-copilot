#!/usr/bin/env python3
"""
setup.py for dev-env-copilot

Makes the package installable via pip install.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Development Environment Copilot - MCP Server for cross-platform development"

setup(
    name="dev-env-copilot",
    version="1.0.0",
    description="MCP Server for intelligent environment detection and command syntax assistance",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/0nilinkz/dev-env-copilot",
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=[
        "mcp[cli]>=1.9.0",
        "httpx",
        "pydantic>=2.7.0",
        "typer",
        "rich",
    ],
    
    # Optional dependencies for development
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "black",
            "ruff",
            "mypy",
        ],
    },
    
    # Console scripts / entry points
    entry_points={
        "console_scripts": [
            "dev-env-copilot=dev_environment_mcp.mcp_server:main",
            "dev-env-copilot-server=dev_environment_mcp.mcp_server:main",
        ],
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Tools",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
    
    # Include additional files
    include_package_data=True,
    zip_safe=False,
    
    # Keywords for PyPI
    keywords="mcp, development, environment, copilot, vscode, shell, commands",
)
