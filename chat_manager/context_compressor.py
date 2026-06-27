from typing import List, Dict, Any
from .turn_context import TurnContext
import math

class ContextWindow:
    def __init__(self, max_tokens: int = 10000):
        # Hermes-inspired limits
        self.max_tokens = max_tokens
        # 3K prompt + 6K output + 1K buffer = 10K total
        self.max_input_tokens = 3000

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Basic estimation: words * 1.3"""
        if not text:
            return 0
        return math.ceil(len(text.split()) * 1.3)

    def process_history(self, turns: List[TurnContext]) -> List[TurnContext]:
        """
        Trims and compresses the history to fit the token budget.
        Keeps the last 3-5 turns fully active.
        Compresses older turns.
        """
        # Sort by turn number to be sure
        sorted_turns = sorted(turns, key=lambda x: x.turn_number)
        
        # We always want to keep the last 4 turns uncompressed if possible (2 user, 2 assistant)
        recent_cutoff = max(0, len(sorted_turns) - 4)
        
        current_tokens = 0
        processed = []
        
        # Process from newest to oldest to guarantee we keep recent context
        for i in range(len(sorted_turns) - 1, -1, -1):
            turn = sorted_turns[i]
            
            # Re-estimate if missing
            if not turn.token_count:
                turn.token_count = self.estimate_tokens(turn.content)
                
            if i >= recent_cutoff:
                # Keep active
                turn.compressed = False
                added_tokens = turn.token_count
            else:
                # Mark as compressed
                turn.compressed = True
                if turn.summary:
                    added_tokens = self.estimate_tokens(turn.summary)
                else:
                    # If not yet summarized, use a minimal placeholder cost
                    added_tokens = 20
            
            # Check budget
            if current_tokens + added_tokens > self.max_input_tokens:
                # We reached our context limit for input. We stop including older turns.
                break
                
            current_tokens += added_tokens
            processed.insert(0, turn)
            
        return processed

    def build_prompt_context(self, processed_turns: List[TurnContext]) -> str:
        """
        Builds the string representation of the history to feed into Gemma.
        """
        lines = []
        for turn in processed_turns:
            role_str = "Utilisateur" if turn.role == "user" else "Assistant"
            content = turn.get_effective_content()
            lines.append(f"{role_str}: {content}")
        return "\n\n".join(lines)
