from flask import Flask, request, jsonify
import requests
import threading
app = Flask(__name__)

def smth():
# Endpoint to handle the button click in Bot A
    app.run(port=5001)

@app.route('/bot_b_action', methods=['GET'])
def perform_bot_b_action(bot):
    # Perform the desired action in Bot B
    chat_id = '-4017494691'  # Replace with your group chat ID
    message = "This message is sent by Bot B in response to Bot A's request."
    bot.send_message(chat_id, message)
    return jsonify({'status': 'Action performed in Bot B'})