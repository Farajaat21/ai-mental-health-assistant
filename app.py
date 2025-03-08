import openai
from flask_httpauth import HTTPBasicAuth
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
from flask_cors import CORS
import os
from dotenv import load_dotenv 
import database 
from models.info import app_description  # Import the app description
from models.mood import analyze_mood  # Import the mood analysis function
from models.user import add_user, verify_user  # Import user management functions

database.create_database() 
load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_gpt(prompt):
    try:
        # Analyze the user's mood
        mood = analyze_mood(prompt)
        
        # Prepend the app description and mood analysis to the user's prompt
        full_prompt = f"{app_description}\n\nUser Mood: {mood}\n\nUser: {prompt}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error with OpenAI: {e}")
        return None

@auth.verify_password
def verify_password(username, password):
    return verify_user(username, password)

@app.route("/")
def home_page():
    return redirect(url_for('login_page'))

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if verify_password(username, password):
            return redirect(url_for('chat_page'))
        else:
            return render_template("loginPage.html", error="Invalid credentials")
    return render_template("loginPage.html")

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not add_user(username, password):
            return render_template("signupPage.html", error="User already exists")
        return redirect(url_for('login_page'))
    return render_template("signupPage.html")

@app.route("/chat")
def chat_page():
    return render_template("main.html")

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    gpt_response = chat_with_gpt(user_message)
    if gpt_response is None:
        return jsonify({"reply": f"Sorry, the AI service is currently unavailable. Please try again later or api key not working.{os.getenv('OPENAI_API_KEY')}"})
    
    user_id = auth.current_user()
    database.logger(user_id, user_message, gpt_response)
    return jsonify({"reply": gpt_response})   

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5001, debug=True)