import sqlite3 as sq
from datetime import datetime as dt 

def create_database(): 
    con = sq.connect("conversations.db") 
    cur = con.cursor() 
    
    # Create conversations table
    conversations_table = '''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            user_messages TEXT NOT NULL, 
            gpt_response TEXT NOT NULL
        )
    '''
    
    # Create users table
    users_table = '''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    '''
    
    cur.execute(conversations_table)
    cur.execute(users_table)
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
        return user  # Returns (username, password) tuple or None
    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        con.close()

#This will work to insert user conversations
def logger(user_id, user_messages, gpt_response): 
    con = sq.connect("conversations.db") 
    cur = con.cursor() 

    date = dt.now().strftime("%Y-%m-%d %H:%M:%S") #sets the date of the message to when it was sent
    cur.execute("INSERT INTO conversations (user_id, date, user_messages, gpt_response) VALUES (?,?,?,?)", 
                   (user_id, date, user_messages, gpt_response)) #inserts the user id, date, user messages, and gpt response into the database
    #line 26-28 sets a group of messages (question + bot response) into the database with their time 
    con.commit()
    con.close()  

#This will retrieve a set of messages 
def grabber(user_id): 
    con = sq.connect("conversations.db")
    cur = con.cursor()
    
    cur.execute("SELECT date, conversation FROM conversations WHERE user_id = ? ORDER BY date DESC", (user_id))
    chats = cur.fetchall()
    
    con.close() 
    history = "\n".join([f"{date}: {conversation}" for date, conversation in chats])
    return history
