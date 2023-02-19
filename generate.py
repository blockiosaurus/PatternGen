from PIL import Image, ImageEnhance, ImageOps
from perlin_noise import PerlinNoise
import math
import numpy as np
import sys
import random
from multiprocessing import Pool
import os

NUMBER = int(sys.argv[1])

skip_list = [
    5806,
    1458,
    6433,
    5006,
    6570,
    1547,
    7030,
    7524,
    4083,
    2663,
    5255,
    6239,
    2865,
    8550,
    7440,
    4068,
    2096,
    65,
    920,
    9218,
    3599,
    270,
    8795,
    5004,
    2889,
    1031,
    8924,
    9017,
    926,
    9186,
    174,
    7220,
    3016,
    1636,
    5238,
    8860,
    4625,
    6500,
    8558,
    1940,
    6923,
    9814,
    3126,
    8960,
    1750,
    140,
    5018,
    7548,
    8321,
    2421,
    6440,
    6004,
    6391,
    936,
    8274,
    8103,
    9306,
    7202,
    3018,
    9471,
    1684,
    2473,
    6919,
    9356,
    4866,
    6248,
    1673,
    6030,
    5915,
    4071,
    1689,
    6312,
    5561,
    5584,
    8682,
    9954,
    6940,
    3027,
    578,
    586,
    3523,
    6997,
    6163,
    5442,
    3732,
    4616,
    594,
    9161,
    2561,
    8570,
    8318,
    8719,
    1928,
    3401,
    3522,
    938,
    2571,
    6320,
    2641,
    6601,
    3220,
    118,
    3440,
    605,
    3172,
    8284,
    7132,
    891,
    4317,
    215,
    1068,
    2464,
    4600,
    8708,
    2335,
    9030,
    5392,
    265,
    6458,
    2425,
    7749,
    475,
    6209,
    6206,
    4581,
    6046,
    1375,
    9116,
    3354,
    7209,
    3854,
    8456,
    1239,
    7673,
    981,
    8193,
    3652,
    6087,
    803,
    7646,
    6071,
    2642,
    5682,
    3173,
    1860,
    436,
    44,
    2476,
    486,
    8000,
    9349,
    6661,
    8256,
    7894,
    1694,
    1521,
    6390,
    375,
    5930,
    3243,
    4249,
    5889,
    3488,
    9944,
    2825,
    2235,
    7828,
    479,
    1593,
    9977,
    342,
    4815,
    3061,
    8597,
    8046,
    5282,
    6748,
    7547,
    3594,
    8364,
    5445,
    3453,
    9181,
    8972,
    9108,
    8486,
    8372,
    6241,
    8475,
    9069,
    3149,
    9466,
    1198,
    3798,
    9794,
    4228,
    6236,
    7731,
    1030,
    7593,
    4320,
    1363,
    9486,
    1791,
    8800,
    7743,
    4187,
    7664,
    8642,
    7558,
    3010,
    4759,
    8025,
    3364,
    356,
    8005,
    7530,
    4635,
    505,
    5640,
    4878,
    4941,
    5692,
    8075,
    8523,
    5149,
    8633,
    9970,
    1105,
]

# Remap the noise to use the full 0.0-1.0 range
def remap(oldMin, oldMax, num):
    oldRange = oldMax - oldMin
    return ((num - oldMin)) / oldRange

def toPixel(pxNoise, color):
    newColor = (color[0], color[1], color[2], int(pxNoise * 255))
    return newColor

def replace_color(img, color, new_color):
    for x in range(img.width):
        for y in range(img.height):
            if img.getpixel((x, y)) == color:
                img.putpixel((x, y), new_color)

# The size of the image in pixels
imgSize = (270, 270)
# How much to scale the image for viewing
scalar = 5


body = Image.open("Body.png").convert("RGBA")
modded = ImageOps.grayscale(body).convert("RGBA")
modded.putalpha(200)
replace_color(modded, (0, 0, 0, 200), (255, 255, 255, 0))
trait_type = "Eyes"
trait_rarity = [
    "Awake",
    "Happy",
    "Sleeping",
    "Winking",
    "Crying",
    "Cute",
    "Ultra Cute",
    "Hearts",
    "Glasses",
    "Vipers",
    "N0uns",
]

trait_weights = (
    18 * 0.01 * NUMBER,
    15 * 0.01 * NUMBER,
    13 * 0.01 * NUMBER,
    12 * 0.01 * NUMBER,
    10 * 0.01 * NUMBER,
    10 * 0.01 * NUMBER,
    8 * 0.01 * NUMBER,
    5 * 0.01 * NUMBER,
    5 * 0.01 * NUMBER,
    2.5 * 0.01 * NUMBER,
    1.5 * 0.01 * NUMBER,
)

def generate(seed):
    img_path = "./output/" + str(seed) + ".png"
    json_path = "./json/" + str(seed) + ".json"
    if seed in skip_list:
        print("Skipping " + str(seed))
        if os.path.exists(img_path):
            print("Removing " + img_path)
            os.remove(img_path)
            os.remove(json_path)
        return
    if os.path.exists(img_path) and os.path.exists(json_path):
        print(str(seed) + " already exists")
        return
    mapSeed = seed + 10000

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
    # body = Image.open("Body.png").convert("RGBA")

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
    # print(MinSimNoise)
    # print(MaxSimNoise)

    for x in range(imgSize[0]):
        for y in range(imgSize[1]):
            SimNoises[x][y] = remap(MinSimNoise, MaxSimNoise, SimNoises[x][y])

    NewMaxSimNoise = np.amax(SimNoises)
    NewMinSimNoise = np.amin(SimNoises)
    # print(NewMinSimNoise)
    # print(NewMaxSimNoise)

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
    bigger.alpha_composite(modded)

    trait = random.choices(trait_rarity, weights=trait_weights, k=1)[0]
    trait_img = Image.open(trait_type + "/" + trait + ".png").convert("RGBA")
    bigger.alpha_composite(trait_img)

    with open("eyes_metadata_template.json", "r") as f:
        metadata = f.read()
        metadata = metadata.replace("#000", "| #" + str(seed + 1))
        metadata = metadata.replace("image.png", str(seed) + ".png")
        metadata = metadata.replace("##TRAIT##", trait)
        metadata = metadata.replace("##NUM##", str(seed))
        with open("json/" + str(seed) + ".json", "w") as out:
            out.write(metadata)

    bigger.save("output/" + str(seed) + ".png")
    # bigger.show()

if __name__ == "__main__":
    with Pool(16) as p:
        p.map(generate, range(NUMBER))