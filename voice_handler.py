import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

def get_next_voice_key():
    """Generator for rotating through available ElevenLabs API keys"""
    api_keys = [
        os.getenv('ELEVENLABS_API_KEY'),
        os.getenv('ELEVENLABS_API_KEY_TWO'),
        os.getenv('ELEVENLABS_API_KEY_THREE')
    ]
    while True:
        for key in [k for k in api_keys if k]:  # Only use non-None keys
            yield key

# Initialize the key generator
voice_key_generator = get_next_voice_key()
current_voice_key = next(voice_key_generator)

def set_next_voice_key():
    """Switch to the next available API key"""
    global current_voice_key, voice_key_generator
    try:
        current_voice_key = next(voice_key_generator)
        logging.info(f"Switched to next ElevenLabs API key: {current_voice_key[:10]}...")
    except StopIteration:
        voice_key_generator = get_next_voice_key()
        current_voice_key = next(voice_key_generator)

def generate_audio(text):
    """Generate audio using ElevenLabs API with key rotation"""
    global current_voice_key
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.getenv('VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": current_voice_key
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }

    # Try each API key until one works or we run out
    for _ in range(3):  # Try up to 3 times
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return response.content
            elif response.status_code in [401, 403]:  # Authentication error
                set_next_voice_key()
                headers["xi-api-key"] = current_voice_key
                continue
            else:
                logging.error(f"ElevenLabs API error: {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"Error generating audio: {e}")
            set_next_voice_key()
            headers["xi-api-key"] = current_voice_key
    
    return None  # All attempts failed
