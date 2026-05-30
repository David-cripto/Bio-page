from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "homepage" / "static" / "homepage" / "blog"

INK = (237, 246, 255)
MUTED = (172, 190, 222)
CYAN = (25, 198, 255)
GREEN = (172, 245, 132)
PURPLE = (190, 100, 255)
RED = (255, 99, 118)
AMBER = (255, 211, 162)

BLUE_FILL = (2, 16, 38)
GREEN_FILL = (20, 73, 45)
PURPLE_FILL = (48, 24, 91)
RED_FILL = (92, 29, 39)
MUTED_FILL = (13, 27, 53)
BG = (2, 8, 22)


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in [
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def background(width: int, height: int) -> Image.Image:
    img = Image.new("RGB", (width, height), BG)
    pix = img.load()
    for y in range(height):
        for x in range(width):
            stripe = 9 if x % 18 in {0, 1} else 0
            glow = max(0, 1 - abs((x / width) - 0.5) * 1.8) * 10
            pix[x, y] = (BG[0], min(30, BG[1] + stripe // 3), min(62, BG[2] + stripe + round(glow)))
    return img.convert("RGBA")


def style(kind: str) -> tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]:
    if kind == "active":
        return GREEN_FILL, GREEN, (230, 255, 220)
    if kind == "unknown":
        return PURPLE_FILL, PURPLE, (221, 184, 255)
    if kind == "bad":
        return RED_FILL, RED, (255, 228, 231)
    if kind == "muted":
        return MUTED_FILL, (93, 128, 174), MUTED
    return BLUE_FILL, CYAN, INK


def draw_text_centered(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    *,
    fill: tuple[int, int, int],
    size: int,
    max_pad: int = 34,
) -> None:
    local_font = font(size)
    max_w = box[2] - box[0] - max_pad
    while size > 26:
        local_font = font(size)
        bbox = draw.textbbox((0, 0), text, font=local_font)
        if bbox[2] - bbox[0] <= max_w:
            break
        size -= 2
    bbox = draw.textbbox((0, 0), text, font=local_font)
    x = box[0] + (box[2] - box[0] - (bbox[2] - bbox[0])) / 2 - bbox[0]
    y = box[1] + (box[3] - box[1] - (bbox[3] - bbox[1])) / 2 - bbox[1] - 2
    draw.text((x, y), text, font=local_font, fill=fill)


def draw_token(
    img: Image.Image,
    box: tuple[int, int, int, int],
    text: str,
    kind: str,
    *,
    focus: bool = False,
    font_size: int = 50,
) -> None:
    fill, outline, text_color = style(kind)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(box, radius=23, fill=(*outline, 74 if kind == "active" else 38))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))

    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=23, fill=(*fill, 244), outline=(*outline, 245), width=4)
    draw.rounded_rectangle((box[0] + 5, box[1] + 5, box[2] - 5, box[3] - 5), radius=18, outline=(255, 255, 255, 26), width=2)
    if focus:
        draw.rounded_rectangle((box[0] - 7, box[1] - 7, box[2] + 7, box[3] + 7), radius=28, outline=(*outline, 210), width=4)
    draw_text_centered(draw, box, text, fill=text_color, size=font_size)


def generation_boxes(width: int) -> list[tuple[int, int, int, int]]:
    token_w = 240
    token_h = 108
    gap = 34
    y = 92
    total = 5 * token_w + 4 * gap
    x0 = (width - total) // 2
    return [(x0 + i * (token_w + gap), y, x0 + i * (token_w + gap) + token_w, y + token_h) for i in range(5)]


def draw_generation_frame(tokens: list[str], kinds: list[str]) -> Image.Image:
    img = background(1400, 295)
    for box, text, kind in zip(generation_boxes(1400), tokens, kinds):
        draw_token(img, box, text, kind, font_size=52)
    return img


def draw_panel(img: Image.Image) -> None:
    draw = ImageDraw.Draw(img)
    box = (26, 26, img.width - 26, img.height - 26)
    draw.rounded_rectangle(box, radius=32, fill=(3, 15, 36, 232), outline=(*CYAN, 205), width=3)


def factor_boxes(width: int) -> list[tuple[int, int, int, int]]:
    token_w = 270
    token_h = 108
    gap = 28
    y = 196
    total = 4 * token_w + 3 * gap
    x0 = (width - total) // 2
    return [(x0 + i * (token_w + gap), y, x0 + i * (token_w + gap) + token_w, y + token_h) for i in range(4)]


def pill(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, color: tuple[int, int, int]) -> None:
    small = font(24)
    bbox = draw.textbbox((0, 0), text, font=small)
    box = (x, y, x + bbox[2] - bbox[0] + 34, y + 44)
    draw.rounded_rectangle(box, radius=20, fill=(3, 15, 36), outline=(*color, 230), width=2)
    draw.text((x + 17, y + 10), text, font=small, fill=color)


def arc_between(
    draw: ImageDraw.ImageDraw,
    boxes: list[tuple[int, int, int, int]],
    *,
    color: tuple[int, int, int],
    broken: bool = False,
) -> None:
    x1 = (boxes[1][0] + boxes[1][2]) // 2
    x2 = (boxes[2][0] + boxes[2][2]) // 2
    y = boxes[1][1] - 68
    draw.arc((x1, y - 74, x2, y + 74), 205, 335, fill=(*color, 230), width=7)
    draw.ellipse((x1 - 10, boxes[1][1] - 15, x1 + 10, boxes[1][1] + 5), fill=(*color, 230))
    draw.ellipse((x2 - 10, boxes[2][1] - 15, x2 + 10, boxes[2][1] + 5), fill=(*color, 230))
    if broken:
        cx = (x1 + x2) // 2
        cy = y + 4
        draw.line((cx - 17, cy - 17, cx + 17, cy + 17), fill=(*RED, 255), width=7)
        draw.line((cx + 17, cy - 17, cx - 17, cy + 17), fill=(*RED, 255), width=7)


def noun_verb_labels(draw: ImageDraw.ImageDraw, boxes: list[tuple[int, int, int, int]]) -> None:
    label_font = font(24)
    for idx, label in [(1, "noun"), (2, "verb")]:
        cx = (boxes[idx][0] + boxes[idx][2]) // 2
        box = (cx - 92, boxes[idx][1] - 96, cx + 92, boxes[idx][1] - 42)
        draw.rounded_rectangle(box, radius=14, fill=(4, 32, 66), outline=(*CYAN, 230), width=2)
        draw_text_centered(draw, box, label, fill=CYAN, size=24, max_pad=20)
        draw.polygon([(cx - 10, boxes[idx][1] - 32), (cx + 10, boxes[idx][1] - 32), (cx, boxes[idx][1] - 12)], fill=CYAN)


def draw_factor_frame(
    tokens: list[str],
    kinds: list[str],
    *,
    label: str,
    label_color: tuple[int, int, int],
    arc: tuple[int, int, int] | None = None,
    broken_arc: bool = False,
    noun_labels: bool = False,
    focus_index: int | None = None,
    underline_bad: bool = False,
) -> Image.Image:
    img = background(1400, 424)
    draw_panel(img)
    draw = ImageDraw.Draw(img)
    boxes = factor_boxes(1400)
    pill(draw, label, 78, 58, label_color)
    if arc is not None:
        arc_between(draw, boxes, color=arc, broken=broken_arc)
    if noun_labels:
        noun_verb_labels(draw, boxes)
    for i, (box, text, kind) in enumerate(zip(boxes, tokens, kinds)):
        draw_token(img, box, text, kind, focus=i == focus_index, font_size=46)
    if underline_bad:
        y = boxes[1][3] + 22
        draw.line((boxes[1][0] + 36, y, boxes[2][2] - 36, y), fill=(*RED, 255), width=6)
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
    save_gif(
        OUT / "idlm-autoregressive-generation.gif",
        [
            draw_generation_frame(["The", "?", "?", "?", "?"], ["active", "unknown", "unknown", "unknown", "unknown"]),
            draw_generation_frame(["The", "small", "?", "?", "?"], ["settled", "active", "unknown", "unknown", "unknown"]),
            draw_generation_frame(["The", "small", "cat", "?", "?"], ["settled", "settled", "active", "unknown", "unknown"]),
            draw_generation_frame(["The", "small", "cat", "sat", "?"], ["settled", "settled", "settled", "active", "unknown"]),
            draw_generation_frame(["The", "small", "cat", "sat", "down"], ["settled", "settled", "settled", "settled", "active"]),
        ],
        [900, 980, 980, 980, 1700],
    )
    save_gif(
        OUT / "idlm-diffusion-generation.gif",
        [
            draw_generation_frame(["?", "?", "?", "?", "?"], ["unknown"] * 5),
            draw_generation_frame(["The", "?", "cat", "?", "down"], ["active", "unknown", "active", "unknown", "active"]),
            draw_generation_frame(["The", "?", "cat", "?", "down"], ["settled", "unknown", "settled", "unknown", "settled"]),
            draw_generation_frame(["The", "small", "cat", "sat", "down"], ["settled", "active", "settled", "active", "settled"]),
            draw_generation_frame(["The", "small", "cat", "sat", "down"], ["settled"] * 5),
        ],
        [900, 980, 980, 980, 1700],
    )


def factorization_gifs() -> None:
    first = draw_factor_frame(
        ["The", "?", "?", "sleeping"],
        ["muted", "unknown", "unknown", "muted"],
        label="two linked blanks",
        label_color=AMBER,
        arc=CYAN,
    )
    save_gif(
        OUT / "idlm-factorization-large-step.gif",
        [
            first,
            draw_factor_frame(
                ["The", "?", "?", "sleeping"],
                ["muted", "unknown", "unknown", "muted"],
                label="factorized large jump",
                label_color=AMBER,
                noun_labels=True,
            ),
            draw_factor_frame(
                ["The", "cat", "are", "sleeping"],
                ["active", "bad", "bad", "active"],
                label="sampled independently",
                label_color=AMBER,
                arc=RED,
                broken_arc=True,
            ),
            draw_factor_frame(
                ["The", "cat", "are", "sleeping"],
                ["active", "bad", "bad", "active"],
                label="inconsistent sentence",
                label_color=RED,
                arc=RED,
                broken_arc=True,
                underline_bad=True,
            ),
        ],
        [900, 1050, 1200, 1500],
    )
    save_gif(
        OUT / "idlm-factorization-small-steps.gif",
        [
            first,
            draw_factor_frame(
                ["The", "cat", "?", "sleeping"],
                ["active", "active", "unknown", "active"],
                label="small step: noun",
                label_color=AMBER,
                arc=CYAN,
                focus_index=1,
            ),
            draw_factor_frame(
                ["The", "cat", "is", "sleeping"],
                ["active", "active", "active", "active"],
                label="next step: verb",
                label_color=AMBER,
                arc=GREEN,
                focus_index=2,
            ),
            draw_factor_frame(
                ["The", "cat", "is", "sleeping"],
                ["active", "active", "active", "active"],
                label="consistent sentence",
                label_color=GREEN,
                arc=GREEN,
            ),
        ],
        [900, 1050, 1200, 1500],
    )


def main() -> None:
    generation_gifs()
    factorization_gifs()


if __name__ == "__main__":
    main()
