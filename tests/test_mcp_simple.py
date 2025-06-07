#!/usr/bin/env python3
"""
Simple MCP server test with better timeout handling
"""

import json
import subprocess
import sys
import time
import threading
import queue


def run_mcp_test():
    """Test the MCP server with proper timeout handling"""
    print("🔍 Testing MCP server functionality...")
    
    try:
        # Start the MCP server
        proc = subprocess.Popen(
            [sys.executable, "src/dev_environment_mcp/server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        def read_output(proc, q):
            """Read output from process in separate thread"""
            try:
                while True:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    q.put(line.strip())
            except:
                pass
        
        # Start output reader thread
        output_queue = queue.Queue()
        reader_thread = threading.Thread(target=read_output, args=(proc, output_queue))
        reader_thread.daemon = True
        reader_thread.start()
        
        def send_request_and_get_response(request, description, timeout=5):
            """Send request and wait for response with timeout"""
            print(f"📤 {description}")
            proc.stdin.write(json.dumps(request) + "\n")
            proc.stdin.flush()
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    response = output_queue.get(timeout=0.1)
                    if response:
                        return json.loads(response)
                except queue.Empty:
                    continue
                except json.JSONDecodeError:
                    continue
            
            return None
        
        # Test 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        init_response = send_request_and_get_response(init_request, "Sending initialize request")
        if not init_response:
            print("❌ No response to initialize request")
            proc.terminate()
            return False
        
        server_name = init_response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')
        print(f"✅ Initialize response: {server_name}")
        
        # Test 2: Initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        proc.stdin.write(json.dumps(initialized_notification) + "\n")
        proc.stdin.flush()
        print("📤 Sent initialized notification")
        
        # Test 3: List tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        tools_response = send_request_and_get_response(tools_request, "Sending tools/list request")
        if not tools_response:
            print("❌ No response to tools/list request")
            proc.terminate()
            return False
        
        tools = tools_response.get('result', {}).get('tools', [])
        print(f"✅ Found {len(tools)} tools: {[t['name'] for t in tools]}")
        
        # Test 4: Call a tool
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
            
            tool_response = send_request_and_get_response(tool_call_request, "Testing detect_environment tool", timeout=10)
            if tool_response and 'result' in tool_response:
                print("✅ Tool call successful")
                content = tool_response.get('result', {}).get('content', [])
                if content and content[0].get('text'):
                    env_data = json.loads(content[0]['text'])
                    print(f"📄 Environment detected: OS={env_data.get('os_type')}, Shell={env_data.get('shell')}")
                proc.terminate()
                return True
            else:
                print(f"❌ Tool call failed or timed out: {tool_response}")
        
        proc.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        if 'proc' in locals():
            proc.terminate()
        return False


if __name__ == "__main__":
    if run_mcp_test():
        print("✅ MCP server test passed!")
        sys.exit(0)
    else:
        print("❌ MCP server test failed!")
        sys.exit(1)
