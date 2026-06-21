#!/usr/bin/env python3
"""
test_mcp.py — MCP Tools Validation Suite
Jérôme's Karmic Gochara MCP Server

Tests en séquence :
1. get_natal_chart(1974-10-31, 08:25, Athis-Mons)
2. get_transits_today(natal_result)
3. get_doctrine_reading(natal_result, transits_result)

Chaque résultat : JSON parseable, status=ok
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"

# ──────────────────────────────────────────────────────────────────
# LOGGING / JSON OUTPUT
# ──────────────────────────────────────────────────────────────────

def log_json(event: str, data: Dict[str, Any]) -> None:
    """Log as JSON."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        **data
    }
    print(json.dumps(log_entry))


def call_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Call MCP tool via HTTP POST."""
    payload = json.dumps({"tool": tool_name, "args": args}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/mcp/call",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            return result
    except urllib.error.URLError as e:
        log_json("TOOL_CALL_ERROR", {
            "tool": tool_name,
            "error": str(e),
            "url": f"{BASE_URL}/mcp/call"
        })
        return {"status": "error", "error": str(e)}


# ──────────────────────────────────────────────────────────────────
# TEST SEQUENCE
# ──────────────────────────────────────────────────────────────────

def main():
    """Run validation suite."""
    print("# MCP VALIDATION SUITE", file=sys.stderr)
    
    # ─ Test 1: get_natal_chart ─
    print("", file=sys.stderr)
    print("## TEST 1: get_natal_chart", file=sys.stderr)
    
    natal_args = {
        "birth_date": "1974-10-31",
        "birth_time": "08:25",
        "birth_place": "Athis-Mons"
    }
    
    log_json("TEST_1_START", {
        "tool": "get_natal_chart",
        "args": natal_args
    })
    
    natal_result = call_tool("get_natal_chart", natal_args)
    
    print(f"Result: {json.dumps(natal_result, indent=2)}", file=sys.stderr)
    
    if natal_result.get("status") != "ok":
        log_json("TEST_1_FAIL", {
            "status": natal_result.get("status"),
            "error": natal_result.get("error")
        })
        return 1
    
    # Validate JSON
    if "natal_data" not in natal_result:
        log_json("TEST_1_FAIL", {"reason": "Missing 'natal_data' in result"})
        return 1
    
    log_json("TEST_1_PASS", {
        "natal_data_keys": list(natal_result["natal_data"].keys())
    })
    
    # ─ Test 2: get_transits_today ─
    print("", file=sys.stderr)
    print("## TEST 2: get_transits_today", file=sys.stderr)
    
    transits_args = {"natal_data": natal_result}
    
    log_json("TEST_2_START", {
        "tool": "get_transits_today",
        "natal_data_keys": list(natal_result.keys())
    })
    
    transits_result = call_tool("get_transits_today", transits_args)
    
    print(f"Result: {json.dumps(transits_result, indent=2)[:500]}...", file=sys.stderr)
    
    if transits_result.get("status") != "ok":
        log_json("TEST_2_FAIL", {
            "status": transits_result.get("status"),
            "error": transits_result.get("error")
        })
        return 1
    
    if "transits" not in transits_result:
        log_json("TEST_2_FAIL", {"reason": "Missing 'transits' in result"})
        return 1
    
    log_json("TEST_2_PASS", {
        "transits_keys": list(transits_result.get("transits", {}).keys())[:5]
    })
    
    # ─ Test 3: get_doctrine_reading ─
    print("", file=sys.stderr)
    print("## TEST 3: get_doctrine_reading", file=sys.stderr)
    
    doctrine_args = {
        "natal_data": natal_result,
        "transits_data": transits_result
    }
    
    log_json("TEST_3_START", {
        "tool": "get_doctrine_reading",
        "has_natal": "natal_data" in doctrine_args,
        "has_transits": "transits_data" in doctrine_args
    })
    
    doctrine_result = call_tool("get_doctrine_reading", doctrine_args)
    
    print(f"Result: {json.dumps(doctrine_result, indent=2)[:500]}...", file=sys.stderr)
    
    if doctrine_result.get("status") != "ok":
        log_json("TEST_3_FAIL", {
            "status": doctrine_result.get("status"),
            "error": doctrine_result.get("error")
        })
        return 1
    
    required_keys = ["timestamp", "birth_info", "interpretation"]
    missing = [k for k in required_keys if k not in doctrine_result]
    if missing:
        log_json("TEST_3_FAIL", {"missing_keys": missing})
        return 1
    
    log_json("TEST_3_PASS", {
        "interpretation_keys": list(doctrine_result.get("interpretation", {}).keys())
    })
    
    # ─ SUMMARY ─
    print("", file=sys.stderr)
    print("## SUMMARY", file=sys.stderr)
    
    log_json("ALL_TESTS_PASS", {
        "tests": 3,
        "server_url": BASE_URL,
        "natal_chart_valid": True,
        "transits_valid": True,
        "doctrine_reading_valid": True
    })
    
    print("", file=sys.stderr)
    print("✅ All 3 MCP tools validated successfully!", file=sys.stderr)
    print("   - get_natal_chart ✓", file=sys.stderr)
    print("   - get_transits_today ✓", file=sys.stderr)
    print("   - get_doctrine_reading ✓", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
