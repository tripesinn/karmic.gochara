from typing import Dict, Any, Tuple
from .turn_context import TurnContext
from .context_compressor import ContextWindow
from .firestore_journal import FirestoreJournal
import logging

class ConversationLoop:
    def __init__(self):
        self.journal = FirestoreJournal()
        self.compressor = ContextWindow(max_tokens=10000)

    def handle_turn(
        self, 
        uid: str, 
        chat_id: str, 
        message: str, 
        user_context: Dict[str, Any], 
        system_prompt: str
    ) -> Tuple[str, int]:
        """
        Handles a complete chat turn:
        1. Loads history
        2. Adds user message
        3. Builds context
        4. Calls AI
        5. Saves AI response
        6. Triggers background compression for older turns
        
        Returns: (answer_text, tokens_remaining_estimation)
        """
        # 1. Load existing history
        history = self.journal.load_chat(uid, chat_id)
        current_turn_num = len(history) + 1
        
        # 2. Add user message
        user_turn = TurnContext(
            turn_number=current_turn_num,
            role="user",
            content=message,
            token_count=self.compressor.estimate_tokens(message)
        )
        user_turn_id = self.journal.save_turn(uid, chat_id, user_turn)
        history.append(user_turn)
        
        # 3. Apply Context Window (budgets and uses summaries where available)
        processed_history = self.compressor.process_history(history)
        history_context_str = self.compressor.build_prompt_context(processed_history)
        
        # 4. Generate AI response
        from ai_interpret import generate_ai
        
        # Construct the final prompt for Gemma
        if history_context_str:
            final_prompt = f"Historique de la conversation:\n\n{history_context_str}\n\nNouveau message de l'utilisateur:\n{message}"
        else:
            final_prompt = message
            
        try:
            # We assume Gemma max_tokens for generation is about 1024 or 2000
            answer = generate_ai(system_prompt, final_prompt, user=user_context, max_tokens=2000).strip()
        except Exception as e:
            logging.error(f"Error calling AI in ConversationLoop: {e}")
            raise e

        # 5. Save AI response
        ai_turn_num = current_turn_num + 1
        ai_turn = TurnContext(
            turn_number=ai_turn_num,
            role="assistant",
            content=answer,
            token_count=self.compressor.estimate_tokens(answer)
        )
        ai_turn_id = self.journal.save_turn(uid, chat_id, ai_turn)
        history.append(ai_turn)
        
        # 6. Trigger background compression for older turns
        # N-4 turns ago (or older) should be compressed.
        recent_cutoff_idx = max(0, len(history) - 4)
        for i in range(recent_cutoff_idx):
            past_turn = history[i]
            if not past_turn.compressed and past_turn.turn_id:
                self.journal.compress_turn_async(uid, chat_id, past_turn.turn_id, past_turn, user_context)

        # Return answer
        return answer, 1000  # Return estimation of remaining quota based on your plan
