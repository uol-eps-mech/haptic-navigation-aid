from fastapi import FastAPI
from hapticOutput import play_direction, play_effect, play_sequence

acknowledgement_effect_id = 27

app = FastAPI()


@app.get("/")
async def root():
    print("Hello World")
    return {"message": "Hello World"}

@app.get("/mapsequence/{sequence}")
def map_sequence(sequence):
    play_direction("N")
    print("Mapping Sequence:", sequence)
    return {"sequence": sequence}

@app.get("/playacksequence")
def play_ack_sequence():
    play_effect(acknowledgement_effect_id, 0.2, 2)
    return {"message": "buzzing motors"}

@app.get("/playsequence/{sequence}")
def play_sequence_1(sequence):
    play_sequence(sequence.split(","))
    return {"message": "playing sequence: " + sequence}

