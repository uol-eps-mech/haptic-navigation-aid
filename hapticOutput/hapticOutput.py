import board, time
import adafruit_tca9548a
import adafruit_drv2605

i2c = board.I2C()  # uses board.SCL and board.SDA
time.sleep(1)

# Create the TCA9548A object and give it the I2C bus
i2cExpander = adafruit_tca9548a.TCA9548A(i2c)

# Create 4 DRV2605 objects and give them each an SDA+SCL on the i2cExpander
north = adafruit_drv2605.DRV2605(i2cExpander[0])
south = adafruit_drv2605.DRV2605(i2cExpander[1])
east = adafruit_drv2605.DRV2605(i2cExpander[2])
west = adafruit_drv2605.DRV2605(i2cExpander[3])

def clear_sequences():
    south.sequence = []
    north.sequence = []
    east.sequence = []
    west.sequence = []

def play_direction(cardinal_direction, intensity=2, delay=0, count=1):
    # Clear sequence on all motors
    clear_sequences()

    # Set effect id based on intensity level 3 = highest 1 = lowest
    effectid = 47 if intensity == 3 else 49 if intensity == 2 else 51
    
    # Add effectid to sequence for motor if it is in cardinal direction
    if "S" in cardinal_direction:
        south.sequence[0] = adafruit_drv2605.Effect(effectid)

    if "N" in cardinal_direction:
        north.sequence[0] = adafruit_drv2605.Effect(effectid)

    if "E" in cardinal_direction:
        east.sequence[0] = adafruit_drv2605.Effect(effectid)
    
    if "W" in cardinal_direction:
        west.sequence[0] = adafruit_drv2605.Effect(effectid)
    
    # Play sequence on motors for 'count' no. of times
    for i in range(count):
        south.play()
        north.play()
        east.play()
        west.play()
        time.sleep(delay) # sleep for 'delay' no. of seconds
    