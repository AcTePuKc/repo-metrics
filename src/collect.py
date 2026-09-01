from __future__ import annotations

import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "repositories.json"
DATA_ROOT = ROOT / "data"
BADGE_ROOT = ROOT / "badges"
AGGREGATE_PATH = DATA_ROOT / "all-repositories.json"
API_ROOT = "https://api.github.com"


def api_get(path: str, token: str) -> Any:
    request = urllib.request.Request(
        f"{API_ROOT}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "repo-metrics",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    temporary.replace(path)


def discover_repositories(config: dict[str, Any], token: str) -> list[dict[str, Any]]:
    owner = config["owner"]
    include_archived = bool(config.get("include_archived", False))
    include_forks = bool(config.get("include_forks", True))
    excluded = set(config.get("exclude", []))

    repositories: list[dict[str, Any]] = []
    page = 1
    while True:
        query = urllib.parse.urlencode(
            {
                "type": "owner",
                "sort": "full_name",
                "direction": "asc",
                "per_page": 100,
                "page": page,
            }
        )
        batch = api_get(f"/users/{owner}/repos?{query}", token)
        if not batch:
            break

        for repository in batch:
            full_name = repository["full_name"]
            if full_name in excluded or repository["name"] in excluded:
                continue
            if repository.get("private", False):
                continue
            if repository.get("archived", False) and not include_archived:
                continue
            if repository.get("fork", False) and not include_forks:
                continue
            repositories.append(repository)

        if len(batch) < 100:
            break
        page += 1

    return repositories


def metric_days(payload: dict[str, Any], key: str, unique_key: str) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for item in payload.get(key, []):
        day = item["timestamp"][:10]
        result[day] = {
            key: int(item.get("count", 0)),
            unique_key: int(item.get("uniques", 0)),
        }
    return result


def merge_daily(existing: dict[str, Any], clones: dict[str, Any], views: dict[str, Any]) -> dict[str, Any]:
    days = dict(existing.get("days", {}))

    clone_days = metric_days(clones, "clones", "unique_cloners")
    view_days = metric_days(views, "views", "unique_visitors")
    for day in sorted(set(clone_days) | set(view_days)):
        current = dict(days.get(day, {}))
        current.update(clone_days.get(day, {}))
        current.update(view_days.get(day, {}))
        current.setdefault("clones", 0)
        current.setdefault("unique_cloners", 0)
        current.setdefault("views", 0)
        current.setdefault("unique_visitors", 0)
        days[day] = current

    return dict(sorted(days.items()))


def sum_window(days: dict[str, Any], window_days: int, end_day: date) -> dict[str, int]:
    start_day = end_day - timedelta(days=window_days - 1)
    selected = [
        values
        for day, values in days.items()
        if start_day <= date.fromisoformat(day) <= end_day
    ]
    return {
        "clones": sum(int(item.get("clones", 0)) for item in selected),
        "unique_cloners_daily_sum": sum(int(item.get("unique_cloners", 0)) for item in selected),
        "views": sum(int(item.get("views", 0)) for item in selected),
        "unique_visitors_daily_sum": sum(int(item.get("unique_visitors", 0)) for item in selected),
    }


def build_summary(
    full_name: str,
    days: dict[str, Any],
    updated_at: str,
    repository_snapshot: dict[str, int],
) -> dict[str, Any]:
    ordered_dates = sorted(days)
    end_day = date.fromisoformat(ordered_dates[-1]) if ordered_dates else date.fromisoformat(updated_at[:10])
    return {
        "repository": full_name,
        "tracking_since": ordered_dates[0] if ordered_dates else None,
        "updated_at": updated_at,
        "days_tracked": len(ordered_dates),
        "clones": sum(int(day.get("clones", 0)) for day in days.values()),
        "unique_cloners_daily_sum": sum(int(day.get("unique_cloners", 0)) for day in days.values()),
        "views": sum(int(day.get("views", 0)) for day in days.values()),
        "unique_visitors_daily_sum": sum(int(day.get("unique_visitors", 0)) for day in days.values()),
        "last_7_days": sum_window(days, 7, end_day),
        "last_30_days": sum_window(days, 30, end_day),
        "repository_snapshot": repository_snapshot,
    }


def repository_snapshot(details: dict[str, Any]) -> dict[str, int]:
    return {
        "stars": int(details.get("stargazers_count", 0)),
        "forks": int(details.get("forks_count", 0)),
        "watchers": int(details.get("subscribers_count", 0)),
        "open_issues": int(details.get("open_issues_count", 0)),
    }


def save_snapshot_history(path: Path, day: str, snapshot: Any, repository: str) -> None:
    existing = load_json(path, {"repository": repository, "days": {}})
    days = dict(existing.get("days", {}))
    days[day] = snapshot
    save_json(path, {"repository": repository, "days": dict(sorted(days.items()))})


def normalize_referrers(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "referrer": str(item.get("referrer", "")),
            "count": int(item.get("count", 0)),
            "uniques": int(item.get("uniques", 0)),
        }
        for item in items
    ]


def normalize_paths(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "path": str(item.get("path", "")),
            "title": str(item.get("title", "")),
            "count": int(item.get("count", 0)),
            "uniques": int(item.get("uniques", 0)),
        }
        for item in items
    ]


def compact_number(value: int) -> str:
    if value < 1_000:
        return str(value)
    if value < 1_000_000:
        number = value / 1_000
        suffix = "k"
    elif value < 1_000_000_000:
        number = value / 1_000_000
        suffix = "M"
    else:
        number = value / 1_000_000_000
        suffix = "B"
    rendered = f"{number:.1f}".rstrip("0").rstrip(".")
    return f"{rendered}{suffix}"


def badge_svg(label: str, value: int) -> str:
    message = compact_number(value)
    label_width = max(54, 7 * len(label) + 14)
    value_width = max(42, 7 * len(message) + 14)
    total_width = label_width + value_width
    label_mid = label_width / 2
    value_mid = label_width + value_width / 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {message}">
  <title>{label}: {message}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r"><rect width="{total_width}" height="20" rx="3"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="#007ec6"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{label_mid}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_mid}" y="14">{label}</text>
    <text x="{value_mid}" y="15" fill="#010101" fill-opacity=".3">{message}</text>
    <text x="{value_mid}" y="14">{message}</text>
  </g>
</svg>
'''


def save_badges(repo_name: str, summary: dict[str, Any]) -> None:
    directory = BADGE_ROOT / repo_name
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "clones.svg").write_text(
        badge_svg("clones", int(summary["clones"])), encoding="utf-8", newline="\n"
    )
    (directory / "views.svg").write_text(
        badge_svg("views", int(summary["views"])), encoding="utf-8", newline="\n"
    )


def remove_stale_public_data(active_repo_names: set[str]) -> None:
    for root in (DATA_ROOT, BADGE_ROOT):
        if not root.exists():
            continue
        for child in root.iterdir():
            if child.is_dir() and child.name not in active_repo_names:
                shutil.rmtree(child)


def collect_repository(repository: dict[str, Any], token: str, updated_at: str) -> dict[str, Any] | None:
    full_name = repository["full_name"]
    repo_name = repository["name"]
    encoded_owner, encoded_repo = [urllib.parse.quote(part, safe="") for part in full_name.split("/", 1)]

    try:
        clones = api_get(f"/repos/{encoded_owner}/{encoded_repo}/traffic/clones?per=day", token)
        views = api_get(f"/repos/{encoded_owner}/{encoded_repo}/traffic/views?per=day", token)
        referrers = api_get(f"/repos/{encoded_owner}/{encoded_repo}/traffic/popular/referrers", token)
        paths = api_get(f"/repos/{encoded_owner}/{encoded_repo}/traffic/popular/paths", token)
        details = api_get(f"/repos/{encoded_owner}/{encoded_repo}", token)
    except urllib.error.HTTPError as error:
        print(f"WARNING: {full_name}: GitHub API returned HTTP {error.code}", file=sys.stderr)
        return None

    daily_path = DATA_ROOT / repo_name / "daily.json"
    existing = load_json(daily_path, {"repository": full_name, "days": {}})
    days = merge_daily(existing, clones, views)
    snapshot = repository_snapshot(details)
    snapshot_day = updated_at[:10]

    summary = build_summary(full_name, days, updated_at, snapshot)
    save_json(daily_path, {"repository": full_name, "days": days})
    save_json(DATA_ROOT / repo_name / "summary.json", summary)
    save_snapshot_history(
        DATA_ROOT / repo_name / "repository-history.json",
        snapshot_day,
        snapshot,
        full_name,
    )
    save_snapshot_history(
        DATA_ROOT / repo_name / "referrers-history.json",
        snapshot_day,
        normalize_referrers(referrers),
        full_name,
    )
    save_snapshot_history(
        DATA_ROOT / repo_name / "popular-paths-history.json",
        snapshot_day,
        normalize_paths(paths),
        full_name,
    )
    save_badges(repo_name, summary)

    print(
        f"{full_name}: {summary['clones']} clones, {summary['views']} views, "
        f"{summary['days_tracked']} days tracked, {snapshot['stars']} stars"
    )
    return summary


def build_aggregate(summaries: list[dict[str, Any]], updated_at: str) -> dict[str, Any]:
    repositories = {
        summary["repository"]: {
            "clones": summary["clones"],
            "views": summary["views"],
            "last_7_days": summary["last_7_days"],
            "last_30_days": summary["last_30_days"],
            "repository_snapshot": summary["repository_snapshot"],
            "tracking_since": summary["tracking_since"],
        }
        for summary in sorted(summaries, key=lambda item: item["repository"].lower())
    }

    return {
        "updated_at": updated_at,
        "repository_count": len(summaries),
        "totals": {
            "clones": sum(int(summary["clones"]) for summary in summaries),
            "views": sum(int(summary["views"]) for summary in summaries),
            "stars": sum(int(summary["repository_snapshot"]["stars"]) for summary in summaries),
            "forks": sum(int(summary["repository_snapshot"]["forks"]) for summary in summaries),
            "watchers": sum(int(summary["repository_snapshot"]["watchers"]) for summary in summaries),
        },
        "last_7_days": {
            "clones": sum(int(summary["last_7_days"]["clones"]) for summary in summaries),
            "views": sum(int(summary["last_7_days"]["views"]) for summary in summaries),
        },
        "last_30_days": {
            "clones": sum(int(summary["last_30_days"]["clones"]) for summary in summaries),
            "views": sum(int(summary["last_30_days"]["views"]) for summary in summaries),
        },
        "repositories": repositories,
    }


def main() -> int:
    token = os.environ.get("GH_TRAFFIC_TOKEN", "").strip()
    if not token:
        print("GH_TRAFFIC_TOKEN is required", file=sys.stderr)
        return 2

    config = load_json(CONFIG_PATH, {})
    if not config.get("discover_public_repositories", True):
        print("Only public repository discovery mode is currently supported", file=sys.stderr)
        return 2

    repositories = discover_repositories(config, token)
    if not repositories:
        print("No public repositories discovered", file=sys.stderr)
        return 1

    active_repo_names = {repository["name"] for repository in repositories}
    remove_stale_public_data(active_repo_names)

    updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    summaries: list[dict[str, Any]] = []
    failed = 0
    for repository in repositories:
        summary = collect_repository(repository, token, updated_at)
        if summary is not None:
            summaries.append(summary)
        else:
            failed += 1

    if summaries:
        save_json(AGGREGATE_PATH, build_aggregate(summaries, updated_at))

    print(f"Collection complete: {len(summaries)} successful, {failed} failed")
    return 0 if summaries else 1


if __name__ == "__main__":
    raise SystemExit(main())
