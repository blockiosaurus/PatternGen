from dataclasses import dataclass
from typing import List, Tuple
import random

# Just store https://stackoverflow.com/a/5709655/562769
# as anti_aliased_line.py in the same directory
from anti_aliased_line import draw_line_antialiased
from PIL import Image, ImageDraw, ImageOps
from multiprocessing import Pool
import sys

NUMBER = int(sys.argv[1])

@dataclass
class Point:
    x: float
    y: float


@dataclass
class Line:
    p1: Point
    p2: Point

    def position(self, p: float) -> Point:
        return Point(
            self.p1.x + (self.p2.x - self.p1.x) * p,
            self.p1.y + (self.p2.y - self.p1.y) * p,
        )


@dataclass
class Rectangle:
    p1: Point
    p2: Point
    p3: Point
    p4: Point

    def __getitem__(self, key: int) -> Point:
        if key == 0:
            return self.p1
        elif key == 1:
            return self.p2
        elif key == 2:
            return self.p3
        elif key == 3:
            return self.p4
        raise ValueError(f"key = {key} is invalid")

    def __setitem__(self, key: int, value: Point) -> None:
        if key == 0:
            self.p1 = value
        elif key == 1:
            self.p2 = value
        elif key == 2:
            self.p3 = value
        elif key == 3:
            self.p4 = value
        else:
            raise ValueError(f"key = {key} is invalid")


def new_point(rect: Rectangle, i: int, pct: float = 0.1) -> Point:
    if i == 0:
        return Line(rect.p1, rect.p2).position(pct)
    elif i == 1:  # top
        return Line(rect.p2, rect.p3).position(pct)
    elif i == 2:
        return Line(rect.p3, rect.p4).position(pct)
    elif i == 3:
        return Line(rect.p4, rect.p1).position(pct)
    raise ValueError(f"i = {i} is invalid")


def get_color(i: int, color, offset) -> Tuple[int, int, int, int]:
    r = (color[0] + offset[0] + i) % 256
    g = (color[1] + offset[1] + i) % 256
    b = (color[2] + offset[2] + i) % 256
    return (r, g, b, 128)

def replace_color(img, color, new_color):
    for x in range(img.width):
        for y in range(img.height):
            if img.getpixel((x, y)) == color:
                img.putpixel((x, y), new_color)


def main(seed):
    body = Image.open("Body.png").convert("RGBA")
    trait_type = "Eyes"
    rarity = {
        "Awake":  18 * 0.01 * NUMBER,
        "Happy":  15 * 0.01 * NUMBER,
        "Sleeping":  13 * 0.01 * NUMBER,
        "Winking":  12 * 0.01 * NUMBER,
        "Crying":  10 * 0.01 * NUMBER,
        "Cute":  9 * 0.01 * NUMBER,
        "Ultra Cute": 7 * 0.01 * NUMBER,
        "Hearts":  5 * 0.01 * NUMBER,
        "Glasses":  5 * 0.01 * NUMBER,
        "Vipers":  3 * 0.01 * NUMBER,
        "N0uns":  3 * 0.01 * NUMBER,
    }

    width = 1350
    height = 1350
    im = Image.new("RGBA", (width, height), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(im)
    rectangle = Rectangle(
        Point(0, 0), Point(width, 0), Point(width, height), Point(0, height)
    )

    base_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    color_offset = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    for i in range(1000):
        p1 = rectangle[i % 4]
        p2 = rectangle[(i + 1) % 4]
        draw_line_antialiased(draw, im, p1.x, p1.y, p2.x, p2.y, get_color(i, base_color, color_offset))
        # draw.line((p1.x, p1.y, p2.x, p2.y), fill=get_color(i))
        rectangle[i % 4] = new_point(rectangle, i % 4, pct=0.01)

    modded = ImageOps.grayscale(body).convert("RGBA")
    modded.putalpha(200)
    replace_color(modded, (0, 0, 0, 200), (255, 255, 255, 0))
    im.alpha_composite(modded)

    trait = random.choice(list(rarity.keys()))
    trait_img = Image.open(trait_type + "/" + trait + ".png").convert("RGBA")
    im.alpha_composite(trait_img)
    rarity[trait] -= 1
    if rarity[trait] == 0:
        rarity.pop(trait)

    # write to stdout
    im.save("output/" + str(seed) + ".png")


if __name__ == "__main__":
     with Pool(8) as p:
        p.map(main, range(NUMBER))