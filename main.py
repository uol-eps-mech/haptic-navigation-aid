from fastapi import FastAPI
from haptic_output.haptic_output import HapticOutput
from localisation.localisation import Localisation
from path_planning.path_planning import PathPlanner
import json
import board
import adafruit_tca9548a
import math
import random
import time
from free_points import free_points

acknowledgement_effect_id = 47
error_effect_id = 27

# uses board.SCL and board.SDA
i2c = board.I2C()
# Create the TCA9548A object and give it the I2C bus
i2cExpander = adafruit_tca9548a.TCA9548A(i2c)
haptic_output = HapticOutput(i2cExpander)
localisation = Localisation(i2cExpander[6])
path_planner = PathPlanner("foyer_1m")

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
    file.write(str(position) + "\n")
    file.close()


def round(x):
    base = int(x)
    if x - base >= 0.75:
        return base + 1
    else:
        return base


@app.get("/")
async def root():
    print("Hello World")
    return {"message": "Hello World"}


@app.get("/playobstacle/{direction}")
def play_obstacle(direction):
    print("Play Obstacle Request Received")
    haptic_output.inidicate_obstacle(format_sequence_bool(direction))
    return {"message": "Played direction: " + str(direction)}


@app.get("/mapsequence/{sequence}")
def map_sequence(sequence):
    print("Map Sequence Request received")
    x, y = localisation.get_user_position()
    add_or_update_sequence_mapping(
        str((x, y)), format_sequence_int(sequence))
    return {"message": "Sequence '" + sequence + "' mapped to location: '" + str((x, y)) + "'"}


@app.get("/playacksequence")
def play_ack_sequence():
    print("PLay ack Request received")
    haptic_output.play_effect(acknowledgement_effect_id, 0.5, 2)
    return {"message": "playing acknowledgement sequence"}


@app.get("/playsequence/{sequence}")
def play_entered_sequence(sequence):
    print("PLay sequence Request received")
    if isinstance(sequence, str) or isinstance(sequence[0], str):
        sequence = format_sequence_int(sequence)

    print("playing sequence", sequence)
    haptic_output.play_sequence(sequence)
    return {"message": "playing sequence: " + str(sequence)}


def play_location_sequence(location):
    print("PLaying location sequence")
    seqeunce = get_sequence_for_location(location)
    play_entered_sequence(seqeunce)


@app.get("/playmotor/{motor}")
def play_button(motor):
    print("Playing motor", motor)
    haptic_output.play_motor(int(motor))
    return {"message": "playing motor: '" + motor + "'"}


@app.get("/getlocation/{sequence}")
def get_location(sequence):
    location = get_location_from_sequence(format_sequence_int(sequence))
    return {"message": location}


@app.get("/getnearestlandmark")
def get_nearest_landmark():
    destination = get_destination()
    update_destination_location(None)
    x, y = localisation.get_user_position()
    landmark, sequence = find_nearest_landmark(x, y)
    if (landmark == None):
        play_ack_sequence()
        return {"message": "Nearest landmark found not found."}
    else:
        play_entered_sequence(sequence)

    print("Landmark", landmark)
    update_destination_location(destination)
    return {"message": "Nearest landmark found: '" + str(landmark) + "' with sequence: '" + str(sequence) + "'."}


@app.get("/setdestination/{sequence}")
def update_destination(sequence):
    destination = get_location_from_sequence(format_sequence_int(sequence))
    if destination:
        update_destination_location(destination)
        return {"message": "destination updated to: " + str(destination)}
    else:
        haptic_output.play_effect(error_effect_id, 0.5, 2)
        return {"message": "Sequence received is not mapped to a location"}


@app.get("/update")
def update():
    destination = get_destination()
    destination = (22 - round(destination[1]), round(destination[0]))
    print(destination)
    if (not destination):
        return
    x, y, h = localisation.get_user_location()
    print("location", x, y, h)
    next_direction, destination_reached = path_planner.calculate_next_direction(
        (22 - round(y), round(x)), destination, 360 - h, 20, True, True)

    if (destination_reached):
        print("Destination Reached")
        play_ack_sequence()
        update_destination_location(None)
        return
    else:
        if (next_direction):
            print("Next Direction", next_direction)
            haptic_output.play_direction(next_direction)
        else:
            pass


@app.get("/testupdate")
def testupdate():
    destination = get_destination()
    destination = (22 - round(destination[1]), round(destination[0]))
    print(destination)
    if (not destination):
        return
    x, y, h = localisation.get_user_location()
    print("location", x, y, h)
    next_direction, destination_reached = path_planner.calculate_next_direction(
        (22 - round(y), round(x)), destination, 360 - h, 20, True, True)

    if (destination_reached):
        print("Destination Reached")
        play_ack_sequence()
        update_destination_location(None)
        add_to_user_path("-------------Destination Reached-------------------")
        return
    else:
        if (next_direction):
            print("Next Direction", next_direction)
            haptic_output.play_direction(next_direction)
            add_to_user_path(str((x, y, 360 - h + 28)))
        else:
            pass

# @app.get("/testupdate")
# def test_update():
#     start_time = time.time()
#     destination = get_destination()
#     destination = (22 - int(destination[1]*2), int(destination[0]*2))

#     if (not destination):
#         return

#     a, b, c = localisation.get_user_location()

#     start = free_points[random.randint(0, len(free_points))]
#     end = free_points[random.randint(0, len(free_points))]
#     h = random.randint(0, 360)

#     next_direction, destination_reached = path_planner.calculate_next_direction(
#         start, end, h, 0, False, False)

#     end_time = time.time()
#     elapsed_time = end_time - start_time
#     add_execution_time(elapsed_time, start, end)

#     if (destination_reached):
#         # print("Destination Reached")
#         # play_ack_sequence()
#         # update_destination_location(None)
#         return
#     else:
#         if (next_direction):
#             pass
#             # print("Next Direction", next_direction)
#             # haptic_output.play_direction(next_direction)
#         else:
#             pass
