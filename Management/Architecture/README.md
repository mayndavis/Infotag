# Architecture

Infotag separates chronological research records from repository governance.

- `Updates/` contains dated provider updates. Each update has a `Data/` directory with only the topics actually covered.
- Each dated update may include a root-level `metadata.json` describing provider identity, publication and coverage dates, topics, organisations, and report locations.
- [Update Metadata Schema](UPDATE-METADATA-SCHEMA.md) defines the machine-readable metadata contract.
- `Management/` contains durable governance, architecture, standards, and operating procedures.
- `README.md` at the repository root is the entry point.

Do not reintroduce a fixed, empty topic tree inside every update. Data directories and metadata arrays grow and vary according to the evidence available in each reporting period.