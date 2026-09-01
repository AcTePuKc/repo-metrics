from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ICON_CACHE_PATH = ROOT / ".cache" / "icon-cache.json"

DARK_BG = "#27272a"
DARK_FG = "#fafafa"
DARK_MUTED = "#a1a1aa"
DARK_BORDER = "#3f3f46"
LIGHT_BG = "#f4f4f5"
LIGHT_FG = "#18181b"
LIGHT_MUTED = "#71717a"
LIGHT_BORDER = "#d4d4d8"
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
    "fira-code": "Fira Code,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace",
    "roboto": "Roboto,Inter,ui-sans-serif,system-ui,sans-serif",
    "space-grotesk": "Space Grotesk,Inter,ui-sans-serif,system-ui,sans-serif",
}

_ICON_CACHE: dict[str, Any] | None = None


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


def clamp(value: int | float, minimum: int | float, maximum: int | float) -> int | float:
    return min(maximum, max(minimum, value))


@dataclass(slots=True)
class BadgeConfig:
    label: str
    value: str = ""
    variant: str = "secondary"
    size: str = "xs"
    font: str = "inter"
    icon: str | None = None
    logo: str | None = None
    brand: str | None = None
    icon_color: str | None = None
    color: str | None = None
    left_color: str | None = None
    right_color: str | None = None
    label_color: str | None = None
    value_color: str | None = None
    border_color: str | None = None
    gradient: list[str] = field(default_factory=list)
    gap: int | None = None
    label_gap: int | None = None
    split: bool = False
    radius: int = 6
    height: int | None = None
    font_size: int | None = None
    pad_x: int | None = None
    icon_size: int | None = None
    label_opacity: float = 0.7
    status_dot: bool = False
    status_color: str | None = None

    @property
    def icon_name(self) -> str | None:
        return self.icon or self.logo or self.brand

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BadgeConfig":
        aliases = {
            "iconColor": "icon_color",
            "logoColor": "icon_color",
            "leftColor": "left_color",
            "rightColor": "right_color",
            "labelColor": "label_color",
            "valueColor": "value_color",
            "borderColor": "border_color",
            "labelGap": "label_gap",
            "fontSize": "font_size",
            "padX": "pad_x",
            "iconSize": "icon_size",
            "labelOpacity": "label_opacity",
            "statusDot": "status_dot",
            "statusColor": "status_color",
        }
        allowed = set(cls.__dataclass_fields__)
        normalized: dict[str, Any] = {}
        for key, value in data.items():
            target = aliases.get(key, key)
            if target in allowed:
                normalized[target] = value
        return cls(**normalized)


def _load_icon_cache() -> dict[str, Any]:
    global _ICON_CACHE
    if _ICON_CACHE is None:
        if ICON_CACHE_PATH.exists():
            with ICON_CACHE_PATH.open("r", encoding="utf-8") as handle:
                _ICON_CACHE = json.load(handle)
        else:
            _ICON_CACHE = {}
    return _ICON_CACHE


def _external_icon(name: str) -> dict[str, Any] | None:
    return _load_icon_cache().get(name)


def _local_icon_body(kind: str) -> str | None:
    if kind == "clone":
        return (
            '<circle cx="6" cy="5" r="2.5"/>'
            '<circle cx="18" cy="19" r="2.5"/>'
            '<circle cx="6" cy="19" r="2.5"/>'
            '<path d="M6 7.5v9M8.5 5h3.25A6.25 6.25 0 0 1 18 11.25v5.25"/>'
        )
    if kind == "eye":
        return (
            '<path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z"/>'
            '<circle cx="12" cy="12" r="3"/>'
        )
    if kind == "pulse":
        return '<path d="M3 12h4l2.2-6 4.1 12 2.2-6H21"/>'
    if kind == "robot":
        return (
            '<rect x="5" y="7" width="14" height="11" rx="2"/>'
            '<path d="M12 3v4M8 12h.01M16 12h.01M9 16h6M3 11v4M21 11v4"/>'
            '<circle cx="12" cy="3" r="1"/>'
        )
    if kind == "construction":
        return (
            '<path d="M4 20V8M20 20V8M2 20h20M3 8h18"/>'
            '<path d="m5 8 4 4 4-4 4 4 4-4"/>'
        )
    return None


def icon_default_color(name: str | None) -> str | None:
    if not name:
        return None
    external = _external_icon(name)
    if not external:
        return None
    color = external.get("defaultColor")
    return None if not color or color == "currentColor" else normalize_color(str(color))


def icon_markup(kind: str, x: float, y: float, size: float) -> str:
    local = _local_icon_body(kind)
    if local is not None:
        scale = size / 24
        return (
            f'<g class="icon" transform="translate({x:g} {y:g}) scale({scale:g})" '
            'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'{local}</g>'
        )

    external = _external_icon(kind)
    if not external:
        scale = size / 24
        return (
            f'<g class="icon" transform="translate({x:g} {y:g}) scale({scale:g})" '
            'fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/></g>'
        )

    view_box = html.escape(str(external.get("viewBox") or "0 0 24 24"))
    paths = [str(item) for item in external.get("paths") or []]
    if external.get("isStroke"):
        stroke_width = float(external.get("strokeWidth") or 2)
        linecap = html.escape(str(external.get("strokeLinecap") or "round"))
        linejoin = html.escape(str(external.get("strokeLinejoin") or "round"))
        body = "".join(f'<path d="{html.escape(path)}"/>' for path in paths)
        return (
            f'<svg class="icon" x="{x:g}" y="{y:g}" width="{size:g}" height="{size:g}" viewBox="{view_box}" '
            f'fill="none" stroke="currentColor" stroke-width="{stroke_width:g}" stroke-linecap="{linecap}" stroke-linejoin="{linejoin}">{body}</svg>'
        )

    body = "".join(f'<path d="{html.escape(path)}"/>' for path in paths)
    return (
        f'<svg class="icon" x="{x:g}" y="{y:g}" width="{size:g}" height="{size:g}" viewBox="{view_box}" fill="currentColor">{body}</svg>'
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
    denominator = max(1, len(normalized) - 1)
    stops = "".join(
        f'<stop offset="{round(index * 100 / denominator)}%" stop-color="{color}"/>'
        for index, color in enumerate(normalized)
    )
    return (
        f'<defs><linearGradient id="badge-gradient" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient></defs>',
        "url(#badge-gradient)",
    )


def render_badge(config: BadgeConfig) -> str:
    preset_height, preset_font, preset_pad, preset_icon, preset_gap = SIZE_PRESETS.get(config.size, SIZE_PRESETS["xs"])
    height = int(clamp(config.height if config.height is not None else preset_height, 8, 240))
    font_size = int(clamp(config.font_size if config.font_size is not None else preset_font, 5, 120))
    pad_x = int(clamp(config.pad_x if config.pad_x is not None else preset_pad, 0, 120))
    icon_size = int(clamp(config.icon_size if config.icon_size is not None else preset_icon, 0, 120))
    gap = int(clamp(config.gap if config.gap is not None else preset_gap, 0, 60))
    label_gap = int(clamp(config.label_gap if config.label_gap is not None else gap, 0, 60))
    radius = int(clamp(config.radius, 0, 120))
    label_opacity = float(clamp(config.label_opacity, 0, 1))
    font_family = FONT_STACKS.get(config.font, FONT_STACKS["inter"])
    label, value = str(config.label), str(config.value)
    icon_name = config.icon_name
    palette = variant_palette(config.variant, config.color)

    label_w = text_width(label, font_size)
    value_w = text_width(value, font_size) if value else 0
    icon_block = icon_size + gap if icon_name else 0
    dot_size = max(4, round(font_size * 0.5)) if config.status_dot else 0
    dot_block = dot_size + gap if config.status_dot else 0
    between = label_gap if label and value and not config.split else 0
    width = pad_x + icon_block + dot_block + label_w + between + value_w + pad_x
    if config.split and value:
        width += label_gap * 2

    icon_x = pad_x
    icon_y = (height - icon_size) / 2
    dot_x = pad_x + icon_block + dot_size / 2
    label_x = pad_x + icon_block + dot_block
    value_x = label_x + label_w + between
    split_x = label_x + label_w + label_gap if config.split and value else None
    if split_x is not None:
        value_x = split_x + label_gap
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
    default_icon = icon_default_color(icon_name)
    dark_icon = normalize_color(config.icon_color, default_icon or palette["dark_icon"])
    light_icon = normalize_color(config.icon_color, default_icon or palette["light_icon"])
    status_color = normalize_color(config.status_color, normalize_color(config.color, "#22c55e"))

    split_shapes = ""
    if config.split and value and split_x is not None:
        left_bg = normalize_color(config.left_color, palette["dark_bg"])
        right_bg = normalize_color(config.right_color, gradient_fill or normalize_color(config.color, palette["dark_bg"]))
        split_shapes = (
            f'<clipPath id="badge-clip"><rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{radius}"/></clipPath>'
            f'<g clip-path="url(#badge-clip)"><rect x="0" y="0" width="{split_x}" height="{height}" fill="{left_bg}"/>'
            f'<rect x="{split_x}" y="0" width="{width - split_x}" height="{height}" fill="{right_bg}"/></g>'
        )

    bg_rect = "" if config.split and value else f'<rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{radius}" stroke-width="1"/>'
    border_rect = f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{radius}" fill="none" class="border" stroke-width="1"/>' if config.split and value else ""
    icon_svg = icon_markup(icon_name, icon_x, icon_y, icon_size) if icon_name else ""
    dot_svg = f'<circle cx="{dot_x:g}" cy="{height / 2:g}" r="{dot_size / 2:g}" fill="{status_color}"/>' if config.status_dot else ""
    value_svg = f'<text class="value" x="{value_x}" y="{baseline}" font-family="{html.escape(font_family)}" font-size="{font_size}" font-weight="700">{html.escape(value)}</text>' if value else ""
    aria = f"{label}: {value}" if value else label

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(aria)}">
  <title>{html.escape(aria)}</title>
  {defs}
  <style>
    .bg {{ fill: {dark_bg}; stroke: {dark_border}; }}
    .border {{ stroke: {dark_border}; }}
    .label {{ fill: {dark_label}; fill-opacity: {label_opacity:g}; }}
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
  {dot_svg}
  <text class="label" x="{label_x}" y="{baseline}" font-family="{html.escape(font_family)}" font-size="{font_size}" font-weight="500">{html.escape(label)}</text>
  {value_svg}
</svg>
'''
