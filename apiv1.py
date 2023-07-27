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

distances = {"NEAR": 1, "MIDDLE": 2, "FAR":3}

# uses board.SCL and board.SDA
i2c = board.I2C()
# Create the TCA9548A object and give it the I2C bus
i2cExpander = adafruit_tca9548a.TCA9548A(i2c)
haptic_output = HapticOutput(i2cExpander)
localisation = Localisation(i2cExpander[6])
path_planner = PathPlanner("lab")

app = FastAPI()


def add_or_update_sequence_mapping(location, sequence):
    jsonFile = open("store.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    try:
        data["mappings"].update({sequence: location})
    except:
        data["mappings"][sequence] = location

    jsonFile = open("store.json", "w")
    jsonFile.write(json.dumps(data))
    jsonFile.close()


def get_location_from_sequence(sequence):
    jsonFile = open("store.json", "r")
    data = json.load(jsonFile)
    mappings = data["mappings"]
    jsonFile.close()

    try:
        location_found = mappings[sequence]
        return location_found
    except:
        return False


def get_sequence_for_location(location):
    jsonFile = open("store.json", "r")
    data = json.load(jsonFile)
    mappings = data["mappings"]
    jsonFile.close()


    for elem in mappings:
        if mappings[elem] == location:
            return elem
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
        print("destination", destination)
        return eval(destination) if type(destination) == str else destination
    except Exception as e:
        error(e)
        return None


def find_nearest_landmark(x, y):
    # Get landmark mappings
    jsonFile = open("store.json", "r")
    mappings = json.load(jsonFile)["mappings"]
    jsonFile.close()

    try:
        # Search for nearest landmark
        shortest_distance = 200
        nearest_landmark, sequence, direction = (None, None, None)
        for seq in mappings:
            distance = math.dist((x, y), mappings[seq])
            if (distance < shortest_distance):
                nearest_landmark = mappings[seq]
                sequence = format_sequence_int(seq)
                shortest_distance = distance

        # If not found return None
        if nearest_landmark == None:
            return (nearest_landmark, sequence, direction, None)
        # Determine direction to nearest landmark
        print("Converted coords",(x,y), (round_coord(x),round_coord(y)))
        
        print("Converted landmark", (round_coord(nearest_landmark[0]),round_coord(nearest_landmark[1]) ))
        heading = path_planner.get_target_heading(
            (round_coord(x),round_coord(y)), (round_coord(nearest_landmark[0]),round_coord(nearest_landmark[1]) ))
        direction = path_planner.map_angle_to_direction(heading)

        distance = distances["NEAR"] if shortest_distance <= 2 else distances["MIDDLE"] if 5 >= shortest_distance > 2 else distances["FAR"]

        # Return data
        return (nearest_landmark, sequence, direction, distance)

    except Exception as e:
        print("Error", e)
        return (None, None, None, None)


def round_coord(x):
    nd = path_planner.node_density
    base = x / nd

    if base % nd <= 0.75 * nd:
        return int(base)
    else:
        return int(base) + 1


def error(e):
    print("Something went wrong.", e)
    t = e.__traceback__
    print(t.tb_lineno)
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
        error(e)
        return {"message": "Error Occured" + str(e)}


@app.get("/mapsequence/{sequence}")
def map_sequence(sequence):
    try:
        print("Map Sequence Request received")
        x, y = localisation.get_user_position()
        add_or_update_sequence_mapping(
            (x, y), sequence)
        return {"message": "Sequence '" + sequence + "' mapped to location: '" + str((x, y)) + "'"}
    except Exception as e:
        error(e)
        return {"message": "Error Occured" + str(e)}


@app.get("/playacksequence")
def play_ack_sequence():
    try:
        print("Play ack Request received")
        haptic_output.play_effect(acknowledgement_effect_id, 0.5, 2)
        return {"message": "playing acknowledgement sequence"}
    except Exception as e:
        error(e)
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
        error(e)
        return {"message": "Error Occured" + str(e)}


def play_location_sequence(location):
    try:
        print("PLaying location sequence")
        seqeunce = get_sequence_for_location(location)
        play_entered_sequence(seqeunce)
    except Exception as e:
        error(e)
        return {"message": "Error Occured" + str(e)}


@app.get("/playdirection/{direction}")
def play_button(direction):
    try:
        print("Playing direction", direction)
        haptic_output.play_direction(direction)
        return {"message": "playing direction: '" + direction + "'"}
    except Exception as e:
        error(e)
        return {"message": "Error Occured" + str(e)}


@app.get("/getlocation/{sequence}")
def get_location(sequence):
    try:
        location = get_location_from_sequence(sequence)
        return {"message": location}
    except Exception as e:
        error(e)
        return {"message": "Error Occured" + str(e)}


@app.get("/getnearestlandmark")
def get_nearest_landmark():
    destination = get_destination()
    try:
        # Temporarily Unset Destination to stop directions
        update_destination_location(None)
        play_ack_sequence()

        # Get user's location
        x, y = localisation.get_user_position()
        landmark, sequence, direction, distance = find_nearest_landmark(x, y)
        print(direction, distance)
        print("landmark calculations complete")

        if (landmark == None):
            # If no landmark is found inform user.
            play_ack_sequence()
            return {"message": "Nearest landmark found not found."}
        else:
            play_entered_sequence(sequence)
            delay = 0.2 + (0.4 * (distance - 1))
            print("delay", delay ,distance)
            haptic_output.play_direction(
                direction, 2, delay, 5)
        
        play_ack_sequence()
        print("Landmark", landmark)
        return {"message": "Nearest landmark found: '" + str(landmark) + "' with sequence: '" + str(sequence) + "'."}

    except Exception as e:
        error(e)
        return {"message": "Error Occured" + str(e)}
    
    finally:
        update_destination_location(destination)


@app.get("/setdestination/{sequence}")
def update_destination(sequence):
    play_ack_sequence()
    try:
        destination = get_location_from_sequence(sequence)
        if destination:
            update_destination_location(destination)
            play_entered_sequence(sequence)
            return {"message": "destination updated to: " + str(destination)}
        else:
            error("Location not found")
            return {"message": "Sequence received is not mapped to a location"}
    except Exception as e:
        error(e)
        return {"message": "Error Occured" + str(e)}


@app.get("/update")
def update():
    try:
        # Get the destination
        destination = get_destination()
        if (not destination):
            print("NO destination set")
            return {"message": "No destination set doing nothing."}
        destination = (round_coord(destination[1]), round_coord(destination[0]))

        # Get user's current location
        print("getting user location")
        x, y, h = localisation.get_user_location()
        current_location = (round_coord(y), round_coord(x))
        print("current location", current_location)

        # TODO: Figure out how offset can be made consistent
        next_direction, destination_reached = path_planner.calculate_next_direction(
            current_location, destination, 360 - h, True, True)

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
        error(e)
        return {"message": "Error Occured" + str(e)}
