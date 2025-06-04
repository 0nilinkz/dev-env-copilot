#!/usr/bin/env python3
"""
Development Environment MCP Package Setup and Distribution Script

This script helps with package setup, testing, and distribution.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(cmd, description="", check=True):
    """Run a command with error handling"""
    print(f"\n{'='*50}")
    print(f"📋 {description or cmd}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"⚠️  Error: {result.stderr}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        return False


def setup_development():
    """Setup development environment"""
    print("🔧 Setting up development environment...")
    
    # Install package in development mode
    success = run_command(
        "pip install -e .",
        "Installing package in development mode"
    )
    
    if success:
        print("✅ Development environment setup complete!")
    else:
        print("❌ Development setup failed!")
    
    return success


def run_tests():
    """Run the test suite"""
    print("🧪 Running test suite...")
    
    # Run pytest
    success = run_command(
        "python -m pytest test_mcp_server.py -v",
        "Running pytest"
    )
    
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return success


def test_standalone():
    """Test standalone functionality"""
    print("🔍 Testing standalone functionality...")
    
    commands = [
        ("dev-env-mcp --version", "Testing version command"),
        ("dev-env-mcp detect-environment --format summary", "Testing environment detection"),
        ("dev-env-mcp get-command-syntax --operation test --format shell", "Testing command syntax"),
    ]
    
    all_success = True
    for cmd, desc in commands:
        success = run_command(cmd, desc, check=False)
        if not success:
            all_success = False
    
    if all_success:
        print("✅ Standalone functionality works!")
    else:
        print("❌ Some standalone tests failed!")
    
    return all_success


def build_package():
    """Build distribution packages"""
    print("📦 Building distribution packages...")
    
    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info", "Cleaning previous builds", check=False)
    
    # Build package
    success = run_command(
        "python -m build",
        "Building wheel and source distribution"
    )
    
    if success:
        print("✅ Package built successfully!")
        # List contents
        run_command("ls -la dist/", "Listing built packages", check=False)
    else:
        print("❌ Package build failed!")
    
    return success


def check_package():
    """Check package quality"""
    print("🔍 Checking package quality...")
    
    commands = [
        ("twine check dist/*", "Checking distribution with twine"),
        ("python -m pip install dist/*.whl --force-reinstall --no-deps", "Testing wheel installation"),
    ]
    
    all_success = True
    for cmd, desc in commands:
        success = run_command(cmd, desc, check=False)
        if not success:
            all_success = False
    
    return all_success


def lint_code():
    """Run code linting"""
    print("🧹 Running code linting...")
    
    commands = [
        ("ruff check src/", "Running ruff linter"),
        ("black --check src/", "Checking code formatting"),
    ]
    
    all_success = True
    for cmd, desc in commands:
        success = run_command(cmd, desc, check=False)
        if not success:
            all_success = False
    
    return all_success


def publish_package():
    """Publish package to PyPI"""
    print("🚀 Publishing package to PyPI...")
    
    # Check if we have API token
    if not os.getenv("TWINE_PASSWORD") and not os.getenv("PYPI_API_TOKEN"):
        print("⚠️  Warning: No PyPI API token found in environment variables.")
        print("   Set TWINE_PASSWORD or PYPI_API_TOKEN to publish.")
        return False
    
    success = run_command(
        "twine upload dist/*",
        "Uploading to PyPI"
    )
    
    if success:
        print("✅ Package published successfully!")
    else:
        print("❌ Package publishing failed!")
    
    return success


def create_github_repo():
    """Create GitHub repository (requires gh CLI)"""
    print("🐙 Creating GitHub repository...")
    
    # Check if gh CLI is available
    if not run_command("gh --version", "Checking GitHub CLI", check=False):
        print("❌ GitHub CLI (gh) not found. Install it first: https://cli.github.com/")
        return False
    
    repo_name = "dev-environment-mcp"
    description = "MCP server for development environment detection and command syntax assistance"
    
    commands = [
        (f"gh repo create {repo_name} --description '{description}' --public", "Creating GitHub repository"),
        ("git remote add origin https://github.com/$(gh api user --jq .login)/dev-environment-mcp.git", "Adding remote origin"),
        ("git add .", "Staging files"),
        ("git commit -m 'Initial commit: MCP server for development environment detection'", "Initial commit"),
        ("git push -u origin main", "Pushing to GitHub"),
    ]
    
    all_success = True
    for cmd, desc in commands:
        success = run_command(cmd, desc, check=False)
        if not success:
            all_success = False
            break
    
    if all_success:
        print(f"✅ GitHub repository created: https://github.com/$(gh api user --jq .login)/{repo_name}")
    else:
        print("❌ GitHub repository creation failed!")
    
    return all_success


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("""
🔧 Development Environment MCP Package Setup

Usage: python setup_package.py <command>

Commands:
  setup       - Setup development environment
  test        - Run test suite
  standalone  - Test standalone functionality
  lint        - Run code linting
  build       - Build distribution packages
  check       - Check package quality
  publish     - Publish to PyPI
  github      - Create GitHub repository
  all         - Run setup, test, lint, build, and check
  
Examples:
  python setup_package.py setup
  python setup_package.py test
  python setup_package.py all
""")
        return
    
    command = sys.argv[1].lower()
    
    # Change to package directory
    package_dir = Path(__file__).parent
    os.chdir(package_dir)
    print(f"📁 Working in: {package_dir}")
    
    if command == "setup":
        setup_development()
    elif command == "test":
        run_tests()
    elif command == "standalone":
        test_standalone()
    elif command == "lint":
        lint_code()
    elif command == "build":
        build_package()
    elif command == "check":
        check_package()
    elif command == "publish":
        publish_package()
    elif command == "github":
        create_github_repo()
    elif command == "all":
        print("🔄 Running full pipeline...")
        success = (
            setup_development() and
            lint_code() and
            run_tests() and
            build_package() and
            check_package()
        )
        
        if success:
            print("\n🎉 All checks passed! Package is ready for distribution.")
            print("\nNext steps:")
            print("  1. python setup_package.py github    # Create GitHub repo")
            print("  2. python setup_package.py publish   # Publish to PyPI")
        else:
            print("\n❌ Some checks failed. Please fix issues before proceeding.")
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
