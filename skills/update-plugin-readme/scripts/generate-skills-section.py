#!/usr/bin/env python3
"""Generate the <!-- SKILLS:START -->...<!-- SKILLS:END --> block for a plugin README.

Usage:
    generate-skills-section.py <plugin-repo-path>

Reads each skills/*/SKILL.md, parses frontmatter, infers category if absent,
and emits the skills section on stdout. Does not modify the README — the
caller decides how to splice it in.
"""
import re, pathlib, sys

CATEGORY_ORDER = [
    "Government & Civic", "Healthcare", "Emergency Preparedness",
    "Finance", "Localization", "Media & Information", "Meta / Tooling", "Other",
]
INFER_RULES = [
    (r"(^|/)(israel-post|.*-municipality-|.*-government-)", "Government & Civic"),
    (r"(^|/)(maccabi-|clalit-|meuhedet-|leumit-|.*-medicine-|.*-medical-)", "Healthcare"),
    (r"(^|/)(.*-shelter|miklat|home-front|pikud-|.*-alert)", "Emergency Preparedness"),
    (r"(^|/)(.*-salary-|salary-|.*-currency|-fx-|-tax-|.*-shekel)", "Finance"),
    (r"(^|/)(hebrew-|.*-translation|.*-fonts-)", "Localization"),
    (r"(^|/)(.*-news-|.*-rss-)", "Media & Information"),
    (r"(^|/)(add-skill-|update-plugin-|install-.*-plugin|.*-plugin-)", "Meta / Tooling"),
]


def parse_fm(md_path):
    text = md_path.read_text()
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m: return {}
    block = m.group(1)
    out = {}
    for key in ("name", "description", "category"):
        km = re.search(rf"^{key}:\s*(.+?)\s*$", block, re.M)
        if km: out[key] = km.group(1).strip()
    return out


def infer(slug, fm):
    if fm.get("category"): return fm["category"]
    for p, c in INFER_RULES:
        if re.search(p, slug): return c
    return "Other"


def clean(d):
    if not d: return ""
    d = re.sub(r"^Use when (the user|Daniel) (wants to|asks about|needs to|is asking about)\s+", "", d, flags=re.I)
    d = re.split(r"\s*Trigger phrases?\s*[:\-]", d, maxsplit=1)[0]
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", d.strip(), maxsplit=1)
    s = parts[0].strip().rstrip(".")
    return (s[0].upper() + s[1:]) if s else s


def main():
    if len(sys.argv) < 2:
        print("usage: generate-skills-section.py <plugin-repo-path>", file=sys.stderr)
        return 2
    plugin = pathlib.Path(sys.argv[1]).resolve()
    skills_dir = plugin / "skills"
    if not skills_dir.is_dir():
        print(f"no skills/ dir at {plugin}", file=sys.stderr); return 1

    groups = {}
    for p in sorted(skills_dir.glob("*/SKILL.md")):
        fm = parse_fm(p)
        cat = infer(p.parent.name, fm)
        groups.setdefault(cat, []).append({
            "name": fm.get("name", p.parent.name),
            "desc": clean(fm.get("description", "")),
        })

    lines = ["<!-- SKILLS:START -->", "## Skills", ""]
    for cat in CATEGORY_ORDER:
        if cat not in groups: continue
        lines += [f"### {cat}", "", "| Skill | What it does |", "|---|---|"]
        for s in sorted(groups[cat], key=lambda x: x["name"]):
            lines.append(f"| **`{s['name']}`** | {s['desc']} |")
        lines.append("")
    lines.append("<!-- SKILLS:END -->")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
