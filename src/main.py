from collections import OrderedDict

from display import Display

import Adafruit_SSD1306

from time import sleep
# from ky040 import KY0404
import ky040 as rot
from controller import Controller

version = "0.0.1"


# Set up scenes here
scenesArray = [
    "Scene 1",
    "Scene 2",
    "Scene 3",
    "Scene 4"
]

# Setting Up
clockpin = 5
datapin = 6
switchpin = 13
buttonpin = 26  # pIN nUMBER FOR ROTARY SWITCH BUTTON
sequencerLedPin = 17
sequencerCtrlPin = 27

# get an instance of our hardware
ky040 = rot.KY040.start(clockpin, datapin, switchpin)
display = Display(padding=-2, totalLines=4)

# some temporary setting up
lastScene = 1

# give controller access to the instances
controller = Controller()
controller.setSecondsToIdle(5)
controller.setDisplay(display)
controller.setRotaryEncoder(ky040)
controller.importScenes(scenesArray)

# controller.setSequencerPins(sequencerLedPin, sequencerCtrlPin)
controller.setInputPins(sequencerLedPin)
controller.setOutputPins(sequencerCtrlPin)

# for AFTER all the initialization
controller.setInitializedEvents()

# For when the pi is idle
controller.setIdleEvents(
    (controller._eventEcho, "peace out.."),
    (controller._eventSecondsToWait, 4),
    (controller._eventClearDisplay)
)

# For when the pi is idle
controller.setOutOfIdleEvents()

### Setting all the rotary events
controller.setRotaryEvents(
    (controller._eventSetSceneDisplay,),
    # (controller._eventSetIdle)
)

# event for rotary button to be pressed more than
controller.setRotaryButtonPressedEvents(
    controller._eventDisplayCountUp, # Voltage goes to zero (FALLING)
)

# time to release: actions for buttonpin
controller.setTimedRotaryButtonReleasedEvents({
    1: [
        (controller._eventEcho, "Hold until\n----------5----------\nto prevent accidental\npresses"),
    ],

    5: [
        (controller._eventExecuteJs, "./scene.js", controller.currentSceneId),
    ],

    ## for turning ON
    6: [
        (controller._eventEcho, "TESTING 3 sec\nECHO!"),
        (controller._eventSequencerPower, sequencerCtrlPin, controller.SEQ_ON),
    ],

    # for turnning off
    10: [
        (controller._eventEcho, "TESTING 5 sec\nECHO!"),
        (controller._eventExecuteJs, "./off.js"),
        (controller._eventSequencerPower, sequencerCtrlPin, controller.SEQ_OFF)
    ],
})


# # set up the supporting events
# controller.setGPIOEvents(buttonpin, controller.IO_OFF,
#     (controller._eventEcho, "Power Up Sequence"),
#     (controller._eventExecuteJs, "src/scene.js", lastScene),
# )

# controller.setGPIOEvents(buttonpin, controller.IO_ON,
#     (controller._eventEcho, "Power Down Sequence"),
#     (controller._eventExecuteJs, "src/scene.js",),
# )


controller.initialize()
controller.runForever()
