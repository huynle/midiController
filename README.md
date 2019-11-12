# Objective
Select scenes for Allen and Heath QU-32 Mixer using a raspberrypi with KY040 Rotary Encoder and a SSD1306 OLED 128x32 pixel display.




# Functions
- Scene select using rotary encoder, have scene display on display
- Scene selection using KY040 push button functionality
- When detect shutdown from sequencer (an input pin falls to zero voltage on Rpi), shutdown sequence gets initiated
- When delete power up from sequencer, power up sequence for mixer gets initiated


# Sequences

**Powering Up System**
- raspberry pi is already running - cron job
- press and hold rotary button for 5 seconds to turn on the sequencer
  - start up sequencer
  - load last/default scene


**Shut Down system**
- press and hold rotary button for 5 seconds to start shutdown
  - store the current scene to text file
  - execute shutdown script for mixer
  - shutdown sequencer

**Scene Selection**
- Rotate the rotary encoder
  - press and hold 3 seconds to select the scene
    - countdown will show on display



# Extra Stuff
- get ESP32 to communicate back to raspberry pi
  - raspberrypi has MQTT server running



# Notes
- Display is has line at the top is because the GPIO has not been completely cleared on each force exit



# Known Bugs
