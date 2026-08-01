from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
INK = (38, 47, 55)
CARD = (248, 246, 240, 255)
FRAME = (148, 126, 91)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def draw_wrapped(draw, text, x, y, width, text_font, line_gap=10):
    lines = []
    current = ""
    for char in text:
        trial = current + char
        if current and draw.textlength(trial, font=text_font) > width:
            lines.append(current)
            current = char
        else:
            current = trial
    if current:
        lines.append(current)
    line_height = text_font.size + line_gap
    for line in lines:
        draw.text((x, y), line, font=text_font, fill=INK)
        y += line_height
    return y


def make_slide(number, title, bullets, caption, art_box):
    source = ROOT / f"漢堡之光：麥斯特・伯特蘭與北德藝術_slide_{number}.png"
    output = ROOT / f"漢堡之光：麥斯特・伯特蘭與北德藝術_slide_{number}_reflow.png"
    image = Image.open(source).convert("RGBA")
    artwork = image.crop(art_box)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((84, 48, 1197, 655), radius=14, fill=CARD)
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    draw.text((128, 82), title, font=font(42), fill=INK)

    body = font(29)
    y = 176
    for bullet in bullets:
        draw.ellipse((130, y + 11, 141, y + 22), fill=INK)
        y = draw_wrapped(draw, bullet, 158, y, 470, body, line_gap=12) + 14

    target_w = 470
    target_h = round(artwork.height * target_w / artwork.width)
    artwork = artwork.resize((target_w, target_h), Image.Resampling.LANCZOS)
    art_x = 677
    art_y = 270
    pad = 10
    draw.rounded_rectangle(
        (art_x - pad, art_y - pad, art_x + target_w + pad, art_y + target_h + pad),
        radius=9,
        fill=(247, 244, 237),
        outline=FRAME,
        width=2,
    )
    image.alpha_composite(artwork, (art_x, art_y))
    cap_font = font(21)
    cap_w = draw.textlength(caption, font=cap_font)
    draw.text((art_x + (target_w - cap_w) / 2, art_y + target_h + 25), caption, font=cap_font, fill=(65, 64, 60))

    image.convert("RGB").save(output, quality=95)
    return output


make_slide(
    "0017",
    "材料判讀：不只是「油畫」",
    [
        "漢堡美術館將《格拉博祭壇屏》描述為：含油性黏結劑，橡木板載體。",
        "這是材料鑑定用語，不宜直接簡化為現代意義的純油畫，也不應在缺乏檢測依據下逕稱蛋彩。",
    ],
    "《格拉博祭壇屏》畫板群",
    (682, 315, 1125, 424),
)

make_slide(
    "0018",
    "大師、工作室與藝術圈子",
    [
        "中世紀大型祭壇多由畫家、雕刻師、木匠與貼金師協作完成。",
        "《布克斯特胡德祭壇屏》等作品與伯特蘭傳統密切相關，但現代研究多審慎歸為他的工作室、藝術圈子或後繼者。",
    ],
    "《布克斯特胡德祭壇屏》",
    (681, 314, 1125, 439),
)
