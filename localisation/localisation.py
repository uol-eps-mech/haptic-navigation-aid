#!/usr/bin/env python

import adafruit_bno055
import board
import time
import serial
import os
import adafruit_tca9548a
from dwm1001_systemDefinitions import SYS_DEFS
from dwm1001_apiCommands import DWM1001_API_COMMANDS


class Localisation:
    def __init__(self, i2c):
        # Initialize the Localisation class with the provided I2C bus
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)

        # Set the permission of the serial port '/dev/ttyACM0' to allow access
        os.popen("sudo chmod 777 /dev/ttyACM0", "w")

        # Create a serial port object for communicating with the DWM1001 device
        self.serialPortDwm1001 = serial.Serial(port="/dev/ttyACM0",
                                               baudrate=115200,
                                               parity=SYS_DEFS.parity,
                                               stopbits=SYS_DEFS.stopbits,
                                               bytesize=SYS_DEFS.bytesize)

        # TODO: Fix BNO055 calibration
        # self.setup_bno055()
        # Initialize the DWM1001 API and establish a connection
        self.initializeDWM1001API()
        self.connectDWM1001()

    def get_user_heading(self):
        # Get the user's heading by reading the Euler angle from the BNO055 sensor
        for _ in range(5):
            heading = self.sensor.euler[0]  # - default_heading
        print(heading)
        return heading

    def setup_bno055(self):
        # Setup the BNO055 sensor for calibration
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
        # TODO: Check if the BNO055 sensor is calibrated. If not, keep checking.
        while not self.sensor.calibrated:
            print("Sensor not calibrated yet. Please follow the calibration process.")
            print("Current Status:", self.sensor.calibration_status)
            time.sleep(1)

        print("Calibrated!")
        print(self.get_bno055_offsets())

    def get_bno055_offsets(self):
        # TODO: Get the offsets and radius values from the BNO055 sensor
        offsets = {
            "accelerometer": self.sensor.offsets_accelerometer,
            "gyroscope": self.sensor.offsets_gyroscope,
            "magnetometer": self.sensor.offsets_magnetometer,
            "accel_radius": self.sensor.radius_accelerometer,
            "mag_radius": self.sensor.radius_magnetometer
        }
        return offsets

    def initializeDWM1001API(self):
        # Reset the DWM1001 in case a previous run didn't close properly
        self.serialPortDwm1001.write(DWM1001_API_COMMANDS.RESET)
        # Send ENTER two times in order to access the DWM1001 API
        self.serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
        time.sleep(0.5)
        self.serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
        time.sleep(0.5)
        self.serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)

    def connectDWM1001(self):
        # Close and reopen the serial port to establish a connection with the DWM1001
        self.serialPortDwm1001.close()
        time.sleep(0.2)
        self.serialPortDwm1001.open()
        time.sleep(0.5)

        # Check if the serial port is open and send the LEC command to the DWM1001
        if self.serialPortDwm1001.isOpen():
            time.sleep(0.5)
            self.serialPortDwm1001.write(DWM1001_API_COMMANDS.LEC)
            self.serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
            time.sleep(0.5)

    def reset_buffer(self):
        # Reset the input and output buffers of the serial port
        self.serialPortDwm1001.reset_input_buffer()
        self.serialPortDwm1001.reset_output_buffer()
        time.sleep(0.1)

    def get_user_position(self):
        global serialReadLine
        if self.serialPortDwm1001.isOpen():
            self.reset_buffer()
            self.serialPortDwm1001.write(DWM1001_API_COMMANDS.APG)
            location_data = []
            while len(location_data) < 1 or location_data[0] != 'POS':
                # Read data from the serial port until a valid location data is received
                serialReadLine = self.serialPortDwm1001.read_until()
                # print(serialReadLine)
                location_data = str(serialReadLine, 'utf-8').split(',')
            x_pos = float(location_data[3])
            y_pos = float(location_data[4])
            coordinates = [x_pos, y_pos]
            return coordinates
        else:
            print("Can't open port: " + str(self.serialPortDwm1001.name))
            return False

    def get_user_location(self):
        # Get the user's position and heading and return them as a tuple (x, y, heading)
        user_position = self.get_user_position()
        heading = self.get_user_heading()
        if user_position:
            return (user_position[0], user_position[1], heading)
        return False


def test():
    # Test function to get user location using the Localisation class
    localisation = Localisation(board.I2C())
    while True:
        location = localisation.get_user_location()
        print(location)


def test_dwm():
    # Test function to get user position using the Localisation class with TCA9548A multiplexer
    i2c = board.I2C()
    i2cExpander = adafruit_tca9548a.TCA9548A(i2c)
    localisation = Localisation(i2cExpander[6])
    while True:
        location = localisation.get_user_position()
        print(location)
        time.sleep(4)

# test_dwm()
