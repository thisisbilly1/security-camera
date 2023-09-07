import socketio

# Create a Socket.IO client instance
sio = socketio.Client()
# Connect to the Socket.io server
sio.connect('http://localhost:4000', wait=True, wait_timeout=10)

# Define an event handler for the "connect" event
@sio.event
def connect():
    print("Connected to the server")

# Define an event handler for the "chat message" event
@sio.event
def chat_message(data):
    print(f"Received a message: {data}")


# Main loop to keep the script running
try:
    while True:
        message = input("Enter a message (or 'exit' to quit): ")
        if message == 'exit':
            break
        # Emit the "chat message" event to the server
        sio.emit('chat message', message)
except KeyboardInterrupt:
    pass

# Disconnect from the server when done
sio.disconnect()


