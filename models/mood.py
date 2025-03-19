import openai
import logging

logging.basicConfig(level=logging.DEBUG)

def classify_emotion(user_input):
    """Use GPT to classify emotions and detect conversation depth."""
    
    classification_prompt = f"""
    Analyze this message and classify the emotional state: "{user_input}"
    
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
    - Overwhelmed (Too many demands, mentally overloaded, feeling suffocated, anxious and stressed)
    - Failure (Defeat, self-doubt, and regret)
    - Anger (Intense frustration, irritation, explosive outbursts or rage)
    - General sadness (neutral sadness)
    - Jealousy (Desire with insecurity and envy)
    - Rejected (Unwanted, dismissed, and unworthy)
    - No sadness (if none of the above)
    
    - Neutral (ONLY for greetings or casual messages that doesn't indicate any sad emotion)
    
    Respond with ONLY the emotion name, nothing else.
    Be very sensitive to emotional content - if there's ANY hint of negative emotion, don't use Neutral.
    """
    
    try:
        if not openai.api_key:
            return "Neutral", None

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an emotion detection specialist. Only respond with the emotion name."},
                {"role": "user", "content": classification_prompt}
            ],
            temperature=0.3
        )
        
        emotion = response.choices[0].message.content.strip()
        print(f"Detected emotion: {emotion}")  
        
        if emotion == "Neutral":
            return emotion, user_input

        
        slang_classification_prompt = f"""
        Analyze this text and determine if it uses informal language, slang, or a casual tone:
        "{user_input}"

        Return one of the following options:
        - "slang" if it contains informal language or strong slang
        - "casual" if it contains informal language but no strong slang
        - "formal" if it contains a more formal tone
        """

        slang_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a language analysis specialist. Analyze text to classify if it uses slang, casual language, or formal language."},
                {"role": "user", "content": slang_classification_prompt}
            ],
            temperature=0.3
        )
        
        tone = slang_response.choices[0].message.content.strip().lower()

        if emotion == "Neutral" or "hello" in user_input.lower() or "hello" in user_input.lower():
            return "Neutral", user_input

        if tone == "slang":
            prompt = f"""User is experiencing {emotion} and shared: "{user_input}"
            
            Provide two parts in this exact format:
            QUOTE: "[A meaningful, comforting quote that acknowledges their pain while offering hope]" - [Author]
            
            RESPONSE: [Write an empathetic response in a slang tone that matches the user's language. Use informal language and slang where appropriate. End with a casual follow-up question to keep the conversation going.]
            
            User input: {user_input}
            - Validate their emotions deeply
            - Show empathy and understanding
            - Use informal, slang-filled language
            - Always end with a casual question to keep the conversation flowing
            - Keep it warm and understanding
            - Be sensitive to their emotional state
            """
            
        elif tone == "casual":
            prompt = f"""User is experiencing {emotion} and shared: "{user_input}"
            
            Provide two parts in this exact format:
            QUOTE: "[A meaningful, comforting quote that acknowledges their pain while offering hope]" - [Author]
            
            RESPONSE: [Write an empathetic response in a casual tone that validates their feelings. Use informal but not slang-filled language. Always end with a gentle follow-up question.]
            
            User input: {user_input}
            - Validate their emotions deeply
            - Show empathy and understanding
            - Offer comfort and reassurance
            - Always end with a casual, thoughtful question
            - Be warm and compassionate
            - Encourage sharing more, if the user feels comfortable
            """

        else:
            prompt = f"""User is experiencing {emotion} and shared: "{user_input}"
            
            Provide two parts in this exact format:
            QUOTE: "[A meaningful, comforting quote that acknowledges their pain while offering hope]" - [Author]
            
            RESPONSE: [Write an empathetic response in a formal tone that validates their feelings. Use formal, polite language. Always end with a gentle follow-up question.]
            
            User input: {user_input}
            - Validate their emotions deeply
            - Show empathy and understanding
            - Offer comfort and reassurance
            - Always end with a thoughtful, polite follow-up question
            - Be warm, compassionate, and understanding
            - Avoid informal language
            - Ensure that the tone is respectful and nurturing
            """

        return emotion, prompt

    except Exception as e:
        logging.error(f"Error during emotion classification: {e}")
        return "Neutral", user_input

def analyze_mood(user_input: str) -> tuple:
    """Enhanced wrapper for classify_emotion that handles deep conversations."""
    emotion, prompts = classify_emotion(user_input)
    return emotion, prompts