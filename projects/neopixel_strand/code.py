import board
from collections import namedtuple
import random
import time

import neopixel

RGB = namedtuple('RGB', ('red', 'green', 'blue'))


def get_color_brightness(
    color: RGB,
    brightness: float = 1.0,
):
    """ Scale the color by brightness """
    brightness = float(min(max(brightness, 0.0), 1.0))
    return RGB(*(
        int(brightness * c)
        for c in color
    ))


def iter_rainbow_colors(step_size: float = 20):
    # TODO: implement blue to red
    red_to_blue = True
    limit = 0 if red_to_blue else 255
    direction = 1 if red_to_blue else -1
    step_size = direction * abs(step_size)

    red, green, blue = 255, 0, 0
    while True: 
        yield RGB(red, green, blue)

        if blue == limit:
            # transition red to green
            red -= step_size
            green += step_size
            blue = int(red <= 0)
        elif red == limit:
            # transition green to blue
            green -= step_size
            blue += step_size
            red = int(green <= 0)
        elif green == limit:
            # transition blue to red
            red += step_size
            blue -= step_size
            green = int(blue <= 0)

        red = int(min(max(red, 0), 255))
        green = int(min(max(green, 0), 255))
        blue = int(min(max(blue, 0), 255))


def apply_rainbow(
    pixels: neopixel.NeoPixel,
    step_delay: float = 0.1,
    brightness: float = 0.1,
):
    """ Create a rainbow for every pixel """
    step_size = (255 * 2.9) / len(pixels)
    rainbow_colors = iter_rainbow_colors(step_size)
    for i in range(len(pixels)):
        pixels[i] = get_color_brightness(next(rainbow_colors), brightness)
        time.sleep(step_delay)


def rainbow_loop(
    pixels: neopixel.NeoPixel,
    step_size: float = None,
    step_delay: float = 0.1,
    brightness: float = 0.1,
):
    if step_size is None:
        step_size = (255 * 2) / len(pixels)
    rainbow_colors = iter_rainbow_colors(step_size)
    i = 0
    while True:
        pixels[i] = get_color_brightness(next(rainbow_colors), brightness)
        i += 1
        i %= len(pixels)
        time.sleep(step_delay)


if __name__ == "__main__":
    on_chip_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
    pixels = neopixel.NeoPixel(board.EXTERNAL_NEOPIXEL, 30)

    on_chip_pixel[0] = RGB(250, 25, 25)

    # apply_rainbow(pixels, step_delay=0.2)
    rainbow_loop(pixels, step_size=10, step_delay=0.05)
    # rainbow_loop(on_chip_pixel, step_size=10, step_delay=0.05)
