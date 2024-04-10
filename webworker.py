from flask import Flask, jsonify, render_template, Response
from flask_socketio import SocketIO
import logging

# # Update dashboard at 60Hz 
UPDATE_INTERVAL = 1/60 # seconds

app = Flask(__name__)
socketio = SocketIO(app)
state = None
thread = None
log = logging.getLogger('werkzeug')

def run(state_):
    global state
    state = state_
    # app.run(host='0.0.0.0', port=5000, use_reloader=False, debug=False)
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)

def background_thread():
    global state
    while True:
        socketio.sleep(UPDATE_INTERVAL)
        socketio.emit('data', state._getvalue())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    global state
    return jsonify(state._getvalue())

@socketio.on('connect')
def connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)