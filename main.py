from fastapi import FastAPI
from haptic_output.haptic_output import HapticOutput
from localisation.localisation import Localisation
from path_planning.path_planning import calculate_next_direction
import json
import board
import adafruit_tca9548a

acknowledgement_effect_id = 47
error_effect_id = 27

# uses board.SCL and board.SDA
i2c = board.I2C()
# Create the TCA9548A object and give it the I2C bus
i2cExpander = adafruit_tca9548a.TCA9548A(i2c)
haptic_output = HapticOutput(i2cExpander)
localisation = Localisation(i2cExpander[6])

app = FastAPI()


def add_or_update_sequence_mapping(location, sequence):
    jsonFile = open("store.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    try:
        data["mappings"].update({location: sequence})
    except:
        data["mappings"][location] = sequence

    jsonFile = open("store.json", "w")
    jsonFile.write(json.dumps(data))
    jsonFile.close()


def get_location_from_sequence(sequence):
    jsonFile = open("store.json", "r")
    data = json.load(jsonFile)
    mappings = data["mappings"]
    jsonFile.close()

    for elem in mappings:
        if mappings[elem] == sequence:
            return elem
    return False


def get_sequence_for_location(location):
    jsonFile = open("store.json", "r")
    data = json.load(jsonFile)
    mappings = data["mappings"]
    jsonFile.close()

    try:
        location_found = mappings[location]
        return location_found
    except:
        return False


def update_destination_location(location):
    jsonFile = open("store.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    try:
        data.update({"destination": location})
    except:
        data["destination"] = location

    jsonFile = open("store.json", "w")
    jsonFile.write(json.dumps(data))
    jsonFile.close()


def format_sequence(sequence):
    string_sequence = sequence.split(",")
    int_sequence = [int(x) for x in string_sequence]
    return int_sequence


def get_destination():
    jsonFile = open("store.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    try:
        destination = data["destination"]
        return eval(destination)
    except:
        return None


@app.get("/")
async def root():
    print("Hello World")
    return {"message": "Hello World"}


@app.get("/mapsequence/{sequence}")
def map_sequence(sequence):
    print("Map Sequence Request received")
    x, y, h = localisation.get_user_location()
    add_or_update_sequence_mapping(
        str((x, y)), format_sequence(sequence))
    return {"message": "Sequence '" + sequence + "' mapped to location: '" + str((x, y)) + "'"}


@app.get("/playacksequence")
def play_ack_sequence():
    print("PLay ack Request received")
    haptic_output.play_effect(acknowledgement_effect_id, 0.5, 2)
    return {"message": "playing acknowledgement sequence"}


@app.get("/playsequence/{sequence}")
def play_entered_sequence(sequence):
    print("PLay sequence Request received")
    haptic_output.play_sequence(format_sequence(sequence))
    return {"message": "playing sequence: " + sequence}


def play_location_sequence(location):
    print("PLaying location sequence")
    seqeunce = get_sequence_for_location(location)
    play_entered_sequence(seqeunce)


@app.get("/playmotor/{motor}")
def play_button(motor):
    print("Playing motor", motor)
    haptic_output.play_motor(motor)
    return {"message": "playing motor: '" + motor + "'"}


@app.get("/getlocation/{sequence}")
def get_location(sequence):
    location = get_location_from_sequence(format_sequence(sequence))
    return {"message": location}


@app.get("/setdestination/{sequence}")
def update_destination(sequence):
    destination = get_location_from_sequence(format_sequence(sequence))
    if destination:
        update_destination_location(destination)
        return {"message": "destination updated to: " + destination}
    else:
        haptic_output.play_effect(error_effect_id, 0.5, 2)
        return {"message": "Sequence received is not mapped to a location"}


@app.get("/update")
def update():
    destination = get_destination()
    destination = (13 - int(destination[1]*2), int(destination[0]*2))
    print(destination)
    if (not destination):
        return
    x, y, h = localisation.get_user_location()
    print("location", x, y, h)
    next_direction, destination_reached = calculate_next_direction(
        (13 - int(y*2), int(x*2)), destination, h, 360-125, "Lab_1", True, True)

    if (destination_reached):
        play_ack_sequence()
        print("Destination Reached")
        return
    else:
        haptic_output.play_direction(next_direction)
        print("Next Direction", next_direction)
