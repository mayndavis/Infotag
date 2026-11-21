"""Tests for the 72-hour continuous interval calculation logic."""

import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile
import shutil

from automation.interval_checker import (
    evaluate_publishing_cadence,
    get_latest_update_info,
    parse_iso_date
)
from automation.config import EAT_TIMEZONE


class TestIntervalCadence(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.updates_dir = self.test_dir / "Updates" / "Provider"
        self.updates_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_no_previous_updates_triggers_immediate_due(self):
        result = evaluate_publishing_cadence(repo_root=self.test_dir)
        self.assertTrue(result["is_due"])
        self.assertIn("baseline update required", result["reason"])

    def test_72_hour_boundary_conditions(self):
        # Create a mock update directory dated 2026-11-10
        mock_date = "2026-11-10"
        (self.updates_dir / mock_date).mkdir(parents=True)

        base_dt = parse_iso_date(mock_date)

        # 1. Test at 71.9 hours -> should NOT be due
        dt_71_9 = base_dt + timedelta(hours=71.9)
        res_71_9 = evaluate_publishing_cadence(repo_root=self.test_dir, current_dt=dt_71_9)
        self.assertFalse(res_71_9["is_due"])
        self.assertIn("Requires", res_71_9["reason"])

        # 2. Test at exactly 72.0 hours -> MUST be due
        dt_72_0 = base_dt + timedelta(hours=72.0)
        res_72_0 = evaluate_publishing_cadence(repo_root=self.test_dir, current_dt=dt_72_0)
        self.assertTrue(res_72_0["is_due"])
        self.assertIn("exceeds configured", res_72_0["reason"])

        # 3. Test at 75.0 hours -> MUST be due
        dt_75_0 = base_dt + timedelta(hours=75.0)
        res_75_0 = evaluate_publishing_cadence(repo_root=self.test_dir, current_dt=dt_75_0)
        self.assertTrue(res_75_0["is_due"])

    def test_force_flag_bypasses_interval(self):
        mock_date = "2026-11-10"
        (self.updates_dir / mock_date).mkdir(parents=True)
        base_dt = parse_iso_date(mock_date)

        # Even at 1 hour elapsed, force=True must trigger is_due=True
        dt_1h = base_dt + timedelta(hours=1.0)
        res_forced = evaluate_publishing_cadence(repo_root=self.test_dir, current_dt=dt_1h, force=True)
        self.assertTrue(res_forced["is_due"])
        self.assertTrue(res_forced["force_run"])
        self.assertIn("forced via manual dispatch", res_forced["reason"])


if __name__ == "__main__":
    unittest.main()
