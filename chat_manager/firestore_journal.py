import threading
import uuid
from typing import List, Optional
from datetime import datetime, UTC
from google.cloud import firestore

from .turn_context import TurnContext
from .context_compressor import ContextWindow

# Initialize Firestore client globally
db = firestore.Client()

class FirestoreJournal:
    def __init__(self):
        self.db = db

    def get_user_ref(self, uid: str):
        return self.db.collection("users").document(uid)

    def load_chat(self, uid: str, chat_id: str) -> List[TurnContext]:
        """Loads all turns for a given chat, ordered by turn_number."""
        turns_ref = (
            self.get_user_ref(uid)
            .collection("chats").document(chat_id)
            .collection("turns")
            .order_by("turn_number")
        )
        docs = turns_ref.stream()
        
        turns = []
        for doc in docs:
            data = doc.to_dict()
            turn = TurnContext.from_dict(data)
            turn.turn_id = doc.id
            turns.append(turn)
            
        return turns

    def save_turn(self, uid: str, chat_id: str, turn: TurnContext) -> str:
        """Saves a new turn to Firestore and returns the turn document ID."""
        chat_ref = self.get_user_ref(uid).collection("chats").document(chat_id)
        
        # Ensure chat document exists
        chat_doc = chat_ref.get()
        if not chat_doc.exists:
            chat_ref.set({"created_at": datetime.now(UTC).isoformat()})
            
        turn_id = str(uuid.uuid4())
        chat_ref.collection("turns").document(turn_id).set(turn.to_dict())
        return turn_id

    def update_turn(self, uid: str, chat_id: str, turn_id: str, turn: TurnContext):
        """Updates an existing turn (useful after compression)."""
        turn_ref = (
            self.get_user_ref(uid)
            .collection("chats").document(chat_id)
            .collection("turns").document(turn_id)
        )
        turn_ref.update({
            "compressed": turn.compressed,
            "summary": turn.summary,
            "token_count": turn.token_count
        })

    def compress_turn_async(self, uid: str, chat_id: str, turn_id: str, turn: TurnContext, user_context: dict):
        """
        Background task: 
        Summarize the turn content and save it back to Firestore.
        Short-circuited so the user isn't blocked.
        """
        def _compress():
            try:
                from ai_interpret import generate_ai
                system_prompt = (
                    "Tu es un expert en synthèse pour la gestion de contexte LLM. "
                    "Résume le propos de ce message en une courte phrase très concise (15-20 mots max). "
                    "Conserve uniquement l'information vitale pour la continuité de la conversation astrologique."
                )
                user_prompt = f"Message à résumer :\n\n{turn.content}"
                
                # We use a short limit
                summary = generate_ai(system_prompt, user_prompt, user=user_context, max_tokens=100)
                
                turn.summary = summary.strip()
                turn.compressed = True
                turn.token_count = ContextWindow.estimate_tokens(turn.summary)
                
                # Update in firestore
                self.update_turn(uid, chat_id, turn_id, turn)
            except Exception as e:
                import logging
                logging.error(f"Error compressing turn {turn_id}: {e}")

        # Start thread
        t = threading.Thread(target=_compress)
        t.start()
