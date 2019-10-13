import RPi.GPIO as GPIO
import collections
import time

from Naked.toolshed.shell import execute_js, muterun_js
version = "0.0.1"

class Controller(object):
    button_pressed = 1
    button_released = 2
    IO_ON = 3
    IO_OFF = 4

    def __init__(self):
        # initialize display
        self._allScenes = {}
        self._display = None
        self._rotEncoder = None

        # curent events
        self._curSceneId = 0
        self._currentTimeCount = None
        self._currentCount = None
        self._switchState= self.button_released
        self._rotaryEvents = []
        self._buttonPressedEvents= []
        self._buttonReleasedEvents= []
        self._eventLock = False
        self._ioEvents = {
            Controller.IO_ON: collections.defauldict(lambda: []),
            Controller.IO_OFF: collections.defauldict(lambda: []),
        }
        self._defaultUpDown = GPIO.PUD_UP

    def _setDefaultPullUpDown(self, updown=GPIO.PUD_UP):
        self._defaultUpDown = updown

    def _switchPressed(self):
        if not self._eventLock:
            print("locking")
            self._eventLock = True
            self._switchState = self.button_pressed
            self._currentTimeCount = time.time()
            self._currentCount = 0
            print("running pressed events")
            self._runRotaryButtonPressedEvents()
            time.sleep(0.05)
            self._eventLock = False
            print("unlocking")
        else:
            while self._eventLock:
                time.sleep(0.01)
            self._switchPressed()

    def _switchReleased(self):
        if not self._eventLock:
            print("locking")
            self._eventLock = True
            self._switchState = self.button_released
            self._runRotaryButtonReleasedEvents()
            self._currentTimeCount = None
            self._currentCount = None
            print("running released events")
            time.sleep(0.05)
            self._eventLock = False
            print("unlocking")
        else:
            while self._eventLock:
                print("there is a current process running")
                time.sleep(0.01)
            self._switchReleased()

    def runForever(self):
        # give the display to the rotary encoder to update
        self._rotEncoder.setController(self)
        print("RUNNING FOREVER!!")
        try:
            while True:
                if self._currentTimeCount and self._switchState is self.button_pressed:
                    # print("RUNNING BUTTON PRESSED IN FOREVER LOOP")
                    self._runRotaryButtonPressedEvents()
                # elif not self._currentTimeCount and self._switchState is self.button_released:
                #     self._runRotaryEvents(self._curSceneId)
                time.sleep(0.1)
        finally:
            self._rotEncoder.stop()

    def initialize(self):
        self._display.initialize()
        self._display.draw("MidiController", lineNumber=1)
        self._display.draw("Version {0}".format(version), lineNumber=2)
        self._rotEncoder.setArraySize(len(self._allScenes))

        def setupPins(pins):
            for pin in pins:
                GPIO.setup(pin, pull_up_down=self._defaultUpDown)
                GPIO.add_event_detect(pin,
                                      GPIO.BOTH,
                                      callback=self._GPIOEventCallback,
                                      bouncetime=self.switchBounceTime)

        usePinIoOff = [pin for pin, events in self._ioEvents[self.IO_OFF].iteritems()]
        setupPins(usePinIoOff)
        usePinIoOn = [pin for pin, events in self._ioEvents[self.IO_ON].iteritems()]
        setupPins(usePinIoOn)

    def setRotaryEncoder(self, rotEncoder):
        self._rotEncoder = rotEncoder

    def setDisplay(self, display):
        self._display = display

    def importScenes(self, scenes):
        self._allScenes = scenes

    def setCurrentSceneId(self, sceneId):
        self._curSceneId = sceneId


    # ------------------------- Event callbacks ----------
    def setRotaryEvents(self, *events):
        for event in events:
            self._rotaryEvents.append(event)

    # def setRotaryButtonEvents(self, *events):
    #     for event in events:
    #         self._rotaryEvents.append(event)

    def setTimeRotaryButtonPressedEvents(self, *events):
        for event in events:
            self._buttonPressedEvents.append(event)

    # def setRotaryButtonReleasedEvents(self, *events):
    #     for event in events:
    #         self._buttonReleasedEvents.append(event)
    def setRotaryButtonReleasedEvents(self, eventDict):
        self._buttonReleasedEvents = eventDict

    def setGPIOEvents(self, io_pin, io_state, *events):
        for events in events:
            self._ioEvents[self.IO_OFF][io_pin].append(event)

    def _GPIOEventCallback(self, pin):
        """
        Special method to execute for event detection.
        """
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

    def _runRotaryEvents(self, sceneId):
        self.setCurrentSceneId(sceneId)
        self._runEvents(self._rotaryEvents)

    def _runRotaryButtonPressedEvents(self):
        self._runEvents(self._buttonPressedEvents)

    def _runRotaryButtonReleasedEvents(self):
            self._runTimeElapsedEvents(self._buttonReleasedEvents)

    def _runTimeElapsedEvents(self, events):
        if not self._currentCount:
            print("NO TIME ELAPSED DETECTED. no event executed. CURRENT COUNT IS: {0}".format(self._currentCount))
            return

        # executing for coarse time, by the second only
        # can be changed to use milliseconds
        time_array = list(events.keys())
        time_selected = closest(time_array, self._currentCount)
        print("selected time closest to {0}: {1}".format(self._currentCount, time_selected))
        self._display.draw([(1, "Activating Scene:"),
                            (2, "{0}".format(self._allScenes[self._curSceneId])),
                            ], clearDisplay=True)
        # self._runEvents(events[time_selected])


    def _runEvents(self, events):
        for event in events:
            # print("event is {0}".format(event))
            if isinstance(event, tuple):
                eventMethod = event[0]
                eventArgs = event[1:]
                eventMethod(*eventArgs)
            # elif isinstance(event, dict):
            else:
                # print("event is {0}".format(event))
                event()

    # ------------------------- EVENTS --------------------

    def _eventSetSceneDisplay(self):
        self._display.clearDisplay()
        self._display.draw("{0}".format(self._allScenes[self._curSceneId]), lineNumber=1)
        print("DISPLAYED: {0}".format(self._allScenes[self._curSceneId]))

    def _eventEcho(self, string):
        """
        Method for cleanly displaying messages to the OLED screen
        """
        print("ECHO: {0}".format(string))

    def _eventExecuteJs(self, scriptPath, *args):
        print("Current Time count is {0}".format(self._currentCount))
        response = muterun_js(scriptPath, *args)

        if response.exitcode == 0:
            print(response.stdout)
            print("EXECUTED: {0}".format(self._allScenes[self._curSceneId]))
        else:
            sys.stderr.write(response.stderr)

        # # try this method if execute with argument doesnt work
        # if len(args) > 0:
        #     js_command = 'node ' + scriptPath + " " + args
        # else:
        #     js_command = 'node ' + scriptPath

    def _eventDisplayCountUp(self):

        if self._switchState is self.button_released:
            return
        if self._currentTimeCount is None:
            print("Something went wrong. shouldnt be counting up if not pressed")
            return

        # self._display.draw("Counting: {0}".format(self._currentCount), lineNumber=2, clearDisplay=True)
        if time.time()>self._currentTimeCount:
            # self._display.clearDisplay()
            # self._display.draw("Counting: {0}".format(self._currentCount), lineNumber=2, clearDisplay=True)
            writelines = [(0,""),
                          (1, self._currentCount),
                          (2,""),
                          (3,"")]
            self._display.draw(writelines, clearDisplay=True)
            self._currentTimeCount = self._currentTimeCount + 1
            self._currentCount = self._currentCount + 1
            print("Count time {0}: {1}".format(self._currentTimeCount,self._allScenes[self._curSceneId]))
            print("Count {0}: {1}".format(self._currentCount,self._allScenes[self._curSceneId]))
        # self._currentTimeCount += 1

    def _eventShutdown(self, switchTimer):
        print("Shutting Down")
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
