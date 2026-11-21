"""Interval and Scheduling Manager for Infotag Autonomous Updates.

Verifies whether at least 72 hours have elapsed since the last published update
to prevent naive calendar-day edge cases and support manual overrides.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import argparse
import json
import re
import sys
import os

from automation.config import (
    REPO_ROOT,
    UPDATES_DIR,
    PUBLISHING_INTERVAL_HOURS,
    EAT_TIMEZONE,
    EAT_OFFSET
)


def parse_iso_date(date_str: str) -> datetime:
    """Parses YYYY-MM-DD string into a timezone-aware datetime at 06:00 EAT (03:00 UTC)."""
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    # Assume targeted 06:00 EAT publication time
    return datetime(d.year, d.month, d.day, 6, 0, 0, tzinfo=EAT_TIMEZONE)


def get_latest_update_info(updates_dir: Path = UPDATES_DIR) -> dict:
    """Discovers the latest published update directory in Updates/Provider/."""
    if not updates_dir.exists():
        return {
            "exists": False,
            "publication_date_str": None,
            "publication_datetime": None,
            "update_id": None,
            "dir_path": None
        }

    date_dirs = []
    for item in updates_dir.iterdir():
        if item.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", item.name):
            date_dirs.append(item)

    if not date_dirs:
        return {
            "exists": False,
            "publication_date_str": None,
            "publication_datetime": None,
            "update_id": None,
            "dir_path": None
        }

    # Sort lexicographically by date YYYY-MM-DD
    date_dirs.sort(key=lambda p: p.name)
    latest_dir = date_dirs[-1]
    date_str = latest_dir.name
    pub_dt = parse_iso_date(date_str)

    update_id = f"infotag-{date_str}"
    metadata_file = latest_dir / "metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
                update_id = meta.get("update_id", update_id)
                # Check for explicit published timestamp if provided
                if "published_at" in meta:
                    try:
                        pub_dt = datetime.fromisoformat(meta["published_at"])
                    except Exception:
                        pass
        except Exception:
            pass

    return {
        "exists": True,
        "publication_date_str": date_str,
        "publication_datetime": pub_dt,
        "update_id": update_id,
        "dir_path": latest_dir
    }


def evaluate_publishing_cadence(
    repo_root: Path = REPO_ROOT,
    current_dt: datetime = None,
    interval_hours: float = PUBLISHING_INTERVAL_HOURS,
    force: bool = False
) -> dict:
    """Evaluates whether an automated research update is due.

    Returns a dict with:
      - is_due: bool
      - reason: str
      - elapsed_hours: float
      - last_publication_date: str
      - next_eligible_datetime: str
      - force_run: bool
    """
    if current_dt is None:
        current_dt = datetime.now(timezone.utc)
    elif current_dt.tzinfo is None:
        current_dt = current_dt.replace(tzinfo=timezone.utc)

    updates_dir = repo_root / "Updates" / "Provider"
    latest_info = get_latest_update_info(updates_dir)

    if force:
        return {
            "is_due": True,
            "reason": "Execution forced via manual dispatch or explicit override.",
            "elapsed_hours": None,
            "last_publication_date": latest_info.get("publication_date_str"),
            "next_eligible_datetime": None,
            "force_run": True,
            "current_time_eat": current_dt.astimezone(EAT_TIMEZONE).isoformat()
        }

    if not latest_info["exists"]:
        return {
            "is_due": True,
            "reason": "No previous publication directories discovered; baseline update required.",
            "elapsed_hours": 999.0,
            "last_publication_date": None,
            "next_eligible_datetime": None,
            "force_run": False,
            "current_time_eat": current_dt.astimezone(EAT_TIMEZONE).isoformat()
        }

    last_pub_dt = latest_info["publication_datetime"]
    elapsed_seconds = (current_dt - last_pub_dt).total_seconds()
    elapsed_hours = elapsed_seconds / 3600.0

    next_eligible_dt = last_pub_dt + timedelta(hours=interval_hours)
    next_eligible_eat_str = next_eligible_dt.astimezone(EAT_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S EAT")

    if elapsed_hours >= interval_hours:
        return {
            "is_due": True,
            "reason": (
                f"Elapsed time ({elapsed_hours:.1f} hours) exceeds configured "
                f"{interval_hours:.1f}-hour interval threshold."
            ),
            "elapsed_hours": round(elapsed_hours, 2),
            "last_publication_date": latest_info["publication_date_str"],
            "next_eligible_datetime": next_eligible_eat_str,
            "force_run": False,
            "current_time_eat": current_dt.astimezone(EAT_TIMEZONE).isoformat()
        }
    else:
        remaining_hours = interval_hours - elapsed_hours
        return {
            "is_due": False,
            "reason": (
                f"Update not due yet: {elapsed_hours:.1f} hours elapsed since {latest_info['publication_date_str']}. "
                f"Requires {remaining_hours:.1f} more hours (due at {next_eligible_eat_str})."
            ),
            "elapsed_hours": round(elapsed_hours, 2),
            "last_publication_date": latest_info["publication_date_str"],
            "next_eligible_datetime": next_eligible_eat_str,
            "force_run": False,
            "current_time_eat": current_dt.astimezone(EAT_TIMEZONE).isoformat()
        }


def main():
    parser = argparse.ArgumentParser(description="Infotag 72-Hour Publishing Cadence Checker")
    parser.add_argument("--repo-root", type=str, default=str(REPO_ROOT), help="Path to repository root")
    parser.add_argument("--force", action="store_true", help="Force update execution regardless of interval")
    parser.add_argument("--interval", type=float, default=PUBLISHING_INTERVAL_HOURS, help="Interval in hours")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON only")
    parser.add_argument("--github-output", action="store_true", help="Append results to GITHUB_OUTPUT environment file")

    args = parser.parse_args()
    root = Path(args.repo_root)
    result = evaluate_publishing_cadence(repo_root=root, interval_hours=args.interval, force=args.force)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n=======================================================")
        print("          INFOTAG PUBLISHING CADENCE CHECKER           ")
        print("=======================================================")
        print(f"Current Time (EAT):    {result['current_time_eat']}")
        print(f"Last Publication:     {result['last_publication_date'] or 'None'}")
        print(f"Hours Elapsed:        {result['elapsed_hours'] if result['elapsed_hours'] is not None else 'N/A'}")
        print(f"Next Due Time:        {result['next_eligible_datetime'] or 'Immediate'}")
        print(f"Status:               {'DUE FOR UPDATE' if result['is_due'] else 'SKIPPED (NOT DUE)'}")
        print(f"Reason:               {result['reason']}")
        print("=======================================================\n")

    if args.github_output:
        github_output_path = os.environ.get("GITHUB_OUTPUT")
        if github_output_path:
            with open(github_output_path, "a", encoding="utf-8") as f:
                f.write(f"is_due={'true' if result['is_due'] else 'false'}\n")
                f.write(f"elapsed_hours={result['elapsed_hours'] or 0}\n")
                f.write(f"last_date={result['last_publication_date'] or ''}\n")
                f.write(f"force_run={'true' if result['force_run'] else 'false'}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
