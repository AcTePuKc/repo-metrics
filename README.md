# repo-metrics

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
- `repository-history.json` - daily stars, forks, watchers and open-issue snapshots
- `referrers-history.json` - daily snapshots of GitHub's popular referrers response
- `popular-paths-history.json` - daily snapshots of GitHub's popular paths response

`data/all-repositories.json` contains aggregate totals and per-repository summaries.

A ready-to-embed `clones.svg` and `views.svg` badge is generated for every tracked repository.

Private repositories are not discovered or published. If a previously tracked public repository stops being public, its generated public metric files are removed on the next successful collection.

## Using the badges

For example, `MrPrepper-Mods` can embed the persistent clone and view counters directly from this repository:

```md
![Repository Clones](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/MrPrepper-Mods/clones.svg) ![Repository Views](https://raw.githubusercontent.com/AcTePuKc/repo-metrics/main/badges/MrPrepper-Mods/views.svg) ![GitHub Downloads](https://img.shields.io/github/downloads/AcTePuKc/MrPrepper-Mods/total)
```

Replace `MrPrepper-Mods` with the repository name for other generated badges.

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
