import unittest
from chat_manager.turn_context import TurnContext
from chat_manager.context_compressor import ContextWindow

class TestChatManager(unittest.TestCase):
    def test_context_window_compression(self):
        compressor = ContextWindow(max_tokens=10000)
        
        turns = []
        for i in range(1, 11):
            turns.append(TurnContext(
                turn_number=i,
                role="user" if i % 2 != 0 else "assistant",
                content=f"This is the full content of turn {i}. " * 50, # ~250 words
                token_count=300,
                summary=f"Summary of turn {i}" if i <= 6 else None
            ))
            
        processed = compressor.process_history(turns)
        
        # Check that we kept the 4 most recent uncompressed
        self.assertFalse(processed[-1].compressed) # Turn 10
        self.assertFalse(processed[-2].compressed) # Turn 9
        self.assertFalse(processed[-3].compressed) # Turn 8
        self.assertFalse(processed[-4].compressed) # Turn 7
        
        # Check that older ones are compressed
        self.assertTrue(processed[0].compressed)
        self.assertEqual(processed[0].get_effective_content(), "[Résumé] Summary of turn 1")

        # Verify token budget is under max_input_tokens (3000)
        total_tokens = sum(t.token_count if not t.compressed else compressor.estimate_tokens(t.summary or "") for t in processed)
        self.assertTrue(total_tokens <= compressor.max_input_tokens)

if __name__ == '__main__':
    unittest.main()
