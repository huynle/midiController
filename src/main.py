from collections import OrderedDict

from display import Display

import Adafruit_SSD1306

from time import sleep
import RPi.GPIO as GPIO
from ky040 import ky040
from controller import Controller

version = "0.0.1"

current_count = 1
# Set up scenes here
scenesArray = ["Ca Doan 1",
               "Speaker",
               "Retreat",
               "Ca Doan 2"]

# Setting Up
clockpin = 5
datapin = 6
switchpin = 13
buttonpin = 26  # pIN nUMBER FOR ROTARY SWITCH BUTTON

# get an instance of our hardware
ky040 = KY040.start(clockPin, dataPin, switchPin)
display = Display(padding=0, totalLines=4)

# some temporary setting up
lastScene = 1

# give controller access to the instances
controller = Controller()
controller.setDisplay(display)
controller.setRotaryEncoder(ky040)
controller.importScenes(scenesArray)


# set up the supporting events
controller.setGPIOEvents(buttonpin, controller.IO_OFF,
    (controller._eventEcho, "Power Up Sequence")
    (controller._eventExecuteJs, "src/scene.js", lastScene),
)

controller.setGPIOEvents(buttonpin, controller.IO_ON,
    (controller._eventEcho, "Power Down Sequence")
    (controller._eventExecuteJs, "src/scene.js",),
)

controller.setRotaryEvents(controller._eventSetSceneDisplay,
                           # (controller._eventExecuteJs, "src/test.js"),
                           )

# event for rotary button to be pressed more than
controller.setRotaryButtonPressedEvents(
    controller._eventDisplayCountUp, # Voltage goes to zero (FALLING)
)

# time to release: actions
controller.setTimedRotaryButtonReleasedEvents({
    1: [(controller._eventEcho, "TESTING 1 sec")],
    3: [(controller._eventExecuteJs, "src/test.js"),],
    10: [(controller._eventEcho, "TESTING 10 sec")],
})

controller.initialize()
controller.runForever()

