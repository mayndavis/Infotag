"""Tests for research source collection and classification."""

import unittest
from automation.sources import (
    SourceCollector,
    generate_source_id,
    detect_tickers,
    detect_pillars,
    ResearchSource
)


class TestSources(unittest.TestCase):

    def test_deterministic_source_id(self):
        id1 = generate_source_id("https://nvidianews.nvidia.com/item1", "NVIDIA Blackwell Update")
        id2 = generate_source_id("https://nvidianews.nvidia.com/item1", "NVIDIA Blackwell Update")
        id3 = generate_source_id("https://nvidianews.nvidia.com/item2", "NVIDIA Blackwell Update")
        self.assertEqual(id1, id2)
        self.assertNotEqual(id1, id3)

    def test_ticker_detection(self):
        text = "NVIDIA and TSMC announced new wafer allocations for Blackwell chips alongside Microsoft Azure deployments."
        tickers = detect_tickers(text)
        self.assertIn("NVDA", tickers)
        self.assertIn("TSM", tickers)
        self.assertIn("MSFT", tickers)

    def test_pillar_detection(self):
        text = "Direct-to-chip liquid cooling architectures improve data centre power efficiency and reduce megawatt power draw."
        pillars = detect_pillars(text)
        self.assertIn("power-and-cooling", pillars)
        self.assertIn("data-centres", pillars)

    def test_baseline_sources_validity(self):
        collector = SourceCollector()
        sources = collector.get_verified_baseline_sources()
        self.assertGreater(len(sources), 5)
        for s in sources:
            self.assertTrue(s.url.startswith("http"))
            self.assertGreater(len(s.title), 10)
            self.assertIn(s.source_tier, [1, 2, 3])
            self.assertGreater(len(s.pillars), 0)


if __name__ == "__main__":
    unittest.main()
