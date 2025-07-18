import unittest
from models.mood import analyze_mood, ConversationContext, classify_emotion

class TestChatbotDemo(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.context = ConversationContext()
        
    def test_1_basic_greeting_flow(self):
        """Test basic greeting and response flow"""
        emotion, depth, needs_quote = classify_emotion("Hi, how are you?")
        self.assertEqual(emotion, "Casual")
        self.assertEqual(depth, "shallow")
        self.assertFalse(needs_quote)
        
    def test_2_emotional_disclosure(self):
        """Test handling of emotional disclosure"""
        emotion, depth, needs_quote = classify_emotion("I'm feeling really sad today")
        self.assertEqual(emotion, "Deep sadness")
        self.assertEqual(depth, "deep")
        self.assertTrue(needs_quote)
        
    def test_3_crisis_detection(self):
        """Test crisis situation detection"""
        emotion, depth, needs_quote = classify_emotion("I just want to disappear")
        self.assertIn(emotion, ["Deep sadness", "Helplessness"])
        self.assertEqual(depth, "deep")
        self.assertTrue(needs_quote)
        
    def test_4_mixed_emotions(self):
        """Test handling of mixed emotions"""
        emotion, depth, needs_quote = classify_emotion("I'm happy about my job but also really anxious about everything else")
        self.assertEqual(emotion, "Mixed emotions")
        self.assertEqual(depth, "deep")
        self.assertTrue(needs_quote)
        
    def test_5_follow_up_questions(self):
        """Test follow-up question handling"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I'm struggling with everything")
        self.assertIn(emotion1, ["Overwhelmed", "Helplessness"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("It's just too much to handle")
        self.assertIn(emotion2, ["Overwhelmed", "Helplessness"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
    def test_6_topic_transition(self):
        """Test topic transition handling"""
        # First topic
        emotion1, depth1, needs_quote1 = classify_emotion("I'm worried about my grades")
        self.assertEqual(emotion1, "Academic stress")
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # New topic
        emotion2, depth2, needs_quote2 = classify_emotion("My family doesn't understand me")
        self.assertIn(emotion2, ["Family concern", "Loneliness"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
    def test_7_casual_vs_sensitive(self):
        """Test distinction between casual and sensitive topics"""
        # Casual message
        emotion1, depth1, needs_quote1 = classify_emotion("How's the weather?")
        self.assertEqual(emotion1, "Casual")
        self.assertEqual(depth1, "shallow")
        self.assertFalse(needs_quote1)
        
        # Sensitive topic
        emotion2, depth2, needs_quote2 = classify_emotion("I feel so alone")
        self.assertEqual(emotion2, "Loneliness")
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
    def test_8_emotional_progression(self):
        """Test tracking of emotional progression"""
        emotion1, depth1, needs_quote1 = classify_emotion("I'm feeling down")
        self.assertIn(emotion1, ["General sadness", "Deep sadness"])
        self.assertTrue(needs_quote1)
        
        emotion2, depth2, needs_quote2 = classify_emotion("Everything seems pointless")
        self.assertIn(emotion2, ["Deep sadness", "Helplessness"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        emotion3, depth3, needs_quote3 = classify_emotion("I don't know what to do anymore")
        self.assertIn(emotion3, ["Helplessness", "Deep sadness"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_9_complex_emotional_states(self):
        """Test handling of complex emotional expressions"""
        emotion, depth, needs_quote = classify_emotion("I'm trying to be strong but inside I'm falling apart")
        self.assertIn(emotion, ["Mixed emotions", "Deep sadness"])
        self.assertEqual(depth, "deep")
        self.assertTrue(needs_quote)
        
    def test_10_recovery_and_support(self):
        """Test responses in recovery scenarios"""
        emotion1, depth1, needs_quote1 = classify_emotion("I've been feeling really depressed")
        self.assertIn(emotion1, ["Deep sadness", "Mental Health concern"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        emotion2, depth2, needs_quote2 = classify_emotion("I think I'm ready to get help")
        self.assertIn(emotion2, ["Mental Health concern", "No sadness"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
    # New test cases for presentation
    def test_11_academic_failure(self):
        """Test handling of academic failure and stress"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I'm really sad today because I failed my test and I don't know what to do")
        self.assertIn(emotion1, ["Academic stress", "Deep sadness"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("I studied so hard but I still couldn't do well. I feel like I'm not smart enough")
        self.assertIn(emotion2, ["Inadequacy", "Academic stress"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I'm worried about my GPA and my future. What if I can't get into a good college?")
        self.assertIn(emotion3, ["Fear", "Academic stress"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_11a_failing_multiple_classes(self):
        """Test handling of failing multiple classes"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I'm failing three classes this semester and I don't know how to catch up")
        self.assertIn(emotion1, ["Academic stress", "Overwhelmed"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("I've been skipping classes because I'm embarrassed about my grades. I feel like a failure")
        self.assertIn(emotion2, ["Shame", "Academic stress"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("My parents are going to be so disappointed. I don't want to tell them but I have to")
        self.assertIn(emotion3, ["Fear", "Guilt"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_11b_school_relationship_problems(self):
        """Test handling of relationship problems at school"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("There's this girl in my class who I really like, but I'm too nervous to talk to her")
        self.assertIn(emotion1, ["Social anxiety", "Fear"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("I think she might like me too, but I'm afraid of rejection. What if I make a fool of myself?")
        self.assertIn(emotion2, ["Fear", "Inadequacy"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I saw her talking to another guy today and I feel so jealous. I can't focus on anything else")
        self.assertIn(emotion3, ["Jealousy", "Distraction"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_11c_school_bullying(self):
        """Test handling of school bullying"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("Some kids at school keep making fun of me and I don't know what to do")
        self.assertIn(emotion1, ["Bullying", "Helplessness"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("I try to ignore them but it's getting harder. I feel like everyone is laughing at me")
        self.assertIn(emotion2, ["Shame", "Loneliness"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I'm thinking about switching schools, but I'm afraid it will just happen again somewhere else")
        self.assertIn(emotion3, ["Fear", "Hopelessness"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_11d_school_social_anxiety(self):
        """Test handling of social anxiety in academic settings"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I have to give a presentation in class tomorrow and I'm terrified")
        self.assertIn(emotion1, ["Social anxiety", "Fear"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("My heart races and I can't breathe when I think about everyone looking at me")
        self.assertIn(emotion2, ["Panic", "Social anxiety"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I'm considering skipping class tomorrow, but I'll get a zero if I don't present")
        self.assertIn(emotion3, ["Avoidance", "Conflict"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_12_relationship_breakup(self):
        """Test handling of relationship breakup"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I just broke up with my girlfriend and I don't know the next step. Everything feels empty")
        self.assertIn(emotion1, ["Loss", "Emptiness"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("We were together for two years and I thought we would be together forever. I miss her so much")
        self.assertIn(emotion2, ["Grief", "Loss"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I keep thinking about what I did wrong. Maybe if I had been better, she would have stayed")
        self.assertIn(emotion3, ["Guilt", "Loss"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_13_family_conflict(self):
        """Test handling of family conflict"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I had a huge fight with my parents last night. They don't understand me at all")
        self.assertIn(emotion1, ["Family concern", "Anger"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("They want me to study medicine but I want to be an artist. They say I'm throwing my life away")
        self.assertIn(emotion2, ["Family concern", "Frustration"])
        self.assertEqual(depth2, "deep")
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I feel like I'm stuck between making them happy and following my dreams. I don't know what to do")
        self.assertIn(emotion3, ["Overwhelmed", "Family concern"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_14_work_stress(self):
        """Test handling of work-related stress"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I'm completely overwhelmed at work. My boss keeps giving me more projects and I can't keep up")
        self.assertIn(emotion1, ["Overwhelmed", "Work concern"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("I'm afraid I'll lose my job if I don't perform well. I need this job to pay my bills")
        self.assertIn(emotion2, ["Fear", "Work concern"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I'm thinking about quitting but I'm scared of the uncertainty. What if I can't find another job?")
        self.assertIn(emotion3, ["Fear", "Work concern"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_15_identity_crisis(self):
        """Test handling of identity crisis"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I've been questioning who I am lately. I feel like I don't know myself anymore")
        self.assertIn(emotion1, ["Identity concern", "Emptiness"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("I look in the mirror and I don't recognize the person staring back at me. It's like I'm lost")
        self.assertIn(emotion2, ["Identity concern", "Emptiness"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I used to have such clear goals and now I feel like I'm just going through the motions without purpose")
        self.assertIn(emotion3, ["Identity concern", "Emptiness"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_16_social_anxiety(self):
        """Test handling of social anxiety"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I'm so nervous about the party tonight. I don't know anyone there and I'm afraid I'll make a fool of myself")
        self.assertIn(emotion1, ["Fear", "Social concern"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("I always feel like people are judging me. I can't relax around others and I end up saying stupid things")
        self.assertIn(emotion2, ["Social concern", "Fear"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I want to make friends but I'm so scared of rejection. Sometimes I wonder if I'll ever be able to connect with people")
        self.assertIn(emotion3, ["Fear", "Social concern"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_17_financial_worries(self):
        """Test handling of financial worries"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I'm really stressed about money. I can barely make ends meet and I'm worried about my future")
        self.assertIn(emotion1, ["Financial concern", "Fear"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("I have student loans to pay off and my job doesn't pay enough. I feel trapped in this cycle")
        self.assertIn(emotion2, ["Financial concern", "Helplessness"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I'm afraid I'll never be able to buy a house or start a family. Everything feels so hopeless")
        self.assertIn(emotion3, ["Fear", "Financial concern"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_18_health_concerns(self):
        """Test handling of health concerns"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I've been having these terrible headaches and I'm really worried about what might be causing them")
        self.assertIn(emotion1, ["Health concern", "Fear"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("I'm scared to go to the doctor because I don't want to hear bad news. What if it's something serious?")
        self.assertIn(emotion2, ["Fear", "Health concern"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I've been reading about symptoms online and I'm even more worried now. I can't stop thinking about it")
        self.assertIn(emotion3, ["Fear", "Health concern"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_19_grief_and_loss(self):
        """Test handling of grief and loss"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("My grandmother passed away last week and I'm really struggling with it. She was like a second mother to me")
        self.assertIn(emotion1, ["Grief", "Loss"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("I keep thinking about all the times we spent together. I miss her so much and I don't know how to move forward")
        self.assertIn(emotion2, ["Grief", "Loss"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("Everyone else seems to be moving on but I'm still stuck. I feel guilty for still being sad when others have accepted it")
        self.assertIn(emotion3, ["Guilt", "Grief"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)
        
    def test_20_recovery_journey(self):
        """Test handling of recovery journey"""
        # Initial message
        emotion1, depth1, needs_quote1 = classify_emotion("I've been struggling with depression for years but I finally decided to get help. I'm nervous about starting therapy")
        self.assertIn(emotion1, ["Mental Health concern", "Fear"])
        self.assertEqual(depth1, "deep")
        self.assertTrue(needs_quote1)
        
        # Follow-up
        emotion2, depth2, needs_quote2 = classify_emotion("My first therapy session went well. It felt good to talk to someone who understands. I'm hopeful but also scared of what might come up")
        self.assertIn(emotion2, ["Mental Health concern", "Mixed emotions"])
        self.assertEqual(depth2, "deep")
        self.assertTrue(needs_quote2)
        
        # Further follow-up
        emotion3, depth3, needs_quote3 = classify_emotion("I've been practicing the coping strategies my therapist suggested and I'm starting to feel a little better. It's a long journey but I'm committed to getting better")
        self.assertIn(emotion3, ["Mental Health concern", "No sadness"])
        self.assertEqual(depth3, "deep")
        self.assertTrue(needs_quote3)

    def test_21_multi_topic_conversation(self):
        """Test handling of multiple topics in one conversation"""
        # Start with academic stress
        emotion1, depth1, needs_quote1 = classify_emotion("I'm worried about my upcoming exams")
        self.assertIn(emotion1, ["Academic stress", "Fear"])
        self.assertEqual(depth1, "deep")
        
        # Switch to relationship issues
        emotion2, depth2, needs_quote2 = classify_emotion("And on top of that, my girlfriend and I have been fighting a lot")
        self.assertIn(emotion2, ["Relationship concern", "Mixed emotions"])
        self.assertEqual(depth2, "deep")
        
        # Switch to family pressure
        emotion3, depth3, needs_quote3 = classify_emotion("My parents keep pressuring me to do better in everything")
        self.assertIn(emotion3, ["Family concern", "Overwhelmed"])
        self.assertEqual(depth3, "deep")

    def test_22_interrupted_conversation(self):
        """Test handling of interrupted conversations"""
        # Initial deep conversation
        emotion1, depth1, needs_quote1 = classify_emotion("I've been feeling really depressed lately")
        self.assertIn(emotion1, ["Deep sadness", "Mental Health concern"])
        
        # Sudden interruption
        emotion2, depth2, needs_quote2 = classify_emotion("Sorry, someone's at the door, I'll be right back")
        self.assertEqual(emotion2, "Casual")
        self.assertEqual(depth2, "shallow")
        
        # Resume conversation
        emotion3, depth3, needs_quote3 = classify_emotion("I'm back, as I was saying about feeling depressed...")
        self.assertIn(emotion3, ["Deep sadness", "Mental Health concern"])
        self.assertEqual(depth3, "deep")

    def test_23_long_term_context(self):
        """Test maintaining context across multiple sessions"""
        context = ConversationContext()
        
        # First session
        context.add_message("I've been struggling with anxiety", "Anxiety")
        self.assertEqual(context.get_last_emotion(), "Anxiety")
        
        # Later session referencing previous
        context.add_message("Remember I mentioned my anxiety? It's getting better", "Mental Health concern")
        self.assertTrue(context.is_follow_up("Remember I mentioned my anxiety? It's getting better"))

    def test_24_crisis_escalation(self):
        """Test detection of escalating crisis situations"""
        # Initial concern
        emotion1, depth1, needs_quote1 = classify_emotion("I'm feeling really down")
        self.assertIn(emotion1, ["Deep sadness", "General sadness"])
        
        # Escalation
        emotion2, depth2, needs_quote2 = classify_emotion("Everything feels pointless and I don't see a way out")
        self.assertIn(emotion2, ["Helplessness", "Deep sadness"])
        
        # Further escalation
        emotion3, depth3, needs_quote3 = classify_emotion("I don't think I can go on like this anymore")
        self.assertIn(emotion3, ["Crisis", "Helplessness"])

    def test_25_recovery_recognition(self):
        """Test recognition of emotional improvement"""
        # Initial state
        emotion1, depth1, needs_quote1 = classify_emotion("I've been feeling so depressed and hopeless")
        self.assertIn(emotion1, ["Deep sadness", "Helplessness"])
        
        # Starting to improve
        emotion2, depth2, needs_quote2 = classify_emotion("I started therapy last week and it's helping a little")
        self.assertIn(emotion2, ["Mental Health concern", "Hope"])
        
        # Clear improvement
        emotion3, depth3, needs_quote3 = classify_emotion("I'm starting to see some light at the end of the tunnel")
        self.assertIn(emotion3, ["Hope", "Mental Health concern"])

    def test_26_topic_depth_progression(self):
        """Test progression from shallow to deep topics"""
        # Start casual
        emotion1, depth1, needs_quote1 = classify_emotion("Hey, how are you?")
        self.assertEqual(emotion1, "Casual")
        self.assertEqual(depth1, "shallow")
        
        # Transition to personal
        emotion2, depth2, needs_quote2 = classify_emotion("Actually, I've been meaning to talk about something")
        self.assertIn(emotion2, ["Transition", "Casual"])
        
        # Deep topic
        emotion3, depth3, needs_quote3 = classify_emotion("I've been struggling with some personal issues")
        self.assertIn(emotion3, ["Deep sadness", "Mental Health concern"])
        self.assertEqual(depth3, "deep")

    def test_27_emotional_complexity(self):
        """Test handling of complex emotional states"""
        # Mixed emotions
        emotion1, depth1, needs_quote1 = classify_emotion("I got the job I wanted but now I'm terrified of failing")
        self.assertEqual(emotion1, "Mixed emotions")
        
        # Conflicting feelings
        emotion2, depth2, needs_quote2 = classify_emotion("I love my partner but sometimes I feel so trapped")
        self.assertIn(emotion2, ["Mixed emotions", "Relationship concern"])
        
        # Complex emotional state
        emotion3, depth3, needs_quote3 = classify_emotion("I'm grateful for what I have but I still feel empty inside")
        self.assertIn(emotion3, ["Mixed emotions", "Emptiness"])

    def test_28_support_system_discussion(self):
        """Test discussions about support systems"""
        # Lack of support
        emotion1, depth1, needs_quote1 = classify_emotion("I feel like I have no one to talk to")
        self.assertIn(emotion1, ["Loneliness", "Isolation"])
        
        # Finding support
        emotion2, depth2, needs_quote2 = classify_emotion("My friend suggested I join a support group")
        self.assertIn(emotion2, ["Hope", "Mental Health concern"])
        
        # Building support
        emotion3, depth3, needs_quote3 = classify_emotion("I'm learning to reach out when I need help")
        self.assertIn(emotion3, ["Growth", "Hope"])

    def test_29_self_reflection(self):
        """Test handling of self-reflection"""
        # Initial reflection
        emotion1, depth1, needs_quote1 = classify_emotion("I've been thinking about my life choices")
        self.assertIn(emotion1, ["Contemplative", "Identity concern"])
        
        # Deeper insight
        emotion2, depth2, needs_quote2 = classify_emotion("I realize I often push people away when I'm hurting")
        self.assertIn(emotion2, ["Self-awareness", "Identity concern"])
        
        # Growth mindset
        emotion3, depth3, needs_quote3 = classify_emotion("I want to work on being more open with others")
        self.assertIn(emotion3, ["Growth", "Hope"])

    def test_30_professional_challenges(self):
        """Test handling of professional challenges"""
        # Career uncertainty
        emotion1, depth1, needs_quote1 = classify_emotion("I don't know if I'm in the right career")
        self.assertIn(emotion1, ["Career concern", "Uncertainty"])
        
        # Workplace stress
        emotion2, depth2, needs_quote2 = classify_emotion("My job is affecting my mental health")
        self.assertIn(emotion2, ["Work concern", "Mental Health concern"])
        
        # Career transition
        emotion3, depth3, needs_quote3 = classify_emotion("I'm thinking of changing careers but it's scary")
        self.assertIn(emotion3, ["Fear", "Career concern"])

    def test_31_personal_growth(self):
        """Test recognition of personal growth journey"""
        emotion1, depth1, needs_quote1 = classify_emotion("I've started journaling and meditation")
        self.assertIn(emotion1, ["Growth", "Hope"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("It's helping me understand myself better")
        self.assertIn(emotion2, ["Self-awareness", "Growth"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("I'm learning to be kinder to myself")
        self.assertIn(emotion3, ["Growth", "Hope"])

    def test_32_relationship_growth(self):
        """Test handling of relationship improvement"""
        emotion1, depth1, needs_quote1 = classify_emotion("My partner and I started couples therapy")
        self.assertIn(emotion1, ["Growth", "Relationship concern"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("We're learning to communicate better")
        self.assertIn(emotion2, ["Growth", "Hope"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("I feel more connected to them now")
        self.assertIn(emotion3, ["Hope", "Relationship improvement"])

    def test_33_grief_stages(self):
        """Test recognition of grief stages"""
        emotion1, depth1, needs_quote1 = classify_emotion("I can't believe they're gone. This can't be real")
        self.assertIn(emotion1, ["Denial", "Grief"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("Why did this have to happen to me?")
        self.assertIn(emotion2, ["Anger", "Grief"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("I'm starting to accept it, but it still hurts")
        self.assertIn(emotion3, ["Acceptance", "Grief"])

    def test_34_anxiety_progression(self):
        """Test handling of anxiety progression"""
        emotion1, depth1, needs_quote1 = classify_emotion("I've been feeling more anxious lately")
        self.assertEqual(emotion1, "Anxiety")
        
        emotion2, depth2, needs_quote2 = classify_emotion("It's getting harder to leave my house")
        self.assertIn(emotion2, ["Anxiety", "Fear"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("I'm afraid this anxiety will never end")
        self.assertIn(emotion3, ["Fear", "Anxiety"])

    def test_35_self_discovery(self):
        """Test handling of self-discovery journey"""
        emotion1, depth1, needs_quote1 = classify_emotion("I'm starting to question my beliefs")
        self.assertIn(emotion1, ["Identity concern", "Contemplative"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("I feel like I'm becoming a different person")
        self.assertIn(emotion2, ["Identity concern", "Growth"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("It's scary but exciting at the same time")
        self.assertEqual(emotion3, "Mixed emotions")

    def test_36_family_healing(self):
        """Test recognition of family relationship healing"""
        emotion1, depth1, needs_quote1 = classify_emotion("I finally talked to my dad after years")
        self.assertIn(emotion1, ["Family concern", "Hope"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("We both apologized for past mistakes")
        self.assertIn(emotion2, ["Growth", "Family concern"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("It feels like a weight has been lifted")
        self.assertIn(emotion3, ["Relief", "Hope"])

    def test_37_academic_growth(self):
        """Test handling of academic improvement"""
        emotion1, depth1, needs_quote1 = classify_emotion("I failed my first semester but I'm not giving up")
        self.assertIn(emotion1, ["Academic stress", "Determination"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("I've started studying differently and it's working")
        self.assertIn(emotion2, ["Growth", "Hope"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("My grades are improving and I feel more confident")
        self.assertIn(emotion3, ["Pride", "Growth"])

    def test_38_social_growth(self):
        """Test handling of social skill development"""
        emotion1, depth1, needs_quote1 = classify_emotion("I'm trying to be more social despite my anxiety")
        self.assertIn(emotion1, ["Social concern", "Growth"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("I joined a club and met some nice people")
        self.assertIn(emotion2, ["Growth", "Hope"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("I'm starting to enjoy social interactions more")
        self.assertIn(emotion3, ["Growth", "Joy"])

    def test_39_financial_recovery(self):
        """Test handling of financial recovery journey"""
        emotion1, depth1, needs_quote1 = classify_emotion("I'm drowning in debt and feel hopeless")
        self.assertIn(emotion1, ["Financial concern", "Helplessness"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("I made a budget and started saving")
        self.assertIn(emotion2, ["Growth", "Hope"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("I can see a path to being debt-free now")
        self.assertIn(emotion3, ["Hope", "Financial improvement"])

    def test_40_health_journey(self):
        """Test handling of health improvement journey"""
        emotion1, depth1, needs_quote1 = classify_emotion("Just got diagnosed with a chronic condition")
        self.assertIn(emotion1, ["Health concern", "Fear"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("Learning to manage my symptoms day by day")
        self.assertIn(emotion2, ["Growth", "Health concern"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("Starting to accept my new normal")
        self.assertIn(emotion3, ["Acceptance", "Growth"])

    def test_41_confidence_building(self):
        """Test recognition of confidence development"""
        emotion1, depth1, needs_quote1 = classify_emotion("I always doubt myself and my abilities")
        self.assertIn(emotion1, ["Inadequacy", "Self-doubt"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("Started taking small steps to build confidence")
        self.assertIn(emotion2, ["Growth", "Hope"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("I'm learning to trust myself more")
        self.assertIn(emotion3, ["Growth", "Self-confidence"])

    def test_42_addiction_recovery(self):
        """Test handling of addiction recovery journey"""
        emotion1, depth1, needs_quote1 = classify_emotion("I can't stop my bad habits")
        self.assertIn(emotion1, ["Addiction concern", "Helplessness"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("One day at a time, trying to stay clean")
        self.assertIn(emotion2, ["Growth", "Determination"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("Three months sober now, feeling proud")
        self.assertIn(emotion3, ["Pride", "Growth"])

    def test_43_trauma_healing(self):
        """Test recognition of trauma healing process"""
        emotion1, depth1, needs_quote1 = classify_emotion("Can't forget what happened to me")
        self.assertIn(emotion1, ["Trauma", "Pain"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("Started EMDR therapy and it's helping")
        self.assertIn(emotion2, ["Growth", "Hope"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("The memories don't control me anymore")
        self.assertIn(emotion3, ["Growth", "Healing"])

    def test_44_life_transition(self):
        """Test handling of major life transitions"""
        emotion1, depth1, needs_quote1 = classify_emotion("Moving to a new country next month")
        self.assertIn(emotion1, ["Anxiety", "Excitement"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("Everything is so different here")
        self.assertIn(emotion2, ["Adjustment", "Mixed emotions"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("Starting to feel at home in my new life")
        self.assertIn(emotion3, ["Growth", "Adaptation"])

    def test_45_spiritual_journey(self):
        """Test handling of spiritual/existential questions"""
        emotion1, depth1, needs_quote1 = classify_emotion("Questioning the meaning of everything")
        self.assertIn(emotion1, ["Existential concern", "Contemplative"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("Exploring different spiritual paths")
        self.assertIn(emotion2, ["Growth", "Contemplative"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("Finding peace in not knowing all answers")
        self.assertIn(emotion3, ["Growth", "Acceptance"])

    def test_46_creative_expression(self):
        """Test handling of creative emotional expression"""
        emotion1, depth1, needs_quote1 = classify_emotion("Started painting to express my feelings")
        self.assertIn(emotion1, ["Growth", "Creative expression"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("My art helps me process my emotions")
        self.assertIn(emotion2, ["Growth", "Self-awareness"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("Creating something makes me feel alive")
        self.assertIn(emotion3, ["Joy", "Growth"])

    def test_47_relationship_ending(self):
        """Test handling of relationship conclusion"""
        emotion1, depth1, needs_quote1 = classify_emotion("We decided to end our relationship")
        self.assertIn(emotion1, ["Loss", "Sadness"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("It hurts but I know it's for the best")
        self.assertIn(emotion2, ["Mixed emotions", "Growth"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("Ready to focus on myself now")
        self.assertIn(emotion3, ["Growth", "Hope"])

    def test_48_career_achievement(self):
        """Test handling of career success"""
        emotion1, depth1, needs_quote1 = classify_emotion("Finally got my dream job")
        self.assertIn(emotion1, ["Joy", "Pride"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("Worried about living up to expectations")
        self.assertIn(emotion2, ["Anxiety", "Self-doubt"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("Learning to believe in my abilities")
        self.assertIn(emotion3, ["Growth", "Self-confidence"])

    def test_49_identity_acceptance(self):
        """Test handling of identity acceptance"""
        emotion1, depth1, needs_quote1 = classify_emotion("Struggling to accept who I am")
        self.assertIn(emotion1, ["Identity concern", "Self-doubt"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("Starting to embrace my true self")
        self.assertIn(emotion2, ["Growth", "Self-acceptance"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("Finally comfortable in my own skin")
        self.assertIn(emotion3, ["Pride", "Self-acceptance"])

    def test_50_emotional_resilience(self):
        """Test recognition of developing emotional resilience"""
        emotion1, depth1, needs_quote1 = classify_emotion("Used to break down at every small thing")
        self.assertIn(emotion1, ["Emotional sensitivity", "Past reference"])
        
        emotion2, depth2, needs_quote2 = classify_emotion("Learning to handle stress better")
        self.assertIn(emotion2, ["Growth", "Resilience"])
        
        emotion3, depth3, needs_quote3 = classify_emotion("Life's challenges don't overwhelm me like before")
        self.assertIn(emotion3, ["Growth", "Strength"])

if __name__ == '__main__':
    unittest.main() 