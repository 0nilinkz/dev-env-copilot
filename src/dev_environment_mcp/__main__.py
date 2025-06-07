#!/usr/bin/env python3
"""
Entry point for running the dev_environment_mcp module
"""

import anyio
from .server import main

if __name__ == "__main__":
    anyio.run(main)
