import time
import RPi.GPIO as GPIO

ledPins = [14,15, 18]

GPIO.setmode(GPIO.BCM)

def setup():    
    GPIO.setup(switchPin, GPIO.IN)
    GPIO.setup(buttonPins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(ledPins, GPIO.OUT)


setup()
pwm1 = GPIO.PWM(ledPins[0], 100)
pwm2 = GPIO.PWM(ledPins[1], 100)
pwm3 = GPIO.PWM(ledPins[2], 100)

pwm1.start(0)
pwm2.start(0)
pwm3.start(0)

dc = 0
while True:

    for dc in range(0, 101, 5):
        pwm1.ChangeDutyCycle(dc)
        time.sleep(1)
    
    pwm1.ChangeDutyCycle(0)

    for dc in range(0, 101, 5):
        pwm2.ChangeDutyCycle(dc)
        time.sleep(1)
    
    pwm2.ChangeDutyCycle(0)

    for dc in range(0, 101, 5):
        pwm3.ChangeDutyCycle(dc)
        time.sleep(1)

    pwm3.ChangeDutyCycle(0)
    
    time.sleep(2)
    