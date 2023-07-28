import serial
from dwm1001_apiCommands import DWM1001_API_COMMANDS
import time
import subprocess
import requests
import json


class Localisation:
    def __init__(self):
        print("Reading COM Ports:")
        
        # Use subprocess to list available COM ports
        s = subprocess.getstatusoutput(f'python -m serial.tools.list_ports')
        print(s[1])

        # Prompt the user to input the COM port for the DWM1001 device
        self.com_port = input("Please enter the COM port to use for DWM1001: ")

        # Define the serial port using the provided COM port number
        self.serial_port = 'COM' + str(self.com_port)
        
        # Set the baud rate to match the configuration of the DWM1001 listener
        self.baud_rate = 115200

        # Create a serial port object for communicating with the DWM1001 device
        self.serialPortDwm1001 = serial.Serial(
            self.serial_port, self.baud_rate)

        # Set the URL for the server to get the user's heading
        self.url = "http://192.168.2.122:8000/getheading"

        # Initialize the DWM1001 API commands and connect to the device
        self.initializeDWM1001API()
        self.connectDWM1001()

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

    def get_user_heading(self):
        # Send a request to the server to get the user's heading and parse the response
        for _ in range(2):
            response = requests.get(self.url)
        print(response.content)
        heading = json.loads(response.content.decode())["heading"]

        return heading

    def get_user_position(self):
        global serialReadLine
        if self.serialPortDwm1001.isOpen():
            self.reset_buffer()
            location_data = []
            while len(location_data) < 1 or location_data[0] != 'POS':
                # Read data from the serial port until a valid location data is received
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
        # Get the user's position and heading and return them as a tuple (x, y, h)
        user_position = self.get_user_position()
        heading = self.get_user_heading()
        if user_position:
            return (user_position[0], user_position[1], heading)
        return False
