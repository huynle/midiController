# Will need to hook the display up to the I2C pins

import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

class Display(object):

    def __init__(self, padding = -2, totalLines=4):
        self._padding = padding
        self._totalLines = totalLines
        self._leftPadding = 10

        self._disp = None
        self._image = None
        self._draw = None

        self._font = ImageFont.load_default()

        self._top = None
        self._bottom = None
        self._width = None
        self._height = None

    def ySpacing(self):
        # int would round down without much work
        return int(self._height/self._totalLines)

    def _yPos(self, lineNumber=0):
        # if lineNumber == 0:
            # return lineNumber*self.ySpacing()+self._padding
        return lineNumber*self.ySpacing()+self._padding
        # return lineNumber*self.ySpacing()

    def _xPos(self):
        return self._leftPadding

    def initialize(self):
        self._disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
        # Initialize library.
        self._disp.begin()

        # Clear display.
        self._disp.clear()
        self._disp.display()

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        self._top = self._padding
        self._width = self._disp.width
        self._height = self._disp.height
        self._bottom = self._height - self._padding

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self._image = Image.new('1', (self._width, self._height))

        # Get drawing object to draw on image.
        self._draw = ImageDraw.Draw(self._image)

        # Draw a black filled box to clear the image.
        self._draw.rectangle((0,0,self._width,self._height), outline=0, fill=0)


    def draw(self, value, lineNumber=0, clearDisplay=False):
        # Move left to right keeping track of the current x position for drawing shapes.
        if clearDisplay:
            self.clearDisplay()

        if value and isinstance(value, list):
            if len(value)>self._totalLines:
                raise NotImplementedError("Cannot display more than {0} at the moment.".format(self._totalLines))
            for ith, linestring in enumerate(value):
                if isinstance(linestring, tuple):
                    self._draw.text((self._xPos(), self._yPos(linestring[0])), "{0}".format(linestring[1]),  font=self._font, fill=255)
                else:
                    self._draw.text((self._xPos(), self._yPos(ith)), "{0}".format(linestring),  font=self._font, fill=255)
        else:
            self._draw.text((self._xPos(), self._yPos(lineNumber)), "{0}".format(value),  font=self._font, fill=255)

        self._disp.image(self._image)
        self._disp.display()
        # time.sleep(0.05)

    def clearDisplay(self):
        # Draw a black filled box to clear the image.
        self._draw.rectangle((0,0,self._width,self._height), outline=0, fill=0)
