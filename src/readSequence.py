import RPi.GPIO as GPIO
# from time import sleep
import time

GPIO.setmode(GPIO.BCM)
pin = 17

GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        state = GPIO.input(pin)
        if state:
            print("ON")
        else:
            print("OFF")
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
