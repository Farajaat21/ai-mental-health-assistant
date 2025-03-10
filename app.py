
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import ssl
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
ssl._create_default_https_context = ssl._create_unverified_context

nltk.download('vader_lexicon')
from dotenv import load_dotenv 
import database 

database.create_database() 
user_id = "1" #Replace with function to classify user
load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error with chat: {e}")
        return None

users = {
    "john": "hello",
    "susan": "bye"
}

@auth.verify_password
def verify_password(username, password):
    actual_password = users.get(username)
    if actual_password == password: 
        return username
   

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

@app.route("/chat")
def chat_page():
    username = session.get('username')
    if not username:
        return redirect(url_for('login_page'))
        
    initial_response = chat_with_gpt(f"Hello {username}", username=username, include_description=True)
    initial_quote = chat_manager.get_default_quote()
    return render_template("main.html", initial_response=initial_response, quote=initial_quote, username=username)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/chat', methods=['POST'])
def chat():
    print("We got here")
    data = request.get_json()
    user_message = data.get('message', '')
    print(f"Received message: {user_message}")
    
    gpt_response = chat_with_gpt(user_message)
    if gpt_response is None:
        error_message = f"Sorry, the AI service is currently unavailable. Please try again later or api key not working.{os.getenv('OPENAI_API_KEY')}"
        print(error_message)
        return jsonify({"reply": error_message})
    
    user_id = auth.current_user()
    print(f"User ID for logging: {user_id}")
    
    
    if user_id is not None:
        print(f"Logging conversation: user_id={user_id}, user_message={user_message}, gpt_response={gpt_response}")
        database.logger(user_id, user_message, gpt_response)
    else:
        print("Skipping database logging because user is not authenticated")
    
    return jsonify({"reply": gpt_response}) 

@app.route('/quote', methods=['POST'])
def quote():
    data = request.get_json()
    user_message = data.get('message', '')
    print(f"Received message for quote: {user_message}")
    
    # Get mood for quote context
    mood = analyze_mood(user_message)
    quote_prompt = chat_manager.generate_quote_prompt(user_message, mood)
    
    quote_response = chat_with_gpt(quote_prompt)
    if quote_response is None:
        error_message = "Sorry, the AI service is currently unavailable. Please try again later."
        print(error_message)
        return jsonify({"quote": error_message})
    
    print(f"Sending quote response: {quote_response}")
    return jsonify({"quote": quote_response})

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5001, debug=True)