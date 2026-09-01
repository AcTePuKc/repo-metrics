# Badge styling

`repo-metrics` renders its badges and charts locally during GitHub Actions. Display-time assets are served directly from this repository, so the generated badges do not depend on a third-party badge service.

The visual system is inspired by ShieldCN's MIT-licensed shadcn/ui badge renderer. See `THIRD_PARTY_NOTICES.md` for attribution.

## Where to look

- [`PREVIEW.md`](../PREVIEW.md) - visual playground with generated examples.
- [`preview_badges.json`](../preview_badges.json) - human-readable experimental badge recipes.
- `src/render_assets.py` - local SVG renderer and `BadgeConfig` implementation.
- `badges/<repo>/` - production badge output.
- `charts/<repo>/` - production chart output.
- `preview/<repo>/` - experimental output used only by the preview page.

## How local badge recipes work

The local renderer now has a generic `BadgeConfig` layer. Preview recipes can be written as JSON instead of adding one-off SVG code.

Example:

```json
{
  "filename": "construction-zone.svg",
  "label": "Construction Zone",
  "value": "",
  "size": "xs",
  "font": "geist",
  "icon": "construction",
  "icon_color": "18181b",
  "gradient": ["FFEA61", "FFD400", "FFDD3C", "FFEA61"],
  "gap": 10,
  "label_color": "18181b"
}
```

The workflow runs `src/render_assets.py`, which loads `preview_badges.json`, converts each object to `BadgeConfig`, renders SVG, and writes it under `preview/MrPrepper-Mods/`.

This is intentionally a build-time recipe system, not an HTTP badge service. There is no `/badge/...` endpoint and no runtime server.

## Production assets

Every tracked repository currently gets:

```text
badges/<repo>/clones.svg
badges/<repo>/views.svg
charts/<repo>/traffic.svg
```

The public URLs remain stable even if the visual style changes later.

## Local support today

| Feature | Values / behaviour | Status |
| --- | --- | --- |
| Light/dark mode | Automatic through SVG `prefers-color-scheme` | Supported |
| Badge variants | `default`, `secondary`, `outline`, `ghost`, `destructive`, `branded` | Supported |
| Size | `xs`, `sm`, `default`, `lg` | Supported |
| Font family hint | `inter`, `geist`, `geist-mono`, `jetbrains-mono` with system fallbacks | Supported |
| Local SVG icons | clone, eye, pulse, robot, construction | Supported |
| Icon color | Per recipe | Supported |
| Main/background color | Per recipe | Supported |
| Label/value colors | Per recipe | Supported |
| Gradient | One or more horizontal color stops | Supported |
| Split layout | Independent left/right segment colors | Supported |
| Gap | Per recipe, clamped to a safe range | Supported |
| Radius | Per recipe | Supported |
| Compact numbers | `1.2k`, `3.4M`, etc. | Supported for metric badges |
| Traffic chart | Clones + views line chart | Supported |
| Compact traffic chart | Smaller preview version | Supported |
| External runtime service | None | Not required |

### Font note

The local renderer does not currently embed font files. A recipe such as `font: "geist"` writes a Geist-first CSS font stack into the SVG and falls back to Inter/system fonts when Geist is not available on the viewer's machine. This keeps the renderer dependency-free.

## ShieldCN upstream design options

ShieldCN still exposes a larger design surface. These are useful as a reference for features we may choose to copy into the local renderer; listing a feature here does **not** imply exact pixel-for-pixel compatibility.

| Area | ShieldCN options | Local status |
| --- | --- | --- |
| Variant | `default`, `secondary`, `outline`, `ghost`, `destructive`, `branded` | Supported |
| Size | `xs`, `sm`, `default`, `lg` | Supported |
| Mode | `dark`, `light` | Automatic rather than URL-selectable |
| Font | Inter, Geist, Geist Mono, JetBrains Mono, Fira Code, Roboto, Space Grotesk | Partial |
| Colors | Main, label, value, label text, opacity overrides | Mostly supported |
| Gradient | Custom gradient backgrounds | Supported |
| Logo/icon | Simple Icons, React Icons, custom SVG, icon color | Small local registry only |
| Layout | Custom label, split, status dot | Split supported; status dot not generic yet |
| Dimensions | Height, font size, radius, padding, icon size, gaps | Presets + gap/radius currently exposed |
| Animation | Pulse, glow, shimmer | Not implemented |
| PNG output | Raster output | Not implemented; SVG only |
| Static arbitrary badge | User-defined label/value/color | Supported through build-time JSON recipes |

## Translating a ShieldCN builder recipe

A ShieldCN-style URL such as:

```text
/badge/Construction%20Zone-abcde3.svg?size=xs&font=geist&logo=lu%3AConstruction&gradient=FFEA61%2CFFD400%2CFFDD3C%2CFFEA61&gap=10
```

maps conceptually to our local recipe as:

```text
Construction%20Zone        -> label: "Construction Zone"
size=xs                    -> size: "xs"
font=geist                 -> font: "geist"
logo=lu:Construction       -> icon: "construction"
gradient=A,B,C,D           -> gradient: [A, B, C, D]
gap=10                     -> gap: 10
```

Icon names are not downloaded from React Icons or Lucide at build time. We add only the local SVG symbols we actually need to the icon registry.

## AI-assisted split recipe

The ShieldCN-style idea:

```text
/badge/assisted-ffee8c.svg?size=xs&split=true&logo=ri%3AFaRobot&logoColor=ec4899
```

can be represented locally with:

```json
{
  "label": "AI",
  "value": "assisted",
  "size": "xs",
  "icon": "robot",
  "icon_color": "ec4899",
  "split": true,
  "left_color": "27272a",
  "right_color": "ffee8c"
}
```

See `PREVIEW.md` for rendered examples.

## Recommended scope

The goal is not to re-create the complete ShieldCN service. `repo-metrics` only needs a small presentation layer for repository traffic data and a convenient local playground for reusable badge styles.

Good candidates for future additions are:

1. More useful local icons such as download, star, GitHub and release.
2. Optional embedded/open font assets only if font consistency becomes important.
3. Generic status-dot support.
4. A tiny CLI that converts a ShieldCN-like recipe string to our JSON format.

Features such as remote providers, databases, counters, HTTP endpoints, PNG rendering and provider auto-detection remain outside the scope of this repository.

## README usage

Production badges can be embedded from any repository with the stable raw URLs:

```md
![Repository Clones](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/REPOSITORY/clones.svg) ![Repository Views](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/REPOSITORY/views.svg)
```

Traffic chart:

```md
![Repository Traffic](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/charts/REPOSITORY/traffic.svg)
```

Replace `REPOSITORY` with the repository name exactly as it appears under `data/`.

## Preview workflow

Experimental styles should be added to `preview_badges.json` when they fit the generic recipe model. Once a style is selected, the production renderer can adopt it without changing external README URLs.
