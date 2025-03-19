from database import add_user_to_db, get_user
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

DEFAULT_USERS = {
    "john": "hello",
    "susan": "bye",
    "admin": "admin",
    "faraja": "faraja"
}

def verify_user(username, password):
    user = get_user(username)
    if user and user[1] == password:
        return True
    
    return DEFAULT_USERS.get(username) == password

def add_user(username, password):
    # Don't allow overwriting default users
    if username in DEFAULT_USERS:
        return False
    return add_user_to_db(username, password)