import board
import terminalio
from adafruit_display_text import label


display = board.DISPLAY

# define text
text = "HELLO WORLD"

# Create the tet label
font = terminalio.FONT
text_area = label.Label(font, text=text)

# set color
text_area.color = bytearray((0, 0, 255))

# Set the location
text_area.x = int(display.width * 0.1)
text_area.y = int(display.height * 0.5)

# Show it
display.show(text_area)

while True:
    continue
