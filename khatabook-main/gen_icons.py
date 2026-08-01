from PIL import Image, ImageDraw, ImageFont

TEAL = (14, 124, 116, 255)
WHITE = (255, 255, 255, 255)


def make_icon(size, path, maskable=False, corner_ratio=0.22):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if maskable:
        # Full-bleed background, safe zone icon (maskable requires no transparent edges)
        draw.rectangle([0, 0, size, size], fill=TEAL)
        scale = 0.6
    else:
        radius = int(size * corner_ratio)
        draw.rounded_rectangle([0, 0, size, size], radius=radius, fill=TEAL)
        scale = 0.56

    # Draw a rupee glyph, bold, centered
    font_size = int(size * scale)
    font = None
    for fp in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        try:
            font = ImageFont.truetype(fp, font_size)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    text = "\u20b9"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) / 2 - bbox[0]
    y = (size - th) / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=WHITE)

    img.save(path)


make_icon(192, "static/icons/icon-192.png")
make_icon(512, "static/icons/icon-512.png")
make_icon(512, "static/icons/icon-512-maskable.png", maskable=True)
print("done")
