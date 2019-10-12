# Objective
Select scenes for Allen and Heath QU-32 Mixer using a raspberrypi with KY040 Rotary Encoder and a SSD1306 OLED 128x32 pixel display.

# Functions
- Scene select using rotary encoder, have scene display on display
- Scene selection using KY040 push button functionality
  - Button must be held down for a defined time for scene to change on QU-32 Mixer
- When detect shutdown from sequencer (an input pin falls to zero voltage on Rpi), shutdown sequence gets initiated
- When delete power up from sequencer, power up sequence for mixer gets initiated
