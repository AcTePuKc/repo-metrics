# repo-metrics

Persistent GitHub repository traffic history for my public repositories.

GitHub only exposes repository clone and view traffic for a rolling 14-day window. This repository collects that data daily and keeps the historical daily values so they are not lost when they fall out of GitHub's window.

## Tracked metrics

- Repository clones
- Unique cloners
- Repository views
- Unique visitors

Release download counts are intentionally not stored here because GitHub already exposes persistent release asset download totals publicly.

## How it works

A scheduled GitHub Actions workflow runs once per day, discovers the public repositories owned by `AcTePuKc`, queries the GitHub Traffic API, and upserts the returned daily values into `data/<repo>/daily.json`.

A compact `summary.json` and ready-to-embed SVG badges are generated for every tracked repository.

Private repositories are not discovered or published. If a previously tracked public repository stops being public, its generated public metric files are removed on the next successful collection.

## Using the badges

For example, `MrPrepper-Mods` can embed the persistent clone and view counters directly from this repository:

```md
![Repository Clones](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/MrPrepper-Mods/clones.svg)
![Repository Views](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/MrPrepper-Mods/views.svg)
```

GitHub release downloads do not need this tracker and can use Shields directly:

```md
![GitHub Downloads](https://img.shields.io/github/downloads/AcTePuKc/MrPrepper-Mods/total)
```

Replace `MrPrepper-Mods` with the repository name for the other generated badges.

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

- Historical totals begin with the oldest day still available from GitHub when the first successful collection runs.
- Daily values are keyed by date and replaced when GitHub returns a newer value for the same day, preventing double counting.
- `clones` and `views` in `summary.json` are persistent totals from the first captured date onward.
- Unique cloners and unique visitors are summed across days. They are daily-unique totals, not guaranteed lifetime-unique people across the entire tracking period.

## License

MIT
