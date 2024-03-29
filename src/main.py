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
controller.setInitializedEvents(
    (controller._eventIntroScreen,),
)

# For when the pi is idle
controller.setIdleEvents(
    # (controller._eventEcho, "Going idle..."),
    (controller._eventSecondsToWait, 5),
    (controller._eventClearDisplay)
)

# For when the pi is idle
# FIXME: not completely working yet
controller.setOutOfIdleEvents(
    # (controller._eventIntroScreen,),
)

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
        (controller._eventEcho, "Hold until\n----------2----------\nto prevent accidental\npresses"),
    ],

    2: [
        (controller._eventExecuteJs, "/home/pi/src/midiController/src/scene.js"),
    ],

    # for turnning off
    5: [
        (controller._eventEcho, "SHUTTING DOWN"),
        (controller._eventExecuteOFFJs, "/home/pi/src/midiController/src/off.js"),
        # (controller._eventSequencerPower, sequencerCtrlPin, controller.SEQ_OFF)
    ],

    # for turnning off
    8: [
        (controller._eventEcho, "Settings Menu:\n\nNot Implemented Yet."),
        (controller._eventSecondsToWait, 2),
        (controller._eventIntroScreen,)
    ],
})


# # set up the supporting events
# controller.setGPIOEvents(buttonpin, controller.IO_OFF,
#     (controller._eventEcho, "Power Up Sequence"),
#     # (controller._eventExecuteJs, "src/scene.js", lastScene),
# )

controller.setGPIOEvents(buttonpin, controller.IO_OFF,
    (controller._eventEcho, "Power Down Sequence"),
    # (controller._eventExecuteJs, "src/off.js",),
)


controller.initialize()
controller.runForever()
