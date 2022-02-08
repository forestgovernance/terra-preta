import requests
import math
from PIL import Image
import os

TILESET_ID = "mapbox.satellite"
FORMAT = "jpg90"
ACCESS_TOKEN = "sk.eyJ1IjoiaXhmeGV4IiwiYSI6ImNrejQ0b3VycjAzNGQyb2xpNmtrdGM2NnIifQ.2w5h9DX8ztxPY_HcuRqVtg"
ZOOM = 18

matrices = {
    'true': [[0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0.299, 0.587, 0.114]],
    'mono': [[0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0.299, 0.587, 0.114, 0.299, 0.587, 0.114]],
    'color': [[1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 1]],
    'halfcolor': [[0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 1]],
    'optimized': [[0, 0.7, 0.3, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 1]],
}


def getTile(z, x, y):
    url = f"https://api.mapbox.com/v4/{TILESET_ID}/{z}/{x}/{y}@2x.{FORMAT}?access_token={ACCESS_TOKEN}"
    return requests.get(url).content


def getXY(LATITUDE, LONGITUDE, ZOOM):
    LATITUDE_RADIANS = math.radians(LATITUDE)
    N = 2.0 ** ZOOM
    X = int((LONGITUDE + 180.0) / 360.0 * N)
    Y = int((1.0 - math.asinh(math.tan(LATITUDE_RADIANS)) / math.pi) / 2.0 * N)
    return X, Y


def createGrid(tile_images, rows, cols):
    assert len(tile_images) == rows * cols

    w, h = tile_images[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))

    for i, tile_image in enumerate(tile_images):
        grid.paste(tile_image, box=(i % cols * w, i // cols * h))

    return grid


def make_anaglyph(left, right, color, path):
    width, height = left.size
    leftMap = left.load()
    rightMap = right.load()
    m = matrices[color]

    for y in range(0, height):
        for x in range(0, width):
            r1, g1, b1 = leftMap[x, y]
            r2, g2, b2 = rightMap[x, y]
            leftMap[x, y] = (
                int(r1*m[0][0] + g1*m[0][1] + b1*m[0][2] +
                    r2*m[1][0] + g2*m[1][1] + b2*m[1][2]),
                int(r1*m[0][3] + g1*m[0][4] + b1*m[0][5] +
                    r2*m[1][3] + g2*m[1][4] + b2*m[1][5]),
                int(r1*m[0][6] + g1*m[0][7] + b1*m[0][8] +
                    r2*m[1][6] + g2*m[1][7] + b2*m[1][8])
            )
    left.save(path)


def create_anaglyph(lat, lng):

    X, Y = getXY(lat, lng, ZOOM)
    GRID_SIZE = 5

    for x in range(X, X + GRID_SIZE):
        for y in range(Y, Y + GRID_SIZE):
            tile = getTile(ZOOM, x, y)
            with open(f"{x}_{y}.{FORMAT}", "wb") as f:
                f.write(tile)

    village_image = createGrid(
        [Image.open(f"{x}_{y}.{FORMAT}") for y in range(Y, Y + GRID_SIZE)
         for x in range(X, X + GRID_SIZE)],
        GRID_SIZE, GRID_SIZE,
    )

    with open("village.png", "wb") as f:
        village_image.save(f, "png")

    for x in range(X, X + GRID_SIZE):
        for y in range(Y, Y + GRID_SIZE):
            os.remove(f"{x}_{y}.{FORMAT}")

    img = Image.open(r'D:\ISB\village.png')
    x, y = img.size

    left = img.crop((0, 0, 0.95*x, y))
    right = img.crop((0.05*x, 0, x, y))

    make_anaglyph(left, right, 'mono',
              r'D:\ISB\Anaglyph Generator Web-app (Github)\Anaglyph-Generator-Prototype\static\anaglyph.jpg')

