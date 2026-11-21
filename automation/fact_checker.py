"""Autonomous Fact-Checking and Corroboration Engine.

Extracts, corroborates, and validates factual propositions across independent sources,
enforcing evidence discipline and assigning standardized verification statuses.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import hashlib
import logging
import re

from automation.sources import ResearchSource

logger = logging.getLogger(__name__)

# Verification Statuses mandated by Infotag specification
STATUS_VERIFIED = "VERIFIED"
STATUS_PARTIALLY_VERIFIED = "PARTIALLY VERIFIED"
STATUS_UNVERIFIED = "UNVERIFIED"
STATUS_DISPUTED = "DISPUTED"

# Evidence Discipline Labels
LABEL_CONFIRMED_FACT = "Confirmed Facts"
LABEL_REPORTED_DEV = "Reported Developments"
LABEL_ANALYST_INTERP = "Analyst Interpretations"
LABEL_SPECULATION = "Speculation"
LABEL_FUTURE_PROJECTION = "Future Projections"


@dataclass
class VerifiedClaim:
    """Represents an independently checked factual claim."""
    claim_id: str
    claim_text: str
    subject: str
    tickers: List[str]
    claim_type: str
    status: str
    evidence_label: str
    primary_source: Dict[str, str]
    corroborating_sources: List[Dict[str, str]]
    numerical_data: List[str]
    dates_referenced: List[str]
    verification_notes: str

    def to_dict(self) -> dict:
        return asdict(self)


class FactChecker:
    """Evaluates factual assertions against source hierarchy and corroboration rules."""

    def __init__(self):
        pass

    def extract_numbers_and_units(self, text: str) -> List[str]:
        """Extracts financial and quantitative figures (e.g. $19.2B, 34%, 132 kW, 288GB)."""
        patterns = [
            r"\$\d+(?:\.\d+)?\s*(?:billion|trillion|million|[BTM])",
            r"\b\d+(?:\.\d+)?\s*%",
            r"\b\d+(?:\.\d+)?\s*(?:kW|MW|GW)",
            r"\b\d+(?:\.\d+)?\s*(?:GB|TB|TB/s)",
            r"\b\d+(?:\.\d+)?x\b",
            r"\b\d+,\d+\s*wafers"
        ]
        found = []
        for pat in patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                found.append(match.group(0))
        return list(dict.fromkeys(found))

    def extract_dates_and_quarters(self, text: str) -> List[str]:
        """Extracts timeframes (e.g. Q3 2027, 2026-11-18, late 2027, 2027--2031)."""
        pattern = r"\b(?:Q[1-4]\s*20\d{2}|20\d{2}|(?:early|mid|late)\s*20\d{2}|\d{4}-\d{2}-\d{2})\b"
        matches = re.findall(pattern, text, re.IGNORECASE)
        return list(dict.fromkeys(matches))

    def determine_evidence_label(self, text: str, source_tier: int) -> str:
        """Determines the appropriate Infotag evidence category."""
        text_lower = text.lower()

        # Forward looking phrases
        if any(term in text_lower for term in ["target", "expected", "guidance", "roadmap", "plans to", "forecast", "projected", "aims to"]):
            return LABEL_FUTURE_PROJECTION

        # Speculation / Unnamed sources
        if any(term in text_lower for term in ["rumour", "speculation", "reportedly", "sources say", "unconfirmed"]):
            return LABEL_SPECULATION

        # Analyst opinions
        if any(term in text_lower for term in ["analysts estimate", "consensus", "survey", "bull case", "bear case"]):
            return LABEL_ANALYST_INTERP

        # Tier 1 official records
        if source_tier == 1:
            return LABEL_CONFIRMED_FACT

        return LABEL_REPORTED_DEV

    def evaluate_source_claim(
        self,
        claim_sentence: str,
        source: ResearchSource,
        all_sources: List[ResearchSource]
    ) -> VerifiedClaim:
        """Fact-checks a single claim sentence against all gathered sources."""
        claim_clean = claim_sentence.strip()
        claim_id = hashlib.sha256(claim_clean.encode("utf-8")).hexdigest()[:12]

        nums = self.extract_numbers_and_units(claim_clean)
        dates = self.extract_dates_and_quarters(claim_clean)
        evidence_label = self.determine_evidence_label(claim_clean, source.source_tier)

        primary_src_meta = {
            "title": source.title,
            "publisher": source.publisher,
            "url": source.url,
            "publication_date": source.publication_date,
            "tier": str(source.source_tier)
        }

        # Check for corroboration across other sources
        corroborating = []
        contradictions = []

        for other in all_sources:
            if other.source_id == source.source_id:
                continue

            # Check if any ticker matches
            common_tickers = set(source.tickers).intersection(set(other.tickers))
            if common_tickers or any(p in other.pillars for p in source.pillars):
                # Search for numeric overlaps
                other_nums = self.extract_numbers_and_units(other.raw_content)
                overlap = set(nums).intersection(set(other_nums))
                if overlap:
                    corroborating.append({
                        "title": other.title,
                        "publisher": other.publisher,
                        "url": other.url,
                        "shared_data": list(overlap)
                    })

        # Determine Verification Status
        if source.source_tier == 1:
            # Official filing or primary corporate release
            status = STATUS_VERIFIED
            notes = f"Verified via primary regulatory/official corporate disclosure ({source.publisher})."
            if corroborating:
                notes += f" Corroborated across {len(corroborating)} related source records."
        elif corroborating:
            status = STATUS_VERIFIED
            notes = f"Corroborated by independent cross-source matches ({len(corroborating)} corroborating sources)."
        elif source.source_tier == 2:
            status = STATUS_PARTIALLY_VERIFIED
            notes = "Reported by reputable technology/financial publication; pending direct SEC filing or primary corporate disclosure."
        else:
            status = STATUS_UNVERIFIED
            notes = "Single secondary source assertion without primary filing confirmation."

        subject = source.tickers[0] if source.tickers else (source.pillars[0] if source.pillars else "General Tech")

        return VerifiedClaim(
            claim_id=claim_id,
            claim_text=claim_clean,
            subject=subject,
            tickers=source.tickers,
            claim_type="quantitative" if nums else "strategic_development",
            status=status,
            evidence_label=evidence_label,
            primary_source=primary_src_meta,
            corroborating_sources=corroborating,
            numerical_data=nums,
            dates_referenced=dates,
            verification_notes=notes
        )

    def fact_check_all_sources(self, sources: List[ResearchSource]) -> List[VerifiedClaim]:
        """Processes all research sources and generates a verified claims register."""
        claims = []
        for src in sources:
            # Split raw content into sentence units
            sentences = re.split(r"(?<=[.!?])\s+", src.raw_content)
            for s in sentences:
                s_strip = s.strip()
                if len(s_strip) >= 35:  # meaningful proposition
                    claim = self.evaluate_source_claim(s_strip, src, sources)
                    claims.append(claim)

        logger.info(f"FactChecker verified {len(claims)} individual propositions.")
        return claims
