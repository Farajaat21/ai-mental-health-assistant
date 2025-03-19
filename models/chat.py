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
        self.greeting_responses = [
            "Hi! 👋 How can I help you today?",
            "Hello again! Is there something specific you'd like to talk about?",
            "I notice you're saying hello again. Is everything okay?",
            "I'm still here! Would you like to talk about something in particular?",
            "Hey! I'm listening if you want to share what's on your mind."
        ]
        self.greeting_count = {}  # Track greeting counts per user
        self.informal_responses = {
            "idk": "That's okay! 'IDK' means 'I don't know'. If you're feeling uncertain or confused about something, I'm here to help. Would you like to talk about what's on your mind?",
            "k": "I see! Just checking - is there anything specific you'd like to discuss?",
            "nah": "Alright! But remember, I'm here if you need someone to talk to.",
            "whatever": "I sense you might be feeling dismissive. Is everything okay?",
            "idc": "I understand you might not care right now, but I'm here to listen if you want to talk about anything bothering you."
        }

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

    def handle_repeated_greeting(self, username):
        """Handle repeated greetings from the same user"""
        count = self.greeting_count.get(username, 0)
        self.greeting_count[username] = count + 1
        
        if count >= len(self.greeting_responses) - 1:
            return self.greeting_responses[-1]
        return self.greeting_responses[count]

    def reset_greeting_count(self, username):
        """Reset the greeting counter for a user"""
        self.greeting_count[username] = 0

    def handle_informal_message(self, message):
        """Handle informal/casual messages appropriately"""
        message = message.lower().strip()
        
        # Check if it's an informal message we recognize
        if message in self.informal_responses:
            return self.informal_responses[message]
            
        return None

chat_manager = ChatManager()
