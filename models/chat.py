from typing import Dict, List

DEFAULT_QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Life is 10% what happens to us and 90% how we react to it. - Charles R. Swindoll",
    "Your time is limited, don't waste it living someone else's life. - Steve Jobs",
    "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt"
]

class ChatManager:
    def __init__(self):
        self.conversation_history: Dict[str, List[Dict]] = {}
        
    def generate_quote_prompt(self, message: str, mood: str) -> str:
        return f"""Based on the user's message: '{message}' and their emotional state: {mood},
        provide a short, meaningful quote that:
        1. Relates to their current situation or feelings
        2. Offers comfort, wisdom, or encouragement
        3. Is concise and impactful
        
        Format: Only return the quote and its author in this format: 'quote - author'"""

    def get_default_quote(self) -> str:
        """Return a default quote when no conversation has started."""
        return DEFAULT_QUOTES[0]

chat_manager = ChatManager()
