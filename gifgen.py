from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
    
_Title_Font = ImageFont.truetype("fonts/megan_serif/Megan_Serif.ttf", 15)
_Body_Font = ImageFont.truetype("fonts/bm_mini/BMmini.TTF", 15)
_Background = Image.open("templates/template.webp")
_Foreground_Color = (90, 85, 89)


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


def _draw_fields(base, title, outcome, reason):
    im = base.copy()
    d = ImageDraw.Draw(im)
    W = im.width
    H = im.height

    d.fontmode = "1" # ensure crisp text rendering without anti-aliasing
    d.text((20, 7), title, font=_Title_Font, fill=_Foreground_Color)

    # wrap reason
    max_w = W - 60
    lines = []
    for line in reason.splitlines():
        words = line.split()
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if _text_size(d, test, _Body_Font)[0] <= max_w:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

    # start of the body text
    y = 40
    for line in lines:
        d.text((20, y), line, font=_Body_Font, fill=_Foreground_Color)
        y += 20
    _, _, w, h = d.textbbox((20, 120), outcome, font=_Body_Font)
    d.text(((W-w)/2, 115+(H-h)/2), outcome, font=_Body_Font, fill=_Foreground_Color)
    return im


def generate_frames(doc, start_y, target_y, time=28):
    frames = []

    # animate the document floating in from below to its final position
    # we animate across the full `time` frames using an ease-out curve
    for t in range(time):
        f = doc.copy().convert('RGBA')
        base_layer = Image.new('RGBA', f.size, (0,0,0,0))
        layer = Image.new('RGBA', f.size, (0,0,0,0))

        progress = t / float(max(1, time - 1))
        # ease-out movement
        ease = 1 - (1 - progress) ** 2
        y = int(start_y - ease * (start_y - target_y))

        ox = 0
        oy = y

        # paste the document at the computed vertical offset so it "floats" in
        layer.paste(f, (ox, oy), f)

        out = Image.alpha_composite(base_layer, layer)

        frames.append(out)
    return frames

def generate_citation_gif(title, penalty, reason):
    base = _Background
    doc = _draw_fields(base, title, penalty, reason)

    frames = []

    frames.extend(generate_frames(doc,
                                  start_y=doc.height,
                                  target_y=int(doc.height*3/5),
                                  time=10))
    
    frames.extend(generate_frames(doc,
                                  start_y=int(doc.height*3/5),
                                  target_y=int(doc.height*2/5),
                                  time=10))
    
    frames.extend(generate_frames(doc,
                                  start_y=int(doc.height*2/5),
                                  target_y=int(doc.height*1/5),
                                  time=10))
    
    frames.extend(generate_frames(doc,
                                  start_y=int(doc.height*1/5),
                                  target_y=0,
                                  time=10))

    # hold final
    for i in range(10):
        frames.append(frames[-1])

    # save to BytesIO
    bio = BytesIO()
    frames[0].save(bio, format='GIF', save_all=True, append_images=frames[1:], duration=100, loop=0, disposal=2)
    bio.seek(0)
    return bio
