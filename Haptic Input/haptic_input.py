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
    switch_state = MCU.get_switch_state()
    return button_states, switch_state

def flash_leds():
    for _ in range(4):
        MCU.turn_off_leds()
        time.sleep(0.2)
        MCU.turn_on_leds()
        time.sleep(0.2)
        MCU.turn_off_leds()
        time.sleep(0.5)

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

def get_closest_anchor():
    anchors = ["0x111", "0x222", "0x333", "0x444", "0x555"]
    index = random.randint(0,4)
    return anchors[index]

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

def loop_sequence():
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
        flash_leds()
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
        _, switch_on = get_input_states()
        if switch_on: break

        loop_sequence()
