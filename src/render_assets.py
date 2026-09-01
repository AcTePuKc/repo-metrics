from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
BADGE_ROOT = ROOT / "badges"
CHART_ROOT = ROOT / "charts"

# Visual tokens adapted from ShieldCN's MIT-licensed shadcn/ui badge renderer.
# Upstream: https://github.com/jal-co/shieldcn
DARK_BG = "#27272a"
DARK_FG = "#fafafa"
DARK_MUTED = "#a1a1aa"
DARK_BORDER = "#3f3f46"
LIGHT_BG = "#f4f4f5"
LIGHT_FG = "#18181b"
LIGHT_MUTED = "#71717a"
LIGHT_BORDER = "#d4d4d8"
ACCENT_CLONES = "#22c55e"
ACCENT_VIEWS = "#60a5fa"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def compact_number(value: int) -> str:
    if value < 1_000:
        return str(value)
    if value < 1_000_000:
        number, suffix = value / 1_000, "k"
    elif value < 1_000_000_000:
        number, suffix = value / 1_000_000, "M"
    else:
        number, suffix = value / 1_000_000_000, "B"
    return f"{number:.1f}".rstrip("0").rstrip(".") + suffix


def text_width(text: str, font_size: int = 12) -> int:
    # Dependency-free approximation suitable for compact README badges.
    return max(1, round(len(text) * font_size * 0.58))


def badge_svg(label: str, value: int, accent: str) -> str:
    message = compact_number(value)
    height = 24
    radius = 6
    font_size = 12
    pad_x = 8
    gap = 6
    label_w = text_width(label, font_size)
    value_w = text_width(message, font_size)
    width = pad_x + label_w + gap + value_w + pad_x
    label_x = pad_x
    value_x = pad_x + label_w + gap
    baseline = 16

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(label)}: {html.escape(message)}">
  <title>{html.escape(label)}: {html.escape(message)}</title>
  <style>
    .bg {{ fill: {DARK_BG}; stroke: {DARK_BORDER}; }}
    .label {{ fill: {DARK_MUTED}; }}
    .value {{ fill: {DARK_FG}; }}
    @media (prefers-color-scheme: light) {{
      .bg {{ fill: {LIGHT_BG}; stroke: {LIGHT_BORDER}; }}
      .label {{ fill: {LIGHT_MUTED}; }}
      .value {{ fill: {LIGHT_FG}; }}
    }}
  </style>
  <rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{radius}" stroke-width="1"/>
  <circle cx="{pad_x - 1}" cy="{height / 2:g}" r="2.5" fill="{accent}"/>
  <text class="label" x="{label_x + 6}" y="{baseline}" font-family="Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="{font_size}" font-weight="500">{html.escape(label)}</text>
  <text class="value" x="{value_x + 6}" y="{baseline}" font-family="Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="{font_size}" font-weight="600">{html.escape(message)}</text>
</svg>
'''


def polyline_points(values: list[int], left: int, top: int, width: int, height: int, maximum: int) -> str:
    if not values:
        return ""
    if len(values) == 1:
        xs = [left + width / 2]
    else:
        xs = [left + (width * i / (len(values) - 1)) for i in range(len(values))]
    ys = [top + height - (height * value / maximum if maximum else 0) for value in values]
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in zip(xs, ys))


def chart_svg(chart: dict[str, Any]) -> str:
    dates = [str(item) for item in chart.get("dates", [])]
    clones = [int(item) for item in chart.get("clones", [])]
    views = [int(item) for item in chart.get("views", [])]
    repository = str(chart.get("repository") or "repository")

    width, height = 640, 220
    left, right, top, bottom = 42, 16, 42, 30
    plot_w = width - left - right
    plot_h = height - top - bottom
    maximum = max([1, *clones, *views])

    clone_points = polyline_points(clones, left, top, plot_w, plot_h, maximum)
    view_points = polyline_points(views, left, top, plot_w, plot_h, maximum)

    grid = []
    for i in range(5):
        y = top + (plot_h * i / 4)
        value = round(maximum * (1 - i / 4))
        grid.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}"/>')
        grid.append(f'<text class="axis" x="{left - 8}" y="{y + 4:.2f}" text-anchor="end">{value}</text>')

    date_labels = ""
    if dates:
        first = html.escape(dates[0])
        last = html.escape(dates[-1])
        date_labels = (
            f'<text class="axis" x="{left}" y="{height - 9}">{first}</text>'
            f'<text class="axis" x="{left + plot_w}" y="{height - 9}" text-anchor="end">{last}</text>'
        )

    clone_line = f'<polyline points="{clone_points}" fill="none" stroke="{ACCENT_CLONES}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>' if clone_points else ""
    view_line = f'<polyline points="{view_points}" fill="none" stroke="{ACCENT_VIEWS}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>' if view_points else ""

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Traffic history for {html.escape(repository)}">
  <title>Traffic history for {html.escape(repository)}</title>
  <style>
    .panel {{ fill: #18181b; stroke: {DARK_BORDER}; }}
    .title {{ fill: {DARK_FG}; }}
    .axis {{ fill: {DARK_MUTED}; font: 10px Inter,ui-sans-serif,system-ui,sans-serif; }}
    .grid {{ stroke: {DARK_BORDER}; stroke-width: 1; opacity: .65; }}
    @media (prefers-color-scheme: light) {{
      .panel {{ fill: #ffffff; stroke: {LIGHT_BORDER}; }}
      .title {{ fill: {LIGHT_FG}; }}
      .axis {{ fill: {LIGHT_MUTED}; }}
      .grid {{ stroke: {LIGHT_BORDER}; }}
    }}
  </style>
  <rect class="panel" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" stroke-width="1"/>
  <text class="title" x="16" y="24" font-family="Inter,ui-sans-serif,system-ui,sans-serif" font-size="13" font-weight="600">{html.escape(repository)} traffic</text>
  <circle cx="{width - 154}" cy="20" r="3" fill="{ACCENT_CLONES}"/><text class="axis" x="{width - 146}" y="23">clones</text>
  <circle cx="{width - 86}" cy="20" r="3" fill="{ACCENT_VIEWS}"/><text class="axis" x="{width - 78}" y="23">views</text>
  {''.join(grid)}
  {clone_line}
  {view_line}
  {date_labels}
</svg>
'''


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def render_repository(repository_dir: Path) -> bool:
    summary_path = repository_dir / "summary.json"
    chart_path = repository_dir / "chart-data.json"
    if not summary_path.exists() or not chart_path.exists():
        return False

    summary = load_json(summary_path)
    chart = load_json(chart_path)
    repo_name = repository_dir.name

    write_text(BADGE_ROOT / repo_name / "clones.svg", badge_svg("clones", int(summary.get("clones", 0)), ACCENT_CLONES))
    write_text(BADGE_ROOT / repo_name / "views.svg", badge_svg("views", int(summary.get("views", 0)), ACCENT_VIEWS))
    write_text(CHART_ROOT / repo_name / "traffic.svg", chart_svg(chart))
    return True


def main() -> int:
    generated = 0
    if not DATA_ROOT.exists():
        print("No data directory found")
        return 0

    for repository_dir in sorted(DATA_ROOT.iterdir()):
        if repository_dir.is_dir() and render_repository(repository_dir):
            generated += 1

    print(f"Rendered local badges and charts for {generated} repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
