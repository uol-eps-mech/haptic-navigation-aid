import serial
from dwm1001_apiCommands import DWM1001_API_COMMANDS
import time
import subprocess
import requests
import json


class Localisation:
    def __init__(self):
        print("Reading COM Ports")
        s = subprocess.getstatusoutput(f'python -m serial.tools.list_ports')
        print(s[1])

        self.com_port = input("Please enter the COM port to use for DWM1001: ")

        # Replace with the name of your serial port
        self.serial_port = 'COM' + str(self.com_port)
        # Set the baud rate to match the configuration of the DWM1001 listener
        self.baud_rate = 115200
        self.serialPortDwm1001 = serial.Serial(
            self.serial_port, self.baud_rate)

        self.url = "http://192.168.2.122:8000/getheading"

        self.initializeDWM1001API()
        self.connectDWM1001()

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
        if (self.serialPortDwm1001.isOpen()):
            time.sleep(0.5)
            self.serialPortDwm1001.write(DWM1001_API_COMMANDS.LEC)
            self.serialPortDwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
            time.sleep(0.5)

    def reset_buffer(self):
        self.serialPortDwm1001.reset_input_buffer()
        self.serialPortDwm1001.reset_output_buffer()
        time.sleep(0.1)

    def get_user_heading(self):
        for _ in range(2):
            response = requests.get(self.url)
        print(response.content)
        heading = json.loads(response.content.decode())["heading"]

        return heading

    def get_user_position(self):
        global serialReadLine
        if (self.serialPortDwm1001.isOpen()):
            self.reset_buffer()
            location_data = []
            while len(location_data) < 1 or location_data[0] != 'POS':
                serialReadLine = self.serialPortDwm1001.read_until()
                location_data = str(serialReadLine, 'utf-8').split(',')
                # print(location_data, location_data[0] != 'POS')
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
            return (user_position[0], user_position[1], heading)  # x, y, h
        return False
