from database import add_user_to_db, get_user, verify as db_verify
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
    # First check if it's a default user
    if username in DEFAULT_USERS and DEFAULT_USERS[username] == password:
        logging.info(f"Default user {username} verified successfully")
        return True
    
    # Then check database
    user_id = db_verify(username, password)
    if user_id:
        logging.info(f"Database user {username} verified successfully")
        return True
    
    logging.warning(f"User verification failed for {username}")
    return False

def add_user(username, password):
    # Don't allow overwriting default users
    if username in DEFAULT_USERS:
        logging.warning(f"Attempt to add default user {username} blocked")
        return False
    
    # Check if user already exists in database
    if get_user(username):
        logging.warning(f"User {username} already exists in database")
        return False
        
    return add_user_to_db(username, password)