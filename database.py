import sqlite3 as sq
from datetime import datetime as dt 
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def create_database(): 
    con = sq.connect("conversations.db") 
    cur = con.cursor() 
    table = '''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            user_message TEXT NOT NULL, 
            gpt_response  TEXT NOT NULL
        )
    '''
    cur.execute(table)  
    con.commit()
    con.close()

def add_user_to_db(username, password):
    con = sq.connect("conversations.db")
    cur = con.cursor()
    
    try:
        date = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO users (username, password, created_at) VALUES (?,?,?)",
                   (username, password, date))
        con.commit()
        return True
    except sq.IntegrityError:
        return False
    finally:
        con.close()

def get_user(username):
    con = sq.connect("conversations.db")
    cur = con.cursor()
    
    try:
        cur.execute("SELECT username, password FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        return user  
    except Exception as e:
        logging.error(f"Database error: {e}")
        return None
    finally:
        con.close()

def logger(user_id, user_message, gpt_response): 
    con = sq.connect("conversations.db") 
    cur = con.cursor() 

    date = dt.now().strftime("%Y-%m-%d %H:%M:%S") #sets the date of the message to when it was sent
    cur.execute("INSERT INTO conversations (user_id, date, user_message, gpt_response) VALUES (?,?,?,?)", 
                   (user_id, date, user_message, gpt_response)) #inserts the user id, date, user messages, and gpt response into the database
    con.commit()
    con.close()  

def grabber(user_id): 
    conn = sq.connect("conversations.db")
    cur = conn.cursor()
    
    cur.execute("SELECT date, user_message, gpt_response FROM conversations WHERE user_id = ?", (user_id,))
    chats = cur.fetchall()
    conn.close() 
    
    history = "\n".join([f"{date}: {message} - {response}" for date, message, response in chats])
    return history

def register(username, password): 
    conn = sq.connect("conversations.db")
    cur = conn.cursor() 
    
    try:
        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return {"success": True, "message": "User registered successfully"}
    finally:
        conn.close() 

def verify(username, password): 
    conn = sq.connect("conversations.db")
    cur = conn.cursor() 

    cur.execute("SELECT user_id, password FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        return user[0]  
    return None
