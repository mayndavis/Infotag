"""Configuration management for the Infotag Autonomous Research & Publishing Engine."""

from datetime import timezone, timedelta
from pathlib import Path
import os

# Base paths
REPO_ROOT = Path(os.environ.get("INFOTAG_REPO_ROOT", Path(__file__).resolve().parent.parent))
UPDATES_DIR = REPO_ROOT / "Updates" / "Provider"
MANAGEMENT_DIR = REPO_ROOT / "Management"
DATA_DIR = REPO_ROOT / "data"
LOGS_DIR = MANAGEMENT_DIR / "Automation" / "Execution-Logs"

# Schedule and Interval Settings
PUBLISHING_INTERVAL_HOURS = float(os.environ.get("INFOTAG_PUBLISHING_INTERVAL_HOURS", "72.0"))
TARGET_TIMEZONE_NAME = os.environ.get("INFOTAG_TIMEZONE", "Africa/Nairobi")  # East Africa Time (EAT)
EAT_OFFSET = timedelta(hours=3)
EAT_TIMEZONE = timezone(EAT_OFFSET, name="EAT")

# Provider Identity
DEFAULT_PROVIDER_NAME = os.environ.get("INFOTAG_PROVIDER_NAME", "ChatGPT")
DEFAULT_PROVIDER_SLUG = os.environ.get("INFOTAG_PROVIDER_SLUG", "chatgpt")

# Core Target Companies to Follow
CORE_COMPANIES = [
    {"name": "NVIDIA", "ticker": "NVDA", "sector": "Semiconductors"},
    {"name": "Microsoft", "ticker": "MSFT", "sector": "Cloud & AI"},
    {"name": "Alphabet", "ticker": "GOOGL", "sector": "Search & Cloud"},
    {"name": "Amazon", "ticker": "AMZN", "sector": "Cloud & E-Commerce"},
    {"name": "Meta Platforms", "ticker": "META", "sector": "Social & AI Infra"},
    {"name": "Apple", "ticker": "AAPL", "sector": "Consumer Hardware & AI"},
    {"name": "TSMC", "ticker": "TSM", "sector": "Foundry & Advanced Packaging"},
    {"name": "Broadcom", "ticker": "AVGO", "sector": "Custom ASICs & Networking"},
    {"name": "AMD", "ticker": "AMD", "sector": "Accelerators & CPUs"},
    {"name": "Intel", "ticker": "INTC", "sector": "Foundry & Compute"},
    {"name": "SK hynix", "ticker": "000660.KS", "sector": "High-Bandwidth Memory"},
    {"name": "Micron Technology", "ticker": "MU", "sector": "Memory & Storage"},
    {"name": "Vertiv", "ticker": "VRT", "sector": "Data Centre Power & Cooling"},
    {"name": "Tesla", "ticker": "TSLA", "sector": "Autonomous Systems & Compute"},
    {"name": "Anthropic", "ticker": "PRIV_ANTHROPIC", "sector": "Frontier AI Models"},
]

# Core Technology Verticals
RESEARCH_VERTICALS = [
    {
        "id": "semiconductors",
        "name": "Semiconductors & Compute",
        "subtopics": ["Advanced Packaging (CoWoS, Foveros)", "HBM3e/HBM4 Stacks", "Sub-2nm Foundry Nodes", "Custom ASICs vs Merchant GPUs"]
    },
    {
        "id": "cloud",
        "name": "Cloud & Disaggregated Serving",
        "subtopics": ["Hyperscaler Capex Cycles", "Inference vs Training Clusters", "Disaggregated Memory/Compute", "GPU/TPU Utilization Rates"]
    },
    {
        "id": "data-centres",
        "name": "Data Centres & Networking",
        "subtopics": ["Rack Power Density (>100kW)", "Co-Packaged Optics (CPO/LPO)", "800G/1.6T Ethernet Topologies", "InfiniBand vs RoCEv2"]
    },
    {
        "id": "power-and-cooling",
        "name": "Power Infrastructure & Cooling",
        "subtopics": ["Direct-to-Chip Liquid Cooling", "Grid Substation Allocation Bottlenecks", "Behind-the-Meter Nuclear/PPAs", "Data Centre PUE Optimization"]
    },
    {
        "id": "software-and-ai",
        "name": "Software & Frontier AI",
        "subtopics": ["Agentic AI Workflows", "Open Weights vs Closed API Economics", "Context Window Expansion", "Fine-Tuning & Distillation"]
    },
    {
        "id": "capital-efficiency",
        "name": "Capital Efficiency & Monetization",
        "subtopics": ["Hyperscaler ROIC & FCF Conversion", "Hardware Depreciation Acceleration", "Enterprise AI Token Unit Economics", "Venture & Sovereign AI Spend"]
    }
]

# Credible News & Regulatory Feed Endpoints
FEED_SOURCES = [
    {
        "name": "SEC EDGAR Form 8-K / 10-Q Feeds",
        "type": "regulatory",
        "url": "https://www.sec.gov/edgar/searchedgar/currentevents.rss",
        "priority": 1
    },
    {
        "name": "ArXiv Computer Science (AI / Computation)",
        "type": "academic",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "priority": 2
    },
    {
        "name": "Hacker News Frontier Technology Stream",
        "type": "tech_community",
        "url": "https://hacker-news.firebaseio.com/v0/topstories.json",
        "priority": 3
    },
    {
        "name": "Ars Technica Technology & Science",
        "type": "journalism",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "priority": 2
    }
]
