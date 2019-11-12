import RPi.GPIO as GPIO
import sys
import os
import collections
import time
import subprocess

from Naked.toolshed.shell import execute_js, muterun_js
version = "0.0.1"

class Controller(object):
    button_pressed = 1
    button_released = 2
    IO_ON = 3
    IO_OFF = 4
    SEQ_OFF = 5
    SEQ_ON = 6

    def __init__(self):
        # initialize display
        self._allScenes = {}
        self._display = None
        self._rotEncoder = None

        # curent events
        self._selectedSceneId = 0
        self._curSceneId = 0
        self._currentTimeCount = None
        self._currentCount = None
        self._switchState= self.button_released

        # lock attributes, to keep things running smoothly
        self._eventLock = False
        self._eventIdleEventLock = False
        self._eventRotaryLock = False
        self._eventButtonPressedLock = False
        self._eventButtonReleasedLock = False
        self._eventActivatedSceneLock = False

        # for idling
        self._timeToIdle = 2
        self._lastTouched = time.time()

        # self._isIdle = True
        self._isIdleExecuted = False

        # Event arrays specifically tied to the rotary encoder
        self._initializedEvents = []
        self._idleEvents = []
        self._outOfIdleEvents = []
        self._rotaryEvents = []
        self._buttonPressedEvents= []
        self._buttonReleasedEvents= []

        # dictionary to hold all the events
        self._ioEvents = {
            Controller.IO_ON: collections.defaultdict(lambda: []),
            Controller.IO_OFF: collections.defaultdict(lambda: []),
        }
        self._defaultUpDown = GPIO.PUD_UP

        self._debug = True

    def touch(func):
        """
        To help track when controller is idle
        """
        def magic(self, *args, **kwargs) :
            self._lastTouched = time.time()
            self._isIdleExecuted = False
            if self._debug: print("Refreshing last touched to: {0}".format(self._lastTouched))
            func(self, *args, **kwargs)
        return magic

    @property
    def isIdle(self):
        # if self._debug: print("checking if idle {0} + {1} > {2}".format(self._lastTouched, self._timeToIdle, time.time()))
        check = False
        if self._lastTouched + self._timeToIdle < time.time():
            # if self._debug: print("GOT IT!")
            check = True
        return check

    @property
    def selectedSceneId(self):
        return self._selectedSceneId

    @property
    def currentSceneId(self):
        return self._curSceneId

    def _setDefaultPullUpDown(self, updown=GPIO.PUD_UP):
        self._defaultUpDown = updown

    def runForever(self):
        self._runInitializedEvents()
        # give the display to the rotary encoder to update
        if self._debug: print("RUNNING FOREVER!!")
        try:
            while True:
                # this if statement is for the count up to happen
                if self._currentTimeCount and self._switchState is self.button_pressed:
                    self._runRotaryButtonPressedEvents()

                # if self._debug: print("is it idle? {0}: {1}".format(self.isIdle, self._isIdleExecuted))
                if self.isIdle and not self._isIdleExecuted:
                    self._runIdleEvents()
                    if self._debug: print("IDLED!!")
                    self._isIdleExecuted = True

                time.sleep(0.1)
        finally:
            if self._debug: print("DOING clean up!")
            self._rotEncoder.stop()
            GPIO.cleanup()

    def initialize(self):
        """
        Initialize the controller
        """
        # set rpi on BCM mode
        GPIO.setmode(GPIO.BCM)

        self._display.initialize()
        # self._display.draw("MidiController", lineNumber=1)
        # self._display.draw("Version: {0}".format(version), lineNumber=2)
        # self._display.draw("IP: {0}".format(IP.decode("utf-8")), lineNumber=3)
        # self._eventIntroScreen()
        # set the order of scenes in the rotary encoder
        self._rotEncoder.setArraySize(len(self._allScenes))

        def setupPins(pins):
            for pin in pins:
                GPIO.setup(pin, GPIO.IN, pull_up_down=self._defaultUpDown)
                GPIO.add_event_detect(pin,
                                      GPIO.BOTH,
                                      callback=self._GPIOEventCallback)

        usePinIoOff = [pin for pin, events in self._ioEvents[self.IO_OFF].items()]
        setupPins(usePinIoOff)
        usePinIoOn = [pin for pin, events in self._ioEvents[self.IO_ON].items()]
        setupPins(usePinIoOn)

        self._rotEncoder.setController(self)

    def setRotaryEncoder(self, rotEncoder):
        self._rotEncoder = rotEncoder

    def setDisplay(self, display):
        self._display = display

    def setSecondsToIdle(self, idleTime):
        self._timeToIdle = idleTime

    def importScenes(self, scenes):
        self._allScenes = scenes

    def setCurrentSceneId(self, sceneId):
        self._curSceneId = sceneId


    # ------------------------- Event callbacks ----------
    def setRotaryEvents(self, *events):
        for event in events:
            self._rotaryEvents.append(event)

    def setIdleEvents(self, *events):
        for event in events:
            self._idleEvents.append(event)

    def setOutOfIdleEvents(self, *events):
        for event in events:
            self._outOfIdleEvents.append(event)

    def setInitializedEvents(self, *events):
        for event in events:
            self._initializedEvents.append(event)

    def setRotaryButtonPressedEvents(self, *events):
        for event in events:
            self._buttonPressedEvents.append(event)

    # def setRotaryButtonReleasedEvents(self, *events):
    #     for event in events:
    #         self._buttonReleasedEvents.append(event)
    def setTimedRotaryButtonReleasedEvents(self, eventDict):
        self._buttonReleasedEvents = eventDict

    def setGPIOEvents(self, io_pin, io_state, *events):
        for event in events:
            self._ioEvents[self.IO_OFF][io_pin].append(event)

    def setInputPins(self, *pins):
        for pin in pins:
            pin_read = GPIO.setup(pin, GPIO.IN)

    def setOutputPins(self, *pins):
        for pin in pins:
            pin_read = GPIO.setup(pin, GPIO.OUT)

    def _switchPressed(self):
        if self._debug: print("Switch Pressed start at {0}".format(time.time()))
        if not self._eventLock:
            if self._debug: print("locking")
            self._eventLock = True
            self._switchState = self.button_pressed
            self._currentTimeCount = time.time()
            self._currentCount = 0
            if self._debug: print("running pressed events")
            self._runRotaryButtonPressedEvents()
            time.sleep(0.05)
            self._eventLock = False
            if self._debug: print("unlocking")
        else:
            while self._eventLock:
                time.sleep(0.01)
            self._switchPressed()
        if self._debug: print("Switch Pressed end at {0}".format(time.time()))

    def _switchReleased(self):
        if self._debug: print("Switch Released start at {0}".format(time.time()))
        if not self._eventLock:
            if self._debug: print("locking")
            self._eventLock = True
            self._switchState = self.button_released
            self._runRotaryButtonReleasedEvents()
            self._currentTimeCount = None
            self._currentCount = None
            if self._debug: print("running released events")
            time.sleep(0.05)
            self._eventLock = False
            if self._debug: print("unlocking")
        else:
            while self._eventLock:
                if self._debug: print("there is a current process running")
                time.sleep(0.01)
            self._switchReleased()
        if self._debug: print("Switch Released end at {0}".format(time.time()))

    def _GPIOEventCallback(self, pin):
        """
        Special method to execute for event detection.
        """
        if self._debug: print("GPIO Callback start at {0}".format(time.time()))
        pin_read = GPIO.input(pin)

        if not pin_read and self._defaultUpDown is GPIO.PUD_UP:
            # if the input is high
            IO_STATE = self.IO_ON
        elif pin_read and self._defaultUpDown is GPIO.PUD_UP:
            IO_STATE = self.IO_OFF
        elif not pin_read and self._defaultUpDown is GPIO.PUD_DOWN:
            IO_STATE = self.IO_OFF
        elif pin_read and self._defaultUPDown is GPIO.PUD_DOWN:
            IO_STATE = self.IO_ON

        events = self._ioEvents[IO_STATE].get(pin, [])
        for event in events:
            if isinstance(event, (tuple, list)):
                actualEvent = event[0]
                args = event[1:]
                actualEvent(*args)
            else:
                event()

    def _runIdleEvents(self):
        if self._debug: print("Running Idle events at {0}...".format(time.time()))

        if self._eventIdleEventLock:
            if self._debug: print("Event Lock is still in place, exiting button pressed event")
            return

        self._eventIdleEventLock = True
        self._runEvents(self._idleEvents)
        self._eventIdleEventLock = False

    def _runOutOfIdleEvents(self):
        if self._debug: print("Running Out of Idle events at {0}...".format(time.time()))
        self._runEvents(self._outOfIdleEvents)

    def _runRotaryEvents(self, sceneId):
        if self._debug: print("Running Rotary Event at {0}".format(time.time()))
        if self._eventRotaryLock:
            if self._debug: print("Event Lock is still in place, exiting button pressed event")
            return

        self.setCurrentSceneId(sceneId)

        self._eventRotaryLock = True
        self._runEvents(self._rotaryEvents)
        self._eventRotaryLock = False

    def _runInitializedEvents(self):
        if self._debug: print("Running Initialized events {0}...".format(time.time()))
        self._runEvents(self._initializedEvents)

    def _runRotaryButtonPressedEvents(self):
        if self._debug: print("Running Rotary Pressed Event at {0}".format(time.time()))
        if self._eventButtonPressedLock:
            if self._debug: print("Event Lock is still in place, exiting button pressed event")
            return

        # for coming out of idle
        if self._isIdleExecuted:
            if self._debug: print("----- Coming out of idle")
            self._runOutOfIdleEvents()
            return

        self._eventButtonPressedLock = True
        self._runEvents(self._buttonPressedEvents)
        self._eventButtonPressedLock = False

    def _runRotaryButtonReleasedEvents(self):
        if self._debug: print("Running Rotary Button Released Event at {0}".format(time.time()))
        if self._eventButtonReleasedLock:
            if self._debug: print("Event Lock is still in place, exiting button pressed event")
            return

        self._eventButtonReleasedLock = True
        self._runTimeElapsedEvents(self._buttonReleasedEvents)
        self._eventButtonReleasedLock = False

    def _runTimeElapsedEvents(self, events):
        """
        Depending on how long the switch button is held down fors
        """
        if not self._currentCount:
            if self._debug: print("NO TIME ELAPSED DETECTED. no event executed. CURRENT COUNT IS: {0}".format(self._currentCount))
            return

        # executing for coarse time, by the second only
        # can be changed to use milliseconds
        time_array = list(events.keys())
        time_selected = closest(time_array, self._currentCount)
        if self._debug: print("selected time closest to {0}: {1}".format(self._currentCount, time_selected))
        # self._display.draw([(1, "Activating Scene:"),
        #                     (2, "{0}".format(self._allScenes[self._curSceneId])),
        #                     ], clearDisplay=True)
        self._runEvents(events[time_selected])

    @touch
    def _runEvents(self, events, *args):
        for event in events:
            # print("event is {0}".format(event))
            if isinstance(event, tuple):
                eventMethod = event[0]
                eventArgs = event[1:]
                eventMethod(*eventArgs)
            else:
                event()

    # ------------------------- EVENTS --------------------

    def _eventSetSceneDisplay(self):
        if self._debug: print("Displaying: {0}".format(self._allScenes[self._curSceneId]))

        self._display.draw([
            (0, "Current Scene is:"),
            (1, "{0}".format(self._allScenes[self.selectedSceneId])),
            (2, "Select New Scene:"),
            (3, self._allScenes[self._curSceneId]),
        ], clearDisplay=True)

    def _eventEcho(self, string):
        """
        Method for cleanly displaying messages to the OLED screen
        """
        if self._debug: print("ECHO: {0}".format(string))

        stringArray = string.split("\n")
        echoString = [(ith, string) for ith, string in enumerate(stringArray)]
        # for ith, string in enumerate(stringArray):
        #     echoString.append((ith, string))
        self._display.draw(echoString, clearDisplay=True)

    def _eventIntroScreen(self):
        if self._debug: print("Intro screen")
        # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "hostname -I | cut -d\' \' -f1"
        # cmd = "hostname -I | cut -d' ' -f1"
        IP = subprocess.check_output(cmd, shell = True )
        self._display.draw([
            (1,"MidiController"),
            (2,"Version: {0}".format(version)),
            (3,"IP: {0}".format(IP.decode("utf-8")))
        ], clearDisplay=True)

    def _eventClearDisplay(self):
        """
        Method for cleanly displaying messages to the OLED screen
        """
        if self._debug: print("Clearing display")
        self._display.clearDisplay()

    def _eventExecuteJs(self, scriptPath):
        if self._debug: print("Current Time {0}".format(time.time()))
        self._display.draw([(1, "Activating Scene:"),
                            (2, "{0}".format(self._allScenes[self._curSceneId])),
                            ], clearDisplay=True)
        if self._debug: print("Executing JS: {0}, with args: {1}".format(scriptPath,self._curSceneId))
        self._eventExecuteJsLock = True
        try:
            subprocess_command = ["node", scriptPath, "{0}".format(self._curSceneId)]
            if self._debug: print("{0}".format(subprocess_command))
            subprocess.run(subprocess_command)
            self._selectedSceneId = self._curSceneId
        except Exception as err:
            self._eventEcho("Error:\n{0}!\nCheck Log.".format(os.path.basename(scriptPath)))
            if self._debug: print("*** EXCEPTION happened with JS script: \n{0}".format(err))

    def _eventExecuteJs_withArgs(self, scriptPath, *args):
        if self._debug: print("Current Time {0}".format(time.time()))
        self._display.draw([(1, "Activating Scene:"),
                            (2, "{0}".format(self._allScenes[self._curSceneId])),
                            ], clearDisplay=True)
        if self._debug: print("Executing JS: {0}, with args: {1}".format(scriptPath, args))
        self._eventExecuteJsLock = True
        try:
            subprocess_command = ["node", scriptPath] + ["{0}".format(arg) for arg in args]
            if self._debug: print("{0}".format(subprocess_command))
            subprocess.run(subprocess_command)
            self._selectedSceneId = args[0]
        except Exception as err:
            self._eventEcho("Error:\n{0}!\nCheck Log.".format(os.path.basename(scriptPath)))
            if self._debug: print("*** EXCEPTION happened with JS script: \n{0}".format(err))

        self._eventExecuteJsLock = False

    def _eventSecondsToWait(self, timeWait):
        if self._debug: print("Current Time {0}".format(time.time()))
        # self._display.draw("TEST", lineNumber=1, clearDisplay=True)
        time.sleep(timeWait)

    def _eventSequencerPower(self, pin, power):
        if self._debug: print("Current Time {0}".format(time.time()))

        try:
            # if self._debug: print("Writing ON to pin {0}".format(pin))
            if power == self.SEQ_OFF:
                if self._debug: print("Writing OFF to pin {0}".format(pin))
                self._eventEcho("Turning off Sequencer")
                GPIO.output(pin, 0)
            elif power == self.SEQ_ON:
                if self._debug: print("Writing ON to pin {0}".format(pin))
                self._eventEcho("Turning on Sequencer")
                GPIO.output(pin, 1)
            else:
                raise NotImplementedError("Unregonized input for power state")
        except Exception as err:
            self._eventEcho("Error:\nSequencer Pwr\nCheck Log.")
            if self._debug: print("*** EXCEPTION happened: \n{0}".format(err))

        # # try this method if execute with argument doesnt work
        # if len(args) > 0:
        #     js_command = 'node ' + scriptPath + " " + args
        # else:
        #     js_command = 'node ' + scriptPath

    def _eventSequencerPowerToggle(self, pin):
        if self._debug: print("Current Time {0}".format(time.time()))

        try:
            # if self._debug: print("Writing ON to pin {0}".format(pin))
            if power == self.SEQ_OFF:
                if self._debug: print("Writing OFF to pin {0}".format(pin))
                GPIO.output(pin, 0)
            elif power == self.SEQ_ON:
                if self._debug: print("Writing ON to pin {0}".format(pin))
                GPIO.output(pin, 1)
            else:
                raise NotImplementedError("Unregonized input for power state")
        except Exception as err:
            self._eventEcho("Error:\nPower Toggle!\nCheck Log.")
            if self._debug: print("*** EXCEPTION happened: \n{0}".format(err))

    def _eventDisplayCountUp(self):

        if self._switchState is self.button_released:
            return
        if self._currentTimeCount is None:
            if self._debug: print("Something went wrong. shouldnt be counting up if not pressed")
            return

        if self._debug: print("******** WHOA start ********* {0}".format(time.time()))
        if time.time() > self._currentTimeCount:
            if self._debug: print("*** Got into if ***")
            # self._display.draw(self._currentCount, lineNumber=2, clearDisplay=True)
            self._currentTimeCount = self._currentTimeCount + 1
            self._currentCount = self._currentCount + 1
            self._display.draw([
                (2, "----------{0}----------".format(self._currentCount)),
            ], clearDisplay=True)
            if self._debug: print("Count time {0}: {1}".format(self._currentTimeCount,self._allScenes[self._curSceneId]))
            if self._debug: print("Count {0}: {1}".format(self._currentCount,self._allScenes[self._curSceneId]))
        if self._debug: print("******** WHOA end ********* {0}".format(time.time()))

    def _eventShutdown(self, switchTimer):
        if self._debug: print("Shutting Down")
        raise NotImplementedError

    # --------------------- HELPERS -----------------------

def closest(myList, K):
    myList = sorted(myList)
    if len(myList) == 1:
        if K >= myList[0]:
            return myList[0]
    elif len(myList) > 1:
        for idx in range(len(myList)):
            try:
                if myList[idx] <= K < myList[idx+1]:
                    return myList[idx]
            except IndexError:
                return myList[idx]
