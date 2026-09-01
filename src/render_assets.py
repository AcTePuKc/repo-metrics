from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from badge_renderer import BadgeConfig, compact_number, render_badge

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
BADGE_ROOT = ROOT / "badges"
CHART_ROOT = ROOT / "charts"
PREVIEW_ROOT = ROOT / "preview"
PREVIEW_REPOSITORY = "MrPrepper-Mods"
PREVIEW_RECIPES = ROOT / "preview_badges.json"

DARK_FG = "#fafafa"
DARK_MUTED = "#a1a1aa"
DARK_BORDER = "#3f3f46"
LIGHT_FG = "#18181b"
LIGHT_MUTED = "#71717a"
LIGHT_BORDER = "#d4d4d8"
ACCENT_CLONES = "#22c55e"
ACCENT_VIEWS = "#60a5fa"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def badge_svg(label: str, value: int) -> str:
    return render_badge(BadgeConfig(label=label, value=compact_number(value), size="xs"))


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


def render_recipe_previews(root: Path) -> None:
    if not PREVIEW_RECIPES.exists():
        return
    recipes = load_json(PREVIEW_RECIPES)
    for recipe in recipes:
        filename = str(recipe.get("filename", "")).strip()
        if not filename or "/" in filename or "\\" in filename:
            continue
        write_text(root / filename, render_badge(BadgeConfig.from_dict(recipe)))


def render_preview(repo_name: str, summary: dict[str, Any], chart: dict[str, Any]) -> None:
    if repo_name != PREVIEW_REPOSITORY:
        return
    root = PREVIEW_ROOT / repo_name
    clones = int(summary.get("clones", 0))
    views = int(summary.get("views", 0))

    write_text(root / "clones-icon-secondary.svg", render_badge(BadgeConfig(label="clones", value=compact_number(clones), icon="clone", variant="secondary", icon_color=ACCENT_CLONES)))
    write_text(root / "views-icon-secondary.svg", render_badge(BadgeConfig(label="views", value=compact_number(views), icon="eye", variant="secondary", icon_color=ACCENT_VIEWS)))
    write_text(root / "clones-icon-outline.svg", render_badge(BadgeConfig(label="clones", value=compact_number(clones), icon="clone", variant="outline", icon_color=ACCENT_CLONES)))
    write_text(root / "views-icon-outline.svg", render_badge(BadgeConfig(label="views", value=compact_number(views), icon="eye", variant="outline", icon_color=ACCENT_VIEWS)))
    write_text(root / "clones-icon-default.svg", render_badge(BadgeConfig(label="clones", value=compact_number(clones), icon="clone", variant="default", size="sm")))
    write_text(root / "views-icon-destructive.svg", render_badge(BadgeConfig(label="views", value=compact_number(views), icon="eye", variant="destructive", size="sm")))
    write_text(root / "traffic-compact.svg", chart_svg(chart, compact=True))
    render_recipe_previews(root)


def render_repository(repository_dir: Path) -> bool:
    summary_path = repository_dir / "summary.json"
    chart_path = repository_dir / "chart-data.json"
    if not summary_path.exists() or not chart_path.exists():
        return False

    summary = load_json(summary_path)
    chart = load_json(chart_path)
    repo_name = repository_dir.name

    write_text(BADGE_ROOT / repo_name / "clones.svg", badge_svg("clones", int(summary.get("clones", 0))))
    write_text(BADGE_ROOT / repo_name / "views.svg", badge_svg("views", int(summary.get("views", 0))))
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
