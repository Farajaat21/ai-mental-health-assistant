from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session
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

logging.basicConfig(level=logging.DEBUG)

load_dotenv(override=True)

print(f"Loaded API Key: {os.getenv('OPENAI_API_KEY')[:10]}...")

load_dotenv()
database.create_database() 
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key-123')  
CORS(app)
auth = HTTPBasicAuth()

# check if we have api key here
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
    global openai
    try:
        openai.api_key = next(api_key_generator)
        print(f"Switched to API Key: {openai.api_key[:10]}...")
    except StopIteration:
        print("No more API keys available.")
        openai.api_key = None

set_next_api_key()

def chat_with_gpt(prompt, conversation_history=[]):
    """Removed unused parameters username and include_description"""
    try:
        if not openai.api_key:
            print("No API key configured")
            return "Sorry, the chatbot is not properly configured. Please check the API key."

        system_message = app_description
        messages = [{"role": "system", "content": system_message}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if verify_user(username, password):
            session['username'] = username
            return redirect(url_for('chat_page'))
        else:
            return render_template("loginPage.html", error="Invalid credentials")
    return render_template("loginPage.html")

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if database.add_user_to_db(username, password):
            return redirect(url_for('login_page'))
        return render_template("signupPage.html", error="Username already exists")
    
    return render_template("signupPage.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home_page'))

@app.route('/chat')
def chat_page():
    username = session.get('username', 'Guest')
    
    initial_response = "Hi! 👋 I'm your AI mental health companion. I'm here to listen and support you. How are you feeling today?"
    
    initial_quote = chat_manager.get_default_quote()
    return render_template("main.html", initial_response=initial_response, quote=initial_quote, username=username)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# type of greeting/
greetings = ["hello", "hi", "hey", "good morning", "good evening", "what's up"]

@app.route('/chat', methods=['POST'])
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

        # Handle greetings using the global greetings list
        if user_message.lower() in greetings:
            response = chat_manager.handle_repeated_greeting(username)
            return jsonify({
                "reply": response,
                "emotion": "No sadness",
                "error": False,
                "default_quote": chat_manager.get_default_quote()
            })

        # Check for informal messages
        informal_response = chat_manager.handle_informal_message(user_message)
        if informal_response:
            return jsonify({
                "reply": informal_response,
                "emotion": "No sadness",
                "error": False,
                "default_quote": chat_manager.get_default_quote()
            })

        # user greeting reset
        chat_manager.reset_greeting_count(username)
        emotion, prompts = analyze_mood(user_message)
        
        # Get response from GPT
        gpt_response = chat_with_gpt(prompts)
        
        if not gpt_response:
            raise Exception("No response from GPT")
            
        # quote formting 
        if "RESPONSE:" in gpt_response and "QUOTE:" in gpt_response:
            parts = gpt_response.split("QUOTE:")
            response = parts[0].replace("RESPONSE:", "").strip()
            quote = parts[1].strip()
        else:
            response = gpt_response
            quote = None

        response_data = {
            "reply": response,
            "emotion": emotion,
            "error": False,
            "default_quote": chat_manager.get_default_quote()
        }
        
        if quote:
            response_data["quote"] = quote

        # gues login
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
    print(f"Received message for quote: {user_message}")
    
    # try to generate quote if depper emotion shown
    mood = analyze_mood(user_message)
    quote_prompt = chat_manager.generate_quote_prompt(user_message, mood[0])
    
    quote_response = chat_with_gpt(quote_prompt)
    if quote_response is None:
        error_message = "Sorry, the AI service is currently unavailable. Please try again later."
        print(error_message)
        return jsonify({"quote": error_message})
    
    print(f"Sending quote response: {quote_response}")
    return jsonify({"quote": quote_response})

def setup_ssl_context():
    """Setup SSL context for development"""
    import os
    import subprocess
    
    cert_dir = os.path.join(os.path.dirname(__file__), 'certs')
    cert_path = os.path.join(cert_dir, 'cert.pem')
    key_path = os.path.join(cert_dir, 'key.pem')
    
    # Check if certs directory exists certificates path: not important for now
    if not os.path.exists(cert_dir):
        print("Creating certs directory...")
        os.makedirs(cert_dir)
    
    # Check if certificates exist
    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        print("Generating new SSL certificates...")
        try:
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-nodes',
                '-out', cert_path,
                '-keyout', key_path,
                '-days', '365',
                '-subj', '/CN=localhost'
            ], check=True)
            print("SSL certificates generated successfully!")
        except Exception as e:
            print(f"Failed to generate certificates: {e}")
            return None
    
    return cert_path, key_path

if __name__ == '__main__':
    ssl_files = setup_ssl_context()
    if ssl_files:
        cert_path, key_path = ssl_files
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_path, key_path)
        
       # Development only - allows self-signed certificates
        context.verify_mode = ssl.CERT_NONE
        context.check_hostname = False
        
        print("Starting server with HTTPS...")
        app.run(host='0.0.0.0', port=5001, debug=True, ssl_context=context)
    else:
        print("Starting server without HTTPS...")
        app.run(host='0.0.0.0', port=5001, debug=True) 