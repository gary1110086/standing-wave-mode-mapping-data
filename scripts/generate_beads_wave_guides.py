from __future__ import annotations

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = REPO_ROOT / "figures"
RAW_BEAD_DIR = FIG_DIR / "raw_beads"
OUT_SIZE = (1706, 1279)
PHOTO_CROP = (0, 320, 1706, 1120)
PHOTO_SIZE = (1706, 900)

TUBE_X0 = 145
TUBE_X1 = 1515
BEAD_Y = 430
INSET = (90, 910, 1616, 1255)


FREQ_META = {
    170: {
        "src": "f170.jpg",
        "out": "f170_beads_wave.png",
        "title": "170 Hz",
        "kind": "quarter-wave-like visual guide",
        "clusters": [(0.04, 0.48)],
        "mode": "oc1",
    },
    255: {
        "src": "f255.jpg",
        "out": "f255_beads_wave.png",
        "title": "255 Hz",
        "kind": "intermediate visual guide",
        "clusters": [(0.04, 0.42)],
        "mode": "intermediate_255",
    },
    345: {
        "src": "f345.jpg",
        "out": "f345_beads_wave.png",
        "title": "345 Hz photo for 343 Hz data",
        "kind": "half-wave-like visual guide",
        "clusters": [(0.25, 0.82)],
        "mode": "cc1",
    },
    425: {
        "src": "f425.jpg",
        "out": "f425_beads_wave.png",
        "title": "425 Hz",
        "kind": "intermediate visual guide",
        "clusters": [(0.02, 0.18), (0.48, 0.93)],
        "mode": "intermediate_425",
    },
    510: {
        "src": "f510.jpg",
        "out": "f510_beads_wave.png",
        "title": "510 Hz",
        "kind": "third-quarter-wave-like visual guide",
        "clusters": [(0.58, 0.96)],
        "mode": "oc2",
    },
    680: {
        "src": "f680.jpg",
        "out": "f680_beads_wave.png",
        "title": "680 Hz",
        "kind": "second half-wave-like visual guide",
        "clusters": [(0.10, 0.42), (0.68, 0.96)],
        "mode": "cc2",
    },
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


FONT_TITLE = font(42, True)
FONT_LABEL = font(30, False)
FONT_SMALL = font(25, False)


def tube_x(t: float) -> float:
    return TUBE_X0 + t * (TUBE_X1 - TUBE_X0)


def pressure_particle(mode: str, t: float) -> tuple[float, float]:
    if mode == "oc1":
        phi = math.pi * t / 2
        pressure = math.sin(phi)
        particle = math.cos(phi)
    elif mode == "oc2":
        phi = 3 * math.pi * t / 2
        pressure = math.sin(phi)
        particle = math.cos(phi)
    elif mode == "cc1":
        phi = math.pi * t
        pressure = math.cos(phi)
        particle = math.sin(phi)
    elif mode == "cc2":
        phi = 2 * math.pi * t
        pressure = math.cos(phi)
        particle = math.sin(phi)
    elif mode == "intermediate_255":
        phi = 0.72 * math.pi * t
        pressure = math.sin(phi)
        particle = math.cos(phi)
    else:
        phi = 1.24 * math.pi * t
        pressure = math.sin(phi)
        particle = math.cos(phi)
    return pressure, particle


def draw_cluster_outline(draw: ImageDraw.ImageDraw, clusters: list[tuple[float, float]]) -> None:
    return


def draw_photo_wave(draw: ImageDraw.ImageDraw, mode: str) -> None:
    pts = []
    for i in range(180):
        t = i / 179
        _, particle = pressure_particle(mode, t)
        y = BEAD_Y - 15 - 72 * abs(particle)
        pts.append((tube_x(t), y))
    draw.line(pts, fill=(255, 214, 10, 245), width=9, joint="curve")
    draw.line(pts, fill=(26, 52, 140, 220), width=4, joint="curve")
    draw.rounded_rectangle((50, 28, 675, 86), radius=20, fill=(255, 255, 255, 195))
    draw.text((78, 40), "qualitative bead-pattern guide", fill=(20, 35, 70), font=FONT_LABEL)


def draw_wave_strip(draw: ImageDraw.ImageDraw, mode: str, title: str, kind: str) -> None:
    x0, y0, x1, y1 = INSET
    draw.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=(248, 250, 252, 220), outline=(203, 213, 225), width=3)
    draw.line((x0 + 185, y0 + 190, x1 - 70, y0 + 190), fill=(132, 145, 165), width=3)
    draw.text((x0 + 38, y0 + 30), title, fill=(15, 23, 42), font=FONT_TITLE)
    draw.text((x0 + 38, y0 + 84), kind, fill=(71, 85, 105), font=FONT_LABEL)

    particle_pts = []
    center = y0 + 205
    amp = 100
    for i in range(240):
        t = i / 239
        _, u = pressure_particle(mode, t)
        xx = x0 + 185 + t * (x1 - x0 - 255)
        particle_pts.append((xx, center - amp * u))

    draw.line(particle_pts, fill=(225, 29, 72), width=10, joint="curve")
    draw.line(particle_pts, fill=(255, 255, 255), width=3, joint="curve")

    draw.text((x0 + 185, y0 + 295), "highlighted: particle-motion guide", fill=(190, 18, 60), font=FONT_SMALL)
    draw.text((x1 - 170, y0 + 295), "0-50 cm", fill=(71, 85, 105), font=FONT_SMALL)


def make_one(freq: int, meta: dict[str, object]) -> None:
    src = RAW_BEAD_DIR / str(meta["src"])
    photo = Image.open(src).convert("RGB").crop(PHOTO_CROP).resize(PHOTO_SIZE, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", OUT_SIZE, (255, 255, 255, 255))
    canvas.paste(photo.convert("RGBA"), (0, 0))

    overlay = Image.new("RGBA", OUT_SIZE, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    draw_cluster_outline(od, meta["clusters"])  # type: ignore[arg-type]
    draw_photo_wave(od, str(meta["mode"]))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(canvas)
    draw_wave_strip(draw, str(meta["mode"]), str(meta["title"]), str(meta["kind"]))
    canvas.convert("RGB").save(FIG_DIR / str(meta["out"]), quality=95)
    print(FIG_DIR / str(meta["out"]))


def main() -> None:
    for freq, meta in FREQ_META.items():
        make_one(freq, meta)


if __name__ == "__main__":
    main()
