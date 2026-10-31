"""Render REV235 review assets from captured Web screenshots and approved copy.

Uses the existing local Pillow and imageio-ffmpeg tools, without adding runtime
dependencies. Inputs stay unchanged. Output is local and must not be uploaded to
AI11. Run from the repository root: python scripts/marketing/build_rev235.py
"""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageOps
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/ru/analytics/rev235"
OUTPUT = ROOT / "build/rev235"
FONT = ROOT / "assets/fonts/Arimo/Arimo.ttf"


def wrapped(draw: ImageDraw.ImageDraw, value: str, font, width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in value.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=font) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def render_video(story: dict) -> None:
    frames = OUTPUT / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    commands: list[str] = []
    for index, scene in enumerate(story["scenes"]):
        frame = Image.new("RGB", (1920, 1080), "#f7f3e7")
        draw = ImageDraw.Draw(frame)
        draw.text((84, 66), "REVELATION  /  1.0.8", font=ImageFont.truetype(str(FONT), 30), fill="#6d5e0f")
        draw.text((84, 140), f"{index+1:02d} / 06", font=ImageFont.truetype(str(FONT), 24), fill="#756d57")
        y = 215
        for line in wrapped(draw, scene["title"], ImageFont.truetype(str(FONT), 56), 610):
            draw.text((84, y), line, font=ImageFont.truetype(str(FONT), 56), fill="#302b20")
            y += 70
        y += 32
        for line in wrapped(draw, scene["caption"], ImageFont.truetype(str(FONT), 33), 610):
            draw.text((84, y), line, font=ImageFont.truetype(str(FONT), 33), fill="#5b5445")
            y += 45
        if y > 900:
            raise ValueError(f"Scene {index+1} caption overflows: {y}")
        screenshot = Image.open(OUTPUT / "screens" / scene["image"]).convert("RGB")
        screenshot = ImageOps.contain(screenshot, (1090, 800), Image.Resampling.LANCZOS)
        x, sy = 750 + (1090-screenshot.width)//2, 160 + (800-screenshot.height)//2
        draw.rounded_rectangle((x-2, sy-2, x+screenshot.width+2, sy+screenshot.height+2), radius=8, fill="#b6ab86")
        frame.paste(screenshot, (x, sy))
        draw.text((84, 965), "Демонстрація Revelation 1.0.8", font=ImageFont.truetype(str(FONT), 25), fill="#756d57")
        draw.text((750, 977), "Текст: Іван Огієнко, видання 1988. Джерело: uk.wikisource.org", font=ImageFont.truetype(str(FONT), 23), fill="#756d57")
        draw.text((750, 1012), "CC BY-SA 4.0 - creativecommons.org/licenses/by-sa/4.0/", font=ImageFont.truetype(str(FONT), 23), fill="#756d57")
        for part in range(6):
            px = 84 + part * 103
            draw.rounded_rectangle((px, 1020, px+88, 1026), radius=3, fill="#6d5e0f" if part <= index else "#d9d1ba")
        name = f"scene-{index+1:02d}.png"
        frame.save(frames / name)
        commands += [f"file 'frames/{name}'", f"duration {scene['end']-scene['start']}"]
    commands.append(f"file 'frames/{name}'")
    (OUTPUT / "video-input.txt").write_text("\n".join(commands)+"\n", encoding="utf-8")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with (OUTPUT / "video-render.log").open("w", encoding="utf-8") as log:
        subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", "video-input.txt", "-t", "60", "-vf", "fps=30,fade=t=in:st=0:d=0.4,fade=t=out:st=59.5:d=0.5", "-c:v", "libx264", "-threads", "2", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", "rev235-uk-reading.mp4"], cwd=OUTPUT, stdout=log, stderr=subprocess.STDOUT, check=True)
    sheet = Image.new("RGB", (1440, 540), "white")
    for i, path in enumerate(sorted(frames.glob("scene-*.png"))):
        sheet.paste(Image.open(path).resize((480, 270)), ((i % 3)*480, (i // 3)*270))
    sheet.save(OUTPUT / "storyboard-preview.jpg", quality=92)


def render_preview(copy: dict, experiment: dict) -> None:
    # Future website content is rendered as a local review artifact. Nothing is
    # inserted into the Flutter app or the separately deployed website.
    languages = "".join(f'<a href="#{lang}">{lang.upper()}</a>' for lang in copy["locales"])
    sections = []
    labels = {
        "uk": ("Опис для магазину", "Короткий допис", "Що змінилося"),
        "en": ("Store listing", "Short post", "Release notes"),
        "es": ("Descripción de la tienda", "Publicación breve", "Novedades"),
        "ru": ("Описание для магазина", "Короткий пост", "Что изменилось"),
    }
    for lang, item in copy["locales"].items():
        listing_label, post_label, notes_label = labels[lang]
        steps = "".join(f"<li>{html.escape(step)}</li>" for step in item["steps"])
        description = "".join(f"<p>{html.escape(p)}</p>" for p in item["description"].split("\n\n"))
        urls = dict(experiment["platform_links"])
        if lang == "uk":
            urls["windows"] = experiment["channels"][0]["windows_url"]
        links = "".join(f'<a class="platform" href="{html.escape(url)}">{name.title()}</a>' for name, url in urls.items())
        sections.append(f'<section id="{lang}" lang="{lang}"><p class="eyebrow">{lang.upper()} / REVELATION 1.0.8</p><h1>{html.escape(item["headline"])}</h1><p class="lead">{html.escape(item["lead"])}</p><img class="example" src="screens/parallel-uk.png" alt="OH1988 and LXX/TR in the Ukrainian Web interface"><ol>{steps}</ol><p>{links}</p><h2>{listing_label}</h2><p class="short">{html.escape(item["short_description"])}</p>{description}<h2>{post_label}</h2><p>{html.escape(item["post"])}</p><h2>{notes_label}</h2><p>{html.escape(item["release_notes"])}</p></section>')
    page = '''<!doctype html><html lang="uk"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>REV235 - Campaign review</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f7f3e7;color:#302b20;font:17px/1.65 Arial,sans-serif}nav{padding:18px 6%;border-bottom:1px solid #cfc5ab;display:flex;gap:22px;flex-wrap:wrap}main{max-width:1100px;margin:auto;padding:32px 24px}a{color:#6d5e0f}h1{font-size:clamp(30px,4vw,48px);line-height:1.12;max-width:880px}h2{font-size:24px;margin-top:32px}.notice{padding:20px 24px;background:#ece2c6;border-left:4px solid #6d5e0f}.eyebrow{letter-spacing:.12em;color:#6d5e0f;font-size:13px;font-weight:700}.lead{font-size:23px;max-width:900px}.example{display:block;max-width:100%;height:auto;border:1px solid #cfc5ab;border-radius:8px}video{width:100%;background:#302b20}.platform{display:inline-block;padding:8px 16px;margin:0 8px 10px 0;border:1px solid #9e916b;border-radius:4px;text-decoration:none}section{padding:26px 0 60px;border-bottom:1px solid #cfc5ab}.short{padding:12px 16px;background:#ebe5d5}li{margin:10px 0}</style>
    <nav><strong>REV235</strong>LANGUAGES</nav><main><div class="notice"><strong>Матеріали оновлено після REV299 і REV300. Не опубліковано.</strong><br>Кадри показують повний текст OH1988 data 2 та доступні для кожного модуля інструменти. Запуск кампанії - після REV301, приймання REV236, публікації REV237 і дозволу власника на розміщення. Публічний Web поки містить 1.0.7; український модуль у ньому ще не опублікований.</div><h2>60 секунд: Об'явлення 1:1-3 і примітка</h2><video controls preload="metadata" poster="frames/scene-01.png" src="rev235-uk-reading.mp4"></video><p>Текст: Іван Огієнко, ювілейне видання 1988 року. Джерело: <a href="https://uk.wikisource.org/wiki/Індекс:Ivan_Ohienko_Bible.djvu">Українські Вікіджерела</a>. <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Технічна нормалізація, реверсифікація та структурування виносок у модулі; скриншоти масштабовано у відео. Атрибуція не означає схвалення проєкту правовласниками або Wikimedia.</p><h2>Кадри для магазинів</h2><p>Справжній смартфон Android: 1080x2160, кадровано з 1080x2400 по прямокутнику (0, 104, 1080, 2264); оригінали 1080x2400 збережено. Windows: нативне вікно 1920x1032. Відео показує Web. Середовища не підміняються одне одним.</p><p><a href="store/android/reading-uk.png">Android: читання</a> · <a href="store/android/footnote-uk.png">Android: примітка</a> · <a href="store/windows/parallel-uk.png">Windows: паралельне читання</a> · <a href="store/windows/module-info-uk.png">Windows: інформація</a></p>SECTIONS</main></html>'''
    (OUTPUT / "preview.html").write_text(page.replace("LANGUAGES", languages).replace("SECTIONS", "\n".join(sections)), encoding="utf-8")


def main() -> None:
    copy = json.loads((SOURCE / "copy.json").read_text(encoding="utf-8"))
    story = json.loads((SOURCE / "storyboard.json").read_text(encoding="utf-8"))
    experiment = json.loads((SOURCE / "experiment.json").read_text(encoding="utf-8"))
    assert set(copy["locales"]) == {"en", "es", "uk", "ru"}
    assert len(experiment["channels"]) <= 2
    assert story["scenes"][0]["start"] == 0
    assert story["scenes"][-1]["end"] == story["duration_seconds"] == 60
    for lang, value in copy["locales"].items():
        assert len(value["short_description"]) <= 80, lang
        assert len(value["description"]) <= 4000, lang
    for scene, following in zip(story["scenes"], story["scenes"][1:]):
        assert scene["end"] == following["start"]
    provenance = json.loads((OUTPUT / "capture-provenance.json").read_text(encoding="utf-8"))
    module_hash = hashlib.sha256((ROOT / "web/db/bible_ohienko_1988.sqlite").read_bytes()).hexdigest()
    if provenance["module_sha256"] != module_hash or provenance["data_version"] != 2:
        raise ValueError("Capture provenance does not match the accepted OH1988 data 2")
    captured = {item["file"] for item in provenance["screenshots"]}
    required = {f"screens/{scene['image']}" for scene in story["scenes"]}
    if not required <= captured:
        raise ValueError("A video scene is missing from the capture provenance")
    for item in provenance["screenshots"]:
        if hashlib.sha256((OUTPUT / item["file"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Capture changed after verification: {item['file']}")
    render_video(story)
    render_preview(copy, experiment)
    artifacts = []
    for path in sorted(OUTPUT.rglob("*")):
        relative = path.relative_to(OUTPUT)
        allowed = relative.parts[0] in {"frames", "screens", "store"} or path.name in {"preview.html", "report.html", "rev235-uk-reading.mp4", "storyboard-preview.jpg", "capture-provenance.json", "phone-verification.json"}
        if allowed and path.suffix in {".png", ".jpg", ".mp4", ".html", ".json"} and path.is_file():
            artifacts.append({"file": path.relative_to(OUTPUT).as_posix(), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (OUTPUT / "artifact-manifest.json").write_text(json.dumps({"status": "materials_ready_not_published", "artifacts": artifacts}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rendered {len(story['scenes'])} scenes, 60 seconds, four locale previews in {OUTPUT}")


if __name__ == "__main__":
    main()
