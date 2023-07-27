# Import necessary libraries
import time
import network
from machine import Pin
from picozero import pico_led
import urequests

# Set debounce time in seconds
debounce = 0.3

# Initialize variables for recording sequences and the default sequence
record_count = 0
sequence = [1, 2, 3, 4]
destination_sequence = [1, 2, 3, 4]

# Define button pins
action_button = 5
location_request_button = 4
buttonPins = [0, 1, 2, 3, 4, 5]
buttons = []

# Set up switch and motor pins
switch = Pin(16, Pin.IN)
motor = Pin(6, Pin.OUT, Pin.PULL_DOWN)

# Function to play haptic motor with specified count, length, and delay
def play_haptic_motor(count=1, length=0.2, delay=0.1):
    for i in range(count):
        motor.value(1)
        time.sleep(length)
        motor.value(0)
        if count > 1:
            time.sleep(delay)

# Functions to play different haptic patterns
def play_error():
    print("playing error")
    play_haptic_motor(3, 0.2, 0.2)

def play_success():
    print("playing succes")
    play_haptic_motor(2, 0.2, 0.2)

def play_start():
    print("playing start")
    play_haptic_motor(1, 1)

def play_acknowledge():
    print("playing acknowledge")
    play_haptic_motor()

# Set up button pins and store them in a list
def setup():
    for pin in buttonPins:
        btn = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        buttons.append(btn)

# Get the states of buttons and the switch
def get_input_states():
    buttonStates = get_buttons_state()
    switchState = switch.value()
    return buttonStates, switchState

# Get the states of the buttons
def get_buttons_state():
    button_states = []
    for button in buttons:
        button_states.append(button.value())
    return button_states

# Function to play a sequence of haptic patterns
def play_seq(seq):
    for i in seq:
        if i == 0:
            play_error()
        elif i == 1:
            play_acknowledge()
        elif i == 2:
            play_success()
        else:
            play_start()
        time.sleep(5)

# Setup button pins
setup()

# Set this to True to test sequence playback, False to run regular input handling
sequence_testing = True

# Regular input handling loop
if sequence_testing == False:
    while True:
        # Get the states of buttons and the switch
        buttonStates, switchOn = get_input_states()

        # Handle input while the switch is ON
        while switchOn:
            # Get the states of buttons and the switch
            buttonStates, switchOn = get_input_states()

            if not switchOn:
                # Play a haptic pattern to acknowledge the switch turning off
                play_haptic_motor(2)
                break

            if not any(buttonStates):
                continue

            if any(buttonStates):
                # Play a haptic pattern in response to a button press
                play_haptic_motor()

        # Handle input while the switch is OFF
        while not switchOn:
            # Get the states of buttons and the switch
            buttonStates, switchOn = get_input_states()

            if switchOn:
                # Play a haptic pattern to acknowledge the switch turning on
                play_haptic_motor()
                break

            if not any(buttonStates):
                continue

            if any(buttonStates):
                # Play a haptic pattern in response to a button press
                play_haptic_motor()

# Test sequence playback
if sequence_testing == True:
    test_seq = [0, 1, 2, 3]
    play_seq(test_seq)

    time.sleep(10)
    seq = [1, 3, 0, 2, 1, 3, 1, 1, 1, 3]
    play_seq(seq)
