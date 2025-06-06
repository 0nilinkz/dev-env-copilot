#!/usr/bin/env python3
"""
Debug NPM wrapper specifically
"""

import json
import subprocess

def test_npm_wrapper_debug():
    """Debug test for NPM wrapper"""
    print("🔍 Testing NPM wrapper with detailed debugging...")
    
    try:
        proc = subprocess.Popen(
            ["node", "bin/dev-env-copilot.js"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Send initialize request
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
        
        print(f"📤 Sending: {json.dumps(init_request)}")
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Read response
        print("📥 Reading response...")
        response = proc.stdout.readline()
        stderr_data = proc.stderr.readline()
        
        print(f"STDOUT: '{response.strip()}'")
        print(f"STDERR: '{stderr_data.strip()}'")
        
        if response:
            try:
                parsed = json.loads(response)
                print(f"✅ Parsed JSON: {parsed}")
                
                if "result" in parsed:
                    print("✅ NPM wrapper is working!")
                else:
                    print("❌ No result field in response")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {repr(response)}")
        else:
            print("❌ No response received")
            
        proc.terminate()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_npm_wrapper_debug()
