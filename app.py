from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session, send_file
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
import os
import openai
from dotenv import load_dotenv
import database
from models.mood import analyze_mood
from models.user import verify_user
from models.chat import chat_manager
from models.info import app_description
import logging
from voice_handler import generate_audio
import io

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
    api_keys = [
        os.getenv("OPENAI_API_KEY"),
        os.getenv("OPENAI_API_KEY_TWO"),
        os.getenv("OPENAI_API_KEY_THREE"),
        os.getenv("OPENAI_API_KEY_FOUR")
    ]
    for key in api_keys:
        if key:
            yield key

api_key_generator = get_next_api_key()

def set_next_api_key():
    global api_key_generator  # Declare global before usage
    try:
        openai.api_key = next(api_key_generator)
        print(f"Switched to API Key: {openai.api_key[:10]}...")
    except StopIteration:
        print("No more API keys available. Restarting API key rotation.")
        api_key_generator = get_next_api_key()  # Reset generator
        openai.api_key = next(api_key_generator, None)  # Assign first key

set_next_api_key()

def chat_with_gpt(prompt, conversation_history=[]):
    try:
        if not openai.api_key:
            print("No API key configured")
            return "Sorry, the chatbot is not properly configured. Please check the API key."

        system_message = app_description
        messages = [{"role": "system", "content": system_message}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except openai.error.AuthenticationError as e:
        print(f"Authentication error: {e}")
        set_next_api_key()
        return "Sorry, there's an issue with the API authentication. Trying another key..."
    except Exception as e:
        print(f"Error with chat: {str(e)}")
        return "Sorry, I encountered an error. Please try again."

@auth.verify_password
def verify_password(username, password):
    return verify_user(username, password)

@app.route("/")
def home_page():
    return render_template('landing_page.html')

@app.route("/login", methods=["GET"])
def login_page():
    return render_template('loginPage.html')

@app.route("/chat", methods=["GET"])
def chat_page():
    from models.chat import get_dynamic_greeting
    greeting = get_dynamic_greeting(session.get('username', 'Guest'))
    return render_template('main.html', initial_response=greeting)

# Existing /chat route accepts POST for chat API calls
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        username = session.get('username', 'Guest')

        if not user_message:
            return jsonify({
                "error": True,
                "reply": "Please enter a message"
            }), 400

        # Append user message to conversation history
        if username not in chat_manager.conversation_history:
            chat_manager.conversation_history[username] = []
        chat_manager.conversation_history[username].append({
            "role": "user",
            "content": user_message
        })

        # Let GPT analyze emotion
        emotion, depth, needs_quote = analyze_mood(user_message)

        # Pass full conversation history for better responses
        conversation_history = chat_manager.conversation_history.get(username, [])
        gpt_response = chat_with_gpt(user_message, conversation_history)

        if not gpt_response:
            raise Exception("No response from GPT")

        # If response contains quote + reply, split them
        if "RESPONSE:" in gpt_response and "QUOTE:" in gpt_response:
            parts = gpt_response.split("QUOTE:")
            response = parts[0].replace("RESPONSE:", "").strip()
            quote = parts[1].strip()
        else:
            response = gpt_response
            quote = None

        # Append GPT response to conversation history
        chat_manager.conversation_history[username].append({
            "role": "assistant",
            "content": response
        })

        response_data = {
            "reply": response,
            "emotion": emotion,
            "error": False,
            "default_quote": chat_manager.get_default_quote()
        }
        if quote:
            response_data["quote"] = quote

        if username != 'Guest':
            try:
                database.logger(username, user_message, gpt_response)
            except Exception as e:
                logging.error(f"Database logging error: {e}")

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Chat endpoint error: {e}")
        return jsonify({
            "error": True,
            "reply": "I'm here to help. Could you please try rephrasing your message?"
        }), 500

@app.route('/quote', methods=['POST'])
def quote():
    data = request.get_json()
    user_message = data.get('message', '')
    mood = analyze_mood(user_message)
    quote_prompt = chat_manager.generate_quote_prompt(user_message, mood[0])
    
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

if __name__ == '__main__':
    print("Starting server...")
    app.run(host='0.0.0.0', port=5001, debug=True)