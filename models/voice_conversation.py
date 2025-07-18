import openai
import logging
from typing import Tuple

class VoiceConversationHandler:
    def __init__(self):
        self.conversation_history = []
        self.response_cache = {}
        self.common_responses = {
            "greeting": "Hello! I'm here to listen and support you. How are you feeling today?",
            "acknowledgment": "I understand. Please tell me more about that.",
            "empathy": "That sounds really difficult. I'm here to listen.",
            "encouragement": "You're showing great strength in sharing this.",
            "clarification": "Could you tell me more about how that makes you feel?",
            "support": "You don't have to go through this alone."
        }
        
    def preload_responses(self):
        """Preload common responses for faster interaction"""
        common_scenarios = [
            "feeling sad",
            "feeling anxious",
            "feeling overwhelmed",
            "feeling lonely",
            "need help",
            "can't sleep",
            "stressed out"
        ]
        
        for scenario in common_scenarios:
            self.response_cache[scenario] = self._generate_cached_response(scenario)
    
    def _generate_cached_response(self, scenario):
        """Generate and cache response for common scenarios"""
        emotion = self._quick_emotion_check(scenario)
        return {
            "response": self._get_quick_response(scenario, emotion),
            "emotion": emotion,
            "follow_up": self._get_follow_up_question(emotion)
        }
    
    def _quick_emotion_check(self, text):
        """Quick emotion detection without API call"""
        emotion_keywords = {
            "sad": "sadness",
            "anxious": "anxiety",
            "worried": "anxiety",
            "lonely": "loneliness",
            "tired": "exhaustion",
            "angry": "anger",
            "happy": "joy",
            "scared": "fear"
        }
        
        for keyword, emotion in emotion_keywords.items():
            if keyword in text.lower():
                return emotion
        return "neutral"
    
    def _get_quick_response(self, text, emotion):
        """Get immediate response while waiting for full processing"""
        if emotion in self.common_responses:
            return self.common_responses[emotion]
        return self.common_responses["empathy"]
    
    def generate_voice_response(self, user_input: str) -> tuple:
        """Enhanced voice response generation"""
        try:
            # Check cache first for instant response
            cached = self._check_cache(user_input)
            if cached:
                return cached["emotion"], cached["response"]
            
            # Quick initial response while processing
            quick_response = self._get_immediate_response(user_input)
            
            # Process full response asynchronously
            full_response = self._process_full_response(user_input)
            
            return "processing", quick_response, full_response
            
        except Exception as e:
            logging.error(f"Voice response error: {e}")
            return "error", "I'm listening. Please continue."
    
    def _check_cache(self, text):
        """Check if we have a cached response"""
        for key, response in self.response_cache.items():
            if key in text.lower():
                return response
        return None
    
    def _get_immediate_response(self, text):
        """Get immediate response while processing"""
        emotion = self._quick_emotion_check(text)
        return self.common_responses.get(emotion, self.common_responses["acknowledgment"])

    def generate_voice_response(self, user_input: str) -> Tuple[str, str]:
        """Generate a supportive conversational response."""
        try:
            system_prompt = """You are MentalAI, a compassionate AI companion trained to provide emotional support.
            IMPORTANT:
            - Always respond with empathy and understanding
            - Validate the user's feelings
            - Provide constructive suggestions when appropriate
            - Be supportive but maintain appropriate boundaries
            - If user mentions self-harm or severe crisis, gently guide them to professional help
            - Keep responses concise but meaningful (2-3 sentences)
            - End with a gentle follow-up question to encourage dialogue
            
            Remember: While you should encourage professional help when needed, you should always 
            provide immediate emotional support and never dismiss the user's feelings. peofessinal help should only be recommmnede in serious situation like sefl harm
            
            IMPORTANT
            - Keep converstion short and supportive
            
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                *[{"role": "user" if i % 2 == 0 else "assistant", "content": msg} 
                  for i, msg in enumerate(self.conversation_history)],
                {"role": "user", "content": user_input}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            reply = response.choices[0].message.content.strip()
            self.conversation_history.extend([user_input, reply])
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
                
            return "Voice", reply
            
        except Exception as e:
            logging.error(f"Error in voice conversation: {e}")
            return "Error", "I'm listening. Could you please say that again?"
            
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
