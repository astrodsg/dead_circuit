""" This script will find the slcpy bmp image and display to the screen
"""
import board
import displayio

IMAGE_FILE = 'slcpy-compressed.bmp'


def change_image(splash, image_file):
    """ Changes the image on the splash screen this this one """
    if len(splash):
        splash.pop()
    print('Image load {}'.format(image_file))
    with open(image_file, 'rb') as fp:
        odb = displayio.OnDiskBitmap(fp)
        face = displayio.TileGrid(odb, pixel_shader=displayio.ColorConverter())
        splash.append(face)
        board.DISPLAY.wait_for_frame()


if __name__ == "__main__":
    splash = displayio.Group()
    board.DISPLAY.show(splash)
    change_image(splash, IMAGE_FILE)

    # just keep code running so image stays up
    while True:
        pass
