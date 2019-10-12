from collections import OrderedDict

from Naked.toolshed.shell import execute_js, muterun_js
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
# Putting the scenes in an orderred dictionary
# scenes = OrderedDict(scenesArray)

display = Display(padding=0, totalLines=4)

controller = Controller()
controller.setDisplay(display)
controller.setRotaryEncoder(ky040)
controller.importScenes(scenesArray)

controller.setRotaryEvents(controller._eventSetSceneDisplay,
                           # (controller._eventExecuteJs, "src/test.js"),
                           )

# event for rotary button to be pressed more than
# {state: action(s)}
controller.setRotaryButtonPressedEvents(
    controller._eventDisplayCountUp, # Voltage goes to zero (FALLING)
)

# time to release: actions
controller.setRotaryButtonReleasedEvents({
    1: [(controller._eventEcho, "TESTING 1 sec")],
    3: [(controller._eventExecuteJs, "src/test.js"),],
    10: [(controller._eventEcho, "TESTING 10 sec")],
})

controller.initialize()
controller.runForever()

