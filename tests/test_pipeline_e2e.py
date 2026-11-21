"""End-to-End Pipeline Integration Tests."""

import unittest
import tempfile
import shutil
from pathlib import Path

from automation.run_pipeline import run_pipeline


class TestPipelineE2E(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        # Set up minimal repository skeleton
        (self.test_dir / "Updates" / "Provider").mkdir(parents=True)
        (self.test_dir / "Management" / "Automation").mkdir(parents=True)
        (self.test_dir / "Management" / "Indexes").mkdir(parents=True)
        (self.test_dir / "Management" / "Change-Log").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_end_to_end_dry_run(self):
        # Run end-to-end pipeline with force and dry-run
        exit_code = run_pipeline(
            repo_root=self.test_dir,
            force=True,
            dry_run=True,
            lookback_days=3,
            target_date="2026-11-21"
        )
        self.assertEqual(exit_code, 0)

        # Verify execution record created in Execution-Logs
        logs_dir = self.test_dir / "Management" / "Automation" / "Execution-Logs"
        self.assertTrue(logs_dir.exists())
        log_files = list(logs_dir.glob("*.json"))
        self.assertGreater(len(log_files), 0)

        # Verify AUTOMATION-STATUS.md updated
        status_file = self.test_dir / "Management" / "Automation" / "AUTOMATION-STATUS.md"
        self.assertTrue(status_file.exists())
        content = status_file.read_text(encoding="utf-8")
        self.assertIn("Automation Status", content)
        self.assertIn("SUCCESS", content)


if __name__ == "__main__":
    unittest.main()
