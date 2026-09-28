#!/usr/bin/env python3
"""Call a tool on the HRDKorea public-data MCP server (openapi.hrdkorea.or.kr/mcp).

Usage:
  python3 call.py list-tools                 # print all available tools + schemas
  python3 call.py <tool_name> '<json_args>'  # call one tool with JSON arguments
  python3 call.py <tool_name>                # call with no arguments

Examples:
  python3 call.py search_qualification '{"keyword": "전기"}'
  python3 call.py get_exam_schedule '{"qualification_name": "정보처리기사"}'

The server speaks MCP over HTTP POST (JSON-RPC 2.0) and answers as an SSE
stream ("event: message\ndata: {...}"). This script handles initialize,
notifications/initialized, and parsing the SSE response automatically.
All tools are read-only lookups; nothing is ever written or submitted.
"""
import json
import sys
import urllib.request

ENDPOINT = "https://openapi.hrdkorea.or.kr/mcp"


def _post(payload):
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8")


def _parse(raw):
    """Parse either plain JSON or an SSE stream into the JSON-RPC result."""
    raw = raw.strip()
    if raw.startswith("{"):
        return json.loads(raw)
    for line in raw.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:])
    raise RuntimeError(f"Unrecognized response format:\n{raw[:500]}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    # Handshake: initialize + initialized notification
    init = _post({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "hrdk-skill", "version": "1.0"},
        },
    })
    _post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    if cmd == "list-tools":
        data = _parse(_post({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}))
        for t in data["result"]["tools"]:
            schema = json.dumps(t.get("inputSchema", {}), ensure_ascii=False)
            print(f"### {t['name']}\n{t.get('description', '')}\n{schema}\n")
        return

    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    data = _parse(_post({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": cmd, "arguments": args},
    }))
    result = data.get("result", {})
    if data.get("error"):
        print(json.dumps(data["error"], ensure_ascii=False, indent=2))
        sys.exit(1)
    # Tool results come back as content blocks; extract text payloads.
    out = []
    for block in result.get("content", []):
        if block.get("type") == "text":
            out.append(block["text"])
        else:
            out.append(json.dumps(block, ensure_ascii=False))
    print("\n".join(out) if out else json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
