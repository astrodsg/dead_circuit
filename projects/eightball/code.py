# Magic 8-Ball
import time
import math
import os
import random
import board
import displayio
import adafruit_lis3dh

SENSITIVITY = 3   # reading in Z direction to trigger, adjustable
GRAVITY = 9.6
IMAGES_DIR = '/answers'


def list_directory(directory, file_extension=None):
    d = directory if directory.endswith('/') else directory + '/'
    filelist = []
    for filename in os.listdir(d):
        filepath = d + filename
        if file_extension:
            if filepath.endswith(file_extension):
                filelist.append(filepath)
        else:
            filelist.append(filepath)
    return filelist


def fade_display_on(fade_on=True, speed=0.01):
    brightness_steps = [i / 100 for i in range(0, 100)]
    if not fade_on:
        # reverse the brightness steps
        brightness_steps = brightness_steps[::-1]
    for b in brightness_steps:
        board.DISPLAY.brightness = b
        time.sleep(speed)
    board.DISPLAY.wait_for_frame()


def change_image(splash, images, i=None):
    fade_display_on(False)
    if len(splash):
        splash.pop()

    if i is None:
        i = random.randint(0, len(images)-1)
    else:
        i = i % len(images)
    img = images[i]

    print('Image load {}'.format(img))
    with open(img, 'rb') as fp:
        try:
            odb = displayio.OnDiskBitmap(fp)
        except ValueError:
            print("Image unsupported {}".format(img))
            del images[i]
            fade_display_on(False)
            return
        face = displayio.TileGrid(odb, pixel_shader=displayio.ColorConverter())

        splash.append(face)
        board.DISPLAY.wait_for_frame()

    fade_display_on()


if __name__ == '__main__':
    splash = displayio.Group()
    board.DISPLAY.show(splash)
    images = list_directory(IMAGES_DIR, 'bmp')

    # Set up accelerometer on I2C bus, 4G range:
    ACCEL = adafruit_lis3dh.LIS3DH_I2C(board.I2C(), address=0x18)
    ACCEL.range = adafruit_lis3dh.RANGE_4_G

    fade_display_on(False)

    while True:
        time.sleep(1)
        try:
            print(ACCEL.acceleration)
            total_accel = math.sqrt(sum([a**2 for a in ACCEL.acceleration]))
            total_accel = abs(total_accel - GRAVITY)
            print(total_accel)
            # ACCEL_Z = ACCEL.acceleration[2]  # Read Z axis acceleration
        except OSError:
            continue
        else:
            if total_accel > SENSITIVITY:
                change_image(splash, images)