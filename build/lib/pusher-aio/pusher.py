import pusher
import websocket
import json
import threading
import time

class pusheraio:
    def __init__(self, app_id, key, secret, cluster, verbose):
        if app_id and key and secret and cluster:
            self.app_id = app_id
            self.key = key
            self.secret = secret
            self.cluster = cluster
            self.verbose = verbose
            self.connect_to_pusher()
            self.log("Pusher AIO initialized.")
        else:
            self.log("Pusher AIO not initialized: Error credentials not submitted.")

    def connect_to_pusher(self):
        try:
            self.pusher_client = pusher.Pusher(
                app_id=self.app_id,
                key=self.key,
                secret=self.secret,
                cluster=self.cluster
            )
        except Exception as e:
            self.log(f"Failed to connect to pusher: {e}")
            self.pusher_client = None  # Set to None if connection fails
       
    def log(self, message):
        """Print a message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def send_message(self, channel, event, message):
        if self.pusher_client:
            try:
                self.pusher_client.trigger(channel, event, {'message': message})
            except Exception as e:
                self.log(f"Failed to send message: {e}")
        else:
            self.log("Pusher client not connected.")


    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        data = json.loads(message)
        if data.get('event') == 'your-event':  # Make sure this is the correct event
            self.response = data['data']  # Store the response data
    
    def on_error(self, ws, error):
        """Handle any errors"""
        print(f"Error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print("WebSocket connection closed")

    def on_open(self, ws):
        """Handle opening the WebSocket connection"""
        subscribe_message = {
            "event": "pusher:subscribe",
            "data": {
                "channel": self.channel
            }
        }
        ws.send(json.dumps(subscribe_message))
    
    def send_message_and_get_response(self, channel, event, message):
        """Send message, wait for response with a 5-second timeout"""
        if self.ws:
            self.ws.close()
        
        self.channel = channel  # Set the channel dynamically
        self.response = None  # Reset the response
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open
        
        # Send the message
        try:
            # Trigger the message to the channel
            self.send_message(channel, event, message)
            self.log(f"Message sent: {message}")
        except Exception as e:
            self.log(f"Failed to send message: {e}")
            return False
        
        # Run the WebSocket connection in a separate thread to listen for responses
        thread = threading.Thread(target=self.ws.run_forever)
        thread.start()

        # Wait for up to 5 seconds for the response
        timeout = 5
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.response is not None:
                return self.response
        
        # Timeout, no response received
        self.ws.close()
        return False


    
