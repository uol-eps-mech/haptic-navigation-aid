import board, time
import adafruit_tca9548a
import adafruit_drv2605
import sys

i2c = board.I2C()  # uses board.SCL and board.SDA
time.sleep(1)

# Create the TCA9548A object and give it the I2C bus
i2cExpander = adafruit_tca9548a.TCA9548A(i2c)

# Create DRV2605 object and give it an SDA+SCL on the i2cExpander
drv = adafruit_drv2605.DRV2605(i2cExpander[int(sys.argv[1])])

while True:
    drv.sequence[0] = adafruit_drv2605.Effect(51)
    drv.play()
    time.sleep(2)
