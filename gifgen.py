from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
    
def _papers_please_font(size=20):
    return ImageFont.truetype("megan_serif/Megan_Serif.ttf", size)


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


def _make_paper():
    # w: 366 h: 160
    im = Image.open("template.webp")
    return im


def _draw_fields(base, title, outcome, reason):
    im = base.copy()
    d = ImageDraw.Draw(im)
    W = 366
    H = 160
    f_body = ImageFont.truetype("bm_mini/BMmini.TTF", 15)
    foreground = (90, 85, 89)

    d.fontmode = "1" # ensure crisp text rendering without anti-aliasing
    d.text((20, 7), title, font=_papers_please_font(15), fill=foreground)

    # wrap reason
    max_w = im.width - 60
    lines = []
    for line in reason.splitlines():
        words = line.split()
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

    # start of the body text
    y = 40
    print(lines)
    for line in lines:
        d.text((20, y), line, font=f_body, fill=foreground)
        y += 20
    _, _, w, h = d.textbbox((20, 120), outcome, font=f_body)
    d.text(((W-w)/2, 115+(H-h)/2), outcome, font=f_body, fill=foreground)
    return im


def _make_square(size=200, color=(160,10,10,255), border=8):
    """Return a square image with transparent background and colored square (with optional border)."""
    im = Image.new('RGBA', (size, size), (0,0,0,0))
    d = ImageDraw.Draw(im)
    # outer filled square
    d.rectangle([ (0,0), (size, size) ], fill=color)
    # inner transparent center to create a hollow-ish look if border > 0
    if border and border*2 < size:
        d.rectangle([ (border, border), (size-border-1, size-border-1) ], fill=(0,0,0,0))
    return im


def generate_citation_gif(title, penalty, reason):
    base = _make_paper()
    doc = _draw_fields(base, title, penalty, reason)

    # create a solid square (we ignore the text for this visual effect)
    square_size = int(min(doc.width, doc.height) * 0.28)
    square = _make_square(square_size, color=(160,10,10,255), border=6)

    frames = []

    # animation parameters
    total = 28
    start_y = doc.height + square.height  # well below the frame
    target_y = int(doc.height/2 - square.height/2)
    center_x = int((doc.width - square.width) / 2)

    # first easing
    for t in range(total):
        f = doc.copy().convert('RGBA')
        layer = Image.new('RGBA', f.size, (0,0,0,0))

        progress = t / float(max(1, total-1))
        # ease-out movement
        ease = 1 - (1 - progress)**2
        y = int(start_y - ease * (start_y - target_y))

        ox = center_x
        oy = y

        # prepare square with adjusted alpha
        # sq = square.copy()

        # layer.paste(sq, (ox, oy), sq)

        out = Image.alpha_composite(f, layer)

        frames.append(out)

    # hold final
    for i in range(10):
        frames.append(frames[-1])

    # save to BytesIO
    bio = BytesIO()
    frames[0].save(bio, format='GIF', save_all=True, append_images=frames[1:], duration=80, loop=0, disposal=2)
    bio.seek(0)
    return bio
