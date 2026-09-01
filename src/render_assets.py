from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
BADGE_ROOT = ROOT / "badges"
CHART_ROOT = ROOT / "charts"
PREVIEW_ROOT = ROOT / "preview"
PREVIEW_REPOSITORY = "MrPrepper-Mods"
PREVIEW_RECIPES = ROOT / "preview_badges.json"

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

SIZE_PRESETS = {
    "xs": (24, 12, 8, 12, 4),
    "sm": (32, 14, 12, 16, 6),
    "default": (36, 14, 16, 16, 8),
    "lg": (40, 14, 24, 16, 8),
}

FONT_STACKS = {
    "inter": "Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif",
    "geist": "Geist,Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif",
    "geist-mono": "Geist Mono,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace",
    "jetbrains-mono": "JetBrains Mono,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_color(value: str | None, fallback: str | None = None) -> str | None:
    if value is None:
        return fallback
    value = value.strip()
    if not value:
        return fallback
    if value == "transparent" or value.startswith("url("):
        return value
    return value if value.startswith("#") else f"#{value}"


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
    return max(1, round(len(text) * font_size * 0.58))


@dataclass(slots=True)
class BadgeConfig:
    label: str
    value: str = ""
    variant: str = "secondary"
    size: str = "xs"
    font: str = "inter"
    icon: str | None = None
    icon_color: str | None = None
    color: str | None = None
    left_color: str | None = None
    right_color: str | None = None
    label_color: str | None = None
    value_color: str | None = None
    border_color: str | None = None
    gradient: list[str] = field(default_factory=list)
    gap: int | None = None
    split: bool = False
    radius: int = 6

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BadgeConfig":
        allowed = {
            "label", "value", "variant", "size", "font", "icon", "icon_color",
            "color", "left_color", "right_color", "label_color", "value_color",
            "border_color", "gradient", "gap", "split", "radius",
        }
        return cls(**{key: value for key, value in data.items() if key in allowed})


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
    elif kind == "robot":
        body = (
            '<rect x="5" y="7" width="14" height="11" rx="2"/>'
            '<path d="M12 3v4M8 12h.01M16 12h.01M9 16h6M3 11v4M21 11v4"/>'
            '<circle cx="12" cy="3" r="1"/>'
        )
    elif kind == "construction":
        body = (
            '<path d="M4 20V8M20 20V8M2 20h20M3 8h18"/>'
            '<path d="m5 8 4 4 4-4 4 4 4-4"/>'
        )
    else:
        body = '<circle cx="12" cy="12" r="4"/>'
    return (
        f'<g class="icon" transform="translate({x:g} {y:g}) scale({scale:g})" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{body}</g>'
    )


def variant_palette(variant: str, color: str | None) -> dict[str, str]:
    custom = normalize_color(color)
    if variant == "outline":
        return {
            "dark_bg": "transparent", "light_bg": "transparent",
            "dark_border": custom or DARK_BORDER, "light_border": custom or LIGHT_BORDER,
            "dark_label": DARK_MUTED, "light_label": LIGHT_MUTED,
            "dark_value": custom or DARK_FG, "light_value": custom or LIGHT_FG,
            "dark_icon": custom or DARK_FG, "light_icon": custom or LIGHT_FG,
        }
    if variant == "destructive":
        bg = custom or ACCENT_DANGER
        return {
            "dark_bg": bg, "light_bg": bg, "dark_border": bg, "light_border": bg,
            "dark_label": "#fee2e2", "light_label": "#fee2e2",
            "dark_value": "#ffffff", "light_value": "#ffffff",
            "dark_icon": "#ffffff", "light_icon": "#ffffff",
        }
    if variant in {"default", "branded"}:
        if custom:
            return {
                "dark_bg": custom, "light_bg": custom, "dark_border": custom, "light_border": custom,
                "dark_label": "#ffffff", "light_label": "#ffffff",
                "dark_value": "#ffffff", "light_value": "#ffffff",
                "dark_icon": "#ffffff", "light_icon": "#ffffff",
            }
        return {
            "dark_bg": DARK_FG, "light_bg": LIGHT_FG,
            "dark_border": DARK_FG, "light_border": LIGHT_FG,
            "dark_label": "#52525b", "light_label": "#d4d4d8",
            "dark_value": "#18181b", "light_value": "#fafafa",
            "dark_icon": "#18181b", "light_icon": "#fafafa",
        }
    if variant == "ghost":
        return {
            "dark_bg": "transparent", "light_bg": "transparent",
            "dark_border": "transparent", "light_border": "transparent",
            "dark_label": DARK_MUTED, "light_label": LIGHT_MUTED,
            "dark_value": DARK_FG, "light_value": LIGHT_FG,
            "dark_icon": custom or DARK_FG, "light_icon": custom or LIGHT_FG,
        }
    return {
        "dark_bg": custom or DARK_BG, "light_bg": custom or LIGHT_BG,
        "dark_border": custom or DARK_BORDER, "light_border": custom or LIGHT_BORDER,
        "dark_label": DARK_MUTED, "light_label": LIGHT_MUTED,
        "dark_value": DARK_FG, "light_value": LIGHT_FG,
        "dark_icon": custom or DARK_FG, "light_icon": custom or LIGHT_FG,
    }


def gradient_defs(colors: list[str]) -> tuple[str, str | None]:
    normalized = [normalize_color(color) for color in colors if color]
    normalized = [color for color in normalized if color]
    if not normalized:
        return "", None
    if len(normalized) == 1:
        return "", normalized[0]
    stops = []
    denominator = max(1, len(normalized) - 1)
    for index, color in enumerate(normalized):
        offset = round(index * 100 / denominator)
        stops.append(f'<stop offset="{offset}%" stop-color="{color}"/>')
    defs = f'<defs><linearGradient id="badge-gradient" x1="0" y1="0" x2="1" y2="0">{"".join(stops)}</linearGradient></defs>'
    return defs, "url(#badge-gradient)"


def render_badge(config: BadgeConfig) -> str:
    height, font_size, pad_x, icon_size, default_gap = SIZE_PRESETS.get(config.size, SIZE_PRESETS["xs"])
    gap = max(0, min(60, int(config.gap if config.gap is not None else default_gap)))
    font_family = FONT_STACKS.get(config.font, FONT_STACKS["inter"])
    label = str(config.label)
    value = str(config.value)
    palette = variant_palette(config.variant, config.color)

    label_w = text_width(label, font_size)
    value_w = text_width(value, font_size) if value else 0
    icon_block = icon_size + gap if config.icon else 0
    between = gap if label and value and not config.split else 0
    width = pad_x + icon_block + label_w + between + value_w + pad_x
    if config.split and value:
        width += gap * 2

    icon_x = pad_x
    icon_y = (height - icon_size) / 2
    label_x = pad_x + icon_block
    value_x = label_x + label_w + between
    split_x = label_x + label_w + gap if config.split and value else None
    if split_x is not None:
        value_x = split_x + gap
    baseline = round(height / 2 + font_size * 0.34)

    defs, gradient_fill = gradient_defs(config.gradient)
    dark_bg = gradient_fill or palette["dark_bg"]
    light_bg = gradient_fill or palette["light_bg"]
    dark_border = normalize_color(config.border_color, palette["dark_border"])
    light_border = normalize_color(config.border_color, palette["light_border"])
    dark_label = normalize_color(config.label_color, palette["dark_label"])
    light_label = normalize_color(config.label_color, palette["light_label"])
    dark_value = normalize_color(config.value_color, palette["dark_value"])
    light_value = normalize_color(config.value_color, palette["light_value"])
    dark_icon = normalize_color(config.icon_color, palette["dark_icon"])
    light_icon = normalize_color(config.icon_color, palette["light_icon"])

    left_color = normalize_color(config.left_color)
    right_color = normalize_color(config.right_color)
    split_shapes = ""
    if config.split and value and split_x is not None:
        left_bg = left_color or palette["dark_bg"]
        right_bg = right_color or gradient_fill or normalize_color(config.color, palette["dark_bg"])
        split_shapes = (
            f'<clipPath id="badge-clip"><rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{config.radius}"/></clipPath>'
            f'<g clip-path="url(#badge-clip)">'
            f'<rect x="0" y="0" width="{split_x}" height="{height}" fill="{left_bg}"/>'
            f'<rect x="{split_x}" y="0" width="{width - split_x}" height="{height}" fill="{right_bg}"/>'
            '</g>'
        )

    bg_rect = "" if config.split and value else (
        f'<rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{config.radius}" stroke-width="1"/>'
    )
    border_rect = (
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{config.radius}" fill="none" class="border" stroke-width="1"/>'
        if config.split and value else ""
    )
    icon_svg = icon_markup(config.icon, icon_x, icon_y, icon_size) if config.icon else ""
    value_svg = (
        f'<text class="value" x="{value_x}" y="{baseline}" font-family="{html.escape(font_family)}" font-size="{font_size}" font-weight="700">{html.escape(value)}</text>'
        if value else ""
    )

    aria = f"{label}: {value}" if value else label
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(aria)}">
  <title>{html.escape(aria)}</title>
  {defs}
  <style>
    .bg {{ fill: {dark_bg}; stroke: {dark_border}; }}
    .border {{ stroke: {dark_border}; }}
    .label {{ fill: {dark_label}; }}
    .value {{ fill: {dark_value}; }}
    .icon {{ color: {dark_icon}; }}
    @media (prefers-color-scheme: light) {{
      .bg {{ fill: {light_bg}; stroke: {light_border}; }}
      .border {{ stroke: {light_border}; }}
      .label {{ fill: {light_label}; }}
      .value {{ fill: {light_value}; }}
      .icon {{ color: {light_icon}; }}
    }}
  </style>
  {bg_rect}
  {split_shapes}
  {border_rect}
  {icon_svg}
  <text class="label" x="{label_x}" y="{baseline}" font-family="{html.escape(font_family)}" font-size="{font_size}" font-weight="500">{html.escape(label)}</text>
  {value_svg}
</svg>
'''


def badge_svg(label: str, value: int, accent: str) -> str:
    return render_badge(BadgeConfig(label=label, value=compact_number(value), icon=None, color=None, size="xs"))


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
        config = BadgeConfig.from_dict(recipe)
        write_text(root / filename, render_badge(config))


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
