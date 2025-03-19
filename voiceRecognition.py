import os
import whisper
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)
# Load Whisper model globally - using the smallest model for quick responses
model = whisper.load_model("base")

@app.route('/whisper', methods=['POST'])
def whisper_transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided."}), 400

    audio_file = request.files['audio']
    try:
        # Save temporary audio file
        temp_path = "temp_audio.webm"
        audio_file.save(temp_path)
        
        # Transcribe using local Whisper model
        result = model.transcribe(temp_path)
        transcript = result["text"]
        
        # Clean up temp file
        os.remove(temp_path)
        
        return jsonify({"transcript": transcript})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
