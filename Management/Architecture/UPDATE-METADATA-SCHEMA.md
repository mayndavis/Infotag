# Update Metadata Schema

**Schema version:** 1.0.0  
**Canonical filename:** `metadata.json`  
**Location:** At the root of each dated update directory, beside its `README.md` and `Data/` directory.

## Purpose

Each dated update may include a machine-readable metadata file so the repository can be indexed, searched, compared, validated, and processed by future automation without relying on folder names or parsing every report.

Metadata describes the contents of one published update. It does not replace the report, its citations, or the human-readable update README.

## Required fields

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | string | Version of this metadata contract. |
| `update_id` | string | Stable, unique identifier. Use a provider slug and publication date. |
| `provider` | string | Actual provider name, not the literal directory name `Provider`. |
| `publication_date` | date string | Date the update was published, in ISO 8601 format. |
| `coverage_period.start` | date string | First date covered. |
| `coverage_period.end` | date string | Last date covered. |
| `update_type` | string | Short machine-readable classification. |
| `status` | string | Publication state, such as `draft`, `published`, or `superseded`. |
| `version` | integer | Revision number for this dated update. |
| `topics_covered` | string array | Topics with material coverage in the update. |
| `companies_and_organisations_covered` | string array | Companies or organisations materially discussed. |
| `report.path` | string | Relative path from the dated update directory to the primary report. |
| `report.format` | string | Media type of the primary report. |

## Optional fields

- `source_references.count`: number of cited reference entries, when it can be counted reliably.
- `source_references.count_basis`: explains exactly what the count represents.
- `source_references.verification_note`: qualifies incomplete or provisional references.
- `notes`: short, update-specific qualifications.

Do not estimate a source count. If it cannot be established, omit the count or use `null` and explain why. Distinguish reference entries from unique publishers, URLs, and independently verified documents.

## Dynamic taxonomy rules

1. Topic and company arrays are **per-update metadata**, not a mandatory list.
2. Add only topics and organisations materially covered by that update.
3. Do not create empty directories or placeholder values for topics that were not covered.
4. New topics, companies, sectors, and organisation types may be added at any time.
5. Do not infer that an absent topic had no news; it only means the update does not contain a material item for it.
6. Use consistent readable names in metadata. If machine filtering needs normalised identifiers, use lowercase snake_case topic IDs while retaining proper names for organisations.

## Validation rules

Before publication, verify:

- The JSON parses successfully and uses UTF-8.
- Dates use `YYYY-MM-DD`, and the coverage start is not after the coverage end.
- `update_id` is unique within the repository.
- Provider identity matches the update README.
- The primary report path exists relative to the update directory.
- Topic and organisation values are supported by the actual report.
- Counts state their counting method and are not presented as more precise than the source record allows.
- `status` reflects the actual GitHub publication state.

## Example

The first implementation is:

`Updates/Provider/2026-10-31/metadata.json`

Use it as a working example, not as a template that must be copied unchanged. Each update's metadata must reflect its actual contents.
