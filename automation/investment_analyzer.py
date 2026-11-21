"""Autonomous Investment Intelligence Engine.

Synthesizes technical findings into institutional investment briefs,
evaluating capital efficiency, hardware bottlenecks, competitive dynamics,
and risk watches without manufacturing price forecasts.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict, Optional
import hashlib
import logging
import re
import time

from automation.sources import ResearchSource
from automation.fact_checker import VerifiedClaim

logger = logging.getLogger(__name__)


@dataclass
class TimeframeAnalysis:
    short_term: str   # 0 to 6 months
    medium_term: str  # 6 to 18 months
    long_term: str    # 18 to 60 months


@dataclass
class InvestmentBrief:
    """Represents a full 4-Quadrant Institutional Research Brief."""
    id: str
    date: str
    title: str
    pillar: str
    secondary_pillars: List[str]
    tickers: List[str]
    hardware_nodes: List[str]
    sentiment: str  # bullish, bearish, neutral, mixed, bottleneck
    impact_rating: str  # HIGH, MEDIUM, LOW
    timeframe: Dict[str, str]
    executive_signal: str
    hardware_bottleneck: str
    capital_efficiency: str
    risk_watch: str
    sources: List[Dict[str, str]]
    updated_at: int
    version: int = 1

    def to_dict(self) -> dict:
        return asdict(self)


class InvestmentAnalyzer:
    """Transforms verified technical research into institutional investor intelligence."""

    def __init__(self):
        pass

    def extract_hardware_nodes(self, text: str) -> List[str]:
        """Identifies key hardware fabrication nodes and packaging architectures."""
        known_nodes = [
            "TSMC N3P", "TSMC N2", "Intel 18A", "CoWoS-L", "CoWoS-S", "SoIC",
            "HBM3e", "HBM4", "Blackwell B200", "Blackwell Ultra B300", "Rubin",
            "Trainium2", "TPUv7", "NVL72", "CPO", "LPO", "800G", "1.6T",
            "Direct-to-Chip Liquid Cooling", "OCS Topologies"
        ]
        found = []
        for node in known_nodes:
            if re.search(rf"\b{re.escape(node)}\b", text, re.IGNORECASE):
                found.append(node)
        return list(dict.fromkeys(found))

    def evaluate_sentiment_and_impact(self, text: str, pillar: str) -> (str, str):
        """Deterministically evaluates investor sentiment and impact rating."""
        text_lower = text.lower()

        # Bottleneck indicators
        if any(w in text_lower for w in ["bottleneck", "constraint", "shortage", "yield drag", "warpage", "friction", "backorder"]):
            sentiment = "bottleneck"
            impact = "HIGH"
        elif any(w in text_lower for w in ["loss", "decline", "pressure", "slowdown", "headwind", "compress", "hesitation"]):
            sentiment = "bearish"
            impact = "HIGH" if any(w in text_lower for w in ["margin", "capex", "guidance"]) else "MEDIUM"
        elif any(w in text_lower for w in ["gain", "accelerat", "expansion", "record", "growth", "breakthrough", "efficiency"]):
            sentiment = "bullish"
            impact = "HIGH"
        elif any(w in text_lower for w in ["mixed", "divergence", "offset"]):
            sentiment = "mixed"
            impact = "MEDIUM"
        else:
            sentiment = "neutral"
            impact = "LOW"

        return sentiment, impact

    def generate_briefs_from_sources(
        self,
        sources: List[ResearchSource],
        claims: List[VerifiedClaim],
        publication_date: str = None
    ) -> List[InvestmentBrief]:
        """Synthesizes comprehensive investment briefs across all examined sources."""
        if publication_date is None:
            publication_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        briefs = []
        now_ms = int(time.time() * 1000)

        # Process each high-conviction research source
        for src in sources:
            hardware = self.extract_hardware_nodes(f"{src.title} {src.raw_content}")
            if not hardware and src.pillars and "semiconductors" in src.pillars:
                hardware = ["Advanced Packaging", "Accelerator Silicon"]

            sentiment, impact = self.evaluate_sentiment_and_impact(src.raw_content, src.pillars[0] if src.pillars else "semiconductors")

            # Determine primary and secondary pillars
            primary_pillar = src.pillars[0] if src.pillars else "semiconductors"
            secondary_pillars = src.pillars[1:] if len(src.pillars) > 1 else ["capital-efficiency"]

            # Format source reference
            src_refs = [{
                "title": src.title,
                "url": src.url,
                "publisher": src.publisher,
                "date": src.publication_date
            }]

            slug = re.sub(r"[^a-z0-9]+", "-", src.title.lower())[:36].strip("-")
            brief_id = f"brief-{publication_date.replace('-', '')}-{slug}"

            # Timeframe synthesis
            short_term = (
                f"Near-term supply allocations and execution on {hardware[0] if hardware else 'accelerator hardware'} "
                f"will govern revenue delivery for {', '.join(src.tickers) if src.tickers else 'the sector'} over the next 1-2 quarters."
            )
            medium_term = (
                f"Transition to next-generation architectures through 2027 will test hyperscaler capex absorption "
                f"and gross margin stability as depreciation schedules expand."
            )
            long_term = (
                f"Multi-year return on invested capital (ROIC) will decouple between custom ASIC deployers "
                f"and merchant silicon purchasers based on token serving unit economics."
            )

            # Synthesize 4 quadrants
            executive_signal = src.summary
            if not executive_signal.endswith("."):
                executive_signal += "."

            hardware_bottleneck = (
                f"Infrastructure and node analysis indicates: {src.raw_content[:260]}... "
                f"Packaging yield and thermal dissipation remain primary governors of deployment velocity."
            )

            capital_efficiency = (
                f"Financial and capital allocation implications: Capex deployment across {', '.join(src.tickers) if src.tickers else 'infrastructure providers'} "
                f"requires sustained revenue expansion to mitigate ROIC compression and manage multi-year balance sheet commitments."
            )

            risk_watch = (
                f"1. Customer and foundry concentration risk at tier-1 manufacturing hubs. "
                f"2. Depreciation drag if enterprise inference demand normalizes faster than hyperscaler capex commitments."
            )

            brief = InvestmentBrief(
                id=brief_id,
                date=src.publication_date,
                title=src.title,
                pillar=primary_pillar,
                secondary_pillars=secondary_pillars,
                tickers=src.tickers if src.tickers else ["TECH"],
                hardware_nodes=hardware,
                sentiment=sentiment,
                impact_rating=impact,
                timeframe={
                    "short_term": short_term,
                    "medium_term": medium_term,
                    "long_term": long_term
                },
                executive_signal=executive_signal,
                hardware_bottleneck=hardware_bottleneck,
                capital_efficiency=capital_efficiency,
                risk_watch=risk_watch,
                sources=src_refs,
                updated_at=now_ms,
                version=1
            )
            briefs.append(brief)

        logger.info(f"InvestmentAnalyzer generated {len(briefs)} institutional investment briefs.")
        return briefs
