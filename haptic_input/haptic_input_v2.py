import time
import random
import network
import json
from picozero import RGBLED, Button, Switch, pico_led
import urequests

debounce = 0.3  # seconds
record_count = 0
sequence = [1, 2, 3, 4]
destination_sequence = [1, 2, 3, 4]

action_button = 5
buttonPins = [0, 1, 2, 3, 4, 5]
buttons = []

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
          (255, 255, 0), (0, 255, 255), (255, 0, 255)]

led = RGBLED(13, 14, 15)
switch = Switch(16)

ssid = 'Johnny'
password = '12345678990'
base_url = "http://192.168.137.13:8000"


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


def turn_off_leds():
    led.off()


def turn_on_leds():
    led.on()


def setup():
    for pin in buttonPins:
        btn = Button(pin, pull_up=False, bounce_time=debounce)
        buttons.append(btn)
    connect()
    sequence.clear()
    destination_sequence.clear()
    turn_off_leds()


def get_input_states():
    buttonStates = get_buttons_state()
    switchState = switch.value
    return buttonStates, switchState


def get_buttons_state():
    button_states = []
    for button in buttons:
        button_states.append(button.value)
    return button_states


def flash_leds():
    for _ in range(1):
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


def update_destination(sequence):
    print("sending map sequence request")
    request_url = base_url + "/updatedestination/" + str(sequence)
    response = urequests.get(str(request_url))
    response.close()


def get_location():
    print("sending get location request")
    request_url = base_url + "/getlocation"
    response = urequests.get(str(request_url))
    response.close()


def map_sequence(sequence):
    if (not sequence or len(sequence) <= 1 or not all(int(id) <= 5 for id in sequence)):
        print("invalid sequence")
        return
    print("sending map sequence request")
    request_url = base_url + "/mapsequence/" + str(",".join(sequence))
    response = urequests.get(str(request_url))
    response.close()


def play_ack_sequence():
    print("Sending ack_sequence request")
    request_url = base_url + "/playacksequence"
    response = urequests.get(str(request_url))
    response.close()


def play_sequence(sequence):
    print("sending play sequence request")
    request_url = base_url + "/playsequence/" + str(",".join(sequence))
    response = urequests.get(str(request_url))
    response.close()


def set_destination(sequence):
    if (not sequence or len(sequence) <= 1 or not all(int(id) <= 5 for id in sequence)):
        print("invalid sequence")
        return
    print("sending set destination request")
    request_url = base_url + "/setdestination/" + str(",".join(sequence))
    response = urequests.get(str(request_url))
    response.close()


def play_button(button):
    if (not (int(button) <= 5 and int(button) >= 0)):
        print("invalid button")
        return
    print("sending play button request")
    request_url = base_url + "/playbutton/" + str(button)
    response = urequests.get(str(request_url))
    response.close()


def record_sequence(buttonStates):
    if (any(buttonStates)):
        if (not buttonStates[action_button]):
            for id, state in enumerate(buttonStates):
                if state == 1:
                    led.on()
                    led.color = colors[id]
                    sequence.append(str(id))
                    play_button(id)
                    time.sleep(debounce)
                    turn_off_leds()
                    print("Button", id+1, "pressed")
                    print("Current Sequence:", sequence)
            return True
        else:
            play_button(action_button)
            time.sleep(0.5)
            map_sequence(sequence)
            flash_leds()
            play_sequence(sequence)
            sequence.clear()
            return False
    return True


def get_destination_sequence(buttonStates):
    if (any(buttonStates)):
        if (not buttonStates[action_button]):
            for id, state in enumerate(buttonStates):
                if state == 1:
                    led.on()
                    led.color = colors[id]
                    destination_sequence.append(str(id))
                    play_button(id)
                    time.sleep(debounce)
                    turn_off_leds()
                    print("Button", id+1, "pressed")
                    print("Current Sequence:", destination_sequence)
            return True
        else:
            play_button(action_button)
            time.sleep(0.5)
            set_destination(destination_sequence)
            flash_leds()
            destination_sequence.clear()
            return False
    return True


setup()
while True:
    time.sleep(0.8)
    buttonStates, switchOn = get_input_states()

    print("here")
    recording_mapping_sequence = False
    recording_destination_sequence = False

    while (switchOn):
        buttonStates, switchOn = get_input_states()
        if (not switchOn):
            break

        if (not any(buttonStates)):
            continue

        if (buttonStates[action_button] and not recording_mapping_sequence):
            print("recording mapping sequence")
            play_button(action_button)
            recording_mapping_sequence = True
            time.sleep(debounce)
            continue

        if (recording_mapping_sequence):
            recording_mapping_sequence = record_sequence(buttonStates)

    while (not switchOn):
        buttonStates, switchOn = get_input_states()
        if (switchOn):
            break

        if (not any(buttonStates)):
            continue

        print(buttonStates)

        if (buttonStates[action_button] and not recording_destination_sequence):
            print("recording destination sequence")
            play_button(action_button)
            recording_destination_sequence = True
            time.sleep(1)
            continue

        if (recording_destination_sequence):
            recording_destination_sequence = get_destination_sequence(
                buttonStates)
