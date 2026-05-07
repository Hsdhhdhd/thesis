from pathlib import Path

from PIL import Image, ImageFilter


BASE = Path(__file__).resolve().parents[2]
SRC = BASE / "插入photos"
OUT = Path(__file__).resolve().parent / "images"


def blur_regions(src_name, out_name, boxes):
    im = Image.open(SRC / src_name).convert("RGB")
    for box in boxes:
        crop = im.crop(box)
        crop = crop.filter(ImageFilter.GaussianBlur(radius=42))
        crop = crop.filter(ImageFilter.GaussianBlur(radius=24))
        im.paste(crop, box)
    dst = OUT / out_name
    im.save(dst, quality=92, optimize=True)
    print(f"{dst.name}: {im.size[0]}x{im.size[1]}, {dst.stat().st_size} bytes")


blur_regions(
    "火车实验环境1.jpg",
    "c6_train_environment_1_anon.jpg",
    [
        (0, 105, 205, 250),
        (220, 115, 360, 260),
        (395, 80, 575, 245),
        (665, 60, 805, 180),
        (900, 70, 1110, 255),
        (1185, 60, 1325, 175),
        (935, 230, 1325, 575),
    ],
)

blur_regions(
    "火车实验环境2.jpg",
    "c6_train_environment_2_anon.jpg",
    [
        (235, 235, 610, 665),
        (1000, 125, 1385, 575),
    ],
)
