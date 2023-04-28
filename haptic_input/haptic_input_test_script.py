import time
import network
from machine import Pin
from picozero import pico_led
import urequests

debounce = 0.3  # seconds
record_count = 0
sequence = [1, 2, 3, 4]
destination_sequence = [1, 2, 3, 4]

action_button = 5
location_request_button = 4
buttonPins = [0, 1, 2, 3, 4, 5]
buttons = []

switch = Pin(16, Pin.IN)
motor = Pin(6, Pin.OUT, Pin.PULL_DOWN)


def play_haptic_motor(count=1, length=0.2, delay=0.1):
    for i in range(count):
        motor.value(1)
        time.sleep(length)
        motor.value(0)
        if count > 1:
            time.sleep(delay)

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

def setup():
    for pin in buttonPins:
        btn = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        buttons.append(btn)

def get_input_states():
    buttonStates = get_buttons_state()
    switchState = switch.value()
    return buttonStates, switchState


def get_buttons_state():
    button_states = []
    for button in buttons:
        button_states.append(button.value())
    return button_states

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

setup()
sequence_testing = True

if sequence_testing == False:
    while True:
        buttonStates, switchOn = get_input_states()
        while (switchOn):
                buttonStates, switchOn = get_input_states()
                if (not switchOn):
                    play_haptic_motor(2)
                    break

                if (not any(buttonStates)):
                    continue

                if (any(buttonStates)):
                    play_haptic_motor()

        while (not switchOn):
                buttonStates, switchOn = get_input_states()
                if (switchOn):
                    play_haptic_motor()
                    break

                if (not any(buttonStates)):
                    continue

                if (any(buttonStates)):
                    play_haptic_motor()

if sequence_testing == True:
    test_seq = [0,1,2,3]
    play_seq(test_seq)
        
    time.sleep(10)
    seq = [1, 3, 0, 2, 1, 3, 1, 1, 1, 3]
    play_seq(seq)





