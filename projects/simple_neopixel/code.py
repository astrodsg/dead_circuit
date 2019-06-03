import time
import board
import neopixel

speed = 0.1  # seconds

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
print(pixels)

# Get the steps in color from 0 to 255 (max color)
color_max = 255
color_step_size = 10
color_values = list(range(0, color_max, color_step_size))


# Increase the red color values 0 to 255
print('increase in red')
for value in color_values:
    pixels[0] = (value, 0, 0)
    print('red {:.0%}'.format(value / color_max))
    time.sleep(speed)


# Increase the green color values 0 to 255
print('increase in green, decrease red')
for value in color_values:
    pixels[0] = (255 - value, value, 0)
    print('green {:.0%}'.format(value / color_max))
    time.sleep(speed)


# Increase the blue color values 0 to 255
print('increase in blue, decrease green')
for value in color_values:
    pixels[0] = (0, 255 - value, value)
    print('blue {:.0%}'.format(value / color_max))
    time.sleep(speed)


# Set the color to white
print('tada!')
pixels[0] = (255, 255, 255)
time.sleep(3)

# Turn off pixel
pixels[0] = (0, 0, 0)
while True:
    continue
