import openai
import json
import logging
import re
from datetime import datetime as dt
import random
import time
from typing import Tuple, List, Dict
from collections import defaultdict

logging.basicConfig(level=logging.DEBUG)

class ConversationContext:
    def __init__(self):
        self.history = []
        self.topics = set()
        self.last_emotion = None
        self.greeting_count = 0
        self.last_greeting_time = None
        self.user_frustrated = False
        
    def add_message(self, message: str, emotion: str):
        """Add a message to conversation history with its emotion"""
        current_time = dt.now()
        
        # Check if this is a frustrated message
        frustrated_indicators = ['annoyed', 'frustrated', 'angry', 'mad', 'hate', 
                               'terrible', 'awful', 'horrible', 'bull', 'crap', 
                               'shit', 'fuck', 'damn', 'hell', 'stupid', 'idiot',
                               'dumb', 'ridiculous', 'useless', 'waste', 'pointless', 'boring']
        
        if any(indicator in message.lower() for indicator in frustrated_indicators):
            self.user_frustrated = True
        
        # Check if this is a greeting
        greeting_phrases = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 
                           'good evening', 'how are you', 'what\'s up', 'sup', 'howdy', 'greetings']
        
        if any(phrase in message.lower() for phrase in greeting_phrases):
            self.greeting_count += 1
            self.last_greeting_time = current_time
        
        self.history.append({
            'message': message,
            'emotion': emotion,
            'timestamp': current_time
        })
        self.last_emotion = emotion
        # Keep only last 5 messages for context
        if len(self.history) > 5:
            self.history.pop(0)
    
    def should_avoid_greeting(self) -> bool:
        """Determine if we should avoid sending another greeting"""
        if self.greeting_count >= 2:
            return True
        if self.user_frustrated:
            return True
        return False
    
    def get_messages(self) -> list:
        """Get list of messages from conversation history"""
        return [msg['message'] for msg in self.history]
    
    def get_emotions(self) -> list:
        """Get list of emotions from conversation history"""
        return [msg['emotion'] for msg in self.history]
    
    def get_last_message(self) -> str:
        """Get the last message from conversation history"""
        if not self.history:
            return None
        return self.history[-1]['message']
    
    def get_last_emotion(self) -> str:
        """Get the emotion of the last message"""
        if not self.history:
            return None
        return self.history[-1]['emotion']
    
    def is_follow_up(self, current_message: str) -> bool:
        """Determine if message is a follow-up to previous conversation"""
        if not self.history:
            return False
            
        try:
            follow_up_prompt = f"""
            Previous messages: {[msg['message'] for msg in self.history]}
            Current message: "{current_message}"
            
            Determine if the current message is a follow-up by checking:
            1. References to previous topics
            2. Pronouns referring to previously mentioned subjects
            3. Continuation of emotional themes
            4. Direct answers to previous questions
            5. Related subject matter
            
            Respond with only "follow-up" or "new-topic".
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4", 
                messages=[
                    {"role": "system", "content": "You analyze conversation continuity."},
                    {"role": "user", "content": follow_up_prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            return response.choices[0].message.content.strip().lower() == "follow-up"
            
        except Exception as e:
            logging.error(f"Follow-up detection error: {e}")
            # Fallback to basic pattern matching
            return self._basic_follow_up_check(current_message)
    
    def _basic_follow_up_check(self, message: str) -> bool:
        """Basic follow-up detection using pattern matching"""
        follow_up_indicators = [
            r'\b(it|this|that|these|those|they|them)\b',
            r'\b(yes|no|yeah|nah)\b',
            r'\b(because|since|so)\b',
            r'\b(also|too|as well)\b',
            r'\b(but|however)\b',
            r'\b(what about|tell me more|what else)\b',
            r'\b(okay|ok|alright|sure)\b',
            r'\b(please|tell me|go ahead)\b'
        ]
        
        message = message.lower()
        
        # Check for basic follow-up indicators
        if any(re.search(pattern, message) for pattern in follow_up_indicators):
            return True
            
        # Get words from previous messages
        prev_words = set()
        for msg in self.history[-3:]:  # Look at last 3 messages
            prev_words.update(msg['message'].lower().split())
        
        # Get words from current message
        curr_words = set(message.split())
        
        # Check for shared words (excluding common stop words)
        stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}
        
        shared_words = curr_words.intersection(prev_words) - stop_words
        if len(shared_words) >= 2:  # If there are 2 or more shared meaningful words
            return True
            
        # Check if it's a direct response to a question
        if self.history and self.history[-1]['message'].endswith('?') and \
           any(word in message for word in ['yes', 'no', 'maybe', 'sure', 'ok', 'okay', 'yeah', 'nah']):
            return True
            
        return False
    
    def get_context(self) -> str:
        """Get formatted conversation context"""
        if not self.history:
            return "No previous context"
            
        return "\n".join([
            f"Message: {msg['message']}\nEmotion: {msg['emotion']}\n"
            for msg in self.history[-3:]  # Last 3 messages
        ])

def is_follow_up(message, context):
    """
    Determine if a message is a follow-up to previous messages.
    Returns True if it's a follow-up, False otherwise.
    """
    if not context or not message:
        return False
        
    message = message.lower()
    previous_messages = context.get_previous_messages() if hasattr(context, 'get_previous_messages') else []
    
    # Direct references to previous messages
    reference_patterns = [
        "like i said", "as i mentioned", "remember when i said",
        "earlier i mentioned", "previously", "before", "last time",
        "continuing from", "following up", "about what i said",
        "regarding my", "about my", "remember i", "remember my",
        "still", "anymore", "these days", "lately", "now"
    ]
    
    if any(pattern in message for pattern in reference_patterns):
        return True
        
    # Check for pronouns referring to previously mentioned subjects
    if any(word in message for word in ["it", "that", "this", "those", "these"]):
        return True
        
    # Check for emotional theme continuation
    emotion_themes = ["feel", "feeling", "felt", "emotion", "mood", "situation", "problem", "issue"]
    if any(theme in message for theme in emotion_themes):
        return True
        
    # Check for related subject matter with previous messages
    for prev_msg in previous_messages:
        if isinstance(prev_msg, str):
            prev_msg = prev_msg.lower()
            # If significant words from previous message appear in current message
            words = set(prev_msg.split()) & set(message.split())
            significant_words = [w for w in words if len(w) > 3]  # Filter out small words
            if len(significant_words) >= 2:  # If 2 or more significant words match
                return True
            
    return False

def classify_emotion(message):
    """
    Classifies the emotional content of a message.
    Returns a tuple of (emotion, depth, needs_quote).
    """
    if not message or not message.strip():
        return "Neutral", "shallow", False

    message = message.lower()
    depth = "shallow"
    needs_quote = False

    # Casual greeting patterns (lowest priority, check first)
    greeting_patterns = [
        r"^(hi|hey|hello)\b",
        r"^(good|hi|hey|hello) (morning|afternoon|evening)",
        r"how are you",
        r"what'?s up",
        r"^sup\b",
        r"nice to meet",
        r"how'?s it going",
        r"how have you been",
        r"what'?s new",
        r"long time no see",
        r"weather"
    ]
    for pattern in greeting_patterns:
        if re.search(pattern, message):
            return "Casual", "shallow", False

    # Crisis patterns (highest priority)
    crisis_patterns = [
        r"(want|wish|thinking about|considering) to (die|disappear|end it|not exist)",
        r"can't (take|handle|deal with) (it|this) anymore",
        r"life (isn't|is not) worth (living|it)",
        r"(rather|better|prefer) be dead",
        r"no (point|future|hope|reason to continue)",
        r"end (it all|my life|everything)",
        r"everything.*pointless|pointless.*everything",
        r"lost all hope",
        r"(giving|gave) up.*life",
        r"no reason.*live",
        r"suicidal|suicide",
        r"kill (myself|me)",
        r"don't want to (exist|be here|live)",
        r"can't go on",
        r"(ready|want) to give up"
    ]
    for pattern in crisis_patterns:
        if re.search(pattern, message):
            return "Helplessness", "deep", True

    # Mixed emotions patterns
    mixed_emotions_patterns = [
        r"(happy|good).*but.*(sad|anxious|worried|scared)",
        r"(sad|anxious|worried|scared).*but.*(happy|good)",
        r"mixed feelings",
        r"conflicted about",
        r"part of me.*another part",
        r"trying to be.*but inside",
        r"happy and sad",
        r"don't know how to feel",
        r"(torn|split|divided) between",
        r"(confused|conflicted) about (my feelings|how I feel)",
        r"emotional rollercoaster",
        r"(good and bad|ups and downs)"
    ]
    for pattern in mixed_emotions_patterns:
        if re.search(pattern, message):
            return "Mixed emotions", "deep", True

    # Academic stress patterns
    academic_patterns = [
        r"(failed|failing|fail) (test|exam|class|course|grade)",
        r"(worried|anxious|stressed) about (grades|school|college|university|studies)",
        r"(bad|poor|low) grades",
        r"(study|studying) (hard|lot|much).*still.*fail",
        r"not smart enough",
        r"academic (pressure|stress)",
        r"behind in (class|school|studies)",
        r"catch up.*class",
        r"gpa.*worry",
        r"education.*stress",
        r"(overwhelmed|stressed) (by|with) (homework|studying|assignments)",
        r"(pressure|stress) from (teachers|professors|parents)"
    ]
    for pattern in academic_patterns:
        if re.search(pattern, message):
            return "Academic stress", "deep", True

    # Social anxiety patterns
    social_anxiety_patterns = [
        r"(nervous|anxious|scared) to (talk|speak|present)",
        r"(afraid|scared) of (people|social|crowd)",
        r"(presentation|public speaking).*terrified",
        r"everyone (looking|staring|judging)",
        r"heart races.*people",
        r"can't breathe.*social",
        r"too nervous to",
        r"social (anxiety|fear|phobia)",
        r"afraid of rejection",
        r"(awkward|uncomfortable) (in|around|with) people",
        r"(hate|dislike|avoid) social situations"
    ]
    for pattern in social_anxiety_patterns:
        if re.search(pattern, message):
            return "Social anxiety", "deep", True

    # Relationship patterns
    relationship_patterns = [
        r"broke up|breaking up|broken up",
        r"(miss|love|want) (him|her|them) (so much|back)",
        r"relationship (ended|over|finished)",
        r"together for.*years",
        r"never love again",
        r"heart.*(broken|hurts)",
        r"can't get over",
        r"dating.*problems",
        r"relationship.*issues",
        r"(lost|losing) someone",
        r"(can't|don't) know how to (cope|deal) with loss"
    ]
    for pattern in relationship_patterns:
        if re.search(pattern, message):
            return "Loss", "deep", True

    # Family concern patterns
    family_patterns = [
        r"(fight|fought|fighting) with (family|parents|mom|dad|sister|brother)",
        r"family (doesn't|don't) understand",
        r"parents (pressure|force|make) me",
        r"family (issues|problems|conflict)",
        r"home.*difficult",
        r"family.*expectations",
        r"parents.*disappointed",
        r"family.*relationship.*strain",
        r"(toxic|dysfunctional) family",
        r"(no support|no help) from family"
    ]
    for pattern in family_patterns:
        if re.search(pattern, message):
            return "Family concern", "deep", True

    # Deep sadness patterns
    deep_sadness_patterns = [
        r"(so|very|really|extremely) (sad|depressed|down)",
        r"can't stop crying",
        r"nothing makes me happy",
        r"(feel|feeling) empty",
        r"lost.*purpose",
        r"don't see the point",
        r"(deep|severe) depression",
        r"overwhelming sadness",
        r"darkness.*inside",
        r"(completely|totally) (lost|empty|numb)",
        r"(never|won't) feel (better|happy) again"
    ]
    for pattern in deep_sadness_patterns:
        if re.search(pattern, message):
            return "Deep sadness", "deep", True

    # Mental Health concern patterns
    mental_health_patterns = [
        r"(anxiety|depression|mental health) (issues|problems|struggles)",
        r"panic attack",
        r"need.*help.*mental",
        r"therapy|counseling",
        r"mental.*treatment",
        r"diagnosed with",
        r"medication.*mental",
        r"seeing a (therapist|counselor|psychiatrist)",
        r"(struggling|dealing) with mental health",
        r"(recovery|recovering) from"
    ]
    for pattern in mental_health_patterns:
        if re.search(pattern, message):
            return "Mental Health concern", "deep", True

    # Fear patterns
    fear_patterns = [
        r"(scared|afraid|terrified) of",
        r"fear.*(future|unknown|change)",
        r"what if.*bad",
        r"(worried|anxious) about",
        r"panic.*thought",
        r"fear.*(taking over|consuming)",
        r"constant worry",
        r"(paralyzed|frozen) with fear",
        r"(overwhelming|crippling) fear"
    ]
    for pattern in fear_patterns:
        if re.search(pattern, message):
            return "Fear", "deep", True

    # Inadequacy patterns
    inadequacy_patterns = [
        r"not good enough",
        r"(feel|feeling) (inadequate|worthless|useless)",
        r"can't do anything right",
        r"everyone.*better than me",
        r"never.*measure up",
        r"failure.*person",
        r"disappoint.*everyone",
        r"(imposter|fake|fraud) syndrome",
        r"(always|constantly) failing"
    ]
    for pattern in inadequacy_patterns:
        if re.search(pattern, message):
            return "Inadequacy", "deep", True

    # Growth patterns
    growth_patterns = [
        r"getting better",
        r"making progress",
        r"positive change",
        r"moving forward",
        r"growing stronger",
        r"(feel|feeling) hopeful",
        r"improving",
        r"proud of myself",
        r"(better|stronger) than before"
    ]
    for pattern in growth_patterns:
        if re.search(pattern, message):
            return "Growth", "deep", True

    # Identity concern patterns
    identity_patterns = [
        r"who am i",
        r"identity crisis",
        r"don't know myself",
        r"lost myself",
        r"finding myself",
        r"true self",
        r"questioning.*identity",
        r"self.*discovery"
    ]
    for pattern in identity_patterns:
        if re.search(pattern, message):
            return "Identity concern", "deep", True

    # General sadness patterns (lower priority than deep sadness)
    sadness_patterns = [
        r"(sad|down|upset)",
        r"feeling (blue|low)",
        r"not (happy|okay|fine)",
        r"bad day",
        r"(feel|feeling) (bad|terrible)",
        r"(crying|cried|tears)",
        r"(lost|losing) (interest|motivation)"
    ]
    for pattern in sadness_patterns:
        if re.search(pattern, message):
            return "General sadness", "deep", True

    # If no patterns match
    return "Neutral", "shallow", False

def fetch_relevant_quote(emotion):
    """Return a verified quote based on the emotion."""
    quotes = {
        "Deep sadness": "The pain passes, but the beauty remains. - Pierre Auguste Renoir",
        "Frustration": "When you get into a tight place and everything goes against you, never give up then, for that is just the place and time that the tide will turn. - Harriet Beecher Stowe",
        "Disappointment": "What seems to us as bitter trials are often blessings in disguise. - Oscar Wilde",
        "Emptiness": "Even the darkest night will end and the sun will rise. - Victor Hugo",
        "Inadequacy": "You yourself, as much as anybody in the entire universe, deserve your love and affection. - Buddha",
        "Helplessness": "Rock bottom became the solid foundation on which I rebuilt my life. - J.K. Rowling",
        "Fear": "Fear is only as deep as the mind allows. - Japanese Proverb",
        "Guilt": "The truth is, unless you let go, unless you forgive yourself, unless you forgive the situation, unless you realize that the situation is over, you cannot move forward. - Steve Maraboli",
        "Loneliness": "Sometimes, the strongest people are the ones who love beyond all faults, cry behind closed doors and fight battles that nobody knows about. - Johnny Depp",
        "Overwhelmed": "Take life day by day and be grateful for the little things. Don't get stressed over what you can't control. - Tony Gaskins",
        "Failure": "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        "Anger": "When you are angry, take a deep breath and count to ten before you speak. If you are very angry, count to one hundred. - Thomas Jefferson",
        "General sadness": "There is no storm that lasts forever. - Seneca",
        "Grief": "Unable are the loved to die, for love is immortality. - Emily Dickinson",
        "Loss": "What we have once enjoyed we can never lose; all that we love deeply becomes a part of us. - Helen Keller",
        "Pet loss": "Until one has loved an animal, a part of one's soul remains unawakened. - Anatole France",
        "Death": "Death ends a life, not a relationship. - Mitch Albom",
        "Mourning": "The risk of love is loss, and the price of loss is grief. But the pain of grief is only a shadow when compared with the pain of never risking love. - Hilary Stanton Zunin",
        "Animal loss": "If having a soul means being able to feel love and loyalty and gratitude, then animals are better off than a lot of humans. - James Herriot",
        "Dog loss": "Dogs are not our whole life, but they make our lives whole. - Roger Caras",
        "Cat loss": "Time spent with cats is never wasted. - Sigmund Freud",
        "Academic stress": "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        "Educational anxiety": "The expert in anything was once a beginner. - Helen Hayes",
        "Learning struggles": "It does not matter how slowly you go as long as you do not stop. - Confucius",
        # Add quotes for new categories
        "Relationship concern": "The most important thing in life is to learn how to give out love, and to let it come in. - Morrie Schwartz",
        "Family concern": "Family is not an important thing. It's everything. - Michael J. Fox",
        "Work concern": "The only way to do great work is to love what you do. - Steve Jobs",
        "Mental Health concern": "You don't have to control your thoughts. You just have to stop letting them control you. - Dan Millman",
        "Identity concern": "Be yourself; everyone else is already taken. - Oscar Wilde",
        "Social concern": "True friendship multiplies the good in life and divides its evils. - Baltasar Gracian",
        "Financial concern": "It's not how much money you make, but how much money you keep. - Robert Kiyosaki",
        "Health concern": "Health is not valued till sickness comes. - Thomas Fuller"
    }
    
    # If no specific quote found, use a verified general comforting quote
    default_quote = "Time is the wisest counselor of all. - Pericles"
    return quotes.get(emotion, default_quote)

def format_quote(response):
    """Ensure the quote is in the correct format."""
    match = re.search(r'"(.+?)"', response)  # Look for text inside quotes
    if match:
        quote = match.group(0)  # Extract the quote
        response = response.replace(quote, f'\n{quote}\n')  # Ensure standalone format
    return response

def is_casual_conversation(message):
    """Enhanced detection of casual conversations and greetings"""
    # List of emotional indicators that suggest non-casual conversation
    emotional_indicators = [
        'sad', 'depressed', 'anxious', 'worried', 'stressed', 'overwhelmed',
        'happy', 'excited', 'joy', 'grateful', 'thankful', 'hopeful',
        'angry', 'frustrated', 'annoyed', 'upset', 'disappointed', 'hurt',
        'scared', 'afraid', 'fear', 'nervous', 'terrified', 'panicked',
        'lonely', 'alone', 'isolated', 'abandoned', 'rejected',
        'confused', 'uncertain', 'unsure', 'doubt', 'questioning',
        'tired', 'exhausted', 'fatigued', 'weary', 'drained',
        'guilty', 'ashamed', 'embarrassed', 'regret', 'remorse',
        'jealous', 'envious', 'resentful', 'bitter',
        'proud', 'accomplished', 'achieved', 'success',
        'grief', 'mourning', 'loss', 'missing', 'gone',
        'annoying', 'stupid', 'ridiculous', 'useless', 'waste',
        'fuck', 'shit', 'damn', 'hell', 'crap'
    ]
    
    # List of casual phrases that indicate a casual conversation
    casual_phrases = [
        'how are you', 'what\'s up', 'what\'s new', 'how\'s it going',
        'good morning', 'good afternoon', 'good evening', 'hey there',
        'hi there', 'hello there', 'greetings', 'hey', 'hi', 'hello',
        'nice to meet you', 'pleasure to meet you', 'good to see you',
        'long time no see', 'it\'s been a while', 'how have you been',
        'what have you been up to', 'tell me about yourself',
        'what do you do', 'where are you from', 'what brings you here',
        'nice weather', 'beautiful day', 'lovely day', 'great day',
        'have a good day', 'have a nice day', 'take care', 'see you later',
        'bye', 'goodbye', 'farewell', 'until next time', 'talk to you later',
        'thanks', 'thank you', 'appreciate it', 'thanks a lot', 'thank you so much',
        'you\'re welcome', 'no problem', 'my pleasure', 'glad to help',
        'okay', 'ok', 'alright', 'sure', 'fine', 'great', 'awesome',
        'cool', 'nice', 'perfect', 'excellent', 'wonderful', 'fantastic',
        'amazing', 'incredible', 'brilliant', 'outstanding', 'superb',
        'terrific', 'marvelous', 'splendid', 'fabulous', 'spectacular',
        'bad', 'terrible', 'awful', 'horrible', 'dreadful', 'atrocious',
        'poor', 'subpar', 'mediocre', 'average', 'ordinary', 'common',
        'boring', 'dull', 'monotonous', 'tedious', 'repetitive',
        'interesting', 'fascinating', 'intriguing', 'captivating', 'engaging',
        'fun', 'enjoyable', 'pleasant', 'delightful', 'entertaining',
        'difficult', 'hard', 'challenging', 'complex', 'complicated',
        'easy', 'simple', 'straightforward', 'uncomplicated', 'basic',
        'quick', 'fast', 'rapid', 'swift', 'speedy', 'prompt',
        'slow', 'sluggish', 'leisurely', 'unhurried', 'relaxed',
        'busy', 'occupied', 'engaged', 'involved', 'preoccupied',
        'free', 'available', 'unoccupied', 'idle', 'at leisure',
        'tired', 'exhausted', 'fatigued', 'weary', 'drained',
        'energetic', 'lively', 'vigorous', 'active', 'dynamic',
        'hungry', 'thirsty', 'starving', 'famished', 'parched',
        'full', 'satisfied', 'content', 'sated', 'quenched',
        'hot', 'cold', 'warm', 'cool', 'chilly', 'freezing',
        'comfortable', 'cozy', 'snug', 'pleasant', 'agreeable',
        'uncomfortable', 'uneasy', 'discomfited', 'ill at ease',
        'happy', 'sad', 'angry', 'mad', 'upset', 'frustrated',
        'excited', 'thrilled', 'elated', 'overjoyed', 'ecstatic',
        'disappointed', 'let down', 'disheartened', 'discouraged',
        'proud', 'accomplished', 'achieved', 'successful', 'triumphant',
        'embarrassed', 'ashamed', 'humiliated', 'mortified', 'chagrined',
        'scared', 'afraid', 'frightened', 'terrified', 'petrified',
        'brave', 'courageous', 'bold', 'fearless', 'intrepid',
        'confused', 'puzzled', 'perplexed', 'bewildered', 'baffled',
        'clear', 'certain', 'sure', 'confident', 'convinced',
        'worried', 'anxious', 'concerned', 'uneasy', 'apprehensive',
        'calm', 'relaxed', 'peaceful', 'serene', 'tranquil',
        'busy', 'occupied', 'engaged', 'involved', 'preoccupied',
        'free', 'available', 'unoccupied', 'idle', 'at leisure',
        'tired', 'exhausted', 'fatigued', 'weary', 'drained',
        'energetic', 'lively', 'vigorous', 'active', 'dynamic',
        'hungry', 'thirsty', 'starving', 'famished', 'parched',
        'full', 'satisfied', 'content', 'sated', 'quenched',
        'hot', 'cold', 'warm', 'cool', 'chilly', 'freezing',
        'comfortable', 'cozy', 'snug', 'pleasant', 'agreeable',
        'uncomfortable', 'uneasy', 'discomfited', 'ill at ease',
        'happy', 'sad', 'angry', 'mad', 'upset', 'frustrated',
        'excited', 'thrilled', 'elated', 'overjoyed', 'ecstatic',
        'disappointed', 'let down', 'disheartened', 'discouraged',
        'proud', 'accomplished', 'achieved', 'successful', 'triumphant',
        'embarrassed', 'ashamed', 'humiliated', 'mortified', 'chagrined',
        'scared', 'afraid', 'frightened', 'terrified', 'petrified',
        'brave', 'courageous', 'bold', 'fearless', 'intrepid',
        'confused', 'puzzled', 'perplexed', 'bewildered', 'baffled',
        'clear', 'certain', 'sure', 'confident', 'convinced',
        'worried', 'anxious', 'concerned', 'uneasy', 'apprehensive',
        'calm', 'relaxed', 'peaceful', 'serene', 'tranquil'
    ]
    
    # List of casual questions
    casual_questions = [
        'how are you', 'what\'s up', 'what\'s new', 'how\'s it going',
        'what do you do', 'where are you from', 'what brings you here',
        'what do you like to do', 'what are your hobbies', 'what do you enjoy',
        'what\'s your favorite', 'what do you think about', 'what\'s your opinion',
        'what\'s your take', 'what\'s your view', 'what\'s your perspective',
        'what\'s your stance', 'what\'s your position', 'what\'s your stand',
        'what\'s your angle', 'what\'s your approach', 'what\'s your method',
        'what\'s your strategy', 'what\'s your plan', 'what\'s your goal',
        'what\'s your aim', 'what\'s your objective', 'what\'s your purpose',
        'what\'s your mission', 'what\'s your vision', 'what\'s your dream',
        'what\'s your aspiration', 'what\'s your ambition', 'what\'s your desire',
        'what\'s your wish', 'what\'s your hope', 'what\'s your expectation',
        'what\'s your prediction', 'what\'s your forecast', 'what\'s your projection',
        'what\'s your estimate', 'what\'s your guess', 'what\'s your speculation',
        'what\'s your assumption', 'what\'s your presumption', 'what\'s your supposition',
        'what\'s your hypothesis', 'what\'s your theory', 'what\'s your concept',
        'what\'s your idea', 'what\'s your thought', 'what\'s your notion',
        'what\'s your understanding', 'what\'s your interpretation', 'what\'s your reading'
    ]
    
    # List of frustration indicators about the chatbot
    chatbot_frustration = [
        'annoying', 'stupid', 'ridiculous', 'useless', 'waste',
        'fuck', 'shit', 'damn', 'hell', 'crap',
        'bot', 'chatbot', 'ai', 'artificial intelligence',
        'greeting', 'greetings', 'hello', 'hi', 'hey',
        'how are you', 'what\'s up', 'what\'s new', 'how\'s it going',
        'what do you do', 'where are you from', 'what brings you here',
        'what do you like to do', 'what are your hobbies', 'what do you enjoy',
        'what\'s your favorite', 'what do you think about', 'what\'s your opinion',
        'what\'s your take', 'what\'s your view', 'what\'s your perspective',
        'what\'s your stance', 'what\'s your position', 'what\'s your stand',
        'what\'s your angle', 'what\'s your approach', 'what\'s your method',
        'what\'s your strategy', 'what\'s your plan', 'what\'s your goal',
        'what\'s your aim', 'what\'s your objective', 'what\'s your purpose',
        'what\'s your mission', 'what\'s your vision', 'what\'s your dream',
        'what\'s your aspiration', 'what\'s your ambition', 'what\'s your desire',
        'what\'s your wish', 'what\'s your hope', 'what\'s your expectation',
        'what\'s your prediction', 'what\'s your forecast', 'what\'s your projection',
        'what\'s your estimate', 'what\'s your guess', 'what\'s your speculation',
        'what\'s your assumption', 'what\'s your presumption', 'what\'s your supposition',
        'what\'s your hypothesis', 'what\'s your theory', 'what\'s your concept',
        'what\'s your idea', 'what\'s your thought', 'what\'s your notion',
        'what\'s your understanding', 'what\'s your interpretation', 'what\'s your reading'
    ]
    
    # Check for emotional content first
    if any(indicator in message.lower() for indicator in emotional_indicators):
        return False
        
    # Check for frustration about the chatbot
    if any(indicator in message.lower() for indicator in chatbot_frustration):
        return False
        
    # Check for greetings
    if any(greeting in message.lower() for greeting in casual_phrases[:20]):
        return True
        
    # Check for casual phrases
    if any(phrase in message.lower() for phrase in casual_phrases[20:]):
        return True
        
    # Check for casual questions
    if any(question in message.lower() for question in casual_questions):
        return True
        
    # Check for very short messages that are likely to be casual
    if len(message.split()) <= 2 and len(message) < 15:
        return True
        
    return False

def format_neutral_response(user_message, context):
    """Format a response for casual or greeting messages"""
    # Check if the user is frustrated with the chatbot
    user_frustrated = context.user_frustrated
    should_avoid_greeting = context.should_avoid_greeting()
    
    # Check if the message is a greeting
    is_greeting = any(greeting in user_message.lower() for greeting in [
        'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
        'how are you', 'what\'s up', 'what\'s new', 'how\'s it going'
    ])
    
    # Check if the message is casual
    is_casual = is_casual_conversation(user_message)
    
    # If the user is frustrated with the chatbot, acknowledge their frustration
    if user_frustrated:
        return f"""You are a mental health chatbot. The user is frustrated with your behavior.

Previous context: {context.get_context()}
Current message: {user_message}

Instructions:
1. Acknowledge the user's frustration without being defensive
2. Explain that you are here to help with their mental health concerns
3. Ask if they would like to talk about what's bothering them
4. Avoid sending another greeting
5. Keep your response concise and empathetic
6. Match the user's tone and level of formality
7. Do not use quotes or philosophical statements
8. Focus on the user's needs, not your own

Response guidelines:
- Start by acknowledging their frustration
- Explain your purpose as a mental health chatbot
- Ask if they would like to talk about their concerns
- Keep your response under 3 sentences
- Be direct and honest
- Avoid being overly formal or casual
- Do not use quotes or philosophical statements
- Focus on the user's needs, not your own"""
    
    # If the user has greeted but we've already greeted recently, avoid another greeting
    elif is_greeting and should_avoid_greeting:
        return f"""You are a mental health chatbot. The user has greeted you, but you've already greeted them recently.

Previous context: {context.get_context()}
Current message: {user_message}

Instructions:
1. Acknowledge the user's greeting without sending another greeting
2. Ask if they would like to talk about what's on their mind
3. Keep your response concise and empathetic
4. Match the user's tone and level of formality
5. Do not use quotes or philosophical statements
6. Focus on the user's needs, not your own

Response guidelines:
- Start by acknowledging their greeting without sending another greeting
- Ask if they would like to talk about what's on their mind
- Keep your response under 3 sentences
- Be direct and honest
- Avoid being overly formal or casual
- Do not use quotes or philosophical statements
- Focus on the user's needs, not your own"""
    
    # If the message is casual, respond in a casual manner
    elif is_casual:
        return f"""You are a mental health chatbot. The user has sent a casual message.

Previous context: {context.get_context()}
Current message: {user_message}

Instructions:
1. Respond in a casual, friendly manner
2. Acknowledge the previous context if relevant
3. Keep your response concise and natural
4. Match the user's tone and level of formality
5. Do not use quotes or philosophical statements
6. Focus on the user's needs, not your own

Response guidelines:
- Start with a simple greeting if appropriate
- Keep your response under 3 sentences
- Be direct and honest
- Avoid being overly formal or casual
- Do not use quotes or philosophical statements
- Focus on the user's needs, not your own"""
    
    # Default response for neutral messages
    else:
        return f"""You are a mental health chatbot. The user has sent a neutral message.

Previous context: {context.get_context()}
Current message: {user_message}

Instructions:
1. Respond in a neutral, empathetic manner
2. Acknowledge the previous context if relevant
3. Keep your response concise and natural
4. Match the user's tone and level of formality
5. Do not use quotes or philosophical statements
6. Focus on the user's needs, not your own

Response guidelines:
- Start with a simple greeting if appropriate
- Keep your response under 3 sentences
- Be direct and honest
- Avoid being overly formal or casual
- Do not use quotes or philosophical statements
- Focus on the user's needs, not your own"""

def format_casual_prompt(user_input, context):
    """Format prompt for casual/neutral conversations."""
    return f"""
    Current message: "{user_input}"
    Previous messages: {context}

    IMPORTANT - This is a casual conversation:
    - NO quotes or philosophical responses
    - Keep it simple and conversational
    - Match the user's casual tone
    - If it's a greeting/casual question, reply similarly
    - Stay warm but not overly formal
    - Focus on natural dialogue
    """

def format_emotional_prompt(emotion: str, user_input: str, conversation_context: str = None) -> str:
    """Format a prompt for emotional conversations with proper quote formatting."""
    quote = fetch_relevant_quote(emotion)
    
    prompt = f"""You are a mental health chatbot. The user is experiencing {emotion}.

IMPORTANT - Your response MUST follow this format:
1. Start with this EXACT quote (including quotation marks):
"{quote}"

2. Add a blank line after the quote

3. Then write your empathetic response that:
   - Acknowledges their specific situation
   - Shows you understand their feelings
   - Offers gentle support
   - Ends with a thoughtful question

Previous context: {conversation_context if conversation_context else "No previous context"}
Current message: {user_input}

Keep your response warm and genuine, but professional.
Focus on being present with them rather than trying to fix their problems.
"""
    return prompt

def generate_response(message, emotion, depth):
    """Generate an appropriate response based on the emotion and depth."""
    if emotion == "Casual":
        return f"""You are a mental health chatbot. The user has sent a casual message.

Previous message: {message}
Emotion: {emotion}
Depth: {depth}

Instructions:
1. Respond in a casual, friendly manner
2. Keep your response concise and natural
3. Match the user's tone and level of formality
4. Do not use quotes or philosophical statements
5. Focus on the user's needs, not your own

Response guidelines:
- Start with a simple greeting if appropriate
- Keep your response under 3 sentences
- Be direct and honest
- Avoid being overly formal or casual
- Do not use quotes or philosophical statements
- Focus on the user's needs, not your own"""

    # For deep emotional states that need quotes
    quote_needed = [
        "Deep sadness", "Crisis", "Helplessness", "Grief", "Loss",
        "Inadequacy", "Identity concern", "Mixed emotions"
    ]

    if emotion in quote_needed or depth == "deep":
        return f"""You are a compassionate mental health chatbot. The user is experiencing {emotion}.

Previous message: {message}
Emotion: {emotion}
Depth: {depth}

IMPORTANT FORMATTING RULES:
1. ALWAYS start your response with the quote in this exact format:
   "Quote that acknowledges their pain while offering hope" - Author
   
2. After the quote, provide your empathetic response following this structure:
   - Acknowledge their specific situation
   - Validate their feelings and emotions
   - Offer gentle support and understanding
   - End with a gentle follow-up question that shows you're listening
   
3. Keep your response concise but meaningful (2-3 sentences after the quote)
4. Be warm and empathetic, but avoid being overly clinical or detached
5. Focus on being present with them, not trying to "fix" it"""

    # For other emotional states that don't need quotes
    return f"""You are a mental health chatbot. The user is experiencing {emotion}.

Previous message: {message}
Emotion: {emotion}
Depth: {depth}

Instructions:
1. Respond with empathy and understanding
2. Validate their feelings
3. Offer gentle support
4. End with a thoughtful question
5. Keep your response concise (2-3 sentences)
6. Match their emotional depth
7. Focus on being present with them

Response guidelines:
- Acknowledge their specific situation
- Show you understand their feelings
- Provide gentle support
- End with a question that encourages sharing
- Keep it warm and genuine"""

def analyze_mood(message, context=None):
    """
    Analyze the mood of a message and generate an appropriate response.
    Returns (emotion, response, needs_quote, updated_context)
    """
    emotion, depth, needs_quote = classify_emotion(message)
    response = generate_response(message, emotion, depth)
    updated_context = update_context(context, message, emotion) if context else None
    return emotion, response, needs_quote, updated_context

def update_context(context, message, emotion):
    """Update the conversation context with the new message and emotion."""
    if context is None:
        return None
        
    if hasattr(context, 'add_message'):
        context.add_message(message, emotion)
    if hasattr(context, 'add_emotion'):
        context.add_emotion(emotion)
    return context

def analyze_new_topic(user_input: str) -> tuple:
    """Handle new conversation topics."""
    # Create a new context for this topic
    context = ConversationContext()
    
    if is_casual_conversation(user_input):
        emotion = "Neutral"
        prompt = format_neutral_response(user_input, context)
        return emotion, prompt, context
    
    emotion_tuple = classify_emotion(user_input)
    emotion = emotion_tuple[0]  # Extract just the emotion string
    
    if emotion == "No sadness" or emotion == "Neutral":
        prompt = format_neutral_response(user_input, context)
        return emotion, prompt, context
        
    prompt = format_emotional_prompt(
        emotion,
        user_input,
        context
    )
    
    return emotion, prompt, context

def chat_with_gpt(prompt, max_retries=2):
    """Enhanced chat function with retries and fallback"""
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an empathetic AI companion..."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                presence_penalty=0.6,
                frequency_penalty=0.5
            )
            
            if response and response.choices and response.choices[0].message:
                return response.choices[0].message.content.strip()
                
        except openai.error.RateLimitError as e:
            logging.error(f"Rate limit error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
                continue
            raise
            
        except Exception as e:
            logging.error(f"Chat error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                continue
            raise
            
    return get_fallback_response()

def get_fallback_response():
    """Provide a fallback response when API fails"""
    fallbacks = [
        "I'm here to listen. Could you tell me more about what's on your mind?",
        "I want to understand better. Could you elaborate on that?",
        "I'm listening. Would you like to share more about how you're feeling?",
        "Your feelings matter. Would you like to talk more about this?"
    ]
    return random.choice(fallbacks)

def format_follow_up_response(message, context):
    """Format response for follow-up messages"""
    previous_context = context.get_context()
    current_messages = context.get_messages()
    current_emotions = context.get_emotions()
    
    # Check if user is ready to share more
    ready_to_share = any(pattern in message.lower() for pattern in [
        'what do you want to know',
        'tell me more',
        'what else',
        'what about',
        'okay',
        'ok',
        'alright',
        'sure',
        'please',
        'tell me',
        'go ahead'
    ])
    
    # Extract the main topic from previous context
    main_topic = None
    if 'loss' in previous_context.lower() or 'grief' in previous_context.lower():
        main_topic = 'loss'
    elif 'anxiety' in previous_context.lower() or 'worried' in previous_context.lower():
        main_topic = 'anxiety'
    elif 'depression' in previous_context.lower() or 'sad' in previous_context.lower():
        main_topic = 'depression'
    
    # Add academic-specific topic detection
    if any(word in message.lower() for word in ['class', 'school', 'failing', 'grades', 'study']):
        topic_questions = [
            "What specific classes are you finding most challenging right now?",
            "Have you been able to talk to your teachers or academic advisors about this?",
            "What kind of support do you think would be most helpful for your studies?",
            "Would you like to explore some study strategies together?"
        ]
        specific_question = random.choice(topic_questions)
    else:
        specific_question = "Could you tell me more about what's been most difficult?"
    
    prompt = f"""Previous context: {previous_context}
Current message: {message}
Current emotions: {current_emotions}

Instructions:
1. Acknowledge the connection to previous messages
2. Show understanding of emotional progression
3. If user is ready to share more ({ready_to_share}), ask a specific question about:
   - For loss/grief: Ask about specific memories, feelings, or coping strategies
   - For anxiety: Ask about triggers, physical symptoms, or coping mechanisms
   - For depression: Ask about daily challenges, support system, or treatment
4. If not ready to share, gently encourage with an open-ended question
5. Maintain empathetic and supportive tone
6. Keep response concise and focused

Remember to:
- Be specific in questions when user is ready to share
- Show genuine interest in their experience
- Validate their feelings
- Offer practical support when appropriate"""
    
    return prompt

# Example usage
if __name__ == "__main__":
    user_input = "I feel like no one understands me, and I just want to disappear."
    conversation_history = [
        "I'm struggling a lot with everything.",
        "I feel like I'm not good enough."
    ]

    emotion, response, needs_quote, updated_context = analyze_mood(user_input, ConversationContext())
    print(f"Detected Emotion: {emotion}")
    print(f"Response:\n{response}")

__all__ = [
    'classify_emotion',
    'ConversationContext',
    'fetch_relevant_quote',
    'format_emotional_prompt',
    'format_follow_up_response',
    'format_neutral_response',
    'analyze_mood',
    'chat_with_gpt'
]