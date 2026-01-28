# ICE & CBP Custodial Mortality (FY2004–2025)

Analysis package for deaths in U.S. immigration custody. ICE deaths are fully enumerated (172 FOIA-era + 94 individual DDRs = 266; filename kept as `all_266_deaths_detailed.csv`). CBP deaths are counts-only (no ADP) from OPR “CBP-Related Deaths” reports, treated separately and not pooled with ICE.

---

## Contents (repo root)
- `manuscript/` – `MANUSCRIPT.md`, `APPENDIX.md`, ICE figures (`Figure1.png`, `Figure2.png`, `Figure3.png`), CBP figure (`Appendix_Figure_A3.png`), appendix figures (`Appendix_Figure_A1_operator.png`, `Appendix_Figure_A2_cause.png`).
- `data/`
  - `all_266_deaths_detailed.csv` (ICE, 266 deaths; name retained for continuity)
  - `complete_death_records.csv`, `detailed_death_data.csv` (ICE subsets)
  - `average_daily_population.csv` (ICE ADP by FY), `mortality_rates_by_administration.csv`
  - `cbp_deaths_summary.csv` (CBP counts FY2021–FY2023: total, in_custody, CBP_involved, additional; no ADP available)
- `replication_code/`
  - `02_calculate_mortality_rates.py` (ICE rates; ADP denominators)
  - `03_generate_figures.py` (ICE figs 1–3; CBP counts figure)
  - `04_verify_and_download_pdfs.py`, `05_generate_appendix_a9.py`, `06_audit_causes.py`, `07_verify_foia_consistency.py`
- `death_report_pdfs/` – ICE FOIA master + individual DDRs (FY2018–2025)
- `verification/` – download checks, cause audit, FOIA consistency outputs
- `source_documents/` – links/guides to public sources

---

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r replication_code/requirements.txt
python replication_code/02_calculate_mortality_rates.py
python replication_code/03_generate_figures.py
```
Outputs land in `manuscript/` (figures) and `data/` (derived CSVs).

---

## What’s in the analyses
- **ICE (FY2004–FY2025):** 266 deaths (age missing for 1) with complete sex/facility/cause; ADP denominators; rates by FY and administration; sensitivity analyses (alt 2025 denominators, COVID exclusions, bounds).
- **CBP (FY2021–FY2023):** Counts-only from OPR reports; plotted separately (`Appendix_Figure_A3.png`). No ADP → no CBP mortality rates. Minors largely fall under CBP, not ICE.
- **Separation of systems:** ICE and CBP are not pooled; CBP results are descriptive and flagged as incomplete due to missing ADP and potential under-reporting of minors/post-release events.

---

## Key files for readers
- `manuscript/MANUSCRIPT.md` – main text (JAMA-style formatting)
- `manuscript/APPENDIX.md` – methods, STROBE, reproducibility, full A9 index
- `data/cbp_deaths_summary.csv` – CBP counts (FY2021–FY2023)
- `manuscript/Appendix_Figure_A3.png` – CBP counts figure
- `manuscript/Figure2.png` – ICE multi-panel (A: ADP; B: deaths; C: mortality rate), FY start=2004, axes at zero, admin demarcations; 2025 uses calendar-year deaths and CY2025 ADP

---

## Verification notes
- ICE source PDFs are mirrored in `death_report_pdfs/`; URLs also in `all_266_deaths_detailed.csv`.
- FOIA/DDR harmonization issues and suspected under-reporting (minors, post-release, ATD) are documented in the manuscript limitations and appendix under “Under‑reporting risk.”
- CBP ADP is not publicly available; counts are copied verbatim from OPR reports (see CBP URLs in appendix references).

---

## Citation
If you use these materials, please cite the manuscript: *Mortality in U.S. Immigration and Customs Enforcement Detention, FY2004–FY2025* (see `manuscript/MANUSCRIPT.md`).

---

**Last updated:** January 2026  
**Maintainer:** sanjay.basu@ucsf.edu
