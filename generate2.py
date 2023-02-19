from PIL import Image, ImageEnhance
from perlin_noise import PerlinNoise
import math
import numpy as np
import sys
import random
from multiprocessing import Pool

# Remap the noise to use the full 0.0-1.0 range
def remap(oldMin, oldMax, num):
    oldRange = oldMax - oldMin
    return ((num - oldMin)) / oldRange

def toPixel(pxNoise, color):
    newColor = (color[0], color[1], color[2], int(pxNoise * 255))
    return newColor

# The size of the image in pixels
imgSize = (270, 270)
# How much to scale the image for viewing
scalar = 5

def generate(seed):
    mapSeed = seed

    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 0)

    # Perlin Noise functions at different octaves (higher octaves == more fine details)
    NoiseFuncs = [
        PerlinNoise(octaves=4, seed=mapSeed),
        PerlinNoise(octaves=8, seed=mapSeed),
        #PerlinNoise(octaves=16, seed=mapSeed),
        # PerlinNoise(octaves=32, seed=mapSeed),
    ]

    img = Image.new("RGBA", imgSize)
    bg = Image.new("RGBA", imgSize, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255))
    body = Image.open("Body.png").convert("RGBA")

    # Create a 2D array to store the noise values
    SimNoises = [[0 for x in range(imgSize[0])] for y in range(imgSize[1])]

    # Generate the noise values
    for x in range(imgSize[0]):
        for y in range(imgSize[1]):
            # Lower octave noise functions have a higher weight to create larger land masses with small variations
            simNoise = 1 * (NoiseFuncs[0]([x / imgSize[0], y / imgSize[1]]) + 1) / 2
            simNoise += 0.5 * (NoiseFuncs[1]([x / imgSize[0], y / imgSize[1]]) + 1) / 2
            # simNoise += 0.25 * (NoiseFuncs[2]([x / imgSize[0], y / imgSize[1]]) + 1) / 2
            #simNoise += 0.125 * (NoiseFuncs[2]([x / imgSize[0], y / imgSize[1]]) + 1) / 2
            simNoise /= 1 + 0.5# + 0.25 + 0.125
            SimNoises[x][y] = simNoise

    # Remap the noises to use the full 0.0 to 1.0 range
    MaxSimNoise = np.amax(SimNoises)
    MinSimNoise = np.amin(SimNoises)
    print(MinSimNoise)
    print(MaxSimNoise)

    for x in range(imgSize[0]):
        for y in range(imgSize[1]):
            SimNoises[x][y] = remap(MinSimNoise, MaxSimNoise, SimNoises[x][y])

    NewMaxSimNoise = np.amax(SimNoises)
    NewMinSimNoise = np.amin(SimNoises)
    print(NewMinSimNoise)
    print(NewMaxSimNoise)

    # Convert the noise to an image
    for y in range(imgSize[1]):
        for x in range(imgSize[0]):
            pxNoise = SimNoises[x][y]
            #scaledNoise = scaleAlt2(SimNoises[x][y])
            #pxNoise = shapeIsland(x, y, round(255 * scaledNoise))
            pxNoise = min(255, pxNoise * 1)
            pixel = toPixel(pxNoise, color)
            img.putpixel((x, y), pixel)

    bg.alpha_composite(img)
    bg = ImageEnhance.Brightness(bg).enhance(1.5)
    bigger = bg.resize((imgSize[0] * scalar, imgSize[1] * scalar))
    bigger.alpha_composite(body)
    bigger.save("output/" + str(seed) + ".png")
    # bigger.show()

if __name__ == "__main__":
    with Pool(8) as p:
        p.map(generate, range(10000))