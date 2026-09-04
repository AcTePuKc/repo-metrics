from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from badge_renderer import BadgeConfig, compact_number, render_badge

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
BADGE_ROOT = ROOT / "badges"
CHART_ROOT = ROOT / "charts"
AGGREGATE_PATH = DATA_ROOT / "all-repositories.json"
PORTFOLIO_PATH = ROOT / "PORTFOLIO.md"
PREVIEW_ROOT = ROOT / "preview"
PREVIEW_REPOSITORY = "MrPrepper-Mods"
PREVIEW_RECIPES = ROOT / "preview_badges.json"

DARK_FG = "#fafafa"
DARK_MUTED = "#a1a1aa"
DARK_BORDER = "#3f3f46"
LIGHT_FG = "#18181b"
LIGHT_MUTED = "#71717a"
LIGHT_BORDER = "#d4d4d8"
ACCENT_CLONES = "#22c55e"
ACCENT_VIEWS = "#60a5fa"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def badge_svg(label: str, value: int) -> str:
    return render_badge(BadgeConfig(label=label, value=compact_number(value), size="xs"))


def write_metric_badge(directory: Path, filename: str, label: str, value: Any) -> None:
    write_text(directory / filename, badge_svg(label, int(value)))


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


def latest_snapshot(path: Path) -> tuple[str | None, list[dict[str, Any]]]:
    if not path.exists():
        return None, []
    history = load_json(path)
    snapshots = history.get("days", {})
    if not snapshots:
        return None, []
    day = sorted(snapshots)[-1]
    return day, snapshots[day]


def repository_short_name(repository: str) -> str:
    return repository.split("/", 1)[-1]


def portfolio_markdown(aggregate: dict[str, Any]) -> str:
    repositories = aggregate.get("repositories", {})
    totals = aggregate.get("totals", {})
    last_7_days = aggregate.get("last_7_days", {})
    last_30_days = aggregate.get("last_30_days", {})
    updated_at = str(aggregate.get("updated_at", "unknown"))

    ranked = sorted(
        repositories.items(),
        key=lambda item: (
            int(item[1].get("last_30_days", {}).get("views", 0))
            + int(item[1].get("last_30_days", {}).get("clones", 0)),
            item[0].lower(),
        ),
        reverse=True,
    )

    repo_rows = []
    for repository, summary in ranked[:10]:
        name = repository_short_name(repository)
        snapshot = summary.get("repository_snapshot", {})
        last_30 = summary.get("last_30_days", {})
        repo_url = f"https://github.com/{repository}"
        chart_url = f"charts/{name}/traffic.svg"
        repo_rows.append(
            f"| [{name}]({repo_url}) | {int(last_30.get('views', 0))} | "
            f"{int(last_30.get('clones', 0))} | {int(snapshot.get('stars', 0))} | "
            f"[chart]({chart_url}) |"
        )

    referrer_totals: dict[str, int] = {}
    referrer_days: set[str] = set()
    path_rows: list[tuple[int, str, str, str, str]] = []
    for repository in repositories:
        name = repository_short_name(repository)
        referrer_day, referrers = latest_snapshot(DATA_ROOT / name / "referrers-history.json")
        if referrer_day:
            referrer_days.add(referrer_day)
        for item in referrers:
            referrer = str(item.get("referrer", "")).strip() or "Unknown"
            referrer_totals[referrer] = referrer_totals.get(referrer, 0) + int(item.get("count", 0))

        path_day, paths = latest_snapshot(DATA_ROOT / name / "popular-paths-history.json")
        if path_day:
            for item in paths:
                path = str(item.get("path", "")).strip() or "/"
                title = str(item.get("title", "")).strip() or path
                count = int(item.get("count", 0))
                path_rows.append((count, repository, path, title, path_day))

    referrer_day = max(referrer_days) if referrer_days else "not available"
    referrer_rows = [
        f"| {html.escape(referrer)} | {count} |"
        for referrer, count in sorted(referrer_totals.items(), key=lambda item: (-item[1], item[0].lower()))[:10]
    ]
    if not referrer_rows:
        referrer_rows = ["| No snapshot data yet | 0 |"]

    path_rows.sort(key=lambda item: (-item[0], item[1].lower(), item[2]))
    popular_path_rows = [
        f"| [{repository_short_name(repository)}](https://github.com/{repository}) | "
        f"{html.escape(title)} | `{html.escape(path)}` | {count} |"
        for count, repository, path, title, _day in path_rows[:10]
    ]
    if not popular_path_rows:
        popular_path_rows = ["| No snapshot data yet | — | — | 0 |"]

    return f"""# Portfolio dashboard

Automatically generated from the repository snapshots in [`data/all-repositories.json`](data/all-repositories.json). Updated: `{html.escape(updated_at)}`.

## At a glance

| Repositories | Stars | Forks | Tracked clones | Tracked views |
| ---: | ---: | ---: | ---: | ---: |
| {int(aggregate.get('repository_count', 0))} | {int(totals.get('stars', 0))} | {int(totals.get('forks', 0))} | {int(totals.get('clones', 0))} | {int(totals.get('views', 0))} |

| Window | Clones | Views |
| --- | ---: | ---: |
| Last 7 days | {int(last_7_days.get('clones', 0))} | {int(last_7_days.get('views', 0))} |
| Last 30 days | {int(last_30_days.get('clones', 0))} | {int(last_30_days.get('views', 0))} |

## Most active repositories

Ranked by combined views and clones in the last 30 days.

| Repository | Views (30d) | Clones (30d) | Stars | Traffic |
| --- | ---: | ---: | ---: | --- |
{chr(10).join(repo_rows) if repo_rows else '| No repository data yet | 0 | 0 | 0 | — |'}

## Latest traffic sources

The table combines the latest available GitHub popular-referrers snapshots for each repository. These are current snapshots, not lifetime totals. Snapshot date: `{html.escape(referrer_day)}`.

| Referrer | Snapshot views |
| --- | ---: |
{chr(10).join(referrer_rows)}

## Latest popular pages

The table combines the latest available popular-path snapshots. It helps identify which repository pages people are opening, but it is not a historical page-view total. Individual snapshot dates may differ.

| Repository | Page | Path | Snapshot views |
| --- | --- | --- | ---: |
{chr(10).join(popular_path_rows)}

Individual repository badges and full traffic charts are available under [`badges/`](badges/) and [`charts/`](charts/).

> Traffic history begins when collection first succeeds for each repository. Referrers and popular paths are stored as dated GitHub snapshots and must not be added together as lifetime traffic.
"""


def render_portfolio() -> None:
    if AGGREGATE_PATH.exists():
        write_text(PORTFOLIO_PATH, portfolio_markdown(load_json(AGGREGATE_PATH)))


def render_recipe_previews(root: Path) -> None:
    if not PREVIEW_RECIPES.exists():
        return
    recipes = load_json(PREVIEW_RECIPES)
    for recipe in recipes:
        filename = str(recipe.get("filename", "")).strip()
        if not filename or "/" in filename or "\\" in filename:
            continue
        write_text(root / filename, render_badge(BadgeConfig.from_dict(recipe)))


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
    badge_directory = BADGE_ROOT / repo_name

    write_metric_badge(badge_directory, "clones.svg", "clones", summary.get("clones", 0))
    write_metric_badge(badge_directory, "views.svg", "views", summary.get("views", 0))

    last_7_days = summary.get("last_7_days", {})
    write_metric_badge(badge_directory, "clones-7d.svg", "clones 7d", last_7_days.get("clones", 0))
    write_metric_badge(badge_directory, "views-7d.svg", "views 7d", last_7_days.get("views", 0))

    last_30_days = summary.get("last_30_days", {})
    write_metric_badge(badge_directory, "clones-30d.svg", "clones 30d", last_30_days.get("clones", 0))
    write_metric_badge(badge_directory, "views-30d.svg", "views 30d", last_30_days.get("views", 0))

    snapshot = summary.get("repository_snapshot", {})
    write_metric_badge(badge_directory, "stars.svg", "stars", snapshot.get("stars", 0))
    write_metric_badge(badge_directory, "forks.svg", "forks", snapshot.get("forks", 0))

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

    render_portfolio()
    print(f"Rendered local badges and charts for {generated} repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
