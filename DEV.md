Changes to make regarding the scrapers in src/text/scrapers:

- [ ] Convert everything related (exports and readings) to JSONL to CSV (always index=None). This should be done in src/text/scrapers/storage.py and all places where it says ".jsonl" and "JsonlStorage". There's also a JSONL reading in src/text/analysis/main.py
  - **Direction**: Confirm conversion is from JSONL → CSV across storage and analysis.
  - **File patterns**: Target filenames/paths (e.g., `news.csv`, `epu_*.csv`); per-newspaper/per-date directory structure.
  - **Schema**: Column order; handling lists like `tags` as strings; date format (YYYY-MM-DD); ensure deterministic types.
  - **Serialization**: Convert `HttpUrl` and other non-primitive types to strings; ensure `index=None`.
  - **Writing mode**: Append vs overwrite; atomic writes; sorting and de-duplication policy.
  - **Back-compat**: Remove `JsonlStorage`.
  - **Code touchpoints**: Update `src/text/scrapers/storage.py`, all ".jsonl"/`JsonlStorage` references, and `src/text/analysis/main.py` readers.
  - **New**: Have a CSVStorage module that exports to CSV, and reads existing CSV files.

Changes to add to src/text/analysis/:

- [ ] Add an additional_name parameter to the EPU class, that matches the additional_terms. this additional_name should indicate what type of EPU is being generated. for example, additional_terms could include words related to inflation or jobs, and the additional_name would be inflation or job. this additional_name should be used in the exports and readings, like epu_{additional_name}.csv.
  - **Location**: Confirm module and constructor for `EPU` (e.g., `src/text/analysis/epu.py`). YES
  - **Defaults/validation**: Behavior when `additional_name` omitted; allowed characters; normalization (lowercase, no spaces). IF additional_name is none, additional_terms should also be none and names should be epu.csv, no additional_name. also, default terms are specified in the constructor.
  - **Coupling to terms**: Require non-empty `additional_terms` when `additional_name` provided? Validation rules. SEE ABOVE
  - **Outputs**: Exact filename pattern `epu_{additional_name}.csv`; output directory; overwrite/append behavior.
  - **Content**: Include `additional_name` as a column/metadata? Any header notes required by consumers. YES. the name of the column should be epu_{additional_name}
  - **CLI/API**: How passed in (flag/config/env)? Backward compatibility for existing calls. NO