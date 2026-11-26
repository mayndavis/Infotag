# Automation

## Scheduled research workflow

- **Task:** Infotag Research & Publish
- **Platform:** ChatGPT Automations
- **Cadence:** Daily scan; routine GitHub publications follow the repository's normal three-day cadence, with interim publications reserved for material time-sensitive events.
- **Timezone:** Africa/Nairobi
- **Status:** Enabled on 2026-11-22.
- **Delivery target:** mayndavis/Infotag, default branch.
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
- **2026-11-24:** The second scheduled ChatGPT run completed a source-backed scan and interim publication. Thirteen unique source documents were opened, seven new research files were published, three chronological files were updated, and all ten changed files were fetched again from GitHub. Publication commit: 7cbbede7283fcfb98036bc58eff4ca32c82a8954.
- **2026-11-25:** The third scheduled run completed the daily scan and due routine publication. Six unique source documents were opened (two primary Dell disclosures and four Reuters reports). Six new research files were published: a README, metadata, master report, Dell report, AI-infrastructure report and source register. Three chronological files were updated, an execution log was created, and the automation status was updated. Research publication commit: 01d01a159a5f204b7df9f5934d8547b88161b852. Final read-back verification is recorded in the execution status.
- **Recurring reliability:** Three consecutive scheduled runs have completed successfully. This is still a short history and does not establish long-term reliability.

- **2026-11-26:** The fourth consecutive daily run completed the scan and published an interim update before the next routine 72-hour interval was due. The trigger was NVIDIA's S&P CreditWatch Negative action and the broad AI-market repricing. Fourteen unique documents were used (five primary/official and nine independent reports; two primary records were pre-window background). AP's post-close report was added to independently corroborate the US market closing observations. Seven research files were created, three chronological files were updated, and the automation status and execution log were updated. Research publication commit: a80449c11e66f01c95c192e79bfa3d573c7548a6. Final read-back verification is recorded in the execution log and automation status.

A research scan, a GitHub commit, and a successful scheduled run are separate outcomes. Record each accurately.

- **2026-11-26 follow-up scan (08:54 EAT):** Covered 2026-11-26 08:27:03–08:54:41 EAT. No new material developments were verified after the prior scan cutoff, so no new daily research folder was created. A quality-control review identified an omitted Microsoft Code Red report from the previous 25 November coverage window; a separate retrospective supplement and two-source register were added to the existing 26 November publication. The original 25 November report was not rewritten. Final read-back verification is recorded in the execution log and automation status.
