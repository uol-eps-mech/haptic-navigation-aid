import haptic_output
import keyboard
from time import sleep
import adafruit_tca9548a
import board

high_intensity_effect_id = 17
low_intensity_effect_id = 20
effectsl=[low_intensity_effect_id, 19, high_intensity_effect_id]

# uses board.SCL and board.SDA
i2c = board.I2C()  
# Create the TCA9548A object and give it the I2C bus
i2cExpander = adafruit_tca9548a.TCA9548A(i2c)
haptic_output = haptic_output.HapticOutput(i2cExpander)
direction = ""

while True:
    try:
        if keyboard.is_pressed('q'):
            haptic_output.play_direction("N", intensity=3, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('w'):
            haptic_output.play_direction("NE", intensity=3, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('e'):
            haptic_output.play_direction("E", intensity=3, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('r'):
            haptic_output.play_direction("SE", intensity=3, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('t'):
            haptic_output.play_direction("S", intensity=3, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('y'):
            haptic_output.play_direction("SW", intensity=3, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('u'):
            haptic_output.play_direction("W", intensity=3, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('i'):
            haptic_output.play_direction("NW", intensity=3, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('a'):
            haptic_output.play_direction("N", intensity=1, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('s'):
            haptic_output.play_direction("NE", intensity=1, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('d'):
            haptic_output.play_direction("E", intensity=1, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('f'):
            haptic_output.play_direction("SE", intensity=1, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('g'):
            haptic_output.play_direction("S", intensity=1, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('h'):
            haptic_output.play_direction("SW", intensity=1, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('j'):
            haptic_output.play_direction("W", intensity=1, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('k'):
            haptic_output.play_direction("NW", intensity=1, count=3, delay=0.5, effects=effectsl)
            sleep(0.5)
        if keyboard.is_pressed('1'):
            break
        
    except:
        continue