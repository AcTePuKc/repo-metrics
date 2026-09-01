# repo-metrics

![CI](https://shieldcn.dev/github/ci/AcTePuKc/repo-metrics.svg?workflow=collect.yml) <picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/dynamic/json.svg?url=https%3A%2F%2Fraw.githubusercontent.com%2FAcTePuKc%2Frepo-metrics%2Fmain%2Fdata%2Frepo-metrics%2Fsummary.json&query=%24.clones&label=clones&variant=secondary&mode=dark"><img alt="clones" src="https://shieldcn.dev/badge/dynamic/json.svg?url=https%3A%2F%2Fraw.githubusercontent.com%2FAcTePuKc%2Frepo-metrics%2Fmain%2Fdata%2Frepo-metrics%2Fsummary.json&query=%24.clones&label=clones&variant=secondary&mode=light"></picture> <picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/dynamic/json.svg?url=https%3A%2F%2Fraw.githubusercontent.com%2FAcTePuKc%2Frepo-metrics%2Fmain%2Fdata%2Frepo-metrics%2Fsummary.json&query=%24.views&label=views&variant=secondary&mode=dark"><img alt="views" src="https://shieldcn.dev/badge/dynamic/json.svg?url=https%3A%2F%2Fraw.githubusercontent.com%2FAcTePuKc%2Frepo-metrics%2Fmain%2Fdata%2Frepo-metrics%2Fsummary.json&query=%24.views&label=views&variant=secondary&mode=light"></picture>

Persistent GitHub repository traffic history for my public repositories.

GitHub only exposes repository clone and view traffic for a rolling 14-day window. This repository collects that data daily and keeps the historical values so they are not lost when they fall out of GitHub's window.

## Tracked metrics

Traffic history:

- Repository clones
- Unique cloners
- Repository views
- Unique visitors
- Popular referrers
- Popular repository paths

Repository snapshots:

- Stars
- Forks
- Watchers/subscribers
- Open issues

Generated summaries also include 7-day and 30-day clone/view totals, plus an aggregate summary across all tracked public repositories.

Release download counts are intentionally not stored here because GitHub already exposes persistent release asset download totals publicly.

## How it works

A scheduled GitHub Actions workflow runs once per day, discovers the public repositories owned by `AcTePuKc`, queries the GitHub API, and stores the current data under `data/<repo>/`.

Each repository can contain:

- `daily.json` - persistent daily clones, views and daily-unique counts
- `summary.json` - lifetime-from-tracking-start plus 7-day and 30-day summaries
- `chart-data.json` - chart-friendly arrays of dates, clones, views and daily-unique counts
- `repository-history.json` - daily stars, forks, watchers and open-issue snapshots
- `referrers-history.json` - daily snapshots of GitHub's popular referrers response
- `popular-paths-history.json` - daily snapshots of GitHub's popular paths response

`data/all-repositories.json` contains aggregate totals and per-repository summaries.

Private repositories are not discovered or published. If a previously tracked public repository stops being public, its generated public metric files are removed on the next successful collection.

## ShieldCN badges

`summary.json` is public, so ShieldCN Dynamic JSON badges can render persistent clones and views without this repository needing to maintain a presentation layer.

For `MrPrepper-Mods`:

```html
<picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/dynamic/json.svg?url=https%3A%2F%2Fraw.githubusercontent.com%2FAcTePuKc%2Frepo-metrics%2Fmain%2Fdata%2FMrPrepper-Mods%2Fsummary.json&query=%24.clones&label=clones&variant=secondary&mode=dark"><img alt="clones" src="https://shieldcn.dev/badge/dynamic/json.svg?url=https%3A%2F%2Fraw.githubusercontent.com%2FAcTePuKc%2Frepo-metrics%2Fmain%2Fdata%2FMrPrepper-Mods%2Fsummary.json&query=%24.clones&label=clones&variant=secondary&mode=light"></picture> <picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/dynamic/json.svg?url=https%3A%2F%2Fraw.githubusercontent.com%2FAcTePuKc%2Frepo-metrics%2Fmain%2Fdata%2FMrPrepper-Mods%2Fsummary.json&query=%24.views&label=views&variant=secondary&mode=dark"><img alt="views" src="https://shieldcn.dev/badge/dynamic/json.svg?url=https%3A%2F%2Fraw.githubusercontent.com%2FAcTePuKc%2Frepo-metrics%2Fmain%2Fdata%2FMrPrepper-Mods%2Fsummary.json&query=%24.views&label=views&variant=secondary&mode=light"></picture> ![downloads](https://shieldcn.dev/github/downloads/AcTePuKc/MrPrepper-Mods.svg)
```

ShieldCN can also read nested values. For example, a 7-day clone badge can query:

```text
$.last_7_days.clones
```

The generated JSON remains provider-independent, so other badge or chart renderers can be used later without changing the collector.

## Chart data

`chart-data.json` is generated from the persistent daily history after each collection. Its shape is intentionally simple:

```json
{
  "repository": "AcTePuKc/MrPrepper-Mods",
  "tracking_since": "2026-08-18",
  "dates": ["2026-08-18", "2026-08-19"],
  "clones": [12, 8],
  "views": [3, 1],
  "unique_cloners": [7, 5],
  "unique_visitors": [2, 1]
}
```

This can be consumed directly by Chart.js, QuickChart, a GitHub Pages dashboard, or another JSON-to-chart renderer without transforming the historical data first.

## Legacy badges

The repository still generates `badges/<repo>/clones.svg` and `views.svg` for backward compatibility with existing README links. New integrations should prefer the ShieldCN Dynamic JSON badges above.

## Configuration

Discovery settings are stored in `repositories.json`. By default the collector tracks active public repositories, including forks, and automatically discovers newly created public repositories.

The workflow requires a repository Actions secret named:

```text
GH_TRAFFIC_TOKEN
```

The token should be a fine-grained personal access token with read-only Administration permission for the repositories being tracked.

## Schedule

The collector runs every day at `04:23 UTC` and can also be started manually with **Actions -> Collect repository traffic -> Run workflow**.

## Data notes

- Historical clone/view totals begin with the oldest day still available from GitHub when the first successful collection runs.
- Daily clone/view values are keyed by date and replaced when GitHub returns a newer value for the same day, preventing double counting.
- `clones` and `views` in `summary.json` are persistent totals from the first captured date onward.
- Unique cloners and unique visitors are summed across days. They are daily-unique totals, not guaranteed lifetime-unique people across the entire tracking period.
- Referrers and popular paths are saved as dated snapshots. GitHub does not attach individual dates to the entries in those responses, so snapshots should not be added together as lifetime totals.
- Repository stars, forks, watchers and open issues are point-in-time daily snapshots, not cumulative event logs.

## License

MIT
