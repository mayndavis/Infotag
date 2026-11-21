"""Unified Autonomous Pipeline Runner for Infotag.

Orchestrates cadence checking, multi-source intelligence gathering,
fact-checking, investment synthesis, report generation, and GitHub publishing.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import argparse
import logging
import sys
import os

from automation.config import (
    REPO_ROOT,
    PUBLISHING_INTERVAL_HOURS,
    EAT_TIMEZONE,
    DEFAULT_PROVIDER_NAME
)
from automation.interval_checker import evaluate_publishing_cadence, get_latest_update_info
from automation.sources import SourceCollector
from automation.fact_checker import FactChecker
from automation.investment_analyzer import InvestmentAnalyzer
from automation.report_generator import ReportGenerator
from automation.publisher import GitHubPublisher
from automation.monitor import (
    ExecutionMonitor,
    STATUS_SUCCESS,
    STATUS_PARTIAL_SUCCESS,
    STATUS_FAILED,
    STATUS_SKIPPED
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("InfotagPipeline")


def run_pipeline(
    repo_root: Path = REPO_ROOT,
    force: bool = False,
    dry_run: bool = False,
    lookback_days: int = 3,
    target_date: str = None
) -> int:
    """Executes the full autonomous Infotag research and publishing cycle."""
    start_dt = datetime.now(timezone.utc)
    now_eat = start_dt.astimezone(EAT_TIMEZONE)
    monitor = ExecutionMonitor(repo_root=repo_root)

    print("\n==================================================================")
    print("      INFOTAG AUTONOMOUS TECHNOLOGY INVESTMENT INTELLIGENCE       ")
    print("==================================================================")
    print(f"Timestamp (EAT):    {now_eat.strftime('%Y-%m-%d %H:%M:%S EAT')}")
    print(f"Repository Root:    {repo_root}")
    print(f"Execution Mode:     {'DRY RUN (No Commit/Push)' if dry_run else 'PRODUCTION PUBLISHING'}")
    print(f"Force Override:     {force}")
    print("==================================================================\n")

    # Step 1: Interval Cadence Check
    cadence = evaluate_publishing_cadence(repo_root=repo_root, current_dt=start_dt, force=force)
    if not cadence["is_due"]:
        logger.info(f"Skipping execution: {cadence['reason']}")
        completion_dt = datetime.now(timezone.utc)
        monitor.create_execution_record(
            start_dt=start_dt,
            completion_dt=completion_dt,
            start_date=cadence.get("last_publication_date", "N/A"),
            end_date=now_eat.strftime("%Y-%m-%d"),
            sources_count=0,
            findings_count=0,
            claims_count=0,
            reports_count=0,
            files_published=[],
            commit_sha=None,
            status=STATUS_SKIPPED,
            warnings=[cadence["reason"]],
            trigger="manual" if force else "scheduled"
        )
        print(f"\n[CADENCE GATE] {cadence['reason']}")
        print("Pipeline finished with status: SKIPPED (Clean Exit)\n")
        return 0

    # Step 2: Establish Publication and Coverage Dates
    pub_date = target_date if target_date else now_eat.strftime("%Y-%m-%d")
    last_info = get_latest_update_info(repo_root / "Updates" / "Provider")

    if last_info["exists"] and last_info["publication_date_str"] != pub_date:
        start_date = last_info["publication_date_str"]
    else:
        calc_start = (datetime.strptime(pub_date, "%Y-%m-%d") - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        start_date = calc_start

    end_date = pub_date

    logger.info(f"Established Research Period: {start_date} to {end_date} (Publication Date: {pub_date})")

    try:
        # Step 3: Multi-Source Research Gathering
        logger.info("Executing Stage A-D: Multi-channel technology source gathering...")
        collector = SourceCollector()
        sources = collector.collect_all_sources()
        if not sources:
            raise ValueError("No research sources could be retrieved or validated.")
        logger.info(f"Audited {len(sources)} primary and secondary source records.")

        # Step 4: Independent Fact-Checking
        logger.info("Executing Stage 5: Independent claim corroboration and fact-checking...")
        checker = FactChecker()
        claims = checker.fact_check_all_sources(sources)
        logger.info(f"Verified {len(claims)} individual propositions across source hierarchy.")

        # Step 5: Investment Intelligence Synthesis
        logger.info("Executing Stage 6: 4-Quadrant institutional investment brief synthesis...")
        analyzer = InvestmentAnalyzer()
        briefs = analyzer.generate_briefs_from_sources(sources, claims, publication_date=pub_date)
        logger.info(f"Synthesized {len(briefs)} institutional investment briefs.")

        # Step 6: Markdown Report and Metadata Generation
        logger.info("Executing Stage 7: Infotag specification Markdown report generation...")
        generator = ReportGenerator(repo_root=repo_root)
        generated_files = generator.generate_all_reports(
            publication_date=pub_date,
            start_date=start_date,
            end_date=end_date,
            sources=sources,
            claims=claims,
            briefs=briefs
        )
        logger.info(f"Generated {len(generated_files)} report and metadata files on disk.")

        # Step 7: Pre-Publication Quality Audit & GitHub Publishing
        logger.info("Executing Stage 8: Quality checklist validation and Git publishing...")
        publisher = GitHubPublisher(repo_root=repo_root)
        pub_result = publisher.publish_update(
            publication_date=pub_date,
            generated_files=generated_files,
            dry_run=dry_run
        )

        if not pub_result["success"]:
            raise RuntimeError(f"Publishing validation or git error: {pub_result['message']} - {pub_result['errors']}")

        commit_sha = pub_result.get("commit_sha")
        logger.info(f"Publication Result: {pub_result['message']}")

        # Step 8: Execution Logging & Dashboard Update
        completion_dt = datetime.now(timezone.utc)
        files_rel = [str(f.relative_to(repo_root)) for f in generated_files]
        status = STATUS_SUCCESS if pub_result["success"] else STATUS_PARTIAL_SUCCESS

        record = monitor.create_execution_record(
            start_dt=start_dt,
            completion_dt=completion_dt,
            start_date=start_date,
            end_date=end_date,
            sources_count=len(sources),
            findings_count=len(briefs),
            claims_count=len(claims),
            reports_count=len(generated_files),
            files_published=files_rel,
            commit_sha=commit_sha,
            status=status,
            errors=pub_result.get("errors", []),
            trigger="manual" if force else "scheduled"
        )

        print("\n==================================================================")
        print("               RESEARCH PIPELINE COMPLETED SUCCESSFULLY           ")
        print("==================================================================")
        print(f"Execution ID:         {record.execution_id}")
        print(f"Publication Date:     {pub_date}")
        print(f"Coverage Window:      {start_date} to {end_date}")
        print(f"Sources Examined:     {len(sources)}")
        print(f"Claims Verified:      {len(claims)}")
        print(f"Briefs Generated:     {len(briefs)}")
        print(f"Files Created:        {len(generated_files)}")
        print(f"Commit SHA:           {commit_sha or 'Dry Run'}")
        print(f"Duration:             {record.duration_seconds}s")
        print(f"Status:               {status}")
        print("==================================================================\n")
        return 0

    except Exception as e:
        logger.error(f"Pipeline execution encountered failure: {e}", exc_info=True)
        completion_dt = datetime.now(timezone.utc)
        monitor.create_execution_record(
            start_dt=start_dt,
            completion_dt=completion_dt,
            start_date=start_date if 'start_date' in locals() else "N/A",
            end_date=end_date if 'end_date' in locals() else "N/A",
            sources_count=len(sources) if 'sources' in locals() else 0,
            findings_count=len(briefs) if 'briefs' in locals() else 0,
            claims_count=len(claims) if 'claims' in locals() else 0,
            reports_count=len(generated_files) if 'generated_files' in locals() else 0,
            files_published=[],
            commit_sha=None,
            status=STATUS_FAILED,
            errors=[str(e)],
            trigger="manual" if force else "scheduled"
        )
        print(f"\n[PIPELINE ERROR] Execution failed: {e}\n")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Infotag Autonomous Research Pipeline Runner")
    parser.add_argument("--repo-root", type=str, default=str(REPO_ROOT), help="Path to repository root")
    parser.add_argument("--force", action="store_true", help="Bypass 72-hour interval check")
    parser.add_argument("--dry-run", action="store_true", help="Validate and generate without committing or pushing")
    parser.add_argument("--lookback-days", type=int, default=3, help="Default lookback days if no previous update")
    parser.add_argument("--target-date", type=str, default=None, help="Explicit publication date override (YYYY-MM-DD)")

    args = parser.parse_args()
    root = Path(args.repo_root)

    return run_pipeline(
        repo_root=root,
        force=args.force,
        dry_run=args.dry_run,
        lookback_days=args.lookback_days,
        target_date=args.target_date
    )


if __name__ == "__main__":
    sys.exit(main())
