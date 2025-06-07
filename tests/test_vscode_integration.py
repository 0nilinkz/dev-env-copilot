#!/usr/bin/env python3
"""
Test script to verify VS Code MCP integration with Docker
"""

import json
import subprocess
import sys
import time

def test_docker_mcp_integration():
    """Test that Docker MCP server can be used by VS Code"""
    print("🐳 Testing Docker MCP Integration for VS Code...")
    
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
        assert "dev-env-copilot-test" in result.stdout, "Docker image not found"
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker command failed: {e}")
        assert False, f"Docker command failed: {e}"
    
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
          # Get current directory (Windows-compatible)
        import os
        current_dir = os.getcwd().replace('\\', '/')
        
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
            print(f"   Response: {stdout.strip()}")
        else:
            print(f"❌ MCP handshake failed")
            print(f"   Stdout: {stdout}")
            print(f"   Stderr: {stderr}")
        assert '"result"' in stdout and '"protocolVersion"' in stdout, f"MCP handshake failed. Stdout: {stdout}, Stderr: {stderr}"
            
    except subprocess.TimeoutExpired:
        print("❌ MCP handshake timed out")
        process.kill()
        assert False, "MCP handshake timed out"
    except Exception as e:
        print(f"❌ MCP handshake error: {e}")
        assert False, f"MCP handshake error: {e}"
      # Test 3: Test tools list
    print("\n3. Testing tools list...")
    try:
        # Initialize notification (required after initialize)
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        list_tools_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        # Get current directory (Windows-compatible)
        import os
        current_dir = os.getcwd().replace('\\', '/')
        
        process = subprocess.Popen(
            ["docker", "run", "--rm", "--interactive",
             "--volume", f"{current_dir}:/workspace:ro",
             "dev-env-copilot-test:latest"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialize, initialized notification, then tools/list
        messages = [
            json.dumps(init_msg),
            json.dumps(initialized_notification),
            json.dumps(list_tools_msg)
        ]
        
        stdout, stderr = process.communicate(input='\n'.join(messages) + '\n', timeout=15)
        
        if 'detect_environment' in stdout and 'get_command_syntax' in stdout:
            print("✅ Tools list successful")
            
            # Extract tools from response
            lines = stdout.strip().split('\n')
            for line in lines:
                if '"tools"' in line and 'detect_environment' in line:
                    try:
                        response = json.loads(line)
                        tools = response.get('result', {}).get('tools', [])
                        print(f"   Found {len(tools)} tools: {[t['name'] for t in tools]}")
                        break
                    except:
                        pass
        else:
            print(f"❌ Tools list failed")
            print(f"   Stdout: {stdout}")
        assert 'detect_environment' in stdout, f"Tools list failed. Stdout: {stdout}"
            
    except Exception as e:
        print(f"❌ Tools list error: {e}")
        assert False, f"Tools list error: {e}"
    
    print("\n🎉 All Docker MCP integration tests passed!")
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

if __name__ == "__main__":
    test_docker_mcp_integration()
