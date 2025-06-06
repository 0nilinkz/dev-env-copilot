#!/usr/bin/env python3
"""
Test the MCP server functionality properly with initialization handshake
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def test_mcp_server():
    """Test the MCP server with proper initialization handshake"""
    print("🔍 Testing MCP server functionality...")
    
    try:
        # Start the MCP server
        proc = subprocess.Popen(
            [sys.executable, "-m", "dev_environment_mcp.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Step 1: Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialize request...")
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Read initialize response
        init_response = proc.stdout.readline()
        if not init_response:
            print("❌ No response to initialize request")
            proc.terminate()
            return False
            
        try:
            init_data = json.loads(init_response)
            print(f"✅ Initialize response: {init_data.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response: {init_response}")
            proc.terminate()
            return False
        
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print("📤 Sending initialized notification...")
        proc.stdin.write(json.dumps(initialized_notification) + "\n")
        proc.stdin.flush()
        
        # Step 3: Test tools/list
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("📤 Sending tools/list request...")
        proc.stdin.write(json.dumps(tools_request) + "\n")
        proc.stdin.flush()
        
        # Read tools response
        tools_response = proc.stdout.readline()
        if not tools_response:
            print("❌ No response to tools/list request")
            proc.terminate()
            return False
            
        try:
            tools_data = json.loads(tools_response)
            tools = tools_data.get('result', {}).get('tools', [])
            print(f"✅ Found {len(tools)} tools: {[t['name'] for t in tools]}")
            
            # Step 4: Test a tool call
            if tools:
                tool_call_request = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "detect_environment",
                        "arguments": {}
                    }
                }
                
                print("📤 Testing detect_environment tool...")
                proc.stdin.write(json.dumps(tool_call_request) + "\n")
                proc.stdin.flush()
                
                # Read tool response
                tool_response = proc.stdout.readline()
                if tool_response:
                    try:
                        tool_data = json.loads(tool_response)
                        if 'result' in tool_data:
                            print("✅ Tool call successful")
                            return True
                        else:
                            print(f"❌ Tool call failed: {tool_data}")
                    except json.JSONDecodeError:
                        print(f"❌ Invalid tool response: {tool_response}")
                
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in tools response: {tools_response}")
        
        proc.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False


if __name__ == "__main__":
    if test_mcp_server():
        print("✅ MCP server test passed!")
        sys.exit(0)
    else:
        print("❌ MCP server test failed!")
        sys.exit(1)
