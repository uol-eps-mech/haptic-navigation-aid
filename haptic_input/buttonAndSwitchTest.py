import time
import RPi.GPIO as GPIO

debounce = 0.2 #seconds

buttonPins = [15,18]

switchPin = 14

GPIO.setmode(GPIO.BCM)

def setup():    
    GPIO.setup(switchPin, GPIO.IN)
    GPIO.setup(buttonPins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def get_input_states():
    buttonStates = get_buttons_state()
    switchState = GPIO.input(switchPin) == GPIO.HIGH
    return buttonStates, switchState

def get_buttons_state():
    button_states = []
    for buttonPin in buttonPins:
        button_states.append(GPIO.input(buttonPin) == GPIO.HIGH)
    return button_states

setup()
while True:
    time.sleep(1)
    buttonStates, switchOn = get_input_states()
    
    while(switchOn):
        print("switch on")
        buttonStates, switchOn = get_input_states()
        if(not switchOn): break
        if (any(buttonStates)):
            print("Button Clicked")
        time.sleep(1)
        

    while(not switchOn):
        buttonStates, switchOn = get_input_states()
        if(switchOn): break
        if (any(buttonStates)):
            print("Button Clicked")
        print("switch off")
        time.sleep(1)


