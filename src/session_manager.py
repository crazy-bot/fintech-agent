import uuid
from typing import Dict, List
from collections import defaultdict

ConversationHistory = List[Dict[str, str]]

class SessionManager:
    """
    Manages conversation sessions and their history using an in-memory cache.
    """
    def __init__(self):
        """
        Initializes the in-memory store for conversation histories.
        """
        self.conversation_histories: Dict[str, ConversationHistory] = defaultdict(list)

    def start_session(self) -> str:
        """
        Generates a new, unique session ID and returns it.
        """
        session_id = str(uuid.uuid4())
        return session_id

    def get_history(self, session_id: str) -> ConversationHistory:
        """
        Retrieves the conversation history for a given session ID.
        """
        return self.conversation_histories[session_id]

    def add_message(self, session_id: str, role: str, content: str):
        """
        Adds a new message to the conversation history for a given session ID.
        
        Args:
            session_id: The ID of the conversation.
            role: The role of the message sender (e.g., 'user', 'assistant').
            content: The text content of the message.
        """
        self.conversation_histories[session_id].append({"role": role, "content": content})