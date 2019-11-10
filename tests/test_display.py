import sys
import time
import os
print("cwd: {0}".format(os.getcwd()))
sys.path.append("./src")

from display import Display

def test_displayTimeCountUp():

    display = Display(padding=0, totalLines=4)
    display.initialize()
    display.draw("test")
    currentCount = 0

    currentTimeCount = time.time()

    while True:
        if time.time()>currentTimeCount:
            writelines = [
                (0, ""),
                (1, currentCount),
                (2, currentTimeCount),
                (3, currentTimeCount)
            ]

            display.draw(writelines, clearDisplay=True)
            currentTimeCount = currentTimeCount + 1
            currentCount = currentCount + 1
            print("Count time {0}".format(currentTimeCount))
            print("Count {0}".format(currentCount))

def test_displayTimeCountUpFast():

    display = Display(padding=-2, totalLines=4)
    display.initialize()
    display.draw("test")
    currentCount = 0

    currentTimeCount = time.time()

    while True:
        if time.time()>currentTimeCount:
            writelines = [
                (0, currentTimeCount),
                (1, currentCount),
                (2, currentTimeCount),
                (3, currentTimeCount)
            ]
            display.draw(writelines, clearDisplay=True)
            currentTimeCount = currentTimeCount + 0.1
            currentCount = currentCount + 1
            # print("Count time {0}".format(currentTimeCount))
            # print("Count {0}".format(currentCount))


def test_cleardisplay():

    display = Display(padding=-2, totalLines=4)
    display.initialize()
    display.draw("test")

    writelines = [
        (0, "asdf"),
        (1, "asdf"),
        (2, "asdf"),
        (3, "asdf")
    ]

    display.draw(writelines, clearDisplay=True)
    time.sleep(2)
    display.clearDisplay()
    # display.draw([], clearDisplay=True)

if __name__ == "__main__":
    test_displayTimeCountUpFast()
    # test_cleardisplay()
