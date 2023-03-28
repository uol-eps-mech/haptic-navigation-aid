import time
import random
import json
import RPi.GPIO as GPIO
from microcontroller_unit import RPi #, Arduino

debounce = 0.2 #seconds
record_count = 0
sequence = [None for _ in range(5)]

button_pins = [15,18,23,8]
led_pins = [14,17,22,7]
switch_pin = 21
MCU = RPi(None, led_pins, button_pins, switch_pin)
# MCU = Arduino("COM7", led_pins, button_pins, switch_pin)

def get_input_states():
    button_states = MCU.get_button_states()
    switch_state = MCU.get_switch_state(switch_pin)
    return button_states, switch_state

def flash_leds(delay, no_of_flashes=4):
    for _ in range(no_of_flashes):
        MCU.turn_off_leds()
        time.sleep(delay/2)
        MCU.turn_on_leds()
        time.sleep(delay)
        MCU.turn_off_leds()
        time.sleep(delay/2)

def print_sequence(sequence):
    print("------------ CURRENT SEQEUENCE ----------------")
    print(sequence)
    print("-----------------------------------------------")

def play_sequence(sequence):
    for led in sequence:
        MCU.turn_on_led(led_pins[led])
        time.sleep(0.5)
        MCU.turn_off_led(led_pins[led])
        time.sleep(0.5)

anchors = ["0x111", "0x222", "0x333", "0x444", "0x555"]
def get_closest_anchor():
    index = random.randint(0,4)
    return anchors[index]

def get_anchor_position(anchor_id):
    return (random.randint(0,12), random.randint(0,12))

def get_user_position():
    return (random.randint(0,12), random.randint(0,12))

def get_distance_from_anchor(anchor_id):
    ux, uy = get_user_position()
    ax, ay = get_anchor_position(anchor_id)
    distance = ((ax-ux)**2+(ay-uy)**2)**0.5
    return distance

def addOrUpdateAnchorMapping(anchor, sequence):
    jsonFile = open("store.json", "r")
    mappings = json.load(jsonFile)
    jsonFile.close()

    try:
        mappings.update({anchor: sequence})
    except:
        mappings[anchor] = sequence

    jsonFile = open("store.json", "w")
    jsonFile.write(json.dumps(mappings))
    jsonFile.close()

# We should play the vibrations on the motor facing the direction of the anchor
# To do this we need to get the direction of the anchor
# Method exposed by haptic output should take direction as an argument
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

def loop_sequence(button_states):
    if (any(button_states)):
        print("switch off", button_states, switch_on)
        closest_anchor = get_closest_anchor()
        jsonFile = open("store.json", "r")
        mappings = json.load(jsonFile)
        jsonFile.close()

        sequence_to_play = [None for _ in range(5)]

        try:
            sequence_to_play = mappings[closest_anchor]
        except:
            pass

        if (any(x != 100 for x in sequence_to_play)):
            time.sleep(0.7)
            print_sequence(sequence_to_play)
            play_sequence(sequence_to_play)
            indicate_distance(closest_anchor)

def record_sequence(button_states, counter):
    print("switch on", button_states, switch_on)
    if counter < 5:
        if (any(button_states)):
            #print("Counter: ", counter)

            for id, state in enumerate(button_states):
                if state == 1:
                    MCU.turn_on_led(led_pins[id])
                    sequence[counter] = (id)
                    time.sleep(debounce)
                    MCU.turn_off_leds()

                    #print("Button" , id+1, "pressed")
                    #print("Current Sequence:", sequence)

            return counter + 1
    else:
        closest_anchor = get_closest_anchor()
        addOrUpdateAnchorMapping(closest_anchor, sequence)
        time.sleep(0.5)
        flash_leds(delay=0.2)
        return 0

    return counter

MCU.turn_off_leds()
while True:
    time.sleep(0.8)
    button_states, switch_on = get_input_states()
    
    print("here")
    counter = 0
    while switch_on:
        button_states, switch_on = get_input_states()
        if(not switch_on): break
        counter = record_sequence(button_states, counter)

    while(not switch_on):
        button_states, switch_on = get_input_states()
        if switch_on: break

        loop_sequence(button_states)
