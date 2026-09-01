from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    temporary.replace(path)


def build_chart_data(repository_dir: Path) -> bool:
    daily_path = repository_dir / "daily.json"
    summary_path = repository_dir / "summary.json"
    if not daily_path.exists() or not summary_path.exists():
        return False

    daily = load_json(daily_path)
    summary = load_json(summary_path)
    days = daily.get("days", {})
    dates = sorted(days)

    chart_data = {
        "repository": daily.get("repository"),
        "tracking_since": summary.get("tracking_since"),
        "updated_at": summary.get("updated_at"),
        "dates": dates,
        "clones": [int(days[day].get("clones", 0)) for day in dates],
        "views": [int(days[day].get("views", 0)) for day in dates],
        "unique_cloners": [int(days[day].get("unique_cloners", 0)) for day in dates],
        "unique_visitors": [int(days[day].get("unique_visitors", 0)) for day in dates],
    }
    save_json(repository_dir / "chart-data.json", chart_data)
    return True


def main() -> int:
    generated = 0
    if not DATA_ROOT.exists():
        print("No data directory found")
        return 0

    for repository_dir in sorted(DATA_ROOT.iterdir()):
        if repository_dir.is_dir() and build_chart_data(repository_dir):
            generated += 1

    print(f"Generated chart data for {generated} repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
