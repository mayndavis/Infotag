"""Tests for the ReportGenerator module."""

import unittest
import tempfile
import shutil
from pathlib import Path

from automation.report_generator import ReportGenerator
from automation.sources import SourceCollector
from automation.fact_checker import FactChecker
from automation.investment_analyzer import InvestmentAnalyzer


class TestReportGenerator(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.generator = ReportGenerator(repo_root=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_full_report_generation_cycle(self):
        collector = SourceCollector()
        sources = collector.get_verified_baseline_sources()[:3]
        checker = FactChecker()
        claims = checker.fact_check_all_sources(sources)
        analyzer = InvestmentAnalyzer()
        briefs = analyzer.generate_briefs_from_sources(sources, claims, "2026-11-21")

        files = self.generator.generate_all_reports(
            publication_date="2026-11-21",
            start_date="2026-11-18",
            end_date="2026-11-21",
            sources=sources,
            claims=claims,
            briefs=briefs
        )

        self.assertGreater(len(files), 4)

        # Verify key required files exist
        update_dir = self.test_dir / "Updates" / "Provider" / "2026-11-21"
        self.assertTrue((update_dir / "README.md").exists())
        self.assertTrue((update_dir / "metadata.json").exists())
        self.assertTrue((update_dir / "Data" / "02-Master-Reports" / "Technology-Market" / "Technology-Market-Research-Report-2026-11-21.md").exists())
        self.assertTrue((update_dir / "Data" / "02-Master-Reports" / "Fact-Checks" / "Fact-Check-Report-2026-11-21.md").exists())
        self.assertTrue((update_dir / "Data" / "05-Investment-Outlook" / "Investment-Outlook-2026-11-21.md").exists())
        self.assertTrue((update_dir / "Data" / "06-Sources-and-References" / "Source-Register-2026-11-21.md").exists())

        # Verify initial_briefs.json sync
        briefs_json = self.test_dir / "data" / "initial_briefs.json"
        self.assertTrue(briefs_json.exists())


if __name__ == "__main__":
    unittest.main()
