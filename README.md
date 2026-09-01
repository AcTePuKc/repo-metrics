# repo-metrics

Persistent GitHub repository traffic history for selected repositories.

GitHub only exposes repository clone and view traffic for a rolling 14-day window. This repository collects that data daily and keeps the historical daily values so they are not lost when they fall out of GitHub's window.

## Tracked metrics

- Repository clones
- Unique cloners
- Repository views
- Unique visitors

Release download counts are intentionally not stored here because GitHub already exposes persistent release asset download totals publicly.

## How it works

A scheduled GitHub Actions workflow runs once per day, queries the GitHub Traffic API for every repository listed in `repositories.json`, and upserts the returned daily values into `data/<owner>/<repo>/daily.json`.

A compact `summary.json` is generated for each repository with totals since tracking began.

## Configuration

Repositories are listed in `repositories.json`.

The workflow requires a repository Actions secret named:

```text
GH_TRAFFIC_TOKEN
```

The token should be a fine-grained personal access token with read-only Administration permission for the repositories being tracked.

## Data notes

- Historical totals begin with the oldest day still available from GitHub when the first successful collection runs.
- Daily values are keyed by date and replaced when GitHub returns a newer value for the same day, preventing double counting.
- Unique cloners and unique visitors are summed across days in `summary.json`. They are therefore daily-unique totals, not guaranteed lifetime-unique people across the whole tracking period.

## License

MIT
