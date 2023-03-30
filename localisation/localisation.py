#!/usr/bin/env python

import adafruit_bno055
import board
import time
import time, serial, os
from dwm1001_systemDefinitions import SYS_DEFS
from dwm1001_apiCommands  import DWM1001_API_COMMANDS

class Localisation:
    def __init__(self, i2c):
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)
        os.popen("sudo chmod 777 /dev/ttyACM0","w")

        self.serialPortDwm1001 = serial.Serial(port = "/dev/ttyACM0", 
            baudrate = 115200,
            parity=SYS_DEFS.parity,
            stopbits=SYS_DEFS.stopbits,
            bytesize=SYS_DEFS.bytesize)
        
        self.setup_bno055()
        self.initializeDWM1001API()
        self.connectDWM1001()
        
    def get_user_heading(self):
        heading = self.sensor.euler[0] #- default_heading
        print(heading)
        return heading

    def setup_bno055(self):
        self.sensor.mode = adafruit_bno055.CONFIG_MODE
        time.sleep(0.2)
        self.sensor.offsets_accelerometer = (-29, 21, -28)
        self.sensor.offsets_gyroscope  = (0, -1, 2)
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
            "accelerometer":self.sensor.offsets_accelerometer,
            "gyroscope":self.sensor.offsets_gyroscope,
            "magnetometer":self.sensor.offsets_magnetometer,
            "accel_radius": self.sensor.radius_accelerometer,
            "mag_radius":self.sensor.radius_magnetometer
        }
        return offsets

    def initializeDWM1001API(self):
        # reset incase previuos run didn't close properly
        self.serialPortDwm1001.write(DWM1001_API_COMMANDS.RESET)
        # send ENTER two times in order to access api
        self.serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
        time.sleep(0.5)
        self.serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
        time.sleep(0.5)
        self.serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)

    def connectDWM1001(self):
        self.serialPortDwm1001.close()
        time.sleep(0.2)
        self.serialPortDwm1001.open()
        time.sleep(0.5)
        if(self.serialPortDwm1001.isOpen()):
            time.sleep(0.5)       
            self.serialPortDwm1001.write(DWM1001_API_COMMANDS.LEC)
            self.serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
            time.sleep(0.5)       

    def get_user_position(self):
        global serialReadLine
        if(self.serialPortDwm1001.isOpen()):
            location_data = []
            while len(location_data) < 1 or location_data[0] != 'POS':
                serialReadLine=self.serialPortDwm1001.read_until()
                location_data = str(serialReadLine, 'utf-8').split(',')
            x_pos = float(location_data[3])
            y_pos = float(location_data[4])
            coordinates = [x_pos, y_pos]
            return coordinates
                            
        else:
            print("Can't open port: " + str(self.serialPortDwm1001.name))
            return False

    def get_user_location(self):
        user_position = self.get_user_position()
        heading = self.get_user_heading()
        if user_position:
            return (user_position[0], user_position[1], heading) #x, y, h
        return False


def test():
    localisation = Localisation(board.I2C())
    while True:
        location = localisation.get_user_location()
        print(location)