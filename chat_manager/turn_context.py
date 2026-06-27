from datetime import datetime, UTC
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class TurnContext:
    turn_number: int
    role: str  # 'user' or 'assistant'
    content: str
    token_count: int
    compressed: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    summary: Optional[str] = None
    turn_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_number": self.turn_number,
            "role": self.role,
            "content": self.content,
            "token_count": self.token_count,
            "compressed": self.compressed,
            "timestamp": self.timestamp,
            "summary": self.summary
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TurnContext":
        return cls(
            turn_number=data.get("turn_number", 0),
            role=data.get("role", "user"),
            content=data.get("content", ""),
            token_count=data.get("token_count", 0),
            compressed=data.get("compressed", False),
            timestamp=data.get("timestamp", datetime.now(UTC).isoformat()),
            summary=data.get("summary"),
            turn_id=data.get("turn_id")
        )

    def get_effective_content(self) -> str:
        """Returns the summary if compressed, otherwise the full content."""
        if self.compressed and self.summary:
            return f"[Résumé] {self.summary}"
        return self.content
