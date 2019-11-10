import RPi.GPIO as GPIO
import time


class KY040(object):

    CLOCKWISE = 0
    ANTICLOCKWISE = 1
    PRESSED = 2
    RELEASED = 3

    def __init__(self, clockPin, dataPin, switchPin, rotaryBounceTime=250, switchBounceTime=300):
        #persist values
        self.clockPin = clockPin
        self.dataPin = dataPin
        self.switchPin = switchPin
        self.rotaryBounceTime = rotaryBounceTime
        self.switchBounceTime = switchBounceTime
        self._count = 0
        self._controller = None
        self._arraySize = 0
        self._switchTimer = 0.1


    def initialize(self):
        #setup pins
        GPIO.setup(self.clockPin, GPIO.IN)
        GPIO.setup(self.dataPin, GPIO.IN)

        # set switch pin to be high. When pressed, voltage goes to zero
        GPIO.setup(self.switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.clockPin,  # this `clockPin` would be the `pin` argument for the callback
                              GPIO.FALLING,
                              callback=self._clockCallback,
                              bouncetime=self.rotaryBounceTime)
        GPIO.add_event_detect(self.switchPin,
                              GPIO.BOTH,
                              callback=self.switchCallback,
                              bouncetime=self.switchBounceTime)

    def stop(self):
        GPIO.remove_event_detect(self.clockPin)
        GPIO.remove_event_detect(self.switchPin)
        GPIO.cleanup()

    def _clockCallback(self, pin):
        if GPIO.input(self.clockPin) == 0:
            data = GPIO.input(self.dataPin)
            if data == 1:
                self.rotaryCallback(self.ANTICLOCKWISE)
            else:
                self.rotaryCallback(self.CLOCKWISE)

    # def _switchCallback(self, pin):
    #     if GPIO.input(self.switchPin) == 0:
    #         self.switchCallback()

    def setArraySize(self, arraySize):
        self._arraySize = arraySize

    def setController(self, controller):
        print("setting controller")
        self._controller = controller

    def setSwitchTimer(self, timer):
        """
        Timer value in seconds
        """
        self._switchTimer = timer

    def loopCounter(self, value):
        arrayLen = self._arraySize-1
        if value < 0:
            value = arrayLen
        elif value > arrayLen:
            value = 0
        return value

    def rotaryCallback(self, direction):
        # global current_count
        current_count = self._count
        print("Current count is {0}".format(current_count))
        if direction:
            current_count += 1
        else:
            current_count -= 1
        self._count = self.loopCounter(current_count)
        # print("Count AFTER is {0}".format(self._count))
        self._controller._runRotaryEvents(self._count)

    def switchCallback(self, pin):
        if GPIO.input(self.switchPin):
            print("Rising edge detected at {0}".format(time.time()))
            self._controller._switchReleased()
        else:
            print("Falling edge detected at {0}".format(time.time()))
            self._controller._switchPressed()

    @classmethod
    def start(cls, clockpin, datapin, switchpin):
        """
        The bounce time has been tuned
        and Pins are in BCM mode
        """
        GPIO.setmode(GPIO.BCM)
        ky040 = cls(clockpin, datapin, switchpin, rotaryBounceTime=250, switchBounceTime=100)
        # (clockPin, dataPin, switchPin, rotaryBounceTime=250, switchBounceTime=300):
        ky040.initialize()
        return ky040

