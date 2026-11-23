# Automation

## Scheduled research workflow

- **Task:** Infotag Research & Publish
- **Platform:** ChatGPT Automations
- **Cadence:** Daily scan; routine GitHub publications follow the repository's normal three-day cadence, with interim publications reserved for material time-sensitive events.
- **Timezone:** Africa/Nairobi
- **Status:** Enabled on 2026-11-22.
- **Delivery target:** `mayndavis/Infotag`, default branch.
- **Research scope:** AI, semiconductors, cloud, data centres, networking, power and cooling; prioritise NVIDIA, Microsoft, Amazon, Alphabet, Meta, Broadcom, SK hynix, Vertiv, AMD, Intel, TSMC, Marvell and Anthropic.

## Publishing safeguards

1. Verify every material claim against opened primary or reputable sources.
2. Preserve historical update folders; do not silently rewrite prior research.
3. Check target paths before creating files and fetch blob SHAs before updating existing files.
4. Keep metadata, README links, report paths, coverage dates and source registers consistent.
5. Read back changed files after a successful commit.
6. If source verification or GitHub publishing fails, report the blocker and do not claim publication.

## Verification status

- **2026-11-22:** The automation was enabled and its instructions were updated to include GitHub publishing.
- **2026-11-22:** A manual interim publication was committed to GitHub and the changed files were read back successfully.
- **2026-11-23:** The first scheduled ChatGPT run completed a source-backed scan, published a material interim update, updated the chronological indexes, and read back the changed GitHub files.
- **Recurring reliability:** Verified for one scheduled run only. Additional successful runs are required before the recurring workflow can be described as reliably proven.

A research scan, a GitHub commit, and a successful scheduled run are separate outcomes. Record each accurately.
