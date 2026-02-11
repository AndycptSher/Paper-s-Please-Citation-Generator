from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import math


def _load_font(size=20):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _text_size(draw, text, font):
    """Return (width, height) of text using available Pillow methods."""
    # Prefer ImageDraw.textbbox if available
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])
    except Exception:
        pass
    # Fallback to font.getsize
    try:
        return font.getsize(text)
    except Exception:
        pass
    # Last resort: try draw.textsize (older versions)
    try:
        return draw.textsize(text, font=font)
    except Exception:
        # give a rough estimate
        return (len(text) * (font.size if hasattr(font, 'size') else 10), int((font.size if hasattr(font, 'size') else 10) * 1.2))


def _make_paper(width=600, height=400):
    im = Image.new('RGBA', (width, height), (240, 235, 220, 255))
    d = ImageDraw.Draw(im)
    # subtle texture lines
    for y in range(20, height, 24):
        d.line([(10, y), (width-10, y)], fill=(230, 225, 200), width=1)
    return im


def _draw_fields(base, name, idnum, reason):
    im = base.copy()
    d = ImageDraw.Draw(im)
    f_title = _load_font(28)
    f_body = _load_font(18)

    d.text((30, 20), "CITATION", font=f_title, fill=(40, 40, 40))
    d.text((30, 70), f"Name: {name}", font=f_body, fill=(30, 30, 30))
    d.text((30, 110), f"ID: {idnum}", font=f_body, fill=(30, 30, 30))
    d.text((30, 150), "Reason:", font=f_body, fill=(30, 30, 30))

    # wrap reason
    max_w = im.width - 60
    lines = []
    words = reason.split()
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if _text_size(d, test, f_body)[0] <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    y = 180
    for line in lines:
        d.text((30, y), line, font=f_body, fill=(25, 25, 25))
        y += 26

    # signature box
    d.rectangle([ (im.width-220, im.height-110), (im.width-30, im.height-40) ], outline=(100,100,100))
    d.text((im.width-210, im.height-105), "Officer: Inspector", font=f_body, fill=(30,30,30))
    return im


def _make_stamp(stamp_text, size=200):
    im = Image.new('RGBA', (size, size), (0,0,0,0))
    d = ImageDraw.Draw(im)
    f = _load_font(int(size*0.18))
    # red circle
    d.ellipse((0,0,size,size), outline=(160,10,10), width=8)
    w, h = _text_size(d, stamp_text, f)
    d.text(((size-w)/2, (size-h)/2), stamp_text, font=f, fill=(160,10,10))
    # rotate a bit
    return im.rotate(-12, resample=Image.BICUBIC, expand=True)


def generate_citation_gif(name, idnum, reason, stamp_text):
    base = _make_paper()
    doc = _draw_fields(base, name, idnum, reason)

    stamp = _make_stamp(stamp_text.upper())

    frames = []
    # initial frames: no stamp
    for i in range(6):
        frames.append(doc.copy())

    # stamping animation: move stamp down and fade
    for t in range(12):
        f = doc.copy()
        ox = int((f.width - stamp.width) / 2)
        oy = int(f.height/2 - stamp.height/2 + t*6)
        layer = Image.new('RGBA', f.size, (0,0,0,0))
        layer.paste(stamp, (ox, oy), stamp)
        out = Image.alpha_composite(f.convert('RGBA'), layer)
        # slight blur on later frames
        if t > 6:
            out = out.filter(ImageFilter.GaussianBlur(radius=(t-6)/3))
        frames.append(out)

    # hold final
    for i in range(8):
        frames.append(frames[-1])

    # save to BytesIO
    bio = BytesIO()
    frames[0].save(bio, format='GIF', save_all=True, append_images=frames[1:], duration=80, loop=0, disposal=2)
    bio.seek(0)
    return bio
