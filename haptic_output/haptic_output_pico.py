import machine
import time
import socket
import network
import json
from machine import Pin, SoftI2C, I2C
from picozero import pico_led
from bno055 import *
from SECRETS import *

# Wi-Fi credentials
SSID = ssid
PASSWORD = password

# Base URL for HTTP requests
BASE_URL = "http://192.168.137.13:8000"

# Define the I2C bus objects
MOTOR0 = I2C(1, sda=Pin(2), scl=Pin(3))  # I2C bus 1, SDA = GPIO2, SCL = GPIO3
MOTOR1 = SoftI2C(sda=Pin(4), scl=Pin(5))  # Soft I2C, SDA = GPIO4, SCL = GPIO5
MOTOR2 = SoftI2C(sda=Pin(6), scl=Pin(7))  # Soft I2C, SDA = GPIO6, SCL = GPIO7
MOTOR3 = SoftI2C(sda=Pin(8), scl=Pin(9))  # Soft I2C, SDA = GPIO8, SCL = GPIO9
# I2C bus 0, SDA = GPIO20, SCL = GPIO21
BNO055_I2C = I2C(0, sda=Pin(20), scl=Pin(21))

MOTORS = [MOTOR0, MOTOR1, MOTOR2, MOTOR3]
SENSOR = BNO055(BNO055_I2C)

# Define the DRV2605L address
DRV_ADDR = 0x5A

# HTTP server with socket
PORT = 81
SOCK = socket.socket()

# Function to establish Wi-Fi connection


def connect():
    pico_led.off()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    wlan.connect(SSID, PASSWORD)
    attempts = 0
    while not wlan.isconnected():
        print('Waiting for connection...')
        time.sleep(1)
        attempts += 1
        if attempts > 10:
            break
    if not wlan.isconnected():
        connect()

    if wlan.isconnected():
        wlan.ifconfig(("192.168.2.122", "255.255.255.0",
                      "192.168.2.1", "8.8.8.8"))
        print(wlan.config('channel'))
        print(wlan.config('essid'))
        print(wlan.config('txpower'))
        print(wlan.ifconfig())
        pico_led.on()

# Write a value to a register on the DRV2605L


def write_register(motor, register, value):
    motor.writeto(DRV_ADDR, bytes([register, value]))


def format_sequence_int(sequence):
    string_sequence = sequence.split(",")
    int_sequence = [int(x) for x in string_sequence]
    return int_sequence

# Function to initialize motors


def initialize_motors():
    for motor in MOTORS:
        # Configure the DRV2605L
        write_register(motor, 0x01, 0x00)  # Set mode to internal trigger
        write_register(motor, 0x02, 0x00)  # Set library selection to RAM

# Function to play a motor


def play_motor(motor, effect=0x04):
    # Write the sequence to the DRV2605L
    write_register(motor, effect, 14)
    write_register(motor, 0x07, 100)

    # Play the sequence
    write_register(motor, 0x0C, 0x01)  # Set GO bit to trigger playback

# Function to play a direction


def play_direction(direction):
    if "S" in direction:
        play_motor(MOTOR0)
    if "N" in direction:
        play_motor(MOTOR1)
    if "E" in direction:
        play_motor(MOTOR2)
    if "W" in direction:
        play_motor(MOTOR3)

# Function to play all motors a certain number of times with a delay


def play_all_motors(count, delay, effect=None):
    for _ in range(count):
        for motor in MOTORS:
            if effect == None:
                play_motor(motor)
            else:
                play_motor(motor, effect)
        time.sleep(delay)


def play_sequence(sequence):
    for motor in format_sequence_int(sequence):
        play_motor(MOTORS[motor])
        time.sleep(1)

# Function to set up the socket


def setup_socket(port):
    try:
        addr = socket.getaddrinfo('0.0.0.0', 8000)[0][-1]
        SOCK.bind(addr)
        SOCK.listen(1)
        print('Listening on', addr)
    except:
        # setup_socket(port+1)
        play_all_motors(3, 0.3)

# Function to get the heading from the sensor


def get_heading():
    readings = SENSOR.euler()
    return json.dumps({"heading": readings[0]})

# Setup function to establish Wi-Fi connection, socket, and initialize motors


def setup():
    connect()
    setup_socket(PORT)
    initialize_motors()
    play_all_motors(2, 0.3, 0x07)


# Call the setup function
setup()

# Main loop
cl = None  # Initialize cl variable outside the try block
while True:
    try:
        if not cl:  # Check if cl is None
            cl, addr = SOCK.accept()
            print('Client connected from', addr)
        r = cl.recv(1024)
        r = str(r)

        url = r.split()[1]
        arguments = url.split("\\")

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')

        if r.find('/playdirection') > -1:
            print(arguments)
            direction = arguments[-1]
            play_direction(direction)
            print('Playing Direction', direction)
            pico_led.toggle()

        elif r.find('/getheading') > -1:
            data = get_heading()
            print("heading found:", data)
            cl.send(data)

        elif r.find('/playsequence') > -1:
            sequence = arguments[-1]
            play_sequence(sequence)
            print("Playing Sequence")

        elif r.find('/playacksequence') > -1:
            play_all_motors(2, 0.5)

        elif r.find('/playerror') > -1:
            play_all_motors(3, 0.3)

        else:
            pass

    except Exception as e:
        print(e)
        print(e.args)
        SOCK.close()
        print('Connection closed')
        print("Restarting")
        machine.reset()

    finally:
        if cl:
            cl.close()
            cl = None  # Reset cl variable after closing the connection
