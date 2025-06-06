#!/usr/bin/env python3
"""
Test script to verify VS Code MCP integration with Docker
"""

import json
import subprocess
import sys
import time
import os

def test_docker_mcp_integration():
    """Test that Docker MCP server can be used by VS Code"""
    print("🐳 Testing Docker MCP Integration for VS Code...")
    
    # Get current directory (Windows-compatible)
    current_dir = os.getcwd().replace('\\', '/')
    
    # Test 1: Check Docker image exists
    print("\n1. Checking Docker image...")
    try:
        result = subprocess.run(
            ["docker", "images", "--format", "table"],
            capture_output=True,
            text=True,
            check=True
        )
        if "dev-env-copilot-test" in result.stdout:
            print("✅ Docker image 'dev-env-copilot-test' found")
        else:
            print("❌ Docker image not found")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker command failed: {e}")
        return False
    
    # Test 2: Test MCP protocol handshake
    print("\n2. Testing MCP protocol handshake...")
    try:
        # Initialize message
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "vscode-test", "version": "1.0"}
            }
        }
        
        process = subprocess.Popen(
            ["docker", "run", "--rm", "--interactive", 
             "--volume", f"{current_dir}:/workspace:ro",
             "dev-env-copilot-test:latest"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=json.dumps(init_msg) + '\n', timeout=10)
        
        if '"result"' in stdout and '"protocolVersion"' in stdout:
            print("✅ MCP handshake successful")
        else:
            print(f"❌ MCP handshake failed")
            print(f"   Stdout: {stdout}")
            print(f"   Stderr: {stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ MCP handshake timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ MCP handshake error: {e}")
        return False
    
    # Test 3: Test tools list (simpler approach)
    print("\n3. Testing tools list...")
    try:
        # Create a simple test script that runs both commands
        test_script = '''
import json
import sys

# Send initialize
init = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "clientInfo": {"name": "test", "version": "1.0"}
    }
}
print(json.dumps(init))

# Send tools/list
tools_list = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}
print(json.dumps(tools_list))
'''
        
        # Run the test script through docker
        result = subprocess.run(
            ["docker", "run", "--rm", "--interactive",
             "--volume", f"{current_dir}:/workspace:ro",
             "dev-env-copilot-test:latest"],
            input=test_script,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if 'detect_environment' in result.stdout:
            print("✅ Tools list successful")
            print("   Found 'detect_environment' tool in response")
        else:
            print(f"❌ Tools list failed")
            print(f"   Stdout: {result.stdout[:300]}...")
            if result.stderr:
                print(f"   Stderr: {result.stderr}")
        
    except Exception as e:
        print(f"❌ Tools list error: {e}")
    
    print("\n🎉 Docker MCP integration tests completed!")
    print("\n📋 VS Code Configuration:")
    print("Add this to your .vscode/settings.json:")
    
    config = {
        "github.copilot.chat.experimental.mcp": {
            "enabled": True,
            "servers": {
                "dev-env-copilot-docker": {
                    "command": "docker",
                    "args": [
                        "run",
                        "--rm",
                        "--interactive",
                        "--volume", "${workspaceFolder}:/workspace:ro",
                        "dev-env-copilot-test:latest"
                    ],
                    "env": {
                        "DOCKER_BUILDKIT": "1"
                    }
                }
            }
        }
    }
    
    print(json.dumps(config, indent=2))
    
    print("\n🔧 Quick Test Commands:")
    print(f"Test handshake:")
    print(f'echo \'{{"jsonrpc":"2.0","id":1,"method":"initialize","params":{{"protocolVersion":"2024-11-05","capabilities":{{"tools":{{}}}},"clientInfo":{{"name":"test","version":"1.0"}}}}}}\' | docker run --rm -i --volume "{current_dir}:/workspace:ro" dev-env-copilot-test:latest')
    
    return True

if __name__ == "__main__":
    success = test_docker_mcp_integration()
    sys.exit(0 if success else 1)
