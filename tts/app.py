from flask import Flask, jsonify, request
from flasgger import Swagger
import torch
from TTS.api import TTS

app = Flask(__name__)
swagger = Swagger(app)  # Initialize Swagger


# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    
@app.route('/ttstofile', methods=['POST'])
def ttstofile():
    """
    Run ttstofile
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              description: The text to convert to speech
              example: "Hello, how are you?"
    responses:
      200:
        description: ttstofile successfully executed
      400:
        description: Bad request, text parameter is missing
    """
    
    # Check if the request content type is JSON
    if not request.is_json:
        return jsonify({"error": "Bad request, JSON content type required"}), 400

    # Get text from request body
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Bad request, text parameter is missing"}), 400

    text = data['text']
    
    tts.tts_to_file(text=text, speaker_wav="ita.wav", language="it", file_path="output.wav")

    return jsonify({"message": "OK!"}), 200

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5010)