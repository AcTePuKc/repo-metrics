# Badge styling

`repo-metrics` renders its badges and charts locally during GitHub Actions. Display-time assets are served directly from this repository, so the generated badges do not depend on a third-party badge service.

The visual system is inspired by ShieldCN's MIT-licensed shadcn/ui badge renderer. See `THIRD_PARTY_NOTICES.md` for attribution.

## Where to look

- [`PREVIEW.md`](../PREVIEW.md) - visual playground with generated examples.
- [`preview_badges.json`](../preview_badges.json) - human-readable experimental badge recipes.
- `src/badge_renderer.py` - generic `BadgeConfig` + SVG renderer.
- `src/resolve_icons.mjs` - build-time Simple Icons / React Icons / Lucide resolver.
- `src/render_assets.py` - metrics/chart orchestration.
- `badges/<repo>/` - production badge output.
- `charts/<repo>/` - production chart output.
- `preview/<repo>/` - experimental output used only by the preview page.

## How local badge recipes work

The local renderer has a generic `BadgeConfig` layer. Preview recipes are written as JSON instead of adding one-off SVG code.

Example:

```json
{
  "filename": "construction-zone.svg",
  "label": "Construction Zone",
  "value": "",
  "size": "xs",
  "font": "geist",
  "icon": "lu:Construction",
  "icon_color": "18181b",
  "gradient": ["FFEA61", "FFD400", "FFDD3C", "FFEA61"],
  "gap": 10,
  "label_color": "18181b"
}
```

The workflow first runs `src/resolve_icons.mjs`, which resolves only the external icons requested by the recipes and writes a temporary `.cache/icon-cache.json`. Python then loads the cache, converts each recipe to `BadgeConfig`, renders the SVG, and writes it under `preview/MrPrepper-Mods/`.

This is intentionally a build-time recipe system, not an HTTP badge service. There is no `/badge/...` endpoint and no runtime server.

## Icon resolution

We do **not** maintain a giant brand table manually.

Supported identifiers:

```text
claude              Simple Icons slug/title lookup
anthropic           Simple Icons slug/title lookup
react               Simple Icons slug/title lookup
lu:Construction     Lucide shorthand via react-icons/lu
lu:Check             Lucide shorthand via react-icons/lu
ri:FaRobot           React Icons component name
ri:MdHome            React Icons component name
```

The `ri:` resolver determines the React Icons pack from the component prefix, matching ShieldCN's approach. For example `FaRobot` loads the Font Awesome pack and `MdHome` loads the Material pack. `lu:` automatically normalizes a Lucide name to its `Lu...` component.

Small repo-specific aliases such as `clone` and `eye` remain built into the Python renderer because they are trivial and do not require a package lookup.

External packages are build-time only:

- `simple-icons`
- `react-icons`
- `react`
- `react-dom`

The resulting SVG contains the resolved paths inline, so README display has no dependency on npm, a CDN or another badge service.

## Production assets

Every tracked repository currently gets:

```text
badges/<repo>/clones.svg
badges/<repo>/views.svg
badges/<repo>/clones-7d.svg
badges/<repo>/views-7d.svg
badges/<repo>/clones-30d.svg
badges/<repo>/views-30d.svg
badges/<repo>/stars.svg
badges/<repo>/forks.svg
charts/<repo>/traffic.svg
```

The public URLs remain stable even if the visual style changes later.

The unsuffixed `clones.svg` and `views.svg` badges are persistent totals from the
start of tracking. The `-7d` and `-30d` badges are rolling windows based on the
latest tracked daily records. `stars.svg` and `forks.svg` are current repository
snapshots, not cumulative events.

## Local support today

| Feature | Values / behaviour | Status |
| --- | --- | --- |
| Light/dark mode | Automatic through SVG `prefers-color-scheme` | Supported |
| Badge variants | `default`, `secondary`, `outline`, `ghost`, `destructive`, `branded` | Supported |
| Size | `xs`, `sm`, `default`, `lg` | Supported |
| Font family hint | Inter, Geist, Geist Mono, JetBrains Mono, Fira Code, Roboto, Space Grotesk | Supported with system fallbacks |
| Simple Icons | Slug/title lookup at build time | Supported |
| React Icons | `ri:ComponentName` | Supported |
| Lucide shorthand | `lu:Name` | Supported |
| Local SVG aliases | clone, eye, pulse, robot, construction | Supported |
| Icon color | Per recipe or library brand default | Supported |
| Main/background color | Per recipe | Supported |
| Label/value colors | Per recipe | Supported |
| Gradient | One or more horizontal color stops | Supported |
| Split layout | Independent left/right segment colors | Supported |
| Gap / label gap | Per recipe, clamped to safe ranges | Supported |
| Radius | Per recipe | Supported |
| Custom height | `height` | Supported |
| Custom font size | `font_size` or ShieldCN-style `fontSize` | Supported |
| Custom padding | `pad_x` or `padX` | Supported |
| Custom icon size | `icon_size` or `iconSize` | Supported |
| Label opacity | `label_opacity` or `labelOpacity` | Supported |
| Status dot | `status_dot` or `statusDot` | Supported |
| Compact numbers | `1.2k`, `3.4M`, etc. | Supported for metric badges |
| Traffic chart | Clones + views line chart | Supported |
| Compact traffic chart | Smaller preview version | Supported |
| External runtime service | None | Not required |

### Font note

The local renderer does not embed font files. A recipe such as `font: "geist"` writes a Geist-first CSS font stack into the SVG and falls back to Inter/system fonts when Geist is not available on the viewer's machine.

## Translating a ShieldCN builder recipe

A ShieldCN-style URL such as:

```text
/badge/Construction%20Zone-abcde3.svg?size=xs&font=geist&logo=lu%3AConstruction&gradient=FFEA61%2CFFD400%2CFFDD3C%2CFFEA61&gap=10
```

maps conceptually to:

```text
Construction%20Zone        -> label: "Construction Zone"
size=xs                    -> size: "xs"
font=geist                 -> font: "geist"
logo=lu:Construction       -> icon: "lu:Construction"
gradient=A,B,C,D           -> gradient: [A, B, C, D]
gap=10                     -> gap: 10
```

The icon identifier can now remain essentially unchanged instead of being translated into a hand-written local alias.

## AI-assisted / brand recipes

React Icons example:

```json
{
  "label": "AI",
  "value": "assisted",
  "size": "xs",
  "icon": "ri:FaRobot",
  "icon_color": "ec4899",
  "split": true,
  "left_color": "27272a",
  "right_color": "ffee8c"
}
```

Simple Icons brand example:

```json
{
  "label": "Built with",
  "value": "Claude",
  "brand": "claude",
  "variant": "secondary"
}
```

No `claude -> SVG path` mapping is stored in this repository. The build resolver finds the brand in Simple Icons.

## Builder compatibility test

`preview_badges.json` also contains an intentionally excessive `builder-kitchen-sink.svg` recipe. It exercises the same concepts as a builder URL containing:

```text
variant=destructive
size=xs
split=true
labelOpacity=1
gradient=3b82f6,3b82f6
brand=claude
height=33
fontSize=13
padX=7
iconSize=17
gap=5
labelGap=4
statusDot=true
```

This gives us one place to catch regressions as the local renderer grows.

## Scope

The goal is still not to re-create the complete ShieldCN hosted service. `repo-metrics` needs a reusable local presentation layer, not providers, databases or an HTTP server.

Potential future additions:

1. A tiny CLI that converts a ShieldCN-like recipe URL directly to our JSON format.
2. Optional embedded/open fonts if pixel-consistent typography becomes important.
3. Animation only if a real README use case appears.

Remote providers, databases, counters, HTTP endpoints and provider auto-detection remain outside the scope of this repository.

## README usage

Production badges can be embedded from any repository with the stable raw URLs:

```md
![Repository Clones](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/REPOSITORY/clones.svg) ![Repository Views](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/REPOSITORY/views.svg) ![Repository Stars](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/REPOSITORY/stars.svg) ![Repository Forks](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/REPOSITORY/forks.svg)
```

Windowed traffic variants use the same path with `-7d` or `-30d` before `.svg`:

```md
![Clones in the last 30 days](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/REPOSITORY/clones-30d.svg) ![Views in the last 30 days](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/REPOSITORY/views-30d.svg)
```

Traffic chart:

```md
![Repository Traffic](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/charts/REPOSITORY/traffic.svg)
```

Replace `REPOSITORY` with the repository name exactly as it appears under `data/`.

## Preview workflow

Experimental styles should be added to `preview_badges.json` when they fit the generic recipe model. Once a style is selected, the production renderer can adopt it without changing external README URLs.
