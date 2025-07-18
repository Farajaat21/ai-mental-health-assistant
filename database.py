import sqlite3 as sq
from datetime import datetime as dt 
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def create_database(): 
    con = sq.connect("conversations.db") 
    cur = con.cursor() 
    
    # Create users table with additional fields
    users_table = '''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    '''
    
    # Enhanced conversations table
    conversations_table = '''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            user_message TEXT NOT NULL,
            gpt_response TEXT NOT NULL,
            emotion TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    '''
    
    try:
        cur.execute(users_table)
        cur.execute(conversations_table)
        con.commit()
    except Exception as e:
        logging.error(f"Database creation error: {e}")
        raise
    finally:
        con.close()

def add_user_to_db(username, password):
    """Add new user with better error handling"""
    con = sq.connect("conversations.db")
    cur = con.cursor()
    
    try:
        date = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        hashed_password = generate_password_hash(password)
        cur.execute("""
            INSERT INTO users (username, password, created_at, last_login) 
            VALUES (?, ?, ?, ?)
        """, (username, hashed_password, date, date))
        con.commit()
        return True
    except sq.IntegrityError:
        logging.warning(f"Username {username} already exists")
        return False
    except Exception as e:
        logging.error(f"Error adding user: {e}")
        return False
    finally:
        con.close()

def get_user(username):
    """Get user details"""
    con = sq.connect("conversations.db")
    cur = con.cursor()
    
    try:
        cur.execute("SELECT user_id, username, password FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'password': user[2]
            }
        return None
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        return None
    finally:
        con.close()

def logger(user_id, user_message, gpt_response, emotion=None): 
    """Enhanced logging with emotion tracking"""
    con = sq.connect("conversations.db") 
    cur = con.cursor() 

    try:
        date = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO conversations 
            (user_id, date, user_message, gpt_response, emotion) 
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, date, user_message, gpt_response, emotion))
        con.commit()
    except Exception as e:
        logging.error(f"Logging error: {e}")
        raise
    finally:
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

def get_user_history(username, limit=10):
    """Get user's conversation history with emotion context"""
    con = sq.connect("conversations.db")
    cur = con.cursor()
    
    try:
        cur.execute("""
            SELECT c.date, c.user_message, c.gpt_response, c.emotion
            FROM conversations c
            JOIN users u ON c.user_id = u.user_id
            WHERE u.username = ?
            ORDER BY c.date DESC
            LIMIT ?
        """, (username, limit))
        
        history = cur.fetchall()
        return [{"date": date, 
                "user_message": msg, 
                "gpt_response": resp,
                "emotion": emo} for date, msg, resp, emo in history]
    except Exception as e:
        logging.error(f"Error retrieving history: {e}")
        return []
    finally:
        con.close()

def verify(username, password): 
    """Verify user credentials"""
    con = sq.connect("conversations.db")
    cur = con.cursor() 

    try:
        # Get user with password
        cur.execute("SELECT user_id, password FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        
        if not user:
            logging.warning(f"User {username} not found in database")
            return None
            
        # Verify password hash
        if check_password_hash(user[1], password):
            # Update last login time
            login_time = dt.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("UPDATE users SET last_login = ? WHERE user_id = ?", 
                       (login_time, user[0]))
            con.commit()
            logging.info(f"User {username} verified successfully")
            return user[0]
            
        logging.warning(f"Invalid password for user {username}")
        return None
        
    except Exception as e:
        logging.error(f"Login verification error: {e}")
        return None
    finally:
        con.close()

def get_db_connection():
    """Get database connection with error handling"""
    try:
        conn = sq.connect("conversations.db")
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        raise

def user_exists(username):
    """Check if username already exists"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        logging.error(f"Error checking user existence: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
