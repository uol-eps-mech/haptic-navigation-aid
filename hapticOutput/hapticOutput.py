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

    
    
    
    
    