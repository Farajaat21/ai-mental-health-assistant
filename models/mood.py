import openai
import json
import logging

logging.basicConfig(level=logging.DEBUG)

def classify_emotion(user_input, conversation_history=[]):
    """Classify emotion with improved parsing and robustness."""
    
    classification_prompt = f"""
    The user provided this message: "{user_input}"
    
    Classify the emotional state of the user into one of the following categories:
    - Deep sadness (grief, sorrow)
    - Frustration (anger mixed with sadness)
    - Disappointment (mild sadness due to unmet expectations)
    - Emptiness (Feeling numb, disconnected, lacking purpose)
    - Inadequacy (Not feeling good enough, self-doubt)
    - Helplessness (Loss of control, powerless, stuck)
    - Fear (Sense of danger, anxiety, uncertainty)
    - Guilt (Self-blame, regret, moral discomfort)
    - Loneliness (Feeling isolated, unseen, disconnected)
    - Overwhelmed (Too many demands, mentally overloaded)
    - Failure (Defeat, self-doubt, and regret)
    - Anger (Intense frustration, irritation, rage)
    - General sadness (neutral sadness)
    - Jealousy (Desire with insecurity and envy)
    - Rejected (Unwanted, dismissed, and unworthy)
    - No sadness (if none of the above)

    Context: {conversation_history[-3:] if conversation_history else 'No previous context'}

    Respond in **JSON format** with:
    {{
        "emotion": "[One of the above categories]",
        "depth": "[shallow/deep]",
        "needs_quote": [true/false]
    }}
    """
    
    try:
        if not openai.api_key:
            return "Neutral", "shallow", False  # Return three values
        
        response = openai.ChatCompletion.create(
            model="gpt-4", 
            messages=[
                {"role": "system", "content": "You are an AI specializing in detecting emotional states with precision."},
                {"role": "user", "content": classification_prompt}
            ],
            temperature=0.3
        )

        analysis = response.choices[0].message.content.strip()

        
        try:
            data = json.loads(analysis)
            emotion = data.get("emotion", "Neutral")
            depth = data.get("depth", "shallow")
            needs_quote = data.get("needs_quote", False)
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON response")
            return "Neutral", "shallow", False

        return emotion, depth, needs_quote

    except Exception as e:
        logging.error(f"Error in emotion classification: {e}")
        return "Neutral", "shallow", False

def fetch_relevant_quote(emotion):
    """Return a default inspirational quote based on the emotion."""
    # In future, this could call an external API or use a database of quotes
    return f"Default inspirational quote for {emotion}"

def generate_response(user_input, conversation_history=[]):
    """Generates an empathetic response based on detected emotion."""
    emotion, depth, needs_quote = classify_emotion(user_input, conversation_history)
    if emotion == "Neutral":
        return "Neutral", "I'm here to listen. Tell me more about what's on your mind."
    quote = fetch_relevant_quote(emotion) if needs_quote else None
    response_prompt = f"""
    The user is experiencing {emotion} and shared: "{user_input}"
    Context: {conversation_history[-3:] if conversation_history else 'No context'}

    Respond in **this exact format**:
    QUOTE: "{quote}" - [Author]  # the quote should be the quote a relavent quote base on the user's emotion 
    RESPONSE: [Empathetic and supportive message]
    
    - The response should validate their feelings.
    - End with a gentle follow-up question to keep the conversation going.
    - Avoid generic responses and focus on the user's emotional state.
    - If the user is feeling neutral, provide a warm and inviting message to encourage sharing.
    - ALWAYS ASK A FOLLOW UP QUESTION
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI therapist providing warm and supportive responses."},
                {"role": "user", "content": response_prompt}
            ],
            temperature=0.5
        )
        return emotion, response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error in response generation: {e}")
        return emotion, "I'm here to support you. How are you feeling right now?"

def analyze_mood(user_input: str) -> tuple:
    """Enhanced wrapper for classify_emotion that handles deep conversations."""
    return classify_emotion(user_input)

#chat examples 
user_input = "I feel like no one understands me, and I just want to disappear."
conversation_history = [
    "I'm struggling a lot with everything.",
    "I feel like I'm not good enough."
]

emotion, response = generate_response(user_input, conversation_history)
print(f"Detected Emotion: {emotion}")
print(f"Response:\n{response}")