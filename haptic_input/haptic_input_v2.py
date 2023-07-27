# Import necessary libraries
import time
import network
from machine import Pin
from picozero import pico_led
import urequests

# Set debounce time in seconds
debounce = 0.3

# Initialize variables for recording sequences and destination sequence
record_count = 0
sequence = [1, 2, 3, 4]
destination_sequence = [1, 2, 3, 4]

# Define pins for buttons, LEDs, and other components
record_button = 5
location_request_button = 4
buttonPins = [0, 1, 2, 3, 4, 5]
buttons = []
colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (0, 1, 1), (1, 0, 1)]

R = Pin(13, Pin.OUT, Pin.PULL_DOWN)
G = Pin(14, Pin.OUT, Pin.PULL_DOWN)
B = Pin(15, Pin.OUT, Pin.PULL_DOWN)
led = [R, G, B]

switch = Pin(16, Pin.IN)
motor = Pin(6, Pin.OUT, Pin.PULL_DOWN)

# SSID and password for the network
ssid = 'Johnny'
password = '12345678990'
# Base URL for server communication
base_url = "http://192.168.137.13:8000"

# Function to connect to the network
def connect():
    # Connect to WLAN
    pico_led.off()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    wlan.connect(ssid, password)
    attempts = 0
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
        attempts += 1
        if attempts > 10:
            break
    if wlan.isconnected() == False:
        connect()

    if wlan.isconnected() == True:
        pico_led.on()

# Functions to control LEDs and haptic motor
def turn_off_led():
    for pin in led:
        pin.value(0)

def turn_on_led():
    for pin in led:
        pin.value(1)

def set_led_color(color):
    for id, val in enumerate(color):
        led[id].value(val)

def play_haptic_motor(count=1, length=0.2, delay=0.1):
    for i in range(count):
        motor.value(1)
        time.sleep(length)
        motor.value(0)
        if count > 1:
            time.sleep(delay)

# Function to setup buttons and establish network connection
def setup():
    for pin in buttonPins:
        btn = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        buttons.append(btn)
    connect()
    sequence.clear()
    destination_sequence.clear()
    turn_off_led()
    play_haptic_motor(3)

# Function to get the states of buttons and the switch
def get_input_states():
    buttonStates = get_buttons_state()
    switchState = switch.value()
    return buttonStates, switchState

# Function to get the states of individual buttons
def get_buttons_state():
    button_states = []
    for button in buttons:
        button_states.append(button.value())
    return button_states

# Function to flash LEDs for indicating status
def flash_leds():
    for _ in range(1):
        turn_off_led()
        time.sleep(0.1)
        turn_on_led()
        time.sleep(0.1)
        turn_off_led()
        time.sleep(0.2)

# Function to print the current sequence (debugging purpose)
def print_sequence(sequence):
    print("------------ CURRENT SEQEUENCE ----------------")
    print(sequence)
    print("-----------------------------------------------")

# Functions to send various requests to the server
def send_update_destination_request(sequence):
    print("sending map sequence request")
    request_url = base_url + "/updatedestination/" + str(sequence)
    response = urequests.get(str(request_url))
    response.close()

def send_map_sequence_request(sequence):
    if (not sequence or len(sequence) <= 1 or not all(int(id) <= 5 for id in sequence)):
        print("invalid sequence")
        play_haptic_motor(3, 0.1, 0.2)
        return
    print("sending map sequence request")
    request_url = base_url + "/mapsequence/" + str(",".join(sequence))
    response = urequests.get(str(request_url))
    response.close()

def send_play_ack_sequence_request():
    print("Sending ack_sequence request")
    request_url = base_url + "/playacksequence"
    response = urequests.get(str(request_url))
    response.close()

def send_play_sequence_request(sequence):
    print("sending play sequence request")
    request_url = base_url + "/playsequence/" + str(",".join(sequence))
    response = urequests.get(str(request_url))
    response.close()

def send_set_destination_request(sequence):
    if (not sequence or len(sequence) <= 1 or not all(int(id) <= 5 for id in sequence)):
        print("invalid sequence")
        return
    print("sending set destination request")
    request_url = base_url + "/setdestination/" + str(",".join(sequence))
    response = urequests.get(str(request_url))
    response.close()

def send_get_nearest_landmark_request():
    print("sending get nearest landmark request")
    request_url = base_url + "/getnearestlandmark"
    response = urequests.get(str(request_url))
    response.close()

def send_play_motor_request(motor):
    if (not (int(motor) <= 5 and int(motor) >= 0)):
        print("invalid motor")
        return
    print("sending play motor request")
    request_url = base_url + "/playmotor/" + str(motor)
    response = urequests.get(str(request_url))
    response.close()

# Function to handle safe server requests, handles exceptions with haptic feedback
def safe_request(request_func, arg=None):
    try:
        if arg == None:
            request_func()
        else:
            request_func(arg)
    except:
        play_haptic_motor(3, 0.4, 0.2)

# Function to record the user's button presses to create a sequence
def record_sequence(buttonStates):
    # If any button other than the record button is clicked
    if any(buttonStates):
        if not buttonStates[record_button]:
            for id, state in enumerate(buttonStates):
                # Find clicked button id
                if state == 1:
                    turn_on_led()
                    set_led_color(colors[id])
                    sequence.append(str(id)) # add button id to sequence
                    safe_request(send_play_motor_request, id) # play appropriate motor
                    time.sleep(debounce)
                    turn_off_led()
                    play_haptic_motor() # indiciate success to user
                    print("Button", id+1, "pressed")
                    print("Current Sequence:", sequence)
            return True
        else:
            # Else stop recording
            play_haptic_motor()
            time.sleep(0.5)
            safe_request(send_map_sequence_request, sequence) # map sequence
            flash_leds()
            safe_request(send_play_sequence_request, sequence) # play sequence to user
            sequence.clear() # clear current sequence
            return False
    return True

# Function to get the destination sequence
def get_destination_sequence(buttonStates):
    if any(buttonStates):
        if not buttonStates[record_button]:
            for id, state in enumerate(buttonStates):
                if state == 1:
                    set_led_color(colors[id])
                    destination_sequence.append(str(id))
                    safe_request(send_play_motor_request, id)
                    time.sleep(debounce)
                    turn_off_led()
                    play_haptic_motor()
                    print("Button", id+1, "pressed")
                    print("Current Sequence:", destination_sequence)
            return True
        else:
            play_haptic_motor()
            time.sleep(0.5)
            safe_request(send_set_destination_request, destination_sequence)
            flash_leds()
            destination_sequence.clear()
            return False
    return True

# Call the setup function to initialize the system
setup()

# Main loop to continuously handle button presses and switch status
while True:
    time.sleep(0.5)
    buttonStates, switchOn = get_input_states()

    recording_mapping_sequence = False
    recording_destination_sequence = False

    while switchOn:
        buttonStates, switchOn = get_input_states()
        if not switchOn:
            play_haptic_motor(2)
            break

        if not any(buttonStates):
            continue

        if any(buttonStates) and not (buttonStates[record_button] or buttonStates[location_request_button]) and not recording_mapping_sequence:
            play_haptic_motor(3, 0.1, 0.2)

        if buttonStates[location_request_button] and not recording_mapping_sequence:
            play_haptic_motor()
            safe_request(send_get_nearest_landmark_request)
            continue

        if buttonStates[record_button] and not recording_mapping_sequence:
            print("recording mapping sequence")
            play_haptic_motor()
            safe_request(send_play_ack_sequence_request)
            recording_mapping_sequence = True
            time.sleep(debounce)
            continue

        if recording_mapping_sequence:
            recording_mapping_sequence = record_sequence(buttonStates)

    while not switchOn:
        buttonStates, switchOn = get_input_states()
        if switchOn:
            play_haptic_motor()
            break

        if not any(buttonStates):
            continue

        if any(buttonStates) and not buttonStates[record_button] and not recording_destination_sequence:
            play_haptic_motor(3, 0.1, 0.2)

        if buttonStates[record_button] and not recording_destination_sequence:
            print("recording destination sequence")
            play_haptic_motor(2)
            safe_request(send_play_ack_sequence_request)
            recording_destination_sequence = True
            time.sleep(1)
            continue

        if recording_destination_sequence:
            recording_destination_sequence = get_destination_sequence(buttonStates)
