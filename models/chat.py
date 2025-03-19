from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class ChatManager:
    def __init__(self):
        self.DEFAULT_QUOTES = [
            "🌟 Your mental health is a priority. Take it one day at a time.",
            "🦋 Every small step forward is still progress!",
            "💫 Healing isn't linear, and that's perfectly okay",
            "🌈 You don't have to have it all figured out right now",
            "💪 Your feelings are valid. You matter.",
            "✨ Be gentle with yourself, you're doing the best you can",
            "🌺 Self-care isn't selfish, it's necessary",
            "🍃 Breathe in peace, breathe out stress",
            "🌙 Even the darkest night will end and the sun will rise",
            "💭 It's okay to take a break when you need one",
            "🌞 New day, new opportunities for growth",
            "💝 You are stronger than you think",
            "🎭 It's okay not to be okay sometimes",
            "🌱 Growth takes time and patience",
            "💫 Your story isn't over yet"
        ]
        self.conversation_history = {}  

    def add_to_history(self, username, message, role='user'):
        """Add message to conversation history"""
        if username not in self.conversation_history:
            self.conversation_history[username] = []
            # Add initial context about the user
            self.conversation_history[username].append({
                'role': 'system',
                'content': f'User identified as: {username}' if username != 'Guest' else 'Anonymous user'
            })
        
        self.conversation_history[username].append({
            'role': role,
            'content': message
        })
        
        # Keep last 10 messages for context
        self.conversation_history[username] = self.conversation_history[username][-10:]

    def get_conversation_context(self, username):
        """Get recent conversation history"""
        if username not in self.conversation_history:
            return []
        return [msg['content'] for msg in self.conversation_history[username]]

    def get_default_quote(self):
        import random
        return random.choice(self.DEFAULT_QUOTES)

    def generate_quote_prompt(self, message, mood):
        """Generate a quote prompt that includes the mood label."""
        try:
            emotion_templates = {
                "Deep sadness": "When experiencing deep sadness and loss",
                "Anxiety": "When feeling overwhelmed with anxiety",
                "Depression": "When battling depression",
                "Loneliness": "When feeling isolated and alone",
                "Hopelessness": "When struggling to find hope",
                "Grief": "When dealing with grief and loss",
                "Trauma": "When healing from trauma",
                "Stress": "When overwhelmed by stress"
            }
            
            template = emotion_templates.get(mood, f"When dealing with {mood}")
            return f"Generate a meaningful and comforting quote specifically for someone {template}. The quote should be profound and relevant to: {message}"
            
        except Exception as e:
            logging.error(f"Error generating quote prompt: {e}")
            return None

# Update get_dynamic_greeting to handle names better
def get_dynamic_greeting(username):
    """Generate personalized initial greeting"""
    from models.info import app_description
    greeting_prompt = f"""
    Generate an initial greeting for a mental health support conversation.
    User status: {"Returning user named " + username if username != "Guest" else "New anonymous user"}

    Requirements:
    - For named users, welcome them by name.
    - For anonymous users, provide a warm general welcome.
    - Keep it simple and encouraging.
    - Always include a follow-up question.
    """
    
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-4",  # updated to use gpt-4
        messages=[
            {"role": "system", "content": app_description},
            {"role": "user", "content": greeting_prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

chat_manager = ChatManager()
