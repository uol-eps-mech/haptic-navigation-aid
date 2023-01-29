import pyfirmata
import time
import pyautogui

pyautogui.FAILSAFE = False
debounce : int = 200
record_count  : int  = 0
sequence = [100 for _ in range(5)]

board=pyfirmata.Arduino('COM7')

it = pyfirmata.util.Iterator(board)
it.start()

buttonPins : list[int] = [2,4,6,8]
buttons = []

ledPins : list[int] = [3,5,7,9]
leds = []

switchPin = 10
switch = board.digital[switchPin]

def setup():
    switch = board.digital[switchPin]
    switch.mode = pyfirmata.INPUT

    for buttonPin in buttonPins:
        button = board.digital[buttonPin]
        button.mode = pyfirmata.INPUT
        buttons.append(button)

    for ledPin in ledPins:
        led = board.digital[ledPin]
        led.mode = pyfirmata.OUTPUT
        leds.append(led)

def get_input_states():
    buttonStates = get_buttons_state()
    switchState = switch.read()
    return buttonStates, switchState

def get_buttons_state():
    button1 = buttons[0].read()
    button2 = buttons[1].read()
    button3 = buttons[2].read()
    button4 = buttons[3].read()
    return [button1, button2, button3, button4]

def turn_off_leds():
    for led in leds:
        led.write(0)

def turn_on_leds():
    for led in leds:
        led.write(1)

def flash_leds():
    for _ in range(4):
        turn_off_leds()
        time.sleep(0.2)
        turn_on_leds()
        time.sleep(0.2)
        turn_off_leds()
        time.sleep(0.5)
    

def print_sequence():
    print("------------ CURRENT SEQEUENCE ----------------")
    print(sequence)
    print("-----------------------------------------------")

def play_sequence():
    for led in sequence:
        leds[led].write(1)
        time.sleep(0.5)
        leds[led].write(0)
        time.sleep(0.5)

def record_sequence():
    counter = 0
    buttonStates, switchState = get_input_states()
    print(buttonStates, switchState)
    while(switchState == 0):
        buttonStates, switchState = get_input_states()
        print("switch off", buttonStates, switchState)
        if (any(x != 100 for x in sequence)):
            time.sleep(0.7)
            print_sequence()
            play_sequence()
        if switchState == 1: break
    
    while(switchState == 1):
        buttonStates, switchState = get_input_states()
        print("switch on", buttonStates, switchState)
        if (any(buttonStates)):
            if counter < 5:
                for id, state in enumerate(buttonStates):
                    if state == 1:
                        board.digital[ledPins[id]].write(1)
                        sequence[counter] = (id)
                        time.sleep(0.5)
                        turn_off_leds()
                        print("Button" , id+1, "pressed")
                        print("Current Sequence:", sequence)
                counter += 1
            
            else:
                time.sleep(0.5)
                flash_leds()    

while True:
    setup()
    time.sleep(0.1)

    record_sequence()