from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

rooms = {}  # Dictionary to track users in rooms

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rooms')
def list_rooms():
    return jsonify(list(rooms.keys()))

@app.route('/rooms/<room>')
def room_info(room):
    participants = rooms.get(room, [])
    return jsonify(participants)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    
    if room not in rooms:
        rooms[room] = []
    rooms[room].append(username)
    
    emit('room_users', rooms[room], to=room)
    send(f'{username} has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    
    if room in rooms and username in rooms[room]:
        rooms[room].remove(username)
        if not rooms[room]:
            del rooms[room]
        else:
            emit('room_users', rooms[room], to=room)
    
    send(f'{username} has left the room.', to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    send(f"{data['username']}: {data['message']}", to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
