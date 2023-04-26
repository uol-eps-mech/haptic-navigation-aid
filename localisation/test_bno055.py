#!/usr/bin/env python

import adafruit_bno055
import board
import time
import board
import adafruit_tca9548a


class Localisation:
    def __init__(self, i2c):
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)

        self.setup_bno055()

    def get_user_heading(self):
        heading = self.sensor.euler[0]  # - default_heading
        print(heading)
        return heading

    def setup_bno055(self):
        self.sensor.mode = adafruit_bno055.CONFIG_MODE
        time.sleep(0.2)
        self.sensor.offsets_accelerometer = (-29, 21, -28)
        self.sensor.offsets_gyroscope = (0, -1, 2)
        self.sensor.offsets_magnetometer = (624, -82, 151)
        self.sensor.radius_accelerometer = 1000
        self.sensor.radius_magnetometer = 632
        self.sensor.mode = adafruit_bno055.NDOF_MODE
        time.sleep(0.2)

    def check_bno055_calibrated(self):
        # Check if the sensor is calibrated. If not, keep checking.
        while not self.sensor.calibrated:
            print("Sensor not calibrated yet. Please follow the calibration process.")
            print("Current Status:", self.sensor.calibration_status)
            time.sleep(1)

        print("Calibrated!")
        print(self.get_bno055_offsets())

    def get_bno055_offsets(self):
        offsets = {
            "accelerometer": self.sensor.offsets_accelerometer,
            "gyroscope": self.sensor.offsets_gyroscope,
            "magnetometer": self.sensor.offsets_magnetometer,
            "accel_radius": self.sensor.radius_accelerometer,
            "mag_radius": self.sensor.radius_magnetometer
        }
        return offsets


def test_bno055():
    i2c = board.I2C()
    # i2cExpander = adafruit_tca9548a.TCA9548A(i2c)
    # localisation = Localisation(i2cExpander[6])
    localisation = Localisation(i2c)

    while True:
        heading = localisation.get_user_heading()
        print(heading)


test_bno055()
