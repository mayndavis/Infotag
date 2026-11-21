"""Tests for metadata schema compliance with Management/Architecture/UPDATE-METADATA-SCHEMA.md."""

import unittest
import json
import tempfile
import shutil
from pathlib import Path

from automation.publisher import PublishingValidator


class TestMetadataSchema(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_valid_metadata_passes(self):
        # Create mock primary report
        rep_dir = self.test_dir / "Data" / "02-Master-Reports" / "Technology-Market"
        rep_dir.mkdir(parents=True)
        rep_file = rep_dir / "Report.md"
        rep_file.write_text("# Report Content That Exceeds Fifty Characters Length For Testing Purpose", encoding="utf-8")

        valid_meta = {
            "schema_version": "1.0.0",
            "update_id": "chatgpt-2026-11-21",
            "provider": "ChatGPT",
            "publication_date": "2026-11-21",
            "coverage_period": {
                "start": "2026-11-18",
                "end": "2026-11-21"
            },
            "update_type": "routine_three_day_research",
            "status": "published",
            "version": 1,
            "topics_covered": ["semiconductors", "cloud"],
            "companies_and_organisations_covered": ["NVIDIA", "Microsoft"],
            "report": {
                "path": "Data/02-Master-Reports/Technology-Market/Report.md",
                "format": "text/markdown"
            }
        }

        meta_path = self.test_dir / "metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(valid_meta, f)

        ok, errors = PublishingValidator.validate_metadata(meta_path)
        self.assertTrue(ok, f"Validation failed with: {errors}")
        self.assertEqual(len(errors), 0)

    def test_missing_required_field_fails(self):
        invalid_meta = {
            "schema_version": "1.0.0",
            # missing update_id
            "provider": "ChatGPT",
            "publication_date": "2026-11-21"
        }
        meta_path = self.test_dir / "metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(invalid_meta, f)

        ok, errors = PublishingValidator.validate_metadata(meta_path)
        self.assertFalse(ok)
        self.assertTrue(any("update_id" in e for e in errors))

    def test_invalid_date_sequencing_fails(self):
        rep_file = self.test_dir / "Report.md"
        rep_file.write_text("# Report with sufficient characters for schema validation check", encoding="utf-8")

        inverted_meta = {
            "schema_version": "1.0.0",
            "update_id": "test-id",
            "provider": "ChatGPT",
            "publication_date": "2026-11-21",
            "coverage_period": {
                "start": "2026-11-25",  # AFTER end date!
                "end": "2026-11-21"
            },
            "update_type": "routine_three_day_research",
            "status": "published",
            "version": 1,
            "topics_covered": ["semiconductors"],
            "companies_and_organisations_covered": ["NVIDIA"],
            "report": {
                "path": "Report.md",
                "format": "text/markdown"
            }
        }
        meta_path = self.test_dir / "metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(inverted_meta, f)

        ok, errors = PublishingValidator.validate_metadata(meta_path)
        self.assertFalse(ok)
        self.assertTrue(any("cannot be after end date" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
