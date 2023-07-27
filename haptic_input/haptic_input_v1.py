# Import necessary libraries
import time
import random
import json
import RPi.GPIO as GPIO
from microcontroller_unit import RPi #, Arduino

# Set debounce time in seconds
debounce = 0.2

# Initialize variables for recording sequences and the default sequence
record_count = 0
sequence = [None for _ in range(5)]

# Define button and LED pins
button_pins = [15, 18, 23, 8]
led_pins = [14, 17, 22, 7]
switch_pin = 21

# Create an instance of the microcontroller unit (MCU) with RPi
MCU = RPi(None, led_pins, button_pins, switch_pin)
# To use with Arduino, uncomment the following line and replace "COM7" with the appropriate port
# MCU = Arduino("COM7", led_pins, button_pins, switch_pin)

# Function to get the states of buttons and the switch
def get_input_states():
    button_states = MCU.get_button_states()
    switch_state = MCU.get_switch_state(switch_pin)
    return button_states, switch_state

# Function to flash LEDs with specified delay and number of flashes
def flash_leds(delay, no_of_flashes=4):
    for _ in range(no_of_flashes):
        MCU.turn_off_leds()
        time.sleep(delay/2)
        MCU.turn_on_leds()
        time.sleep(delay)
        MCU.turn_off_leds()
        time.sleep(delay/2)

# Function to print the current sequence
def print_sequence(sequence):
    print("------------ CURRENT SEQEUENCE ----------------")
    print(sequence)
    print("-----------------------------------------------")

# Function to play a sequence of LEDs
def play_sequence(sequence):
    for led in sequence:
        MCU.turn_on_led(led_pins[led])
        time.sleep(0.5)
        MCU.turn_off_led(led_pins[led])
        time.sleep(0.5)

# List of anchors and functions to get anchor position, user position, and distance
anchors = ["0x111", "0x222", "0x333", "0x444", "0x555"]
def get_closest_anchor():
    # Randomly select an anchor from the list
    index = random.randint(0, 4)
    return anchors[index]

def get_anchor_position(anchor_id):
    # Generate random x and y positions for the anchor
    return (random.randint(0, 12), random.randint(0, 12))

def get_user_position():
    # Generate random x and y positions for the user
    return (random.randint(0, 12), random.randint(0, 12))

def get_distance_from_anchor(anchor_id):
    # Get the positions of the anchor and the user
    ux, uy = get_user_position()
    ax, ay = get_anchor_position(anchor_id)

    # Calculate the Euclidean distance between the anchor and the user
    distance = ((ax - ux) ** 2 + (ay - uy) ** 2) ** 0.5
    return distance

# Function to add or update anchor mappings in the JSON file
def addOrUpdateAnchorMapping(anchor, sequence):
    # Read the existing anchor mappings from the JSON file
    jsonFile = open("store.json", "r")
    mappings = json.load(jsonFile)
    jsonFile.close()

    try:
        # Try updating the existing anchor mapping
        mappings.update({anchor: sequence})
    except:
        # If the anchor mapping does not exist, add it to the mappings
        mappings[anchor] = sequence

    # Write the updated anchor mappings back to the JSON file
    jsonFile = open("store.json", "w")
    jsonFile.write(json.dumps(mappings))
    jsonFile.close()

# Function to indicate the distance to the anchor using haptic feedback
def indicate_distance(anchor_id):
    print("Indicating Distance")
    distance = get_distance_from_anchor(anchor_id)
    print("Distance from anchor:", distance)
    if distance > 10:
        flash_leds(delay=2)
    elif distance > 7:
        flash_leds(delay=1)
    elif distance > 4:
        flash_leds(delay=0.5, no_of_flashes=6)
    else:
        flash_leds(delay=0.25, no_of_flashes=6)

# Function to handle button presses while in sequence playback mode
def loop_sequence(button_states):
    if any(button_states):
        print("switch off", button_states, switch_on)
        # Get the closest anchor to the user
        closest_anchor = get_closest_anchor()
        # Read the anchor mappings from the JSON file
        jsonFile = open("store.json", "r")
        mappings = json.load(jsonFile)
        jsonFile.close()

        sequence_to_play = [None for _ in range(5)]

        try:
            # Try to get the sequence associated with the closest anchor
            sequence_to_play = mappings[closest_anchor]
        except:
            pass

        if any(x != 100 for x in sequence_to_play):
            # Play the sequence associated with the closest anchor
            time.sleep(0.7)
            print_sequence(sequence_to_play)
            play_sequence(sequence_to_play)
            indicate_distance(closest_anchor)

# Function to record the user's button presses to create a sequence
def record_sequence(button_states, counter):
    print("switch on", button_states, switch_on)
    if counter < 5:
        if any(button_states):
            for id, state in enumerate(button_states):
                if state == 1:
                    # Turn on the corresponding LED and record the button press in the sequence
                    MCU.turn_on_led(led_pins[id])
                    sequence[counter] = id
                    time.sleep(debounce)
                    MCU.turn_off_leds()

            return counter + 1
    else:
        # When the sequence is complete, get the closest anchor and store the sequence
        closest_anchor = get_closest_anchor()
        addOrUpdateAnchorMapping(closest_anchor, sequence)
        time.sleep(0.5)
        flash_leds(delay=0.2)
        return 0

    return counter

# Turn off all LEDs at the beginning
MCU.turn_off_leds()

# Main loop that runs continuously
while True:
    time.sleep(0.8)
    button_states, switch_on = get_input_states()

    print("here")
    counter = 0
    while switch_on:
        button_states, switch_on = get_input_states()
        if not switch_on:
            break
        counter = record_sequence(button_states, counter)

    while not switch_on:
        button_states, switch_on = get_input_states()
        if switch_on:
            break

        loop_sequence(button_states)
