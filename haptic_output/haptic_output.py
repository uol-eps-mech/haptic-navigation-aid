import adafruit_drv2605
from time import sleep


class HapticOutput:
    # Map Buttons to Effects
    button_to_effect_map = {
        0: 1,  # strong click
        1: 10,  # double click
        2: 75,  # ramp down
        3: 51,  # soft buzz
        4: 87,  # long ramp up
        5: 12,  # triple click
    }

    def __init__(self, i2cBus):
        # Create 4 DRV2605 objects and give them each an SDA+SCL on the i2cBus
        self.north = adafruit_drv2605.DRV2605(i2cBus[1])
        self.south = adafruit_drv2605.DRV2605(i2cBus[0])
        self.east = adafruit_drv2605.DRV2605(i2cBus[2])
        self.west = adafruit_drv2605.DRV2605(i2cBus[3])
        self.motors = [self.north, self.south, self.east, self.west]

    def clear_sequences(self):
        # Set sequence on motor to empty list
        self.south.sequence[0] = adafruit_drv2605.Pause(0)
        self.north.sequence[0] = adafruit_drv2605.Pause(0)
        self.east.sequence[0] = adafruit_drv2605.Pause(0)
        self.west.sequence[0] = adafruit_drv2605.Pause(0)

    def play_direction(self, cardinal_direction, intensity=2, delay=0, count=1, effects=None):
        # Clear sequence on all motors
        self.clear_sequences()

        # Set effect id based on intensity level 3 = highest 1 = lowest
        if effects:
            effectid = effects[2] if intensity == 3 else effects[1] if intensity == 2 else effects[0]
        else:
            effectid = 47 if intensity == 3 else 49 if intensity == 2 else 51

        # Add effectid to sequence for motor if it is in cardinal direction
        if "S" in cardinal_direction:
            self.south.sequence[0] = adafruit_drv2605.Effect(effectid)

        if "N" in cardinal_direction:
            self.north.sequence[0] = adafruit_drv2605.Effect(effectid)

        if "E" in cardinal_direction:
            self.east.sequence[0] = adafruit_drv2605.Effect(effectid)

        if "W" in cardinal_direction:
            self.west.sequence[0] = adafruit_drv2605.Effect(effectid)

        # Play sequence on motors for 'count' no. of times
        for i in range(count):
            self.south.play()
            self.north.play()
            self.east.play()
            self.west.play()
            sleep(delay)  # sleep for 'delay' no. of seconds

    def play_effect(self, effect_id, delay=0, count=1):
        # Clear sequence on all motors
        self.clear_sequences()

        self.south.sequence[0] = self.north.sequence[0] = self.west.sequence[0] = self.east.sequence[0] = adafruit_drv2605.Effect(
            effect_id)

        # Play sequence on motors for 'count' no. of times
        for i in range(count):
            self.south.play()
            self.north.play()
            self.east.play()
            self.west.play()
            sleep(delay)  # sleep for 'delay' no. of seconds

    def play_motor(self, motor_id):
        self.motors[motor_id].sequence[0] = 1
        self.motors[motor_id].play()

    def play_sequence(self, sequence):
        # Clear sequence on all motors
        self.clear_sequences()

        for button in sequence:
            self.south.sequence[0] = self.north.sequence[0] = self.west.sequence[0] = self.east.sequence[0] = adafruit_drv2605.Effect(
                self.map_button_to_effect(button))
            self.south.play()
            self.north.play()
            self.east.play()
            self.west.play()
            sleep(1)

    def map_button_to_effect(self, button):
        return self.button_to_effect_map[button]

# Usage
# i2c = board.I2C()  # uses board.SCL and board.SDA
# # Create the TCA9548A object and give it the I2C bus
# i2cExpander = adafruit_tca9548a.TCA9548A(i2c)
# haptic_output = HapticOutput(i2cExpander)
