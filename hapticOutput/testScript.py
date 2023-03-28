from hapticOutput import play_direction
import keyboard
from time import sleep

high_intensity_effect_id = 17
low_intensity_effect_id = 20
effectsl=[low_intensity_effect_id, 19, high_intensity_effect_id]

while True:
    try:
        if keyboard.is_pressed('q'):
            play_direction("N", 3, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('w'):
            play_direction("S", 3, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('e'):
            play_direction("E", 3, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('r'):
            play_direction("W", 3, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('t'):
            play_direction("NE", 3, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('y'):
            play_direction("SE", 3, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('u'):
            play_direction("NW", 3, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('i'):
            play_direction("SW", 3, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('a'):
            play_direction("N", 1, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('s'):
            play_direction("S", 1, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('d'):
            play_direction("E", 1, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('f'):
            play_direction("W", 1, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('g'):
            play_direction("NE", 1, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('h'):
            play_direction("SE", 1, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('j'):
            play_direction("NW", 1, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('k'):
            play_direction("SW", 1, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('1'):
            break
        
    except:
        continue