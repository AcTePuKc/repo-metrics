# repo-metrics

![Collect repository traffic](https://github.com/AcTePuKc/repo-metrics/actions/workflows/collect.yml/badge.svg) ![Repository Clones](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/repo-metrics/clones.svg) ![Repository Views](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/repo-metrics/views.svg)

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

A scheduled GitHub Actions workflow runs once per day, discovers the public repositories owned by `AcTePuKc`, queries the GitHub API, stores the data under `data/<repo>/`, and locally renders the SVG presentation assets.

Each repository can contain:

- `daily.json` - persistent daily clones, views and daily-unique counts
- `summary.json` - lifetime-from-tracking-start plus 7-day and 30-day summaries
- `chart-data.json` - chart-friendly arrays of dates, clones, views and daily-unique counts
- `repository-history.json` - daily stars, forks, watchers and open-issue snapshots
- `referrers-history.json` - daily snapshots of GitHub's popular referrers response
- `popular-paths-history.json` - daily snapshots of GitHub's popular paths response

Generated SVG assets:

- `badges/<repo>/clones.svg`
- `badges/<repo>/views.svg`
- `charts/<repo>/traffic.svg`

`data/all-repositories.json` contains aggregate totals and per-repository summaries.

Private repositories are not discovered or published. If a previously tracked public repository stops being public, its generated public metric files are removed on the next successful collection.

## Local badges

The badges are generated locally by the GitHub Actions workflow and served directly from this repository. There is no runtime dependency on ShieldCN, Shields.io, Vercel, a database, or another badge service.

For `MrPrepper-Mods`:

```md
![Repository Clones](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/MrPrepper-Mods/clones.svg) ![Repository Views](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/MrPrepper-Mods/views.svg)
```

The renderer uses a compact shadcn-style visual design adapted from ShieldCN's MIT-licensed design tokens. The generated SVGs support light and dark system color schemes through CSS media queries.

## Traffic charts

A traffic chart is generated from `chart-data.json` for every tracked repository:

```md
![Repository Traffic](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/charts/MrPrepper-Mods/traffic.svg)
```

The chart currently plots daily clones and views. The underlying `chart-data.json` remains generic, so other renderers can consume it later without changing the collector.

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

## Third-party attribution

See `THIRD_PARTY_NOTICES.md` for the ShieldCN MIT attribution covering the adapted visual design tokens.

## License

MIT
