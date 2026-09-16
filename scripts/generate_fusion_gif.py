"""Regenerate the README preview with Pillow (python -m pip install Pillow).

Preserve original PNGs; render a tight scrolling crop with one fixed label pair.
Use per-frame 256-color palettes, retaining the 39.36-second loop.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "ivoe"
CARD_WIDTH = 960
LABEL_WIDTH = 48
GAP = 5
FRAME_COUNT = 82
FRAME_DURATION_MS = 480
# Original images share this content area, excluding labels and outer whitespace.
CONTENT_BOX = (104, 40, 3368, 1056)


def main():
    paths = sorted(ASSETS.glob("[0-9][0-9]_*.png"))
    if len(paths) != 4:
        raise ValueError("Expected four source comparison PNGs")
    height = round(CARD_WIDTH * 1016 / 3264)
    strip_width = (CARD_WIDTH + GAP) * len(paths)
    strip = Image.new("RGB", (strip_width + CARD_WIDTH, height), "white")
    for index, path in enumerate(paths):
        with Image.open(path) as source:
            resized = source.convert("RGB").crop(CONTENT_BOX).resize(
                (CARD_WIDTH, height), Image.Resampling.LANCZOS
            )
        strip.paste(resized, (index * (CARD_WIDTH + GAP), 0))
    strip.paste(strip.crop((0, 0, CARD_WIDTH, height)), (strip_width, 0))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 12)
    except OSError:
        font = ImageFont.load_default()

    def render(index):
        offset = round(index * strip_width / FRAME_COUNT)
        original = Image.new("RGB", (CARD_WIDTH, height), "white")
        original.paste(strip.crop((offset, 0, offset + CARD_WIDTH - LABEL_WIDTH, height)), (LABEL_WIDTH, 0))
        draw = ImageDraw.Draw(original)
        for text, y in (("VI", 240 / 1016), ("Fusion", 776 / 1016)):
            draw.text((LABEL_WIDTH / 2, height * y), text, font=font, fill="#172033", anchor="mm")
        return original

    frames = [render(i).quantize(colors=256, method=Image.Quantize.MEDIANCUT) for i in range(FRAME_COUNT)]
    output = ASSETS / "fusion_comparison.gif"
    frames[0].save(
        output, save_all=True, append_images=frames[1:],
        duration=FRAME_DURATION_MS, loop=0, optimize=False, disposal=1,
    )
    with Image.open(output) as decoded:
        assert decoded.n_frames == FRAME_COUNT
        assert decoded.info["loop"] == 0
        errors = []
        duration = 0
        for index in range(decoded.n_frames):
            decoded.seek(index)
            duration += decoded.info["duration"]
            original = render(index)
            actual = decoded.convert("RGB")
            error = ImageStat.Stat(ImageChops.difference(original, actual)).mean
            errors.append(sum(error) / 3)
            if index in (0, 20, 41, 61):
                comparison = Image.new("RGB", (CARD_WIDTH, height * 2 + 12), "white")
                comparison.paste(original, (0, 0))
                comparison.paste(actual, (0, height + 12))
                comparison.save(Path("/tmp") / f"epofusion-color-check-{index}.png")
        assert duration == FRAME_COUNT * FRAME_DURATION_MS
        print(f"{decoded.size}, {decoded.n_frames} frames, {duration/1000:.2f}s, {output.stat().st_size / 1024**2:.2f} MiB")
        print(f"Decoded RGB mean absolute error: {sum(errors)/len(errors):.2f}/255; worst frame: {max(errors):.2f}/255")


if __name__ == "__main__":
    main()
