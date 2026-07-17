#!/usr/bin/env python3
"""Resize an image to 1024x564 and overlay an exact, readable video title."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


WIDTH = 1024
HEIGHT = 564


def find_font(explicit: str | None) -> str:
    candidates = [
        explicit,
        r"C:\Windows\Fonts\msjhbd.ttc",
        r"C:\Windows\Fonts\msjh.ttc",
        r"C:\Windows\Fonts\mingliu.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise FileNotFoundError(
        "No CJK font found. Pass --font with a Traditional Chinese-capable font."
    )


def split_title(title: str) -> tuple[str, str]:
    for separator in (" - ", " — ", " – ", "：", ":"):
        if separator in title:
            primary, secondary = title.split(separator, 1)
            visible_separator = separator.strip()
            joiner = " " if visible_separator in {"-", "—", "–"} else ""
            return primary.strip(), f"{visible_separator}{joiner}{secondary.strip()}"
    return title.strip(), ""


def wrap_chars(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    if not text:
        return []
    if " " in text:
        lines: list[str] = []
        current = ""
        for word in text.split():
            candidate = f"{current} {word}".strip()
            if current and draw.textlength(candidate, font=font) > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if current and draw.textlength(candidate, font=font) > max_width:
            lines.append(current.rstrip())
            current = char.lstrip()
        else:
            current = candidate
    if current:
        lines.append(current.rstrip())
    return lines


def layout_title(
    draw: ImageDraw.ImageDraw,
    title: str,
    font_path: str,
    box_width: int,
    box_height: int,
) -> tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont, list[str], list[str], int]:
    primary, secondary = split_title(title)
    for secondary_size in range(54, 25, -2):
        primary_font = ImageFont.truetype(font_path, int(secondary_size * 1.18))
        secondary_font = ImageFont.truetype(font_path, secondary_size)
        primary_lines = wrap_chars(draw, primary, primary_font, box_width)
        secondary_lines = wrap_chars(draw, secondary, secondary_font, box_width)
        if len(primary_lines) > 1:
            continue
        primary_step = int(primary_font.size * 1.18)
        secondary_step = int(secondary_font.size * 1.22)
        gap = max(12, secondary_size // 2) if secondary_lines else 0
        total_height = len(primary_lines) * primary_step + gap + len(secondary_lines) * secondary_step
        if total_height <= box_height:
            return primary_font, secondary_font, primary_lines, secondary_lines, gap
    raise ValueError("Title is too long to fit the thumbnail safely.")


def draw_title(image: Image.Image, title: str, font_path: str, side: str) -> Image.Image:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    margin = 34
    panel_width = 560
    panel_height = 466
    x0 = WIDTH - panel_width - margin if side == "right" else margin
    y0 = (HEIGHT - panel_height) // 2
    x1 = x0 + panel_width
    y1 = y0 + panel_height
    draw.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=(12, 10, 8, 178), outline=(218, 170, 78, 115), width=2)

    inner_x = x0 + 30
    inner_y = y0 + 30
    inner_width = panel_width - 60
    inner_height = panel_height - 60
    primary_font, secondary_font, primary_lines, secondary_lines, gap = layout_title(
        draw, title, font_path, inner_width, inner_height
    )

    primary_step = int(primary_font.size * 1.18)
    secondary_step = int(secondary_font.size * 1.22)
    total_height = len(primary_lines) * primary_step + gap + len(secondary_lines) * secondary_step
    y = inner_y + max(0, (inner_height - total_height) // 2)
    for line in primary_lines:
        draw.text(
            (inner_x, y),
            line,
            font=primary_font,
            fill=(244, 190, 76, 255),
            stroke_width=3,
            stroke_fill=(25, 16, 8, 255),
        )
        y += primary_step
    y += gap
    for line in secondary_lines:
        draw.text(
            (inner_x, y),
            line,
            font=secondary_font,
            fill=(255, 244, 213, 255),
            stroke_width=3,
            stroke_fill=(25, 16, 8, 255),
        )
        y += secondary_step

    return Image.alpha_composite(image.convert("RGBA"), overlay)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Generated source image")
    parser.add_argument("--output", required=True, help="Final PNG path")
    parser.add_argument("--title", required=True, help="Exact video title")
    parser.add_argument("--text-side", choices=("left", "right"), default="right")
    parser.add_argument("--font", help="Path to a CJK-capable TrueType/OpenType font")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.is_file():
        raise FileNotFoundError(f"Input image not found: {input_path}")
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {output_path}")

    font_path = find_font(args.font)
    with Image.open(input_path) as source:
        source = ImageOps.exif_transpose(source).convert("RGB")
        fitted = ImageOps.fit(source, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    final = draw_title(fitted, args.title, font_path, args.text_side).convert("RGB")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, format="PNG", optimize=True)
    print(f"Saved {output_path} ({final.width}x{final.height}) using {os.path.basename(font_path)}")


if __name__ == "__main__":
    main()
