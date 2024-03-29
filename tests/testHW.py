from Naked.toolshed.shell import execute_js, muterun_js
import RPi.GPIO as GPIO
# from time import sleep
import time
import sys
from datetime import datetime




def testReadSequencer():
    GPIO.setmode(GPIO.BCM)
    pin = 17

    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(pin,
                          GPIO.BOTH,
                          callback=detectCallback,
                          bouncetime=500)
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()

def testWriteSequencer():
    GPIO.setmode(GPIO.BCM)
    pin = 27

    GPIO.setup(pin, GPIO.OUT)
    try:
        while True:
            time.sleep(5)
            print("write ON")
            GPIO.output(pin, 1)
            time.sleep(5)
            print("write OFF")
            GPIO.output(pin, 0)
    except KeyboardInterrupt:
        GPIO.cleanup()

def detectCallback(pin):
    state = GPIO.input(pin)
    if not state:
        print("OFF at {0}".format(datetime.now()))
    else:
        print("ON at {0}".format(datetime.now()))

def runJsScript():
    """
    JS script takes string arguments
    """

    print("The arguments are: " , str(sys.argv))

    response = execute_js("src/scene.js", "1")

    if response:
        print("got it")

    # if response.exitcode == 0:
    #     print(response.stdout)
    # else:
    #     sys.stderr.write(response.stderr)

if __name__ == "__main__":
    # run()
    testReadSequencer()
    # testWriteSequencer()
