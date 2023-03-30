from fastapi import FastAPI
from haptic_output.haptic_output import HapticOutput
from localisation.localisation import Localisation
import json
import random
import board
import adafruit_tca9548a

acknowledgement_effect_id = 47
error_effect_id = 27

# uses board.SCL and board.SDA
i2c = board.I2C()  
# Create the TCA9548A object and give it the I2C bus
i2cExpander = adafruit_tca9548a.TCA9548A(i2c)
haptic_output = HapticOutput(i2cExpander[0:5])
localisation = Localisation(i2cExpander[5])

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

@app.get("/")
async def root():
    print("Hello World")
    return {"message": "Hello World"}

@app.get("/mapsequence/{sequence}")
def map_sequence(sequence):
    user_location = localisation.get_user_location()
    add_or_update_sequence_mapping(str(user_location), format_sequence(sequence))
    return {"message": "Sequence '" + sequence + "' mapped to location: '"  + str(user_location) + "'"}

@app.get("/playacksequence")
def play_ack_sequence():
    haptic_output.play_effect(acknowledgement_effect_id, 0.5, 2)
    return {"message": "playing acknowledgement sequence"}

@app.get("/playsequence/{sequence}")
def play_entered_sequence(sequence):
    haptic_output.play_sequence(format_sequence(sequence))
    return {"message": "playing sequence: " + sequence}

@app.get("/playbutton/{button}")
def play_button(button):
    effect_id = haptic_output.map_button_to_effect(int(button))
    haptic_output.play_effect(effect_id)
    return {"message": "playing effect: '" + str(effect_id) + "' for button: '" + button + "'"}

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
