import time
import random
import json
import RPi.GPIO as GPIO

debounce : int = 200
record_count  : int  = 0
sequence = [100 for _ in range(5)]

buttonPins = [4]

ledPins = [2]

#switchPin = 10
#switch = board.digital[switchPin]

GPIO.setmode(GPIO.BCM)

def setup():
    #switch = board.digital[switchPin]
    switch = True

    GPIO.setup(buttonPins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(ledPins, GPIO.OUT)

def get_input_states():
    buttonStates = get_buttons_state()
    switchState = True
    return buttonStates, switchState

def get_buttons_state():
    button_states = []
    for buttonPin in buttonPins:
        print(GPIO.input(buttonPin), buttonPin)
        button_states.append(GPIO.input(buttonPin) == GPIO.HIGH)
    print(button_states)
    return button_states

def turn_off_leds():
    GPIO.output(ledPins, GPIO.LOW)

def turn_on_leds():
    GPIO.output(ledPins, GPIO.HIGH)

def flash_leds():
    for _ in range(4):
        turn_off_leds()
        time.sleep(0.2)
        turn_on_leds()
        time.sleep(0.2)
        turn_off_leds()
        time.sleep(0.5)
    

def print_sequence(sequence):
    print("------------ CURRENT SEQEUENCE ----------------")
    print(sequence)
    print("-----------------------------------------------")

def play_sequence(sequence):
    for led in sequence:
        GPIO.output(ledPins[led], GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(ledPins[led], GPIO.LOW)
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
    # print("switch off", buttonStates, switchOn)
    closest_anchor = get_closest_anchor()
    jsonFile = open("store.json", "r")
    mappings = json.load(jsonFile)
    jsonFile.close()

    sequence_to_play = [100, 100, 100, 100, 100]

    try:
        sequence_to_play = mappings[closest_anchor]
    except:
        pass

    if (any(x != 100 for x in sequence_to_play)):
        time.sleep(0.7)
        print_sequence(sequence_to_play)
        play_sequence(sequence_to_play)
    

def record_sequence(buttonStates, counter):
    # print("switch on", buttonStates, switchOn)
    if counter < 5:
        if (any(buttonStates)):
            #print("Counter: ", counter)
            for id, state in enumerate(buttonStates):
                if state == 1:
                    GPIO.output(ledPins[id], GPIO.HIGH)
                    sequence[counter] = (id)
                    time.sleep(0.5)
                    turn_off_leds()
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

while True:
    setup()
    time.sleep(0.4)
    buttonStates, switchOn = get_input_states()
    
    print("here")
    counter = 0
    while(switchOn):
        buttonStates, switchOn = get_input_states()
        if(not switchOn): break
        counter = record_sequence(buttonStates, counter)

    while(not switchOn):
        _, switchOn = get_input_states()
        if(switchOn): break

        loop_sequence()
