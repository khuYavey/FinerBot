from flask import Flask, request, jsonify
import requests
import threading

app = Flask(__name__)

@contextmanager
def flask_app_context(app):
    with app.app_context():
        yield

def run_app():
    with flask_app_context(app):
        app.run(port=5000)

@app.route('/trigger_inspector_side', methods=['POST'])
def trigger_inspector_side():
        # Trigger Bot B by sending an HTTP request
        response = requests.get('http://localhost:5001/pushing_new_data_to_inspector')  # Change the URL to the Bot B server
        if response.status_code == 200:
            return jsonify({'status': 'Action triggered in inspector_side'})
        else:
            return jsonify({'status': 'Failed to trigger inspector_side'})

webhook = threading.Thread(target=run_app)
webhook.start()

