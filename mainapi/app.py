from flask import Flask, jsonify, request
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)  # Initialize Swagger


# In-memory storage for the command text
command_text = {"text": ""}


@app.route('/get_command', methods=['GET'])
def get_command():
    """
    Retrieve a test command
    ---
    responses:
      200:
        description: A successful response
        content:
          application/json:
            schema:
              type: object
              properties:
                text:
                  type: string
                  example: "This is a test notification from backend"
    """
    return jsonify(command_text)

@app.route('/set_command', methods=['POST'])
def set_command():
    """
    Set the command text
    ---
    parameters:
      - name: text
        in: query
        type: string
        required: true
        description: The text to set as the command
    responses:
      200:
        description: Command successfully set
    """
    text = request.args.get('text')
    if text:
        command_text['text'] = text
        return jsonify({"message": "Command text successfully set."}), 200
    return jsonify({"message": "No text provided."}), 400


@app.route('/clear_command', methods=['POST'])
def clear_command():
    """
    Clear the command text after execution
    ---
    responses:
      200:
        description: Command text successfully cleared
    """
    command_text['text'] = ""
    return jsonify({"message": "Command text successfully cleared."}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5030)