"""
server.py — Karmic Gochara MCP Server (stdlib only, no external deps)
Port: localhost:8000

Architecture:
  GET  /health           → health check
  GET  /mcp/tools        → tool schemas (MCP format)
  POST /mcp/call         → execute tool
"""

import json
import logging
from datetime import datetime, date
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, List

# Import astro + doctrine
from astro_calc import calculate_transits
try:
    from doctrine import NAKSHATRA_KARMA, VAULT_CORE
except ImportError:
    NAKSHATRA_KARMA = {}
    VAULT_CORE = "Gochara doctrine reference"

# ──────────────────────────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────
# TOOLS SCHEMA (MCP format)
# ──────────────────────────────────────────────────────────────────

TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "name": "get_natal_chart",
        "description": "Calculate natal chart for a given birth data",
        "parameters": {
            "type": "object",
            "properties": {
                "birth_date": {
                    "type": "string",
                    "description": "Birth date as YYYY-MM-DD (e.g. '1974-10-31')"
                },
                "birth_time": {
                    "type": "string",
                    "description": "Birth time as HH:MM (24h, e.g. '08:25')"
                },
                "birth_place": {
                    "type": "string",
                    "description": "Birth place / city (e.g. 'Athis-Mons')"
                }
            },
            "required": ["birth_date", "birth_time", "birth_place"]
        }
    },
    {
        "name": "get_transits_today",
        "description": "Calculate current transits (today) based on natal chart data",
        "parameters": {
            "type": "object",
            "properties": {
                "natal_data": {
                    "type": "object",
                    "description": "Natal chart data from get_natal_chart"
                }
            },
            "required": ["natal_data"]
        }
    },
    {
        "name": "get_doctrine_reading",
        "description": "Generate complete astrological interpretation",
        "parameters": {
            "type": "object",
            "properties": {
                "natal_data": {"type": "object", "description": "Natal chart data"},
                "transits_data": {"type": "object", "description": "Current transits data"}
            },
            "required": ["natal_data", "transits_data"]
        }
    }
]


# ──────────────────────────────────────────────────────────────────
# TOOL IMPLEMENTATIONS
# ──────────────────────────────────────────────────────────────────

def tool_get_natal_chart(birth_date: str, birth_time: str, birth_place: str) -> Dict[str, Any]:
    """Get natal chart (returns birth data structure)."""
    try:
        bd = datetime.strptime(birth_date, "%Y-%m-%d")
        bt = datetime.strptime(birth_time, "%H:%M").time()
        birth_datetime = datetime.combine(bd.date(), bt)
        
        logger.info(f"Calculating natal chart: {birth_datetime} @ {birth_place}")
        
        natal_data = {
            "name": birth_place,
            "year": birth_datetime.year,
            "month": birth_datetime.month,
            "day": birth_datetime.day,
            "hour": birth_datetime.hour,
            "minute": birth_datetime.minute,
            "lat": 48.75,  # French default
            "lon": 2.35,
            "tz": "Europe/Paris",
            "city": birth_place
        }
        
        logger.info(f"Natal chart structure created for {birth_place}")
        return {
            "status": "ok",
            "birth_datetime": birth_datetime.isoformat(),
            "birth_place": birth_place,
            "natal_data": natal_data
        }
    except Exception as e:
        logger.error(f"Error calculating natal chart: {e}")
        return {"status": "error", "error": str(e)}


def tool_get_transits_today(natal_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get current transits (today)."""
    try:
        if not natal_data or "natal_data" not in natal_data:
            raise ValueError("natal_data must contain 'natal_data' key")
        
        natal = natal_data["natal_data"]
        today = date.today()
        
        logger.info(f"Calculating transits for today: {today}")
        
        transit_loc = {
            "lat": natal.get("lat", 48.75),
            "lon": natal.get("lon", 2.35),
            "tz": natal.get("tz", "Europe/Paris")
        }
        
        transits = calculate_transits(
            natal=natal,
            transit_loc=transit_loc,
            year=today.year,
            month=today.month,
            day=today.day,
            hour=12,
            minute=0
        )
        
        logger.info(f"Transits calculated for {today}")
        return {
            "status": "ok",
            "date": today.isoformat(),
            "transits": transits
        }
    except Exception as e:
        logger.error(f"Error calculating transits: {e}")
        return {"status": "error", "error": str(e)}


def tool_get_doctrine_reading(natal_data: Dict[str, Any], transits_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete doctrine reading."""
    try:
        if not natal_data or "natal_data" not in natal_data:
            raise ValueError("natal_data must contain 'natal_data' key")
        if not transits_data or "transits" not in transits_data:
            raise ValueError("transits_data must contain 'transits' key")
        
        natal = natal_data["natal_data"]
        transits = transits_data["transits"]
        
        logger.info("Generating doctrine reading...")
        
        reading = {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "birth_info": {
                "date": f"{natal.get('year')}-{natal.get('month'):02d}-{natal.get('day'):02d}",
                "time": f"{natal.get('hour'):02d}:{natal.get('minute'):02d}",
                "place": natal.get("city", "unknown")
            },
            "core_identity": VAULT_CORE[:300] + "..." if VAULT_CORE else "Gochara doctrine reference",
            "interpretation": {
                "nakshatra_karma": {},
                "transit_effects": {},
                "synthesis": ""
            }
        }
        
        # Transit effects summary
        reading["interpretation"]["transit_effects"] = {
            "total_aspects": len(transits.get("aspects", [])) if transits else 0,
            "major_transits": list(transits.keys())[:5] if transits else []
        }
        
        # Synthesis
        reading["interpretation"]["synthesis"] = (
            f"Doctrine reading for birth: {reading['birth_info']['date']} {reading['birth_info']['time']} "
            f"@ {reading['birth_info']['place']}. "
            f"Current transits indicate evolution through karmic themes. "
            f"Reference: Gochara Karmique MCP Server v1.0"
        )
        
        logger.info("Doctrine reading generated")
        return reading
    except Exception as e:
        logger.error(f"Error generating doctrine reading: {e}")
        return {"status": "error", "error": str(e)}


# ──────────────────────────────────────────────────────────────────
# HTTP HANDLER
# ──────────────────────────────────────────────────────────────────

class MCPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP endpoints."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "ok", "service": "karmic-mcp"}
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == "/mcp/tools":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(TOOLS_SCHEMA).encode())
            
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/mcp/call":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode()
                data = json.loads(body)
                
                tool = data.get("tool", "")
                args = data.get("args", {})
                
                logger.info(f"Tool call: {tool}")
                
                if tool == "get_natal_chart":
                    result = tool_get_natal_chart(
                        birth_date=args.get("birth_date", ""),
                        birth_time=args.get("birth_time", ""),
                        birth_place=args.get("birth_place", "")
                    )
                elif tool == "get_transits_today":
                    result = tool_get_transits_today(natal_data=args.get("natal_data", {}))
                elif tool == "get_doctrine_reading":
                    result = tool_get_doctrine_reading(
                        natal_data=args.get("natal_data", {}),
                        transits_data=args.get("transits_data", {})
                    )
                else:
                    result = {"status": "error", "error": f"Unknown tool: {tool}"}
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                logger.error(f"Error handling POST: {e}")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "error": str(e)}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        logger.info(format % args)


# ──────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Starting Karmic Gochara MCP Server on localhost:8000")
    server = HTTPServer(("127.0.0.1", 8000), MCPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
        server.server_close()
