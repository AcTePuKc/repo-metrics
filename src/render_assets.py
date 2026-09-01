from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
BADGE_ROOT = ROOT / "badges"
CHART_ROOT = ROOT / "charts"
PREVIEW_ROOT = ROOT / "preview"
PREVIEW_REPOSITORY = "MrPrepper-Mods"

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
ACCENT_DANGER = "#dc2626"


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


def icon_markup(kind: str, x: float, y: float, size: float) -> str:
    scale = size / 24
    if kind == "clone":
        body = (
            '<circle cx="6" cy="5" r="2.5"/>'
            '<circle cx="18" cy="19" r="2.5"/>'
            '<circle cx="6" cy="19" r="2.5"/>'
            '<path d="M6 7.5v9M8.5 5h3.25A6.25 6.25 0 0 1 18 11.25v5.25"/>'
        )
    elif kind == "eye":
        body = (
            '<path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z"/>'
            '<circle cx="12" cy="12" r="3"/>'
        )
    elif kind == "pulse":
        body = '<path d="M3 12h4l2.2-6 4.1 12 2.2-6H21"/>'
    else:
        body = '<circle cx="12" cy="12" r="4"/>'
    return (
        f'<g class="icon" transform="translate({x:g} {y:g}) scale({scale:g})" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{body}</g>'
    )


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


def preview_badge_svg(
    label: str,
    value: int,
    icon: str,
    *,
    variant: str = "secondary",
    size: str = "xs",
    accent: str = ACCENT_CLONES,
) -> str:
    message = compact_number(value)
    sizes = {
        "xs": (24, 12, 8, 12, 4),
        "sm": (32, 14, 12, 16, 6),
    }
    height, font_size, pad_x, icon_size, gap = sizes.get(size, sizes["xs"])
    radius = 6
    label_w = text_width(label, font_size)
    value_w = text_width(message, font_size)
    width = pad_x + icon_size + gap + label_w + gap + value_w + pad_x
    icon_y = (height - icon_size) / 2
    label_x = pad_x + icon_size + gap
    value_x = label_x + label_w + gap
    baseline = round(height / 2 + font_size * 0.34)

    if variant == "outline":
        dark_bg, dark_border, dark_label, dark_value = "transparent", DARK_BORDER, DARK_MUTED, DARK_FG
        light_bg, light_border, light_label, light_value = "transparent", LIGHT_BORDER, LIGHT_MUTED, LIGHT_FG
        dark_icon, light_icon = accent, accent
    elif variant == "destructive":
        dark_bg = light_bg = ACCENT_DANGER
        dark_border = light_border = ACCENT_DANGER
        dark_label = light_label = "#fee2e2"
        dark_value = light_value = "#ffffff"
        dark_icon = light_icon = "#ffffff"
    elif variant == "default":
        dark_bg, dark_border, dark_label, dark_value = DARK_FG, DARK_FG, "#52525b", "#18181b"
        light_bg, light_border, light_label, light_value = LIGHT_FG, LIGHT_FG, "#d4d4d8", "#fafafa"
        dark_icon, light_icon = "#18181b", "#fafafa"
    else:
        dark_bg, dark_border, dark_label, dark_value = DARK_BG, DARK_BORDER, DARK_MUTED, DARK_FG
        light_bg, light_border, light_label, light_value = LIGHT_BG, LIGHT_BORDER, LIGHT_MUTED, LIGHT_FG
        dark_icon, light_icon = accent, accent

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(label)}: {html.escape(message)}">
  <title>{html.escape(label)}: {html.escape(message)}</title>
  <style>
    .bg {{ fill: {dark_bg}; stroke: {dark_border}; }}
    .label {{ fill: {dark_label}; }}
    .value {{ fill: {dark_value}; }}
    .icon {{ color: {dark_icon}; }}
    @media (prefers-color-scheme: light) {{
      .bg {{ fill: {light_bg}; stroke: {light_border}; }}
      .label {{ fill: {light_label}; }}
      .value {{ fill: {light_value}; }}
      .icon {{ color: {light_icon}; }}
    }}
  </style>
  <rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{radius}" stroke-width="1"/>
  {icon_markup(icon, pad_x, icon_y, icon_size)}
  <text class="label" x="{label_x}" y="{baseline}" font-family="Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="{font_size}" font-weight="500">{html.escape(label)}</text>
  <text class="value" x="{value_x}" y="{baseline}" font-family="Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="{font_size}" font-weight="700">{html.escape(message)}</text>
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


def chart_svg(chart: dict[str, Any], *, compact: bool = False) -> str:
    dates = [str(item) for item in chart.get("dates", [])]
    clones = [int(item) for item in chart.get("clones", [])]
    views = [int(item) for item in chart.get("views", [])]
    repository = str(chart.get("repository") or "repository")

    width, height = (520, 170) if compact else (640, 220)
    left, right, top, bottom = (36, 14, 38, 26) if compact else (42, 16, 42, 30)
    plot_w = width - left - right
    plot_h = height - top - bottom
    maximum = max([1, *clones, *views])

    clone_points = polyline_points(clones, left, top, plot_w, plot_h, maximum)
    view_points = polyline_points(views, left, top, plot_w, plot_h, maximum)

    grid = []
    grid_lines = 4 if compact else 5
    for i in range(grid_lines):
        denominator = max(1, grid_lines - 1)
        y = top + (plot_h * i / denominator)
        value = round(maximum * (1 - i / denominator))
        grid.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}"/>')
        grid.append(f'<text class="axis" x="{left - 7}" y="{y + 4:.2f}" text-anchor="end">{value}</text>')

    date_labels = ""
    if dates:
        first = html.escape(dates[0])
        last = html.escape(dates[-1])
        date_labels = (
            f'<text class="axis" x="{left}" y="{height - 8}">{first}</text>'
            f'<text class="axis" x="{left + plot_w}" y="{height - 8}" text-anchor="end">{last}</text>'
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


def render_preview(repo_name: str, summary: dict[str, Any], chart: dict[str, Any]) -> None:
    if repo_name != PREVIEW_REPOSITORY:
        return
    root = PREVIEW_ROOT / repo_name
    clones = int(summary.get("clones", 0))
    views = int(summary.get("views", 0))

    write_text(root / "clones-icon-secondary.svg", preview_badge_svg("clones", clones, "clone", variant="secondary", accent=ACCENT_CLONES))
    write_text(root / "views-icon-secondary.svg", preview_badge_svg("views", views, "eye", variant="secondary", accent=ACCENT_VIEWS))
    write_text(root / "clones-icon-outline.svg", preview_badge_svg("clones", clones, "clone", variant="outline", accent=ACCENT_CLONES))
    write_text(root / "views-icon-outline.svg", preview_badge_svg("views", views, "eye", variant="outline", accent=ACCENT_VIEWS))
    write_text(root / "clones-icon-default.svg", preview_badge_svg("clones", clones, "clone", variant="default", size="sm", accent=ACCENT_CLONES))
    write_text(root / "views-icon-destructive.svg", preview_badge_svg("views", views, "eye", variant="destructive", size="sm", accent=ACCENT_VIEWS))
    write_text(root / "traffic-compact.svg", chart_svg(chart, compact=True))


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
    render_preview(repo_name, summary, chart)
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
