from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session, send_file
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
import os
import openai
import time  # Add this import
from dotenv import load_dotenv
import database
from models.mood import analyze_mood, ConversationContext, fetch_relevant_quote
from models.user import verify_user
from models.chat import chat_manager
from models.info import app_description
import logging
from voice_handler import generate_audio
import io
from collections import defaultdict
from models.voice_conversation import VoiceConversationHandler
import subprocess
import sys
from pathlib import Path
from models.camera_emotion import CameraEmotionDetector
from itertools import cycle
import random
import whisper
from models.mood import (
    classify_emotion,
    ConversationContext,
    fetch_relevant_quote,
    format_emotional_prompt,
    format_follow_up_response,
    format_neutral_response,
    analyze_mood,
    chat_with_gpt
)

logging.basicConfig(level=logging.DEBUG)

load_dotenv(override=True)

print(f"Loaded API Key: {os.getenv('OPENAI_API_KEY')[:10]}...")

database.create_database()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key-123')
CORS(app)
auth = HTTPBasicAuth()

# Check if API key exists
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not found in environment variables!")
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_next_api_key():
    global openai_api_keys
    if not openai_api_keys:
        logging.error("No API keys available")
        return None
    
    # Get the next key
    key = next(api_key_generator)
    logging.info(f"Switching to API key: {key[:10]}...")
    openai.api_key = key
    return key

def set_next_api_key():
    global openai_api_keys
    if not openai_api_keys:
        logging.error("No API keys available")
        return None
    
    # Reset the generator if we've used all keys
    if not hasattr(set_next_api_key, 'current_index'):
        set_next_api_key.current_index = 0
    
    set_next_api_key.current_index = (set_next_api_key.current_index + 1) % len(openai_api_keys)
    key = openai_api_keys[set_next_api_key.current_index]
    
    logging.info(f"Switching to API key: {key[:10]}...")
    openai.api_key = key
    return key

# Initialize API keys
openai_api_keys = []
for i in range(1, 6):  # Support up to 5 API keys
    key = os.getenv(f'OPENAI_API_KEY_{i}')
    if key:
        openai_api_keys.append(key)
        logging.info(f"Loaded API key {i}: {key[:10]}...")

if not openai_api_keys:
    logging.error("No OpenAI API keys found in environment variables")
else:
    logging.info(f"Successfully loaded {len(openai_api_keys)} API keys")
    openai.api_key = openai_api_keys[0]
    api_key_generator = cycle(openai_api_keys)

@auth.verify_password
def verify_password(username, password):
    return verify_user(username, password)

@app.route("/")
def home_page():
    return render_template('landing_page.html')

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username or not password:
            return render_template("loginPage.html", 
                error="Please provide both username and password")
        
        # Get user first
        user = database.get_user(username)
        if not user:
            return render_template("loginPage.html", 
                error="Username not found")
                
        # Verify password
        user_id = database.verify(username, password)
        if user_id:
            session['username'] = username
            session['user_id'] = user_id
            logging.info(f"User {username} logged in successfully")
            return redirect(url_for("chat_page"))
        
        return render_template("loginPage.html", 
            error="Invalid password")
            
    return render_template("loginPage.html")

# Added signup route
@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Check if username exists
        if database.user_exists(username):
            return render_template("signupPage.html", 
                error="Username already exists. Please choose a different username.")
        
        if database.add_user_to_db(username, password):
            return redirect(url_for("login_page"))
        return render_template("signupPage.html", 
            error="Error creating account. Please try again.")
    return render_template("signupPage.html")

@app.route("/chat", methods=["GET"])
def chat_page():
    from models.chat import get_dynamic_greeting
    greeting = get_dynamic_greeting(session.get('username', 'Guest'))
    return render_template('main.html', initial_response=greeting)

# Existing /chat route accepts POST for chat API calls
conversation_histories = defaultdict(list)
MAX_HISTORY = 15  # Keep last 15 messages for richer context

# Initialize conversation contexts with proper import
conversation_contexts = defaultdict(ConversationContext)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        username = session.get('username', 'Guest')
        
        logging.info(f"[Chat] Received message: {user_message[:50]}...")
        
        if not user_message:
            return jsonify({"error": True, "reply": "Please enter a message"}), 400
            
        try:
            # Get or create conversation context
            context = conversation_contexts.get(username)
            if not context:
                context = ConversationContext()
                conversation_contexts[username] = context
            
            # Analyze mood and get response
            emotion, depth, needs_quote = classify_emotion(user_message)
            logging.info(f"[Chat] Detected emotion: {emotion}, depth: {depth}, needs_quote: {needs_quote}")
            
            # Format appropriate prompt based on conversation state
            if context.is_follow_up(user_message):
                prompt = format_follow_up_response(user_message, context)
                logging.info(f"Using follow-up prompt with emotion: {context.last_emotion}")
                # For follow-ups, use the last emotion if it exists
                if context.last_emotion and emotion == "Neutral":
                    emotion = context.last_emotion
                    logging.info(f"Using last emotion for continuity: {emotion}")
            else:
                prompt = format_emotional_prompt(emotion, user_message, context.get_context())
                logging.info(f"Using standard prompt with emotion: {emotion}")
            
            # Get response from GPT
            gpt_response = chat_with_gpt(prompt)
            
            # Ensure quote is properly formatted
            if needs_quote or (context.last_emotion and context.last_emotion != "Casual" and context.last_emotion != "Neutral"):
                # Check if response already has a quote format
                if not (gpt_response.strip().startswith('"') and '"' in gpt_response[:200]):
                    # Add relevant quote if missing
                    quote = fetch_relevant_quote(emotion if not context.last_emotion else context.last_emotion)
                    gpt_response = f'"{quote}"\n\n{gpt_response}'
            
            # Update context with new message and emotion
            context.add_message(user_message, emotion)
            
            # Store conversation
            store_conversation(username, user_message, gpt_response, emotion)
            
            # Map specific emotions that might not be in the frontend mapping
            emotion_mapping = {
                "Academic stress": "Academic stress",
                "Social anxiety": "Social anxiety",
                "Deep sadness": "Deep sadness",
                "General sadness": "General sadness",
                "Family concern": "Family concern",
                "Identity concern": "Identity concern", 
                "Mental Health concern": "Mental Health concern",
                "Pet loss": "Pet loss",
                "Mixed emotions": "Mixed emotions"
            }
            
            # Use the mapped emotion if available, otherwise use the original
            display_emotion = emotion_mapping.get(emotion, emotion)
            logging.info(f"[Chat] Responding with mapped emotion: {display_emotion} (original: {emotion})")
            
            return jsonify({
                "error": False,
                "reply": gpt_response,
                "emotion": display_emotion,
                "needs_quote": needs_quote
            })
            
        except Exception as e:
            logging.error(f"[Chat] Inner error: {str(e)}")
            return jsonify({
                "error": True, 
                "reply": "I'm having trouble processing your message. Please try again."
            }), 500
            
    except Exception as e:
        logging.error(f"[Chat] Error: {str(e)}")
        return jsonify({
            "error": True, 
            "reply": "An error occurred. Please try again."
        }), 500

@app.route('/quote', methods=['POST'])
def quote():
    data = request.get_json()
    user_message = data.get('message', '')
    
    # Create a new context for this request
    context = ConversationContext()
    emotion, prompt, needs_quote, updated_context = analyze_mood(user_message, context)
    
    quote_prompt = chat_manager.generate_quote_prompt(user_message, emotion)
    
    quote_response = chat_with_gpt(quote_prompt)
    if quote_response is None:
        return jsonify({"quote": "Sorry, the AI service is currently unavailable. Please try again later."})
    
    return jsonify({"quote": quote_response})

@app.route('/speak', methods=['POST'])
def speak():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
            
        audio_content = generate_audio(text)
        if audio_content is None:
            return jsonify({"error": "Failed to generate audio"}), 500

        return send_file(
            io.BytesIO(audio_content),    
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        )
        
    except Exception as e:
        print(f"Error in /speak endpoint: {e}")
        return jsonify({"error": str(e)}), 500

voice_handler = VoiceConversationHandler()

@app.route('/voice-chat', methods=['POST'])
def voice_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                "error": True,
                "reply": "I couldn't hear that clearly. Could you please repeat?"
            }), 400

        # Format the response properly
        emotion, raw_response = voice_handler.generate_voice_response(
            user_message, 
            max_tokens=150
        )
        
        # Ensure proper formatting of response
        if '"' in raw_response:
            parts = raw_response.split('\n\n')
            formatted_response = '\n\n'.join(parts)
        else:
            formatted_response = raw_response
        
        return jsonify({
            "reply": formatted_response,
            "emotion": emotion,
            "error": False
        })

    except Exception as e:
        logging.error(f"Voice chat error: {e}")
        return jsonify({
            "error": True,
            "reply": "I'm having trouble understanding. Could you try again?"
        }), 500

whisper_model = whisper.load_model("base")

@app.route('/whisper', methods=['POST'])
def whisper_transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    try:
        audio_file = request.files['audio']
        # Save temporary file
        temp_path = "temp_audio.webm"
        audio_file.save(temp_path)
        
        # Transcribe with whisper
        result = whisper_model.transcribe(temp_path)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return jsonify({
            'transcript': result['text'].strip(),
            'success': True
        })
        
    except Exception as e:
        logging.error(f"Transcription error: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

camera_detector = CameraEmotionDetector()

@app.route('/detect-emotion', methods=['POST'])
def detect_emotion():
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400
            
        result = camera_detector.detect_emotion(image_data)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Emotion detection error: {e}")
        return jsonify({"error": str(e), "emotion": "neutral", "confidence": 0.5}), 500

@app.route('/emotion-chat', methods=['POST'])
def emotion_chat():
    try:
        data = request.get_json()
        emotion = data.get('emotion', '')
        confidence = data.get('confidence', 0)
        
        # Format prompt based on visual emotion detection
        prompt = f"""Based on visual emotion detection:
        Detected Emotion: {emotion}
        Confidence: {confidence}
        
        Provide a supportive response addressing the user's emotional state.
        Keep it brief and encouraging."""
        
        response = chat_with_gpt(prompt)
        return jsonify({"reply": response, "error": False})
        
    except Exception as e:
        logging.error(f"Emotion chat error: {e}")
        return jsonify({"error": True, "reply": "I'm having trouble processing your emotions right now."}), 500

def generate_ssl_certificates():
    """Auto-generate SSL certificates if they don't exist"""
    cert_path = Path("cert.pem")
    key_path = Path("key.pem")
    
    if cert_path.exists() and key_path.exists():
        print("SSL certificates already exist")
        return True
        
    try:
        print("Generating SSL certificates...")
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-nodes',
            '-out', 'cert.pem', '-keyout', 'key.pem', '-days', '365',
            '-subj', '/CN=localhost'
        ], check=True)
        print("SSL certificates generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating SSL certificates: {e}")
        return False
    except FileNotFoundError:
        print("OpenSSL not found. Please install OpenSSL first")
        return False

def store_conversation(username, user_message, bot_response, emotion):
    """Store the conversation in the database if the user is not a guest."""
    if username != 'Guest':
        try:
            database.logger(username, user_message, bot_response, emotion)
        except Exception as e:
            logging.error(f"[Chat] Database error: {e}")

def get_messages(self):
    """Get the list of messages from history"""
    if not hasattr(self, 'history') or not self.history:
        return []
    return [msg['message'] for msg in self.history]

def get_emotions(self):
    """Get the list of emotions from history"""
    if not hasattr(self, 'history') or not self.history:
        return []
    return [msg['emotion'] for msg in self.history]

if __name__ == '__main__':
    print("Starting server...")
    cert_file = "cert.pem"
    key_file = "key.pem"
    
    # Check if certificates exist, if not create them
    if not (os.path.exists(cert_file) and os.path.exists(key_file)):
        print("Generating SSL certificates...")
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096", "-nodes",
            "-out", cert_file, "-keyout", key_file, "-days", "365",
            "-subj", "/CN=localhost"
        ])
    else:
        print("SSL certificates already exist")
    
    print("Starting with HTTPS...")
    # Change port from 5000 to 5001
    app.run(debug=True, ssl_context=(cert_file, key_file), host='0.0.0.0', port=5001)