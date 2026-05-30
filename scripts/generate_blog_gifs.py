from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "homepage" / "static" / "homepage" / "blog"

BG_TOP = (11, 30, 72)
BG_BOTTOM = (3, 10, 28)
INK = (237, 246, 255)
MUTED = (171, 190, 224)
CYAN = (77, 211, 255)
GREEN = (172, 240, 134)
PURPLE = (188, 104, 255)
RED = (255, 106, 119)
AMBER = (255, 211, 162)
TOKEN_BG = (7, 24, 55)
TOKEN_UNKNOWN_BG = (48, 24, 92)
TOKEN_GREEN_BG = (18, 68, 52)
TOKEN_RED_BG = (84, 30, 40)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TOKEN = font(54)


def lerp(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def gradient_background(width: int, height: int) -> Image.Image:
    img = Image.new("RGB", (width, height), BG_BOTTOM)
    pix = img.load()
    for y in range(height):
        ty = y / max(1, height - 1)
        for x in range(width):
            tx = x / max(1, width - 1)
            wave = 0.08 * (1 - tx) + 0.06 * (1 - ty)
            r = lerp(BG_TOP[0], BG_BOTTOM[0], ty) + round(24 * wave)
            g = lerp(BG_TOP[1], BG_BOTTOM[1], ty) + round(36 * wave)
            b = lerp(BG_TOP[2], BG_BOTTOM[2], ty) + round(80 * wave)
            pix[x, y] = (min(r, 255), min(g, 255), min(b, 255))
    return img


def add_panel(img: Image.Image, margin: int = 22) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    box = (margin, margin, img.width - margin, img.height - margin)
    draw.rounded_rectangle(box, radius=28, fill=(2, 10, 28, 190), outline=(77, 211, 255, 90), width=3)
    draw.line((margin + 28, margin + 38, img.width - margin - 28, margin + 38), fill=(77, 211, 255, 150), width=4)
    img.alpha_composite(layer)


def token_style(kind: str) -> tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]:
    if kind == "unknown":
        return TOKEN_UNKNOWN_BG, PURPLE, (216, 180, 255)
    if kind == "green":
        return TOKEN_GREEN_BG, GREEN, (232, 255, 219)
    if kind == "red":
        return TOKEN_RED_BG, RED, (255, 225, 228)
    if kind == "muted":
        return (16, 25, 48), (86, 117, 153), MUTED
    return TOKEN_BG, CYAN, INK


def draw_token(
    img: Image.Image,
    box: tuple[int, int, int, int],
    text: str,
    kind: str,
    *,
    active: bool = False,
) -> None:
    fill, outline, text_color = token_style(kind)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(box, radius=22, fill=(*outline, 95 if active else 50))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12 if active else 8))
    img.alpha_composite(shadow)

    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=22, fill=(*fill, 244), outline=(*outline, 235), width=4)
    inner = (box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 4)
    draw.rounded_rectangle(inner, radius=18, outline=(255, 255, 255, 28), width=2)

    max_w = box[2] - box[0] - 30
    size = 54
    local_font = FONT_TOKEN
    while size > 34:
        local_font = font(size)
        bbox = draw.textbbox((0, 0), text, font=local_font)
        if bbox[2] - bbox[0] <= max_w:
            break
        size -= 2
    bbox = draw.textbbox((0, 0), text, font=local_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = box[0] + (box[2] - box[0] - tw) / 2 - bbox[0]
    y = box[1] + (box[3] - box[1] - th) / 2 - bbox[1] - 2
    draw.text((x, y), text, font=local_font, fill=text_color)


def row_boxes(width: int, count: int, *, token_w: int = 218, token_h: int = 108, y: int = 88) -> list[tuple[int, int, int, int]]:
    gap = 24
    total = count * token_w + (count - 1) * gap
    x0 = (width - total) // 2
    return [(x0 + i * (token_w + gap), y, x0 + i * (token_w + gap) + token_w, y + token_h) for i in range(count)]


def draw_row(tokens: list[str], kinds: list[str], *, width: int = 1400, height: int = 280, y: int = 94) -> Image.Image:
    img = gradient_background(width, height).convert("RGBA")
    add_panel(img)
    for box, text, kind in zip(row_boxes(width, len(tokens), y=y), tokens, kinds):
        draw_token(img, box, text, kind, active=kind in {"green", "red"})
    return img


def save_gif(path: Path, frames: list[Image.Image], durations: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    palette_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for frame in frames]
    palette_frames[0].save(
        path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )


def generation_gifs() -> None:
    unknown = ["unknown"] * 5
    save_gif(
        OUT / "idlm-autoregressive-generation.gif",
        [
            draw_row(["The", "?", "?", "?", "?"], ["green", *unknown[1:]]),
            draw_row(["The", "small", "?", "?", "?"], ["green", "green", "unknown", "unknown", "unknown"]),
            draw_row(["The", "small", "cat", "?", "?"], ["green", "green", "green", "unknown", "unknown"]),
            draw_row(["The", "small", "cat", "sat", "?"], ["green", "green", "green", "green", "unknown"]),
            draw_row(["The", "small", "cat", "sat", "down"], ["green"] * 5),
        ],
        [520, 560, 560, 560, 1150],
    )

    save_gif(
        OUT / "idlm-diffusion-generation.gif",
        [
            draw_row(["?", "?", "?", "?", "?"], ["unknown"] * 5),
            draw_row(["The", "?", "cat", "?", "down"], ["green", "unknown", "green", "unknown", "green"]),
            draw_row(["The", "small", "cat", "?", "down"], ["green", "green", "green", "unknown", "green"]),
            draw_row(["The", "small", "cat", "sat", "down"], ["green"] * 5),
        ],
        [620, 680, 680, 1300],
    )


def draw_factor_row(tokens: list[str], kinds: list[str], *, connector: str | None = None) -> Image.Image:
    img = draw_row(tokens, kinds, width=1400, height=360, y=126)
    boxes = row_boxes(1400, len(tokens), y=126)
    draw = ImageDraw.Draw(img)
    if connector == "bad":
        x1 = (boxes[1][0] + boxes[1][2]) // 2
        x2 = (boxes[2][0] + boxes[2][2]) // 2
        y = boxes[1][1] - 34
        draw.line((x1, y, x2, y), fill=(*RED, 230), width=5)
        draw.line((x2 - 15, y - 15, x2 + 15, y + 15), fill=(*RED, 240), width=5)
        draw.line((x2 + 15, y - 15, x2 - 15, y + 15), fill=(*RED, 240), width=5)
    elif connector == "good":
        x1 = (boxes[1][0] + boxes[1][2]) // 2
        x2 = (boxes[2][0] + boxes[2][2]) // 2
        y = boxes[1][1] - 34
        draw.line((x1, y, x2, y), fill=(*GREEN, 230), width=5)
        draw.line((x2 - 18, y - 2, x2 - 6, y + 12), fill=(*GREEN, 240), width=5)
        draw.line((x2 - 6, y + 12, x2 + 18, y - 16), fill=(*GREEN, 240), width=5)
    return img


def factorization_gifs() -> None:
    save_gif(
        OUT / "idlm-factorization-large-step.gif",
        [
            draw_factor_row(["The", "?", "?", "sleepy", "."], ["green", "unknown", "unknown", "muted", "muted"]),
            draw_factor_row(["The", "cat", "?", "sleepy", "."], ["green", "green", "unknown", "muted", "muted"]),
            draw_factor_row(["The", "cat", "are", "sleepy", "."], ["green", "green", "red", "muted", "muted"]),
            draw_factor_row(["The", "cat", "are", "sleepy", "."], ["green", "green", "red", "muted", "muted"], connector="bad"),
        ],
        [620, 660, 760, 980],
    )

    save_gif(
        OUT / "idlm-factorization-small-steps.gif",
        [
            draw_factor_row(["The", "?", "?", "sleepy", "."], ["green", "unknown", "unknown", "muted", "muted"]),
            draw_factor_row(["The", "cat", "?", "sleepy", "."], ["green", "green", "unknown", "muted", "muted"]),
            draw_factor_row(["The", "cat", "is", "sleepy", "."], ["green", "green", "green", "muted", "muted"]),
            draw_factor_row(["The", "cat", "is", "sleepy", "."], ["green", "green", "green", "muted", "muted"], connector="good"),
        ],
        [620, 660, 760, 980],
    )


def main() -> None:
    generation_gifs()
    factorization_gifs()


if __name__ == "__main__":
    main()
