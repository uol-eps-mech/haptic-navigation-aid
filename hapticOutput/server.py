from fastapi import FastAPI
from hapticOutput import play_direction, play_effect, play_sequence, map_button_to_effect
import json
import random

acknowledgement_effect_id = 47
error_effect_id = 27

app = FastAPI()

def get_user_location():
    anchors = [(0,0), (11,5), (3,4), (12,9), (2,7)]
    index = random.randint(0,4)
    return anchors[index]

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
    user_location = get_user_location()
    add_or_update_sequence_mapping(str(user_location), format_sequence(sequence))
    return {"message": "Sequence '" + sequence + "' mapped to location: '"  + str(user_location) + "'"}

@app.get("/playacksequence")
def play_ack_sequence():
    play_effect(acknowledgement_effect_id, 0.5, 2)
    return {"message": "playing acknowledgement sequence"}

@app.get("/playsequence/{sequence}")
def play_entered_sequence(sequence):
    play_sequence(format_sequence(sequence))
    return {"message": "playing sequence: " + sequence}

@app.get("/playbutton/{button}")
def play_button(button):
    effect_id = map_button_to_effect(int(button))
    play_effect(effect_id)
    return {"message": "playing effect: '" + str(effect_id) + "' for button: '" + button + "'"}

@app.get("/getlocation/{sequence}")
def get_location(sequence):
    location = get_location_from_sequence(format_sequence(sequence))
    return {"message": location}

@app.get("/updatedestination/{location}")
def update_destination(location):
    update_destination_location(location)
    return {"message": "destination updated to: " + location}