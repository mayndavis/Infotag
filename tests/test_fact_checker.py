"""Tests for the Fact-Checking and Evidence Corroboration Engine."""

import unittest
from automation.fact_checker import (
    FactChecker,
    STATUS_VERIFIED,
    STATUS_PARTIALLY_VERIFIED,
    LABEL_CONFIRMED_FACT,
    LABEL_FUTURE_PROJECTION
)
from automation.sources import ResearchSource


class TestFactChecker(unittest.TestCase):

    def setUp(self):
        self.checker = FactChecker()

    def test_numeric_and_unit_extraction(self):
        text = "TSMC allocated $19.2B for CoWoS packaging, targeting 75,000 wafers with 34% margin improvement and 132 kW cooling capacity."
        nums = self.checker.extract_numbers_and_units(text)
        self.assertIn("$19.2B", nums)
        self.assertIn("34%", nums)
        self.assertIn("132 kW", nums)

    def test_date_and_quarter_extraction(self):
        text = "Deliveries commence in Q3 2027 and run through late 2027 before the 2028 node transition."
        dates = self.checker.extract_dates_and_quarters(text)
        self.assertIn("Q3 2027", dates)
        self.assertIn("late 2027", dates)
        self.assertIn("2028", dates)

    def test_evidence_labels(self):
        future_text = "Management roadmap targets 45% capacity expansion by Q4 2027."
        label_fut = self.checker.determine_evidence_label(future_text, source_tier=1)
        self.assertEqual(label_fut, LABEL_FUTURE_PROJECTION)

        fact_text = "The company filed Form 10-Q reporting capital expenditure of $19.2 billion."
        label_fact = self.checker.determine_evidence_label(fact_text, source_tier=1)
        self.assertEqual(label_fact, LABEL_CONFIRMED_FACT)

    def test_tier1_source_is_verified(self):
        src = ResearchSource(
            source_id="src1",
            title="SEC Filing 10-Q",
            publisher="U.S. Securities and Exchange Commission",
            publication_date="2026-11-12",
            url="https://www.sec.gov/edgar/data/123",
            date_accessed="2026-11-21",
            source_tier=1,
            tickers=["MSFT"],
            pillars=["cloud"],
            summary="Microsoft reported $19.2B capex additions.",
            raw_content="Additions to property and equipment were $19.2 billion."
        )
        claims = self.checker.fact_check_all_sources([src])
        self.assertGreater(len(claims), 0)
        self.assertEqual(claims[0].status, STATUS_VERIFIED)
        self.assertEqual(claims[0].subject, "MSFT")


if __name__ == "__main__":
    unittest.main()
