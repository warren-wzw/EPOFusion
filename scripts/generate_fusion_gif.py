"""Regenerate the README preview with Pillow (python -m pip install Pillow).

Use full per-frame 256-color palettes to preserve photographic colors.
The website continues to use the original PNG files.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "ivoe"
CARD_WIDTH = 960
GAP = 24
STEP = 48
FRAME_DURATION_MS = 160


def main():
    paths = sorted(ASSETS.glob("[0-9][0-9]_*.png"))
    if len(paths) != 4:
        raise ValueError("Expected four source comparison PNGs")
    height = round(CARD_WIDTH * 1096 / 3392)
    strip_width = (CARD_WIDTH + GAP) * len(paths)
    strip = Image.new("RGB", (strip_width + CARD_WIDTH, height), "white")
    for index, path in enumerate(paths):
        with Image.open(path) as source:
            resized = source.convert("RGB").resize(
                (CARD_WIDTH, height), Image.Resampling.LANCZOS
            )
        strip.paste(resized, (index * (CARD_WIDTH + GAP), 0))
    strip.paste(strip.crop((0, 0, CARD_WIDTH, height)), (strip_width, 0))

    frames = []
    for offset in range(0, strip_width, STEP):
        original = strip.crop((offset, 0, offset + CARD_WIDTH, height))
        # Each frame gets all 256 colors, instead of sharing a tiny palette
        # across four scenes. Median-cut quantization preserves subtle tones.
        frame = original.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        frames.append(frame)

    output = ASSETS / "fusion_comparison.gif"
    frames[0].save(
        output, save_all=True, append_images=frames[1:],
        duration=FRAME_DURATION_MS, loop=0, optimize=False, disposal=1,
    )
    with Image.open(output) as decoded:
        assert decoded.n_frames == len(frames)
        assert decoded.info["loop"] == 0
        errors = []
        for index in range(decoded.n_frames):
            decoded.seek(index)
            offset = index * STEP
            original = strip.crop((offset, 0, offset + CARD_WIDTH, height))
            actual = decoded.convert("RGB")
            error = ImageStat.Stat(ImageChops.difference(original, actual)).mean
            errors.append(sum(error) / 3)
            # Save four original/decoded pairs for visual comparison outside the repo.
            if index in (0, 20, 41, 61):
                comparison = Image.new("RGB", (CARD_WIDTH, height * 2 + 12), "white")
                comparison.paste(original, (0, 0))
                comparison.paste(actual, (0, height + 12))
                comparison.save(Path("/tmp") / f"epofusion-color-check-{index}.png")
        print(f"{decoded.size}, {decoded.n_frames} frames, {output.stat().st_size / 1024**2:.2f} MiB")
        print(f"Decoded RGB mean absolute error: {sum(errors)/len(errors):.2f}/255; worst frame: {max(errors):.2f}/255")


if __name__ == "__main__":
    main()
