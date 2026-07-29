"""
COMPANION API - Universal Adapter
=================================
Simple HTTP/JSON API untuk companion layer.
Bisa dipanggil oleh Gemini CLI, Claude, atau AI lain.

Usage:
    python companion/api.py
    # Starts server on http://localhost:8080

Endpoints:
    POST /analyze     - Analyze intent
    POST /plan        - Plan steps
    POST /execute     - Execute tool
    POST /companion   - Full workflow (analyze + plan + execute)
    GET  /tools       - List available tools
    GET  /health      - Health check
"""

import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add companion to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from companion_core import (
    analyze_intent,
    plan_steps,
    get_command,
    learn,
    recall,
    memory_stats
)
from executor import Executor

# Configuration
PORT = 8080
HOST = "localhost"

# Initialize executor
executor = Executor()


class CompanionHandler(BaseHTTPRequestHandler):
    """HTTP handler for Companion API."""

    def _send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _read_json(self):
        """Read JSON from request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except:
            return {}

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            self._send_json({"status": "ok", "service": "companion-api"})
        elif path == "/tools":
            self._send_json({"tools": list(executor.script_map.keys())})
        elif path == "/stats":
            self._send_json(memory_stats())
        elif path == "/":
            self._send_json({
                "service": "Companion API",
                "version": "v4.3",
                "endpoints": ["/health", "/tools", "/stats", "/analyze", "/plan", "/execute", "/companion"]
            })
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        data = self._read_json()

        if path == "/analyze":
            result = self._analyze(data)
            self._send_json(result)

        elif path == "/plan":
            result = self._plan(data)
            self._send_json(result)

        elif path == "/execute":
            result = self._execute(data)
            self._send_json(result)

        elif path == "/companion":
            result = self._companion(data)
            self._send_json(result)

        else:
            self._send_json({"error": "Not found"}, 404)

    def _analyze(self, data):
        """Analyze user intent."""
        user_input = data.get("input", "")
        if not user_input:
            return {"error": "Missing 'input' field"}

        intent = analyze_intent(user_input)
        return {
            "clarity": intent.clarity,
            "intent_type": intent.intent_type,
            "keywords": intent.keywords,
            "needs_clarification": intent.needs_clarification,
            "clarification_msg": intent.clarification_msg
        }

    def _plan(self, data):
        """Plan execution steps."""
        user_input = data.get("input", "")
        if not user_input:
            return {"error": "Missing 'input' field"}

        intent = analyze_intent(user_input)
        steps = plan_steps(user_input, intent)

        return {
            "steps": [
                {
                    "order": s.order,
                    "tool": s.tool,
                    "params": s.params,
                    "reason": s.reason,
                    "needs_clarify": s.needs_clarify,
                    "command": get_command(s) if not s.needs_clarify else None
                }
                for s in steps
            ]
        }

    def _execute(self, data):
        """Execute a tool."""
        tool = data.get("tool", "")
        params = data.get("params", "")

        if not tool:
            return {"error": "Missing 'tool' field"}

        # Create step object
        class Step:
            tool = tool
            params = params
            needs_clarify = False

        result = executor.execute_step(Step())
        return {
            "success": result.success,
            "tool": result.tool,
            "output": result.output,
            "error": result.error,
            "duration_ms": result.duration_ms
        }

    def _companion(self, data):
        """Full companion workflow."""
        user_input = data.get("input", "")
        auto_execute = data.get("auto_execute", False)

        if not user_input:
            return {"error": "Missing 'input' field"}

        # Step 1: Analyze
        intent = analyze_intent(user_input)

        # Step 2: Plan
        steps = plan_steps(user_input, intent)

        # Step 3: Execute (if requested)
        results = []
        if auto_execute:
            for step in steps:
                if not step.needs_clarify:
                    exec_result = executor.execute_step(step)
                    results.append({
                        "tool": exec_result.tool,
                        "success": exec_result.success,
                        "output": exec_result.output[:500] if exec_result.output else None,  # Truncate
                        "error": exec_result.error,
                        "duration_ms": exec_result.duration_ms
                    })
                    # Learn
                    learn(user_input, intent.keywords, step.tool, exec_result.success)

        return {
            "input": user_input,
            "intent": {
                "clarity": intent.clarity,
                "keywords": intent.keywords,
                "needs_clarification": intent.needs_clarification
            },
            "steps": [
                {
                    "tool": s.tool,
                    "params": s.params,
                    "command": get_command(s) if not s.needs_clarify else None,
                    "needs_clarify": s.needs_clarify
                }
                for s in steps
            ],
            "execution_results": results if auto_execute else None,
            "suggestion": recall(user_input, intent.keywords)
        }


def run_server(port=PORT, host=HOST):
    """Run the API server."""
    server = HTTPServer((host, port), CompanionHandler)
    print(f"=" * 60)
    print(f"COMPANION API SERVER")
    print(f"=" * 60)
    print(f"URL: http://{host}:{port}")
    print(f"")
    print(f"Endpoints:")
    print(f"  GET  /health     - Health check")
    print(f"  GET  /tools      - List tools")
    print(f"  GET  /stats      - Memory stats")
    print(f"  POST /analyze    - Analyze intent")
    print(f"  POST /plan       - Plan steps")
    print(f"  POST /execute    - Execute tool")
    print(f"  POST /companion  - Full workflow")
    print(f"")
    print(f"Example:")
    print(f'  curl -X POST http://{host}:{port}/companion \\')
    print(f'    -H "Content-Type: application/json" \\')
    print(f'    -d \'{{"input": "cari semua import axios"}}\'')
    print(f"")
    print(f"Press Ctrl+C to stop")
    print(f"=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Companion API Server")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port (default: {PORT})")
    parser.add_argument("--host", type=str, default=HOST, help=f"Host (default: {HOST})")
    args = parser.parse_args()

    run_server(port=args.port, host=args.host)
