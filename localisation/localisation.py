#!/usr/bin/env python

import adafruit_bno055
import board
import time
import time, serial, os
from dwm1001_systemDefinitions import SYS_DEFS
from dwm1001_apiCommands  import DWM1001_API_COMMANDS

i2c = board.I2C()
sensor = adafruit_bno055.BNO055_I2C(i2c)
os.popen("sudo chmod 777 /dev/ttyACM0","w")

serialPortDwm1001 = serial.Serial(port = "/dev/ttyACM0", 
    baudrate = 115200,
    parity=SYS_DEFS.parity,
    stopbits=SYS_DEFS.stopbits,
    bytesize=SYS_DEFS.bytesize)

def get_user_heading():
    heading = sensor.euler[0] #- default_heading
    print(heading)
    return heading

def setup_bno055():
    sensor.mode = adafruit_bno055.CONFIG_MODE
    time.sleep(0.2)
    sensor.offsets_accelerometer = (-29, 21, -28)
    sensor.offsets_gyroscope  = (0, -1, 2)
    sensor.offsets_magnetometer = (624, -82, 151)
    sensor.radius_accelerometer = 1000
    sensor.radius_magnetometer = 632
    sensor.mode = adafruit_bno055.NDOF_MODE
    time.sleep(0.2)
    
def check_bno055_calibrated():
    # Check if the sensor is calibrated. If not, calibrate it.
    while not sensor.calibrated:
        print("Sensor not calibrated yet. Please follow the calibration process.")
        cal = sensor.calibration_status
        print(cal)
        time.sleep(1)

    print("Calibrated!")
    print(sensor.offsets_accelerometer)
    print(sensor.offsets_gyroscope)
    print(sensor.offsets_magnetometer)
    print(sensor.radius_accelerometer)
    print(sensor.radius_magnetometer)

def initializeDWM1001API():
    # reset incase previuos run didn't close properly
    serialPortDwm1001.write(DWM1001_API_COMMANDS.RESET)
    # send ENTER two times in order to access api
    serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
    time.sleep(0.5)
    serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
    time.sleep(0.5)
    serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)

def connectDWM1001():
    serialPortDwm1001.close()
    time.sleep(0.2)
    serialPortDwm1001.open()
    time.sleep(0.5)
    if(serialPortDwm1001.isOpen()):
        time.sleep(0.5)       
        serialPortDwm1001.write(DWM1001_API_COMMANDS.LEC)
        serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
        time.sleep(0.5)       

def get_user_position():
    global serialReadLine
    if(serialPortDwm1001.isOpen()):
        location_data = []
        while len(location_data) < 1 or location_data[0] != 'POS':
            serialReadLine=serialPortDwm1001.read_until()
            location_data = str(serialReadLine, 'utf-8').split(',')
        x_pos = float(location_data[3])
        y_pos = float(location_data[4])
        coordinates = [x_pos, y_pos]
        return coordinates
                          
    else:
        print("Can't open port: " + str(serialPortDwm1001.name))
        return False

def get_user_location():
    user_position = get_user_position()
    heading = get_user_heading()
    if user_position:
        return (user_position[0], user_position[1], heading) #x, y, h
    return False


def test():
    setup_bno055()
    initializeDWM1001API()
    connectDWM1001()

    while True:
        location = get_user_location()
        print(location)
    
test()