import requests
# Import requests library to make HTTP requests

class HapticOutput:
    def __init__(self):
        self.BASE_URL = "http://192.168.2.122:8000"  # Base URL for the HTTP requests

    def play_direction(self, cardinal_direction, count=1, delay=0.0):
        # Send a request to play a haptic effect in the specified cardinal direction
        print("playing direction", cardinal_direction, count, delay)
        requests.get(self.BASE_URL + "/playdirection/" +
                     ",".join([str(i) for i in [cardinal_direction, count, delay]]))

    def play_error(self):
        # Send a request to play an error signal
        print("playing error signal")
        requests.get(self.BASE_URL + "/playerror")

    def play_motor(self, motor_id):
        # Send a request to play a specific motor
        print("playing motor", motor_id)
        requests.get(self.BASE_URL + "/playmotor/" + str(motor_id))

    def inidicate_obstacle(self, direction):
        # Placeholder function, not implemented
        pass

    def play_sequence(self, sequence):
        # Send a request to play a sequence of haptic effects
        print("playing sequence", sequence)
        requests.get(self.BASE_URL + "/playsequence/" +
                     ','.join([str(i) for i in sequence]))

    def play_ack_sequence(self):
        # Send a request to play an acknowledgment sequence
        print("playing ack sequence")
        requests.get(self.BASE_URL + "/playacksequence/")

