import time
import board
import displayio

display = board.DISPLAY

print(display.width, display.height)

# Create a bitmap with two colors
bitmap = displayio.Bitmap(display.width, display.height, 2)

# Create a two color palette
palette = displayio.Palette(2)
palette[0] = 0x000000
palette[1] = 0xffffff

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)

# Create a Group
group = displayio.Group()

# Add the TileGrid to the Group
group.append(tile_grid)

# Add the Group to the Display
display.show(group)

# change base color
palette[0] = bytearray((255, 0, 0))  # rgb
board.DISPLAY.wait_for_frame()

# Draw a pixel
bitmap[10, 10] = 1

# Draw even more pixels
for iy in range(0, display.height):
    for ix in range(0, display.width):
        bitmap[ix, iy] = 1
    time.sleep(0.01)
    display.show(group)
    board.DISPLAY.wait_for_frame()

while True:
    continue
