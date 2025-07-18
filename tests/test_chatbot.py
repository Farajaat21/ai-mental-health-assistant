import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.mood import classify_emotion, ConversationContext, analyze_mood
from models.chat import ChatManager, get_dynamic_greeting

class TestChatbot(unittest.TestCase):
    def setUp(self):
        self.chat_manager = ChatManager()
        self.context = ConversationContext()

    def test_emotion_classification(self):
        """Test emotion classification for different types of messages"""
        test_cases = [
            # Format: (input_message, expected_emotion, expected_depth, needs_quote)
            ("hi there", "Casual", "shallow", False),
            ("I feel really sad today", "Deep sadness", "deep", True),
            ("I'm failing all my classes", "Academic stress", "deep", True),
            ("I feel so alone", "Loneliness", "deep", True),
            ("I'm really anxious about everything", "Anxiety", "deep", True)
        ]

        for message, expected_emotion, expected_depth, expected_quote in test_cases:
            emotion, depth, needs_quote = classify_emotion(message)
            self.assertEqual(emotion, expected_emotion, f"Failed for message: {message}")
            self.assertEqual(depth, expected_depth, f"Wrong depth for: {message}")
            self.assertEqual(needs_quote, expected_quote, f"Wrong quote flag for: {message}")

    def test_conversation_context(self):
        """Test conversation context management"""
        context = ConversationContext()
        context.add_message("I'm feeling sad", "sadness")
        context.add_message("No one understands me", "loneliness")
        
        self.assertEqual(len(context.history), 2)
        self.assertEqual(context.history[-1]['emotion'], "loneliness")

    def test_follow_up_detection(self):
        """Test follow-up message detection"""
        context = ConversationContext()
        context.add_message("I'm having a hard time at school", "academic stress")
        
        follow_ups = [
            "it's really affecting my grades",
            "yes, that's exactly how I feel",
            "because I can't focus",
            "that's what I meant"
        ]
        
        for message in follow_ups:
            self.assertTrue(context._basic_follow_up_check(message), 
                          f"Failed to detect follow-up: {message}")

    def test_mixed_emotions(self):
        """Test detection of mixed emotions"""
        mixed_messages = [
            "I'm happy but also sad",
            "part of me is excited but I'm also nervous",
            "I feel both grateful and anxious"
        ]
        
        for message in mixed_messages:
            emotion, depth, needs_quote = classify_emotion(message)
            self.assertEqual(emotion, "Mixed emotions", 
                           f"Failed to detect mixed emotions in: {message}")
            self.assertTrue(needs_quote)

    def test_greeting_responses(self):
        """Test appropriate responses to greetings"""
        greetings = [
            "hi",
            "hello",
            "hey there",
            "good morning"
        ]
        
        for greeting in greetings:
            emotion, depth, needs_quote = classify_emotion(greeting)
            self.assertEqual(emotion, "Casual",
                           f"Wrong emotion for greeting: {greeting}")
            self.assertFalse(needs_quote,
                           f"Greeting shouldn't need quote: {greeting}")

    def test_crisis_detection(self):
        """Test detection of crisis messages"""
        crisis_messages = [
            "I want to end it all",
            "I don't want to live anymore",
            "thinking of suicide"
        ]
        
        for message in crisis_messages:
            emotion, depth, needs_quote = classify_emotion(message)
            self.assertEqual(emotion, "Crisis",
                           f"Failed to detect crisis in: {message}")
            self.assertEqual(depth, "deep")
            self.assertTrue(needs_quote)

    def test_chat_history(self):
        """Test chat history management"""
        self.chat_manager.add_to_history("test_user", "Hello")
        self.chat_manager.add_to_history("test_user", "I'm feeling sad", "user")
        self.chat_manager.add_to_history("test_user", "I understand how you feel", "bot")
        
        history = self.chat_manager.get_conversation_context("test_user")
        self.assertEqual(len(history), 3)

    def test_academic_stress(self):
        """Test detection of academic-related stress"""
        academic_messages = [
            ("I'm failing my classes", "Academic stress"),
            ("My grades are terrible", "Academic stress"),
            ("Can't keep up with coursework", "Academic stress"),
            ("Stressed about exams", "Academic stress")
        ]
        
        for message, expected in academic_messages:
            emotion, depth, needs_quote = classify_emotion(message)
            self.assertEqual(emotion, expected, 
                           f"Failed to detect academic stress in: {message}")
            self.assertTrue(needs_quote)

    def test_emotion_intensity(self):
        """Test detection of emotion intensity"""
        intensity_pairs = [
            ("I'm sad", "General sadness"),
            ("I'm really sad", "Deep sadness"),
            ("I'm so incredibly sad", "Deep sadness"),
            ("feeling down", "General sadness"),
            ("feeling completely broken", "Deep sadness")
        ]
        
        for message, expected in intensity_pairs:
            emotion, depth, _ = classify_emotion(message)
            self.assertEqual(emotion, expected,
                           f"Wrong intensity detected for: {message}")

    def test_conversation_flow(self):
        """Test conversation flow and context maintenance"""
        context = ConversationContext()
        
        # Simulate a conversation
        messages = [
            ("Hi there", "Casual"),
            ("I'm not doing well", "General sadness"),
            ("Everything feels hopeless", "Deep sadness"),
            ("yes, exactly", "Deep sadness"),  # Follow-up
            ("I can't focus on anything", "Helplessness")
        ]
        
        for message, expected_emotion in messages:
            emotion, _, _ = classify_emotion(message)
            context.add_message(message, emotion)
            self.assertEqual(emotion, expected_emotion,
                           f"Wrong emotion for message: {message}")
            
        # Test context length
        self.assertEqual(len(context.history), 5)
        
        # Test follow-up detection
        self.assertTrue(context._basic_follow_up_check("yes, exactly"))
        self.assertTrue(context._basic_follow_up_check("that's how I feel"))
        self.assertFalse(context._basic_follow_up_check("I like pizza"))

if __name__ == '__main__':
    unittest.main(verbosity=2)