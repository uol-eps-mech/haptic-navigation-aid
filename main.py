from fastapi import FastAPI
from haptic_output.haptic_output import HapticOutput
from localisation.localisation import Localisation
from path_planning.path_planning import PathPlanner, Node
import json
import board
import adafruit_tca9548a
import math

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
    # Get landmark mappings
    jsonFile = open("store.json", "r")
    mappings = json.load(jsonFile)["mappings"]
    jsonFile.close()

    try:
        # Search for nearest landmark
        shortest_distance = 200
        nearest_landmark, sequence, direction = None
        for location in mappings:
            distance = math.dist((x, y), eval(location))
            if (distance < shortest_distance):
                nearest_landmark = eval(location)
                sequence = mappings[location]
                shortest_distance = distance

        # If not found return None
        if nearest_landmark == None:
            return (nearest_landmark, sequence, direction, None)

        # Determine direction to nearest landmark
        heading = path_planner.__get_target_heading(
            Node(None, (x, y)), Node(None, nearest_landmark))
        direction = path_planner.__map_angle_to_direction(heading)

        # Return data
        return (nearest_landmark, sequence, direction, shortest_distance)

    except:
        return (None, None, None, None)


def round(x):
    base = int(x)
    if x - base >= 0.75:
        return base + 1
    else:
        return base


def error():
    haptic_output.play_effect(error_effect_id, 0.5, 4)


@app.get("/")
async def root():
    print("Hello World")
    return {"message": "Hello World"}


@app.get("/playobstacle/{direction}")
def play_obstacle(direction):
    try:
        print("Play Obstacle Request Received")
        haptic_output.inidicate_obstacle(format_sequence_bool(direction))
        return {"message": "Played direction: " + str(direction)}
    except Exception as e:
        error()
        return {"message": "Error Occured" + str(e)}


@app.get("/mapsequence/{sequence}")
def map_sequence(sequence):
    try:
        print("Map Sequence Request received")
        x, y = localisation.get_user_position()
        add_or_update_sequence_mapping(
            str((x, y)), format_sequence_int(sequence))
        return {"message": "Sequence '" + sequence + "' mapped to location: '" + str((x, y)) + "'"}
    except Exception as e:
        error()
        return {"message": "Error Occured" + str(e)}


@app.get("/playacksequence")
def play_ack_sequence():
    try:
        print("Play ack Request received")
        haptic_output.play_effect(acknowledgement_effect_id, 0.5, 2)
        return {"message": "playing acknowledgement sequence"}
    except Exception as e:
        error()
        return {"message": "Error Occured" + str(e)}


@app.get("/playsequence/{sequence}")
def play_entered_sequence(sequence):
    try:
        print("Play sequence request received")
        if isinstance(sequence, str) or isinstance(sequence[0], str):
            sequence = format_sequence_int(sequence)

        print("Playing sequence", sequence)
        haptic_output.play_sequence(sequence)
        return {"message": "Playing sequence: " + str(sequence)}

    except Exception as e:
        error()
        return {"message": "Error Occured" + str(e)}


def play_location_sequence(location):
    try:
        print("PLaying location sequence")
        seqeunce = get_sequence_for_location(location)
        play_entered_sequence(seqeunce)
    except Exception as e:
        error()
        return {"message": "Error Occured" + str(e)}


@app.get("/playmotor/{motor}")
def play_button(motor):
    try:
        print("Playing motor", motor)
        haptic_output.play_motor(int(motor))
        return {"message": "playing motor: '" + motor + "'"}
    except Exception as e:
        error()
        return {"message": "Error Occured" + str(e)}


@app.get("/getlocation/{sequence}")
def get_location(sequence):
    try:
        location = get_location_from_sequence(format_sequence_int(sequence))
        return {"message": location}
    except Exception as e:
        error()
        return {"message": "Error Occured" + str(e)}


@app.get("/getnearestlandmark")
def get_nearest_landmark():
    try:
        # Temporarily Unset Destination to stop directions
        # TODO: maybe use an internal flag?
        destination = get_destination()
        update_destination_location(None)

        # Get user's location
        x, y = localisation.get_user_position()
        landmark, sequence, direction, distance = find_nearest_landmark(x, y)

        if (landmark == None):
            # If no landmark is found inform user.
            play_ack_sequence()
            return {"message": "Nearest landmark found not found."}
        else:
            play_entered_sequence(sequence)
            haptic_output.play_direction(
                direction, 2, 0.1 * round(distance, -1), 5)

        print("Landmark", landmark)
        update_destination_location(destination)
        return {"message": "Nearest landmark found: '" + str(landmark) + "' with sequence: '" + str(sequence) + "'."}

    except Exception as e:
        error()
        return {"message": "Error Occured" + str(e)}


@app.get("/setdestination/{sequence}")
def update_destination(sequence):
    try:
        destination = get_location_from_sequence(format_sequence_int(sequence))
        if destination:
            update_destination_location(destination)
            return {"message": "destination updated to: " + str(destination)}
        else:
            error()
            return {"message": "Sequence received is not mapped to a location"}
    except Exception as e:
        error()
        return {"message": "Error Occured" + str(e)}


@app.get("/update")
def update():
    try:
        # Get the destination
        destination = get_destination()
        # TODO: Modify this to get dimensions from map (maybe store map dimensions as a property)
        destination = (22 - round(destination[1]), round(destination[0]))
        if (not destination):
            return {"message": "No destination set doing nothing."}

        x, y, h = localisation.get_user_location()

        # TODO: Modify this to get dimensions from map (maybe store map dimensions as a property)
        # TODO: Figure out how offset can be made consistent
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
                return {"message": "No Next Direction found."}

    except Exception as e:
        error()
        return {"message": "Error Occured" + str(e)}
