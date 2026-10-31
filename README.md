# Infotag

Infotag is a structured archive of technology research, company developments, industry analysis, and investment outlooks.

## Repository structure

- [Updates](Updates/README.md): chronological research publications.
  - [Provider](Updates/Provider/README.md): stable provider directory; provider identity is recorded in metadata.
  - [31 October 2026 update](Updates/Provider/2026-10-31/README.md): initial consolidated report.
- [Management](Management/README.md): architecture, research standards, publishing operations, quality control, automation records, change log, and indexes.

## Dynamic update model

Every update follows:

`Updates/Provider/YYYY-MM-DD/Data/`

The date is the publication date. Each `Data` directory is dynamic and contains only topics supported by material findings from that reporting period. Company and industry folders are not pre-created as empty templates. New companies and themes can be added whenever they become relevant.

Routine updates are intended to cover three-day intervals. The initial 31 October 2026 update preserves its original 22–31 October research coverage.

## Research integrity

- Cite material claims and record publication and measurement dates.
- Distinguish verified facts, company guidance, analyst estimates, forecasts, rumours, and interpretation.
- Include positive and negative implications, risks, and uncertainty.
- Preserve historical updates; publish corrections rather than silently rewriting them.
- Do not commit secrets, credentials, personal data, or copyrighted material without redistribution rights.

## Publication status

A research brief is not considered published until the GitHub commit succeeds and the resulting files are verified.
