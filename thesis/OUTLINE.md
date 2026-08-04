# Master's Thesis Outline

**Title (working):** *Smart Accounting Platform: Design and Implementation of a Tax-Compliant Financial Analysis System for Algerian SMEs*

**Proposed framework:** Master's thesis under the national mechanism "One Diploma, One Startup / One Diploma, One Patent" (Arrêté ministériel n° 1275 du 27 septembre 2022, modifié par l'arrêté n° 008) — the thesis presents a functional software product (Smart Accounting Platform v3.1.7) eligible for startup status or a software patent.

> **Note on project data:** earlier drafts cited "22 screens / 318 tests". The actual system (v3.1.7, Aug 2026) comprises **35 screens, 37 engine modules, 20 financial ratios + Z-Score + DuPont, 1800 passing tests, 100% module coverage, 3 languages (AR/EN/FR) with 1925 i18n keys**. All page estimates below assume A4, Times New Roman 12pt, 1.5 line spacing.

---

## I. Introduction — 3 pages

**Objective:** establish the context, formulate the problem, state objectives, delimit scope, and present the thesis road map.

### 1.1 Background
- **SMEs in Algeria:** ~1.36 million registered SMEs (end 2022, MIM statistical bulletin n° 42); SMEs represent ≈95% of enterprises and >70% of private-sector employment; 97.6% are micro-enterprises (<10 employees); density 28 SMEs/1000 inhabitants vs ~45 international average; ≈70% concentrated in the North.
- **Accounting challenges:** manual/bookkeeper-driven record keeping, weak internal control, informality, late and erroneous tax declarations (TVA G50 monthly, IRG/CNAS/CNAC monthly, IBS instalments March/June/November + annual balance by 30 April, DAS by 31 January).
- **Digital transformation needs:** state push toward e-administration (DGI e-services), startup ecosystem (1275 mechanism, incubators, IBTIKAR platform), SME financing requires reliable financial statements.
- **Figure 1.1:** Growth of SME population 2012–2022 (711,832 → 1,359,803) — line chart.
- **Figure 1.2:** SME distribution by region (North 69.5% / Highlands 22.1% / South 8.4%) — pie chart.

### 1.2 Problem Statement
- No affordable, Algerian-specific accounting software for SMEs: international suites (SAP, Oracle, Sage) are costly, English-centric, and ignore the Algerian tax calendar and rates.
- Local commercial software is closed-source, single-entity, and does not embed compliance (IBS/VF/IRG/CNAS), financial analysis (ratios/DuPont/Z-Score), or forecasting.
- Result: SMEs under-utilize financial data for decision-making and face penalties for non-compliance.
- **Explicit research questions (RQ1–RQ4)** listed here (see Style Guide for format).

### 1.3 Research Objectives
- O1: Design a modular desktop architecture for an SME accounting platform (MVP→35 screens).
- O2: Implement the Algerian tax engine (IBS 19/23/26%, TVA 19/9/6/0%, IRG progressive brackets, CNAS/CNAC social contributions, VF, DAS) with an automated tax calendar.
- O3: Provide advanced financial analysis (20 ratios, DuPont decomposition, Altman Z-Score, scenario analysis, benchmarking, cost-center profitability).
- O4: Integrate lightweight AI capabilities (forecasting, anomaly detection, risk patterns) without heavy ML dependencies.
- O5: Validate quality via 1800 automated tests + 100% module coverage + performance targets (startup ≈44 ms, memory ≤45 MB).

### 1.4 Methodology (brief)
Design-science research: problem identification → requirement elicitation → iterative prototyping (v1.0→v3.1.7) → automated testing → UAT. Full methodology in Chapter 3.

### 1.5 Thesis Structure
One-paragraph preview of chapters I–VIII.

---

## II. Literature Review — 6–7 pages

**Objective:** position the work against AIS theory, financial-analysis literature, tax-compliance systems, and AI-in-finance; justify the gap.

### 2.1 Accounting Information Systems (AIS)
- Definition & components (people, processes, data, software, IT infrastructure — Romney & Steinbart).
- Evolution: manual → spreadsheet → packaged ERP → cloud/embedded intelligence.
- Modern AIS architecture: layered (data / business logic / presentation), modular extensibility.
- Table 2.1: AIS evolution stages (era, technology, limitations).

### 2.2 Financial Ratios & Analysis
- Ratio families: liquidity, solvency, profitability, efficiency, market.
- DuPont decomposition (ROE = Net margin × Asset turnover × Equity multiplier).
- Altman Z-Score (1968, emerging-market variants 2007) and bankruptcy prediction.
- Financial statement analysis for SMEs (limited audited data, cash-based reality).
- Table 2.2: the 20 implemented ratios grouped by family (liquidity/solvency/profitability/efficiency + 3 new input fields cash, operating expenses, average payables).

### 2.3 Tax Compliance Systems
- Algerian tax framework: IBS (production 19%, construction 23%, other 26%; minimum tax 10,000 DZD; loss carryforward 4 years; instalments 20/03–20/06–20/11; balance 30/04), TVA (19/9/6/0%, G50 monthly by day 20), IRG (0/20/30/35% brackets + 40% proportional deduction, 10% withholding), CNAS (employer 24.5% + employee 9%, ceiling 8×), CNAC (2%), VF (2%/1%), DAS (31/01).
- Digital tax solutions: e-filing platforms, DGI e-services, compliance automation research.
- Penalty structure (10% late + 3%/month) motivating automation.

### 2.4 AI in Financial Analysis
- Classical ML for SMEs: regression/ETS forecasting, z-score anomaly detection, IQR rules — chosen over deep learning for explainability and resource constraints.
- Explainability requirement for advisory outputs.
- Table 2.3: forecasting methods compared (linear regression / moving average / exponential smoothing with 95% confidence intervals).

### 2.5 Current Solutions & Gaps
- International: SAP Business One, Oracle NetSuite, Sage — cost, language, non-Algerian tax logic.
- Local Algerian offerings: brief survey (closed, desktop-only, weak analytics).
- **Identified gaps (G1–G5):** localization, compliance automation, affordability, analytics depth, testability/openness.

---

## III. Problem Analysis & Requirements — 4–5 pages

**Objective:** translate the gap into a verifiable requirements specification (IEEE 830-style).

### 3.1 Stakeholders & Use Cases
- Actors: SME owner, accountant/bookkeeper, tax preparer, administrator.
- UML use-case diagram (Figure 3.1) + priority matrix.

### 3.2 Functional Requirements
- FR1 Data entry: income statement/balance sheet editing, multi-year, validation (Table 3.1: FR catalogue with IDs, descriptions, priority).
- FR2 Analysis: 20 ratios, DuPont, Z-Score, comparative, cash-flow, forecasting, cost centers.
- FR3 Tax: IBS/TVA/IRG/CNAS calculators, reminders, G50/G57/DAS declaration templates, TVA carryover, IBS instalments.
- FR4 Reporting: PDF/Excel/HTML/TXT with Arabic PDF support; unified export layer (ui/exporters.py).
- FR5 Data: SQLite persistence, DB pooling, CSV import, cloud backup (AES-GCM optional), demo companies, multi-currency.
- FR6 Collaboration: user testing module, local AI chat assistant.

### 3.3 Non-Functional Requirements
- Performance: cold start ≤3 s (actual 44 ms), view load ≤1.5 s, memory ≤700 MB (actual 45 MB RSS), DB batch saves 4.6×.
- Security: PBKDF2 (100 k iterations + salt), AES-256 vault, encrypted SMTP/API keys, HTTPS-only update, 2FA, roles.
- Usability: 3 languages + RTL, 3 themes (light/dark/modern), accessibility contrast, keyboard shortcuts.
- Portability: Nuitka standalone (no Python install), silent auto-update.
- Maintainability: 100% module coverage, 1800 tests, i18n 1925 keys ×3.

---

## IV. Proposed Solution (Design) — 6–8 pages

**Objective:** present the architecture and justify technology choices.

### 4.1 System Overview
- Figure 4.1: layered architecture (presentation ui/views → controllers/services → modules/engines → persistence db/state) with lazy loading.
- Figure 4.2: package/module diagram (37 modules grouped by domain).
- Figure 4.3: data flow for a typical analysis request (view → engine → state/db → chart/PDF).

### 4.2 Technology Stack & Justification
- PyQt5 (desktop, RTL, themes), SQLite (zero-admin, WAL, pooling), matplotlib/NumPy/Pandas (analysis), FPDF/openpyxl (Arabic PDF/Excel), Nuitka (standalone exe 143 MB), Inno Setup (installer 66.9 MB), GitHub Actions CI.
- Table 4.1: technology vs alternative vs rationale.

### 4.3 Feature Modules (map to the 35 screens)
- Group by domain: data entry, analysis (ratios/DuPont/Z-Score/comparative/cash flow/forecasting/benchmarks/scenarios/cost centers/AI insights), tax (calculators/declarations/reminders), business (ledger/partners/invoicing/inventory/payroll/budgeting), platform (settings/security/currency/cloud sync/demo data/user testing/import/backup).
- Each group: screen list, engine module, key algorithm pointer.

### 4.4 Design Patterns
- Lazy view factory + PEP 562 module proxy (startup 778→44 ms), theme system, unified exporters, i18n engine (1925×3), command shortcuts.

### 4.5 Unique Features (differentiators)
- Algerian tax engine with legal calendar; RTL trilingual UI; offline AI insights; audit & exceptions logging; competitive benchmarking; demo companies with consistent fiscal data.

---

## V. Implementation Details — 8–10 pages

**Objective:** give reproducible implementation depth (pseudo-code + real results).

### 5.1 Core Implementation
- Database: schema design (financial data, ratios, tax tables, users, backups, dashboard layouts), WAL mode, connection pool, executemany batches (4.6× write gain).
- Security: PBKDF2 key derivation, AES-GCM cloud encryption, token-based session, credential vault.

### 5.2 Key Algorithms (pseudo-code + formulas)
- Ratio engine: canonical formulas for the 20 ratios (Table 5.1: ratio, formula, source).
- DuPont decomposition & waterfall chart.
- Z-Score (1.2X1+1.4X2+3.3X3+0.6X4+1.0X5) + Algerian/emerging-market sensitivity note.
- Forecasting: linear regression / moving average / exponential smoothing + 95% CI (Figure 5.1).
- Anomaly detection: z-score on profits + IQR on transactions (Figure 5.2).
- Cost-center allocation: direct/indirect keys (revenue, headcount, area, equal).
- Payroll: CNAS/IRG computation with 40% deduction logic (listing 5.1).

### 5.3 Export & Reporting
- Unified export layer (ui/exporters.py): new_workbook/add_excel_sheet/ask_save_path/style_header_row/write_charts_pdf; Arabic PDF via Amiri font fallback (cp1252 handling).
- PDF vs Excel vs HTML vs TXT matrix (Table 5.2).

### 5.4 Hardening & Packaging
- Lazy loading, no-redraw dashboard, memory cap verification.
- Nuitka build pipeline (build_nuitka.py incl. dynamic imports fix — include-package ui.views), Inno Setup installer excluding state files (upgrade preserves users.json), portable ZIP, auto-update (version.json + silent VBS update).

---

## VI. Testing & Results — 6–8 pages

**Objective:** evidence-based validation of correctness, quality, and performance.

### 6.1 Testing Strategy
- Pyramid: unit (37 modules) → integration (workflows, DB integrity, concurrency, stress) → UI (35 views) → UAT (9 end-to-end journeys) → performance (4 regression tests).
- Table 6.1: test suite inventory (test files, counts, focus) — total 1800.
- CI: GitHub Actions (Ubuntu, Python 3.11, xvfb-run) + coverage informational.

### 6.2 Test Results
- Figure 6.1: pass-rate trend across versions (v1.x → v3.1.7: 318 → 1800).
- Figure 6.2: coverage by module (all 100%, 5768 lines).
- Bugs found & fixed table (Table 6.2): e.g., installer empty screens (missing sqlite3/pandas in upgrade), DuPont freeze (missing numpy), language-switch crash (_clear_layout), black-screen navigation animation, update resetting credentials (installer Excludes).

### 6.3 Performance & Validation Results
- Table 6.3: startup 778→44 ms, RSS 128→45 MB, DB write 4.6×, read 17×.
- UAT: full journey across 35 screens in 3 languages, user-satisfaction module results.
- Validation of tax calculations against hand-computed cases (Table 6.4: IBS/TVA/IRG/CNAS test vectors).

---

## VII. Evaluation & Discussion — 3–4 pages

**Objective:** interpret results against objectives and literature.

### 7.1 Achievement vs Objectives
- Table 7.1: objective → evidence (test/perf/feature).
- Comparison with baseline (spreadsheet workflows): time saved, error reduction argument.

### 7.2 Limitations
- Single-machine (no multi-user), static tax rates require config updates, forecasting accuracy limited on short histories, no bank API integration (manual bank sync), AI insights are rule-based (no deep learning).

### 7.3 Threats to Validity & Ethics
- Data privacy (GDPR-aligned consent), licensing of bundled libraries (PyQt5 GPL/commercial note), tax data handling.

---

## VIII. Conclusion & Future Work — 2–3 pages

### 8.1 Conclusion
- Restate problem → solution → verified results (1800 tests, 100% coverage, 44 ms startup, tax compliance embedded).

### 8.2 Contributions
- Scientific: localized tax-compliance model for SME software; lightweight explainable AI-in-finance pattern; open test-driven methodology for desktop financial apps.
- Practical: deployable product (v3.1.7), installer + portable + auto-update.
- Commercial: startup readiness under Arrêté 1275; patentable novelty (Algerian tax engine + unified export + offline AI).

### 8.3 Future Enhancements
- Cloud SaaS + multi-user, mobile companion, bank API (SADAD/ETEB interbank), OCR document capture, deeper ML (XGBoost/Prophet), ERP integration (SAP-style charts of accounts), e-filing DGI integration.

---

## IX. References
- See REFERENCES_TEMPLATE.md (APA 7th). Sections: academic papers (~25–35), regulations & official texts (loi 01-18/2001, arrêté 1275/2022, DGI directives, MIM bulletins), software documentation (PyQt5, SQLite, Nuitka, FPDF, pandas).

---

## X. Appendices (suggested)
- A: installation & run guide; B: screen catalogue (35 screens, 1 page each optional); C: test vectors for tax calculations; D: coverage report summary; E: i18n key statistics; F: patent/startup dossier notes (Arrêté 1275: description of innovation, novelty, prototype evidence).

---

## Figures & Tables Register (proposed numbering)
| # | Type | Content | Chapter |
|---|------|---------|---------|
| 1.1 | Figure | SME population growth 2012–2022 | I |
| 1.2 | Figure | Regional SME distribution | I |
| 2.1 | Figure | AIS evolution timeline | II |
| 3.1 | Figure | Use-case diagram | III |
| 4.1–4.3 | Figures | Architecture / modules / data flow | IV |
| 5.1–5.2 | Figures | Forecast & anomaly outputs | V |
| 6.1–6.2 | Figures | Test trend / coverage | VI |
| 2.1–2.3 | Tables | AIS stages / ratios / forecast methods | II |
| 3.1 | Table | FR catalogue | III |
| 4.1 | Table | Technology stack | IV |
| 5.1–5.2 | Tables | Ratio formulas / export matrix | V |
| 6.1–6.4 | Tables | Test inventory / bugs / perf / tax vectors | VI |
| 7.1 | Table | Objectives vs evidence | VII |

## Writing Workflow (suggested order)
1. Chapter I (this draft) → 2. Chapter VI skeleton (test inventory exists) → 3. Chapters III–IV (requirements + design) → 4. Chapter V (deepest; reuse modules/) → 5. Chapters II & VII (lit review last touches, discussion) → 6. Chapter VIII + Abstract (AR/FR/EN) + references.
