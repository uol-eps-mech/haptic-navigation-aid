import time
import random
import json
from gpiozero import Button, LED
import time

debounce : int = 200
record_count  : int  = 0
sequence = [100 for _ in range(5)]

buttonPin = [24]
buttons = []

ledPin = [23]
leds = []

switchPin = 10
# switch = board.digital[switchPin]

def setup():
    # switch = board.digital[switchPin]
    # switch.mode = pyfirmata.INPUT
    # GPIO.setup(18,GPIO.OUT)

    button = Button(buttonPin)
    buttons.append(button)

    led = LED(ledPin)
    leds.append(led)

def get_input_states():
    buttonStates = get_buttons_state()
    switchState = True
    return buttonStates, switchState

def get_buttons_state():
    buttonStates = []
    for button in buttons:
        buttonStates.append(button.is_pressed)
    return buttonStates

def turn_off_leds():
    for led in leds:
        led.value = 0

def turn_on_leds():
    for led in leds:
        led.value = 1

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
        leds[led].value = 1
        time.sleep(0.5)
        leds[led].value = 1
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
    jsonFile.write(json.dumps(mappings, sort_keys=True))
    jsonFile.close()

def wait_for_location_request(buttonStates):
    # print("switch off", buttonStates, switchOn)
    if (any(buttonStates)):
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
            print("Counter: ", counter)
            for id, state in enumerate(buttonStates):
                if state == 1:
                    led = LED(ledPins[id])
                    led.value = 1
                    sequence[counter] = (id)
                    time.sleep(0.5)
                    turn_off_leds()
                    print("Button" , id+1, "pressed")
                    print("Current Sequence:", sequence)
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
        buttonStates, switchOn = get_input_states()
        if(switchOn): break

        wait_for_location_request(buttonStates)
