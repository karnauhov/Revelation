"""Build the shared roadmap SVG and the demo assets from one milestone list."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name("milestones.json")
LOCALES = ("en", "es", "uk", "ru")
STATES = ("past", "plan", "conditional")
START = "<!-- roadmap milestones: start -->"
END = "<!-- roadmap milestones: end -->"


def read_lanes():
    lanes = json.loads(SOURCE.read_text(encoding="utf-8"))
    seen = set()
    for lane in lanes:
        if lane["code"] != lane["short"][0]:
            raise ValueError("Lane letter must match its label")
        if not 1 <= len(lane["nodes"]) <= 8:
            raise ValueError("Use 1-8 milestones per lane to preserve mobile readability")
        last_x = 0
        for node in lane["nodes"]:
            if (
                not re.fullmatch(lane["code"] + r"[1-9]\d?", node["id"])
                or node["id"] in seen
                or node["state"] not in STATES
                or not isinstance(node["stage"], int)
                or not 0 <= node["stage"] <= 3
                or not (211, 465, 765, 948)[node["stage"]] <= node["x"] < (465, 765, 948, 1143)[node["stage"]]
                or (node["state"] == "past") != (node["stage"] == 0)
                or set(node["hint"]) != set(LOCALES)
                or not all(node["hint"].values())
                or not node["detail"]
                or node["x"] - last_x < 40
            ):
                raise ValueError(f'Invalid milestone: {node["id"]}')
            seen.add(node["id"])
            last_x = node["x"]
    return lanes


def point(node, lane, sequence, mobile):
    if mobile:
        return 45 + 54 * sequence, 105 + 80 * lane
    return node["x"], 101 + 64 * lane


def draw(lanes, mobile):
    w, h = (480, 733) if mobile else (1200, 635)
    ink, pale, gold = "#121c35", "#e9f0ff", "#ecd39d"
    font = 'font-family="Arial, sans-serif"'
    result = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
        "  <title id=\"title\">Revelation roadmap</title>",
        "  <desc id=\"desc\">App, Study, Manuscripts, Notes, Languages, Bible texts, Outreach and Platforms. Filled circles show past work, open circles show plans, diamonds show work that depends on readiness. Each code has a description in the roadmap.</desc>",
        '  <defs><linearGradient id="night" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#17243f"/><stop offset=".58" stop-color="#101830"/><stop offset="1" stop-color="#241a39"/></linearGradient></defs>',
        f'  <rect width="{w}" height="{h}" rx="22" fill="url(#night)"/>',
        f'  <rect x="8" y="8" width="{w-16}" height="{h-16}" rx="17" fill="none" stroke="#a8b9d9" stroke-opacity=".28"/>',
    ]
    if mobile:
        result.append(f'  <text x="24" y="36" fill="{gold}" {font} font-size="22" font-weight="700">Revelation</text>')
    else:
        result.extend([
            '  <rect x="211" y="71" width="254" height="520" fill="#42597e" opacity=".28"/>',
            '  <path d="M465 57V591" stroke="#d3e0f6" stroke-opacity=".62" stroke-width="2"/>',
            '  <path d="M765 57V591M948 57V591" stroke="#b1c3df" stroke-opacity=".42" stroke-dasharray="4 8"/>',
            '  <path d="M211 54H1148m-8-5 8 5-8 5M211 593H1148" fill="none" stroke="#aabfdd" stroke-opacity=".55"/>',
            '  <path d="M465 44l10 10-10 10-10-10z" fill="#15223b" stroke="#ecd39d" stroke-width="2"/>',
        ])
        for x, label in ((221, "2024-26"), (501, "1.0.9-1.0.12"),
                         (785, "1.0.13-1.0.18"), (974, "1.0.19+")):
            result.append(f'  <text x="{x}" y="37" fill="{pale}" {font} font-size="18" font-weight="700">{label}</text>')

    positions = {}
    for i, lane in enumerate(lanes):
        color, label = lane["color"], html.escape(lane["short"])
        y = point(lane["nodes"][0], i, 0, mobile)[1]
        result.append(f'  <g id="{lane["id"]}" fill="none" stroke="{color}" stroke-linecap="round" stroke-linejoin="round">')
        if mobile:
            result.append(f'    <path d="{lane["icon"]}" transform="translate(33 {y-35}) scale(.75)" stroke-width="2.25"/>')
            result.append(f'    <text x="54" y="{y-28}" stroke="none" fill="{pale}" {font} font-size="22" font-weight="700">{label}</text>')
            past_count = sum(n["state"] == "past" for n in lane["nodes"])
            split = 18+54*past_count
            result.append(f'    <path d="M30 {y}H{split}" stroke-width="2.5" opacity=".81"/>')
            result.append(f'    <path d="M{split} {y}H449" stroke-width="2" stroke-dasharray="4 6" opacity=".69"/>')
        else:
            result.append(f'    <rect x="41" y="{y-18}" width="45" height="36" rx="11" fill="{color}" fill-opacity=".09" stroke-opacity=".58"/>')
            result.append(f'    <path d="{lane["icon"]}" transform="translate(63 {y})" stroke-width="1.8"/>')
            result.append(f'    <text x="99" y="{y+6}" stroke="none" fill="{pale}" {font} font-size="17" font-weight="700">{label}</text>')
            result.append(f'    <path d="M211 {y}H465" stroke-width="2.7" opacity=".82"/>')
            result.append(f'    <path d="M465 {y}H1143" stroke-width="2.4" stroke-dasharray="5 7" opacity=".64"/>')
        for j, node in enumerate(lane["nodes"]):
            x, y = point(node, i, j, mobile)
            positions[node["id"]] = [round(x / w * 100, 4), round((y + 7) / h * 100, 4)]
            if node["state"] == "conditional":
                result.append(f'    <path d="M{x} {y-6}l6 6-6 6-6-6z" fill="{ink}" stroke-width="2"/>')
            else:
                past = node["state"] == "past"
                result.append(f'    <circle cx="{x}" cy="{y}" r="5.5" fill="{color if past else ink}" stroke="{ink if past else color}" stroke-width="2"/>')
            result.append(f'    <text x="{x}" y="{y+(25 if mobile else 24)}" text-anchor="middle" fill="{pale}" stroke="none" {font} font-size="{19 if mobile else 16}" font-weight="700">{node["id"]}</text>')
        result.append("  </g>")
    y = h-23
    x1, x2, x3 = (97, 197, 300) if mobile else (218, 309, 402)
    result.extend([
        f'  <g fill="{pale}" {font} font-size="{19 if mobile else 16}">',
        f'    <circle cx="{x1}" cy="{y-5}" r="4.5" fill="#b9cffa"/><text x="{x1+13}" y="{y}">Past</text>',
        f'    <circle cx="{x2}" cy="{y-5}" r="4.5" fill="none" stroke="#b9cffa" stroke-width="1.6"/><text x="{x2+13}" y="{y}">Plan</text>',
        f'    <path d="M{x3} {y-10}l5 5-5 5-5-5z" fill="none" stroke="#b9cffa" stroke-width="1.6"/><text x="{x3+13}" y="{y}">If ready</text>',
        "  </g>",
        "</svg>",
        "",
    ])
    return "\n".join(result), positions


def markdown(lanes):
    result = [START, "", '<a name="milestones"></a>', "", "## Что означает каждый узел", ""]
    for lane in lanes:
        result.extend([f'### {lane["code"]} · {lane["title"]}', ""])
        for node in lane["nodes"]:
            code = node["id"]
            result.append(f'- <a name="{code.lower()}"></a> **{code}** · {node["detail"]}')
        result.append("")
    return "\n".join([*result, END])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, help="Root of the Revelation.website checkout")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    lanes = read_lanes()
    desktop, wide = draw(lanes, False)
    mobile, narrow = draw(lanes, True)
    catalogue = {
        node["id"]: {"wide": wide[node["id"]], "narrow": narrow[node["id"]], "text": node["hint"]}
        for lane in lanes for node in lane["nodes"]
    }
    doc = ROOT / "ROADMAP.md"
    content, replacements = re.subn(f"{re.escape(START)}.*?{re.escape(END)}", lambda _: markdown(lanes), doc.read_text(encoding="utf-8"), flags=re.S)
    if replacements != 1:
        raise ValueError("ROADMAP.md needs one milestone block")
    output = {doc: content, ROOT / "docs" / "roadmap.svg": desktop}
    if args.site:
        target = args.site / "demo"
        if not all((target / f"{lang}.html").is_file() for lang in LOCALES):
            parser.error("--site must point to the checkout with all four demo pages")
        output.update({
            target / "roadmap.svg": desktop,
            target / "roadmap-mobile.svg": mobile,
            target / "roadmap-milestones.js": (
                "// Generated by scripts/roadmap/build.py in the Revelation repository.\n"
                "globalThis.revelationRoadmapMilestones = "
                + json.dumps(catalogue, ensure_ascii=False, indent=2)
                + ";\n"
            ),
        })
    for path, expected in output.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                parser.error(f"Regenerate {path}")
        elif not path.is_file() or path.read_text(encoding="utf-8") != expected:
            path.write_text(expected, encoding="utf-8", newline="\n")
    print(f"{len(catalogue)} milestones; {'verified' if args.check else 'generated'}")


if __name__ == "__main__":
    main()
