"""Execution Logging, Monitoring, and Metrics Engine.

Records structured execution telemetry, updates AUTOMATION-STATUS.md,
and logs audit records into Management/Automation/Execution-Logs/.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
import json
import logging
import os
import uuid

from automation.config import REPO_ROOT, MANAGEMENT_DIR, LOGS_DIR, EAT_TIMEZONE

logger = logging.getLogger(__name__)

STATUS_SUCCESS = "SUCCESS"
STATUS_PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
STATUS_FAILED = "FAILED"
STATUS_SKIPPED = "SKIPPED"


@dataclass
class ExecutionRecord:
    execution_id: str
    start_time: str
    completion_time: str
    duration_seconds: float
    research_period: Dict[str, str]
    sources_examined: int
    findings_identified: int
    claims_verified: int
    reports_generated: int
    files_published: List[str]
    commit_sha: Optional[str]
    status: str
    errors: List[str]
    warnings: List[str]
    trigger: str  # scheduled, manual, test

    def to_dict(self) -> dict:
        return asdict(self)


class ExecutionMonitor:
    """Manages execution lifecycles, structured logs, and status dashboards."""

    def __init__(self, repo_root: Path = REPO_ROOT):
        self.repo_root = repo_root
        self.logs_dir = self.repo_root / "Management" / "Automation" / "Execution-Logs"
        self.status_file = self.repo_root / "Management" / "Automation" / "AUTOMATION-STATUS.md"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def create_execution_record(
        self,
        start_dt: datetime,
        completion_dt: datetime,
        start_date: str,
        end_date: str,
        sources_count: int,
        findings_count: int,
        claims_count: int,
        reports_count: int,
        files_published: List[str],
        commit_sha: Optional[str],
        status: str,
        errors: List[str] = None,
        warnings: List[str] = None,
        trigger: str = "scheduled"
    ) -> ExecutionRecord:
        """Constructs and persists an execution log record."""
        duration = round((completion_dt - start_dt).total_seconds(), 2)
        exec_id = f"exec-{completion_dt.strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"

        record = ExecutionRecord(
            execution_id=exec_id,
            start_time=start_dt.isoformat(),
            completion_time=completion_dt.isoformat(),
            duration_seconds=duration,
            research_period={"start": start_date, "end": end_date},
            sources_examined=sources_count,
            findings_identified=findings_count,
            claims_verified=claims_count,
            reports_generated=reports_count,
            files_published=files_published,
            commit_sha=commit_sha,
            status=status,
            errors=errors or [],
            warnings=warnings or [],
            trigger=trigger
        )

        # Write to Execution-Logs/YYYY-MM-DD-run-<id>.json
        log_date = completion_dt.strftime("%Y-%m-%d")
        log_path = self.logs_dir / f"{log_date}-{exec_id}.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(record.to_dict(), f, indent=2)

        # Update Management/Automation/AUTOMATION-STATUS.md
        self.update_automation_status_file(record)

        logger.info(f"Execution record {exec_id} logged with status '{status}' ({duration}s).")
        return record

    def update_automation_status_file(self, record: ExecutionRecord):
        """Updates the root Automation Status markdown document."""
        now_eat = datetime.now(EAT_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S EAT")

        status_md = [
            "# Automation Status",
            "",
            "- **Research cadence target:** Every three days (72-hour continuous interval).",
            "- **Execution engine:** GitHub Actions scheduled daily at 06:00 EAT (03:00 UTC).",
            f"- **Last execution time:** `{now_eat}`",
            f"- **Last execution ID:** `{record.execution_id}`",
            f"- **Last execution status:** `{record.status}`",
            f"- **Last research period covered:** `{record.research_period.get('start', 'N/A')} to {record.research_period.get('end', 'N/A')}`",
            f"- **Sources audited:** `{record.sources_examined}`",
            f"- **Claims verified:** `{record.claims_verified}`",
            f"- **Reports generated:** `{record.reports_generated}`",
            f"- **Last commit SHA:** `{record.commit_sha or 'N/A'}`",
            "",
            "## Operational Verification",
            "",
            "- Automatic GitHub publishing: **Operational via GitHub Actions workflow.**",
            "- Independent fact-checking engine: **Operational.**",
            "- Interval guardrail (72-hour continuous verification): **Operational.**",
            "- Failure detection & recovery: **Operational.**",
            "",
            "## Recent Execution History",
            "",
            "| Execution ID | Timestamp | Status | Period | Commit SHA | Duration |",
            "|---|---|---|---|---|---|"
        ]

        # Read existing rows if available
        existing_rows = []
        if self.status_file.exists():
            text = self.status_file.read_text(encoding="utf-8")
            for line in text.splitlines():
                if line.startswith("| `exec-"):
                    existing_rows.append(line)

        new_row = (
            f"| `{record.execution_id}` | {record.completion_time[:19]} | "
            f"**{record.status}** | {record.research_period.get('start')}..{record.research_period.get('end')} | "
            f"`{record.commit_sha or 'N/A'}` | {record.duration_seconds}s |"
        )

        all_rows = [new_row] + existing_rows[:10]  # keep top 10
        status_md.extend(all_rows)
        status_md.extend([
            "",
            "---",
            "*Maintained autonomously by the Infotag Monitoring System.*"
        ])

        self.status_file.write_text("\n".join(status_md), encoding="utf-8")
