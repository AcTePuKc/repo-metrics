# Badge styling

`repo-metrics` renders its badges and charts locally during GitHub Actions. Display-time assets are served directly from this repository, so the generated badges do not depend on a third-party badge service.

The visual system is inspired by ShieldCN's MIT-licensed shadcn/ui badge renderer. See `THIRD_PARTY_NOTICES.md` for attribution.

## Where to look

- [`PREVIEW.md`](../PREVIEW.md) - visual playground with generated examples.
- `src/render_assets.py` - local SVG renderer.
- `badges/<repo>/` - production badge output.
- `charts/<repo>/` - production chart output.
- `preview/<repo>/` - experimental output used only by the preview page.

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
| Badge variants | `secondary`, `outline`, `default`, `destructive` in the preview renderer | Supported |
| Compact production badge | 24 px shadcn-style badge | Supported |
| Local SVG icons | Clone/branch and eye icons | Supported |
| Badge accent colors | Metric-specific clone/view accents | Supported |
| Compact numbers | `1.2k`, `3.4M`, etc. | Supported |
| Traffic chart | Clones + views line chart | Supported |
| Compact traffic chart | Smaller preview version | Supported |
| External runtime service | None | Not required |

## ShieldCN upstream design options

ShieldCN exposes a much larger design surface. These are useful as a reference for features we may choose to copy into the local renderer; listing a feature here does **not** mean it is already implemented by `repo-metrics`.

| Area | ShieldCN options | Local status |
| --- | --- | --- |
| Variant | `default`, `secondary`, `outline`, `ghost`, `destructive`, `branded` | Partial |
| Size | `xs`, `sm`, `default`, `lg` | Partial |
| Mode | `dark`, `light` | Automatic rather than selectable |
| Font | Inter, Geist, Geist Mono, JetBrains Mono, Fira Code, Roboto, Space Grotesk | Not implemented |
| Colors | Main, label, value, label text, opacity overrides | Partial |
| Gradient | Custom gradient backgrounds | Not implemented |
| Logo/icon | Simple Icons, React Icons, custom SVG, icon color | Local custom SVG only |
| Layout | Custom label, split, status dot | Not implemented |
| Dimensions | Height, font size, radius, padding, icon size, gaps | Renderer-internal only |
| Animation | Pulse, glow, shimmer | Not implemented |
| PNG output | Raster output | Not implemented; SVG only |
| Static arbitrary badge | User-defined label/value/color | Not exposed as a general generator |

## Recommended scope

The goal is not to re-create the complete ShieldCN service. `repo-metrics` only needs a small presentation layer for repository traffic data.

Good candidates to add locally if they prove useful in the preview:

1. `ghost` and `branded` variants.
2. A real `size` setting shared by production and preview badges.
3. Optional `split` layout.
4. A small local icon registry for GitHub/clone/view/download/star-style symbols.
5. Optional chart dimensions and compact/full presets.

Features such as remote providers, databases, counters, HTTP endpoints, PNG rendering and provider auto-detection are intentionally outside the scope of this repository.

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

Experimental styles should go into `preview/<repo>/` and be listed in `PREVIEW.md`. Once a style is selected, the production renderer can adopt it without changing external README URLs.
