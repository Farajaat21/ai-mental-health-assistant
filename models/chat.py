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
        
        self.conversation_history[username].append({
            'role': role,
            'content': message
        })
        
        # Keep last 10 messages for context
        self.conversation_history[username] = self.conversation_history[username][-10:]

    def get_conversation_context(self, username):
        """Get conversation history for a user"""
        if username not in self.conversation_history:
            return []
        return self.conversation_history[username]

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
                "Stress": "When overwhelmed by stress",
                "Academic stress": "When struggling with academic challenges and pressure"
            }
            
            template = emotion_templates.get(mood, f"When dealing with {mood}")
            return f"Generate a meaningful and comforting quote specifically for someone {template}. The quote should be profound and relevant to: {message}"
            
        except Exception as e:
            logging.error(f"Error generating quote prompt: {e}")
            return None

# Update get_dynamic_greeting to handle names better
def get_dynamic_greeting(username):
    """Generate personalized initial greeting"""
    try:
        from models.info import app_description
        
        if not openai.api_key:
            raise ValueError("OpenAI API key not configured")

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": app_description},
                {"role": "user", "content": f"Generate a warm greeting for {username}"}
            ],
            temperature=0.7,
            max_tokens=100,  # Limit token usage
            timeout=10  # Add timeout
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error generating greeting: {str(e)}")
        # Return a fallback greeting
        if username != "Guest":
            return f"Welcome back, {username}! How are you feeling today?"
        return "Hello! I'm here to listen and support you. How are you feeling today?"

def format_sadness_response(emotion, message):
    """Format the prompt for sadness-related emotions."""
    # Always include an encouraging quote for sad emotions
    return f'''
    The user is experiencing {emotion}. Their message: "{message}"
    
    IMPORTANT - Your response MUST follow this EXACT format:
    1. Start with a relevant quote in quotes followed by author: "Quote" - Author
    2. Leave one blank line
    3. Write a validating and empathetic response
    4. End with a gentle question to encourage sharing
    
    Example format:
    "Hope is the thing with feathers that perches in the soul" - Emily Dickinson
    
    I understand you're feeling [emotion]. [Empathetic response]
    
    [Gentle follow-up question]?
    '''

def process_response(response_text):
    """Ensure response follows the correct format with quote."""
    if '"' not in response_text:
        quote = chat_manager.get_default_quote()
        return f'"{quote}"\n\n{response_text}'
        
    parts = response_text.split('\n\n', 1)
    if len(parts) < 2:
        quote = parts[0] if '"' in parts[0] else chat_manager.get_default_quote()
        return f'{quote}\n\n{response_text}'
        
    return response_text

chat_manager = ChatManager()
