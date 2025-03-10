
import openai
from nltk.sentiment import SentimentIntensityAnalyzer

def classify_emotion(text):
    """Use OpenAI to classify different shades of emotions with NLTK as backup."""
    classification_prompt = f"""
    The user provided this message: "{text}"
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
    - Faliure (Defeat, self-doubt, and regret)
    - Anger (Intense frustration, irritation, rage)
    - General sadness (neutral sadness)
    - Jealousy (Desire with insecurity and envy)
    - Rejected (Unwanted, dismissed, and unworthy)
    - No sadness (if none of the above)

    Only return the category name.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an emotion detection assistant."},
                {"role": "user", "content": classification_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except:
        
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(text)
        
        if sentiment['compound'] <= -0.5:
            return "Deep sadness"
        elif sentiment['compound'] < -0.2:
            return "General sadness"
        elif sentiment['compound'] < 0:
            return "Disappointment"
        else:
            return "No sadness"

def analyze_mood(text):
    """Get detailed emotion analysis with intensity."""
    emotion = classify_emotion(text)
    
    sia = SentimentIntensityAnalyzer()
    intensity = abs(sia.polarity_scores(text)['compound'])
    
    intensity_level = 'moderate'
    if intensity > 0.5:
        intensity_level = 'strong'
    elif intensity < 0.2:
        intensity_level = 'mild'
        
    return f"{intensity_level} {emotion}"

def get_emotion_prompt(emotion, user_input):
    """Generate appropriate prompt based on emotional state."""
    emotion_prompts = {
        "Deep sadness": "User is a teenager/young adult. The user is deeply sad and possibly grieving. Analyze the user's input and provide two things based on the user input: A quote suited for the situation based on the analysis and A comforting and deeply empathetic conversatioal response.",
        "Frustration": "User is a teenager/young adult. The user is frustrated and upset. Analyze the user's input and provide two things based on the user input: A quote suited for the situation based on the analysis and a calm response, validating their feelings, and offering constructive advice.",
        "Disappointment": "User is a teenager/young adult. The user is disappointed. Analyze the user's input and provide two things based on the user input: A quote suited for the situation based on the analysis and Offer reassurance and help them see potential positives or ways to improve.",
        "Emptiness": "User is a teenager/young adult. The user feels empty, as if something is missing in their life or lacking purpose. Analyze the user's input and provide two things based on the user input: A quote suited for the situation based on the analysis and respond with deep empathy and offer words that help them feel seen and understood.",
        "No sadness": "The user does not seem sad. Provide a normal, friendly response."
    }
    
    base_prompt = emotion_prompts.get(emotion, emotion_prompts["No sadness"])
    return f"{base_prompt} Ask questions when needed to carry on the conversation and make user feel cared for. User input: {user_input}"

def get_gpt_response(user_input, emotion):
    """Get GPT response based on emotional state."""
    prompt = get_emotion_prompt(emotion, user_input)
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an empathetic mental health support assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting GPT response: {e}")
        return None
    