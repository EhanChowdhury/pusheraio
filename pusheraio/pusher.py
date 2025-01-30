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
            self.events = {}
            self.connect_to_pusher()
            self.log("Pusher AIO initialized.")
        else:
            self.log("Pusher AIO not initialized: Error credentials not submitted.")

    def connect_to_pusher(self):
        try:
            self.ws_url = f"wss://ws.pusherapp.com/app/{self.key}?protocol=7&client=Python"
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

    def event(self, channel_name, event_name):
        """Decorator to register an event."""
        def decorator(func):
            if channel_name not in self.events:
                self.events[channel_name] = {}
            self.events[channel_name][event_name] = func
            return func
        return decorator

    def start(self):
        """Start the WebSocket connection and listen for messages."""
        def on_message(ws, message):
            """Handle incoming WebSocket messages."""
            try:
                data = json.loads(message)
                event_name = data.get("event")
                event_data = data.get("data")
                channel_name = data.get("channel")

                # Check if the event matches any registered event for the channel
                if channel_name in self.events and event_name in self.events[channel_name]:
                    self.events[channel_name][event_name](event_data)
                else:
                    print(f"Unhandled event on {channel_name}: {event_name}")
            except Exception as e:
                print(f"Error processing message: {e}")

        def on_error(ws, error):
            """Handle WebSocket errors."""
            print(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            """Handle WebSocket closure."""
            print(f"WebSocket closed: {close_msg}")

        def on_open(ws):
            """Handle WebSocket opening."""
            print("WebSocket connection established.")
            # Subscribe to all registered channels
            for channel_name in self.events.keys():
                ws.send(json.dumps({
                    "event": "pusher:subscribe",
                    "data": {"channel": channel_name}
                }))
                print(f"Subscribed to channel: {channel_name}")

        def run():
            """Run the WebSocket connection."""
            self.running = True
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open,
            )
            while self.running:
                self.ws.run_forever()

        # Start WebSocket in a background thread
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def quit(self):
        self.running = False
        try:
            if self.ws:
                self.ws.close()
        except:
            self.log("WS has not been created yet.")

    def send_message_and_get_response(self, channel, event, message, response_event, timeout):
        """Send message, wait for response with a timeout"""
        try:
           if self.nondynamicws:
               self.nondynamicws.close()
        except:
              self.log("WS has not been created yet.")


        # WebSocket event handler methods
        def on_message(nondynamicws, message):
            self.log(f"Message received: {message}")
            if self.response_event in message:
                self.response = message
                self.log(f"Response event matched, message received: {message}")
            else:
                self.log(f"Response event not found, continuing to wait.")

        def on_error(nondynamicws, error):
            self.log(f"Error: {error}")

        def on_close(nondynamicws, close_status_code, close_msg):
            self.log("Connection closed")

        def on_open(nondynamicws):
            """Handle WebSocket opening."""
            print("WebSocket connection established.")
            # Subscribe to all registered channels
            nondynamicws.send(json.dumps({
                "event": "pusher:subscribe",
                    "data": {"channel": channel}
            }))
            print(f"Subscribed to channel: {channel}")

        self.channel = channel  # Set the channel dynamically
        self.response = None  # Reset the response
        self.response_event = response_event
        self.nondynamicws = websocket.WebSocketApp(
            self.ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        

        # Send the message
        try:
           # Trigger the message to the channel
          self.send_message(channel, event, message)
          self.log(f"Message sent: {message}")
        except Exception as e:
          self.log(f"Failed to send message: {e}")
          return False



        # Run the WebSocket connection in a separate thread to listen for responses
        thread = threading.Thread(target=self.nondynamicws.run_forever)
        thread.start()

        # Wait for up to 5 seconds for the response
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.response is not None:
                return self.response

        # Timeout, no response received
        self.nondynamicws.close()
        return False    
