from fastapi import FastAPI
import json
import math
import time

acknowledgement_effect_id = 47
error_effect_id = 27

app = FastAPI()

times = []

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


def format_sequence_int(sequence):
    string_sequence = sequence.split(",")
    int_sequence = [int(x) for x in string_sequence]
    return int_sequence


def format_sequence_bool(sequence):
    string_sequence = sequence.split(",")
    bool_sequence = [bool(x) for x in string_sequence]
    return bool_sequence


def get_destination():
    jsonFile = open("store.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    try:
        destination = data["destination"]
        return eval(destination)
    except:
        return None


def find_nearest_landmark(x, y):
    jsonFile = open("store.json", "r")
    mappings = json.load(jsonFile)["mappings"]
    jsonFile.close()

    try:
        shortest_distance = 200
        nearest_landmark = None
        for location in mappings:
            distance = math.dist((x, y), eval(location))
            if (distance < shortest_distance):
                nearest_landmark = (eval(location), mappings[location])
                shortest_distance = distance
        return (None, None) if nearest_landmark == None else nearest_landmark
    except:
        return (None, None)
    
def add_execution_time(time, start, end):
    file = open("update_execution_times.csv", "a+")
    file.write(str(time) + "," + str(start) + "," + str(end) + "\n")
    file.close()

def add_to_user_path(position):
    file = open("user_paths.csv", "a+")
    file.write( str(position) + "\n")
    file.close()


@app.get("/")
async def root():
    print("Hello World")
    return {"message": "Hello World"}


@app.get("/playobstacle/{direction}")
def play_obstacle(direction):
    print("Play Obstacle Request Received")
    return {"message": "Played direction: " + str(direction)}


@app.get("/mapsequence/{sequence}")
def map_sequence(sequence):
    print("Map Sequence Request received")
    return {"message": "Sequence '" + sequence + "' mapped to location: '" + str((x, y)) + "'"}


@app.get("/playacksequence")
def play_ack_sequence():
    print("PLay ack Request received")
    return {"message": "playing acknowledgement sequence"}


@app.get("/playsequence/{sequence}")
def play_entered_sequence(sequence):
    print("PLay sequence Request received")
    if isinstance(sequence, str) or isinstance(sequence[0], str):
        sequence = format_sequence_int(sequence)

    print("playing sequence", sequence)
    return {"message": "playing sequence: " + str(sequence)}


def play_location_sequence(location):
    print("PLaying location sequence")
    seqeunce = get_sequence_for_location(location)
    play_entered_sequence(seqeunce)


@app.get("/playmotor/{motor}")
def play_button(motor):
    print("Playing motor", motor)
    return {"message": "playing motor: '" + motor + "'"}


@app.get("/getlocation/{sequence}")
def get_location(sequence):
    location = get_location_from_sequence(format_sequence_int(sequence))
    return {"message": location}


@app.get("/getnearestlandmark")
def get_nearest_landmark():
    update_destination_location(None)
    return {"message": "Nearest landmark found:"}


@app.get("/setdestination/{sequence}")
def update_destination(sequence):
    destination = get_location_from_sequence(format_sequence_int(sequence))
    if destination:
        update_destination_location(destination)
        return {"message": "destination updated to: " + destination}
    else:
        return {"message": "Sequence received is not mapped to a location"}

@app.get("/update")
def update():
    return {"message": "Udpated"}

@app.get("/ping")
def ping():
    t = time.time()
    times.append(t)
    if (len(times) > 1):
        add_execution_time(times[-1] - times[-2], 0, 0)
        # print("Latency", times[-1] - times[-2])
    return {"message": "hey"}