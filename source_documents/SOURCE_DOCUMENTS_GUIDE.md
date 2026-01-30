# Source Documents Guide

This document provides complete information on all primary data sources used in this analysis, with direct download links.

---

## Primary Data Sources

### 1. ICE Deaths 2003-2017 (172 deaths)

**Document:** List of Deaths in ICE Custody - Data from: 10/01/2003 to 06/05/2017

**Download URL:** https://www.ice.gov/doclib/foia/reports/detaineedeaths-2003-2017.pdf

**Description:** Official ICE FOIA release containing detailed information on all 172 in-custody deaths from October 1, 2003 through June 5, 2017. This 35-page PDF includes:
- Name, sex, date of birth, country of citizenship
- Date of death
- Location of death (hospital)
- Last detention facility
- Facility type
- Cause of death

**Data Extracted:** All 172 deaths are included in `all_274_deaths_detailed.csv`

---

### 2. ICE Detainee Death Reporting Webpage (FY2018-2025)

**Webpage URL:** https://www.ice.gov/detain/detainee-death-reporting

**Description:** Official ICE webpage listing all detainee deaths by fiscal year from FY2018 through FY2025. Each death links to an individual death report PDF.

**Data Extracted:** All 77 deaths from FY2018-2025 are included in `all_274_deaths_detailed.csv` with individual PDF URLs for each death.

---

### 3. Public Reporting Updates (CY2025 and January 2026)

**Sources:**
- https://www.theguardian.com/us-news/ng-interactive/2026/jan/04/ice-2025-deaths-timeline
- https://www.theguardian.com/us-news/2026/jan/28/deaths-ice-2026-

**Description:** Public reporting used to complete the CY2025 series and catalog deaths through January 29, 2026. These entries are flagged in the dataset and linked in the per‑death index.

---

## Individual Death Reports (FY2018-2025)

Each of the 77 deaths from FY2018-2025 has an individual death report PDF available at ICE.gov. The URLs for all individual reports are included in the `PDF_URL` column of `all_274_deaths_detailed.csv`.

**URL Pattern:**
```
https://www.ice.gov/doclib/foia/reports/ddr[LastName][FirstName].pdf
```

**Example:**
- Mirimanian, Gourgen: https://www.ice.gov/doclib/foia/reports/ddrMirimanianGourgen.pdf

**To Access:** See the `PDF_URL` column in `all_274_deaths_detailed.csv` for the complete list of all 77 individual death report URLs.

---

## Average Daily Population (ADP) Data Sources

### FY2001-2006: Migration Policy Institute
**Source:** "Immigration Enforcement in the United States: The Rise of a Formidable Machinery"
**URL:** https://www.migrationpolicy.org/article/immigration-enforcement-united-states-2006
**Data Location:** Table 1, page 14

### FY2007-2009: ICE Total Removals Report
**Source:** ICE Enforcement and Removal Operations Report
**URL:** https://www.ice.gov/doclib/about/offices/ero/pdf/eroReportFY2009.pdf

### FY2010-2024: ICE FOIA Releases
**Source:** ICE Enforcement and Removal Operations Reports (various years)
**URL:** https://www.ice.gov/statistics

### FY2025: TRAC Immigration
**Source:** Transactional Records Access Clearinghouse
**URL:** https://tracreports.org/reports/753/
**Note:** CY2025 ADP is estimated at 51,130 based on the TRAC daily‑series calendar‑year average; sensitivity analyses use 48,984 (FY mean) and 39,703 (Jan 12 snapshot).

### January 2026 (partial): ICE FY2026 Detention Statistics
**Source:** US Immigration and Customs Enforcement
**URL:** https://www.ice.gov/doclib/detention/FY26_detentionStats01082026.xlsx
**Note:** January 2026 ICE Average Daily Population (ADP = 69,919) used as a partial‑month denominator through January 29, 2026.

---

## How to Download All Source Documents

### Method 1: Direct Download

1. **ICE 2003-2017 PDF:**
   ```bash
   wget https://www.ice.gov/doclib/foia/reports/detaineedeaths-2003-2017.pdf
   ```

2. **Individual FY2018-2025 Death Reports:**
   Use the URLs listed in `all_274_deaths_detailed.csv` (PDF_URL column)

### Method 2: Browser Download

1. Visit https://www.ice.gov/doclib/foia/reports/detaineedeaths-2003-2017.pdf
2. Click the download button in your browser
3. For individual reports, visit each URL listed in the data file

---

## Data Verification

To verify the completeness and accuracy of the extracted data:

1. **Compare death counts:**
   - ICE 2003-2017 PDF: 172 deaths
   - ICE FY2018-2025 webpage: 77 deaths
   - Public reporting updates (CY2025 + Jan 2026): 25 deaths
   - Total: 274 deaths ✓

2. **Verify individual deaths:**
   - Each death in `all_274_deaths_detailed.csv` includes the source PDF URL
   - Cross-reference names, dates, and causes of death with source documents

3. **Check for updates:**
   - Visit https://www.ice.gov/detain/detainee-death-reporting
   - Check for any newly reported deaths after September 30, 2025

---

## Notes for Researchers

1. **Data Currency:** This analysis includes all deaths through September 30, 2025 (end of FY2025). Check the ICE website for any deaths reported after this date.

2. **Cause of Death Information:** 
   - FY2003-2017: Cause listed in the master PDF
   - FY2018-2025: Detailed cause in individual death reports

3. **Facility Information:**
   - Historical data (2003-2017): Facility names standardized from PDF
   - Recent data (2018-2025): Facility names as reported in individual death reports

4. **Data Quality:** All data extracted directly from official ICE sources. No imputation or estimation used except for FY2025 ADP.

---

## Contact ICE for Additional Information

For questions about specific deaths or to request additional information:

**ICE FOIA Office:**
- Website: https://www.ice.gov/foia
- Email: ice-foia@dhs.gov

**ICE Detainee Death Reporting:**
- Website: https://www.ice.gov/detain/detainee-death-reporting

---

**Last Updated:** November 15, 2025
