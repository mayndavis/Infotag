# Infotag Autonomous Technology Research & Publishing Automation

Welcome to the **Infotag Autonomous Intelligence System**. This architecture continuously monitors, gathers, fact-checks, analyzes, and publishes technology investment research directly to the Infotag repository on a continuous 72-hour cadence.

---

## 1. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│             GitHub Actions Workflow Runner (Ubuntu Linux)              │
│       Daily Trigger at 06:00 EAT (03:00 UTC) or Manual Dispatch        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │                Interval Cadence Checker                  │
       │       Calculates Elapsed Hours Since Prior Update        │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                    [Elapsed < 72h & Not Forced]
                                    ├──────────────────────────┐
                                    │                          ▼
                                    │                ┌──────────────────┐
                                    │                │   Status: SKIP   │
                                    │                │   (Clean Exit)   │
                                    │                └──────────────────┘
                    [Elapsed >= 72h OR Forced]
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │             Stage A–D: Multi-Channel Collector           │
       │     SEC Filings (8-K/10-Q), Tech Feeds, Corporate IR     │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │             Stage 5: Independent Fact-Checking           │
       │     Quantitative Extraction, Source Corroboration,       │
       │      Statuses: VERIFIED / PARTIAL / UNVERIFIED / DISPUTE │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │         Stage 6: 4-Quadrant Investment Analysis          │
       │     Executive Signal, Hardware Bottlenecks, FCF/ROIC,    │
       │        Risk Watches & Multi-Horizon Timeframes           │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │           Stage 7: Markdown & Metadata Generator         │
       │       Generates Updates/Provider/YYYY-MM-DD/ & Data/     │
       │       Strict Compliance with UPDATE-METADATA-SCHEMA.md   │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │           Stage 8: Pre-Publication Quality Audit         │
       │        Schema Validation, Link Integrity, UTF-8          │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │           Stage 9: Atomic Git Commit & Remote Push       │
       │      Commits to 'main' & Updates Execution Logs / Status │
       └──────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

1. **Interval Checker (`automation/interval_checker.py`):**
   - Implements strict 72-hour continuous interval calculation (never a naive calendar-day cron).
   - Reads the latest update directory under `Updates/Provider/` and evaluates elapsed hours.
   - Allows manual bypass via `--force`.

2. **Source Collector (`automation/sources.py`):**
   - Aggregates primary regulatory filings (SEC EDGAR Form 8-K, 10-Q), official corporate releases, and high-reputation technology news (Ars Technica, Hacker News, TechCrunch).
   - Records publisher, publication date, URL, access date, and evidence tier.
   - Preserves offline resilience and deterministic fallbacks.

3. **Fact-Checking Engine (`automation/fact_checker.py`):**
   - Extracts quantitative metrics ($B, %, kW, TB/s, wafer yields) and dates.
   - Corroborates claims across multiple independent records.
   - Categorizes findings into: `Confirmed Facts`, `Reported Developments`, `Analyst Interpretations`, `Speculation`, and `Future Projections`.
   - Assigns verification statuses: `VERIFIED`, `PARTIALLY VERIFIED`, `UNVERIFIED`, `DISPUTED`.

4. **Investment Intelligence Engine (`automation/investment_analyzer.py`):**
   - Evaluates capital efficiency, infrastructure bottlenecks (CoWoS, HBM4, liquid cooling), ROIC, and thesis invalidation risks.
   - Synthesizes full **4-Quadrant Institutional Briefs**:
     1. Executive Signal
     2. Hardware & Infrastructure Bottleneck
     3. Capital Efficiency & Monetization
     4. Risk Watch & Thesis Invalidation

5. **Report & Metadata Generator (`automation/report_generator.py`):**
   - Instantiates dynamic update directories conforming to Infotag architecture:
     - `Updates/Provider/YYYY-MM-DD/README.md`
     - `Updates/Provider/YYYY-MM-DD/metadata.json`
     - `Updates/Provider/YYYY-MM-DD/Data/02-Master-Reports/Technology-Market/`
     - `Updates/Provider/YYYY-MM-DD/Data/02-Master-Reports/Fact-Checks/`
     - `Updates/Provider/YYYY-MM-DD/Data/03-Company-Research/<Company>/` (dynamic; only created for covered companies)
     - `Updates/Provider/YYYY-MM-DD/Data/05-Investment-Outlook/`
     - `Updates/Provider/YYYY-MM-DD/Data/06-Sources-and-References/`
   - Synchronizes `data/initial_briefs.json` to immediately feed the Institutional Terminal UI.
   - Updates durable indexes: `Management/Indexes/UPDATE-INDEX.md`, `Management/Change-Log/CHANGELOG.md`, `Management/Automation/AUTOMATION-STATUS.md`, and `Updates/README.md`.

6. **Publishing & Quality Gate (`automation/publisher.py`):**
   - Pre-publication schema validation against `UPDATE-METADATA-SCHEMA.md`.
   - Validates UTF-8 encoding, non-empty files, and date sequencing.
   - Atomic Git staging and commit with message `Automated Infotag Research Update - YYYY-MM-DD`.

7. **Monitoring & Audit (`automation/monitor.py`):**
   - Generates structured audit logs in `Management/Automation/Execution-Logs/YYYY-MM-DD-exec-<id>.json`.
   - Updates `Management/Automation/AUTOMATION-STATUS.md` dashboard.

---

## 3. GitHub Secrets & Configuration

To enable the automation in GitHub Actions:

### Required Permissions
The default GitHub Actions token `GITHUB_TOKEN` is used automatically. Ensure your repository settings allow GitHub Actions to write commits:
1. Go to repository **Settings** → **Actions** → **General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Check **Allow GitHub Actions to create and approve pull requests**.
4. Click **Save**.

### Optional AI Enrichment Secrets
The pipeline features a **100% deterministic fallback engine** that executes with zero external API dependencies. If you wish to enable advanced LLM-assisted prose enrichment:
1. Navigate to **Settings** → **Secrets and variables** → **Actions**.
2. Click **New repository secret** and add any of the following:
   - `GEMINI_API_KEY`: Google Gemini API key (recommended for cost-effective speed). Obtain free at [Google AI Studio](https://aistudio.google.com/).
   - `OPENAI_API_KEY`: OpenAI API key. Obtain at [OpenAI Platform](https://platform.openai.com/).
   - `ANTHROPIC_API_KEY`: Anthropic API key. Obtain at [Anthropic Console](https://console.anthropic.com/).

---

## 4. Triggering and Operating Updates

### Scheduled Automated Execution
- Scheduled via cron: `'0 3 * * *'` (daily check at **06:00 East Africa Time / EAT**, which is 03:00 UTC).
- The daily runner checks whether at least 72 hours have elapsed since the prior publication date.
- If fewer than 72 hours have passed, it records status `SKIPPED` and terminates cleanly without failing CI.
- When 72 hours have elapsed, it executes the research pipeline, generates reports, commits, and pushes to `main`.

### Manual On-Demand Execution
To trigger an update manually regardless of the 72-hour timer:
1. In your GitHub repository, click the **Actions** tab.
2. Select **Infotag Autonomous Research & Publishing Pipeline** on the left.
3. Click the **Run workflow** dropdown button.
4. (Optional) Check **Bypass 72-hour interval check and force immediate execution** (`force_run: true`).
5. (Optional) Check **Execute research and validation without committing or pushing changes** (`dry_run: true`).
6. Click **Run workflow**.

---

## 5. Local Execution & Testing

You can run the entire pipeline or test suite on your local workstation.

### Running Automated Tests
```powershell
pytest tests/ -v
```

### Checking Cadence
```powershell
python -m automation.interval_checker
```

### Executing a Dry-Run Pipeline
```powershell
python -m automation.run_pipeline --dry-run --force
```

### Executing a Full Local Publication
```powershell
python -m automation.run_pipeline --force
```

---

## 6. Modifying the Publishing Cadence

To adjust the interval (e.g. from 72 hours to 48 hours or 96 hours):
1. In repository settings or environment variables, configure `INFOTAG_PUBLISHING_INTERVAL_HOURS`:
   ```bash
   export INFOTAG_PUBLISHING_INTERVAL_HOURS=48.0
   ```
2. Or modify the default in `automation/config.py`:
   ```python
   PUBLISHING_INTERVAL_HOURS = float(os.environ.get("INFOTAG_PUBLISHING_INTERVAL_HOURS", "72.0"))
   ```

---

## 7. Inspecting Logs and Troubleshooting

- **Live CI Run Output:** Check the **Actions** tab in GitHub to inspect step-by-step logs and the Markdown summary.
- **Durable Audit Records:** Every run writes a JSON record into `Management/Automation/Execution-Logs/` containing execution duration, sources examined, claims verified, and status.
- **Repository Dashboard:** Current health and recent runs are summarized in `Management/Automation/AUTOMATION-STATUS.md`.
- **Pre-Publication Rejections:** If validation fails, changes are rejected before commit to protect repository integrity. Check `Management/Automation/Execution-Logs/` for the exact validation failure reason.
