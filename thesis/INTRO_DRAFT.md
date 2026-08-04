# Chapter I — Introduction (Draft, ~3 pages)

> **Placeholders to fill before submission:** [University Name], [Faculty/Department], [Advisor Name], [Academic Year]. Citation numbers `[n]` map to REFERENCES_TEMPLATE.md.

---

## 1.1 Background

Small and medium-sized enterprises (SMEs) constitute the backbone of the Algerian private economy. According to the Ministry of Industry and Mines statistical bulletins, the SME population grew from 711,832 entities in 2012 to 1,359,803 at the end of 2022, representing approximately 95% of all registered enterprises and employing more than 70% of the private-sector workforce [MIM, 2022]. The structure of this population is dominated by micro-enterprises, which account for 97.6% of the total, while medium-sized enterprises represent only 0.27% [Sifer & Guehairia, 2024]. Regional distribution remains heavily imbalanced: nearly 70% of SMEs operate in the northern coastal region, with 22.1% on the High Plateaus and only 8.4% in the South; the national SME density of 28 enterprises per 1,000 inhabitants remains far below the international average of approximately 45 [Sifer & Guehairia, 2024].

Despite this demographic weight, Algerian SMEs face structural difficulties that limit their contribution to value added and formal economic growth. Access to finance is constrained by the absence of reliable, standardized financial statements; managerial capacity is concentrated in family-run structures with limited accounting expertise; and the operational environment is dominated by manual bookkeeping and spreadsheet-based record keeping [Saidat, Ataouat & Benchouiha, 2024]. These conditions generate late, erroneous, or absent tax declarations, exposing enterprises to the penalties defined by the tax code — a 10% late-payment penalty plus 3% per additional month of delay, as implemented in the platform's compliance engine.

## 1.2 Problem Statement

Three interconnected problems motivate this research.

First, **the absence of localized accounting solutions**. The leading international suites — SAP Business One, Oracle NetSuite, Sage — target large organizations, are priced beyond SME budgets, operate primarily in English, and apply generic tax frameworks that do not reflect the Algerian fiscal system. The Algerian tax calendar is demanding: monthly value-added tax declarations (TVA, form G n° 50, due by the 20th of each month); monthly income tax withholding (IRG) and social security contributions (CNAS/CNAC); three IBS instalments on 20 March, 20 June, and 20 November, with the annual balance due on 30 April; and the annual DAS salary declaration by 31 January. A compliant software product must encode these rules and deadlines natively.

Second, **the compliance burden falls disproportionately on micro-enterprises**. With rates varying by activity — IBS at 19% for production activities, 23% for construction, and 26% for other activities, with a 10,000 DZD minimum tax and a four-year loss carryforward; TVA at 19%, 9%, 6%, and 0% depending on the product category; IRG brackets of 0% to 35% with a 40% proportional deduction — manual computation is error-prone, and errors are costly for entities that cannot afford dedicated tax staff.

Third, **the absence of decision-support tools**. Even when SMEs maintain accounts, they rarely exploit the resulting data: financial ratio analysis, DuPont decomposition, bankruptcy-risk assessment (Altman Z-Score), scenario analysis, and forecasting remain academic exercises rather than daily managerial practices, because no affordable tool makes them accessible in the SME's own language (Arabic, French, or English) with right-to-left interface support.

## 1.3 Research Objectives

The overall objective of this thesis is to design, implement, and validate a desktop accounting platform that reconciles Algerian tax compliance with advanced financial analysis for SMEs. Specifically, the research pursues five objectives:

- **O1** — Design a modular, testable architecture for a lightweight desktop accounting platform that supports 35 interactive screens across data entry, analysis, tax, and administration domains.
- **O2** — Implement an Algerian tax-compliance engine covering IBS (19/23/26%), TVA (19/9/6/0%), IRG (progressive brackets with proportional deduction), CNAS/CNAC social contributions, the Versement Forfaitaire, and an automated tax calendar with reminders and declaration templates (G50, G57, DAS).
- **O3** — Provide an advanced financial analysis layer: 20 financial ratios, DuPont decomposition, Altman Z-Score, comparative and cash-flow analysis, scenario and benchmarking analysis, and cost-center profitability.
- **O4** — Integrate lightweight, explainable AI capabilities — forecasting (linear regression, moving average, exponential smoothing with 95% confidence intervals), anomaly detection (z-score and IQR rules), and risk-pattern identification — without external ML services or heavy dependencies.
- **O5** — Validate the platform through rigorous software-engineering practice: 1800 automated tests, 100% coverage of the 37 engine modules, performance regression tests (cold start of 44 ms, resident memory ≤45 MB), and end-to-end user acceptance journeys in three languages.

## 1.4 Methodology (Summary)

The research follows the design-science paradigm for information systems: the problem is formalized as a requirements specification (Chapter III); an artifact — the Smart Accounting Platform — is designed (Chapter IV) and implemented (Chapter V); and the artifact is validated through automated testing, performance measurement, and user acceptance testing (Chapter VI). Iterative releases (v1.0 through v3.1.7) allowed continuous feedback integration.

## 1.5 Expected Contributions

The thesis is expected to deliver:

- **Scientific contribution** — a localized model of tax-compliance automation for Algerian SME software (encoded rules, calendar, declaration templates), and a reusable pattern for lightweight explainable AI in desktop financial applications.
- **Practical contribution** — a deployable product distributed as a standalone executable (Nuitka, 143 MB), a silent auto-update mechanism, and a portable edition, usable by non-specialists.
- **Commercial contribution** — a product aligned with the national mechanism "One Diploma, One Startup / One Diploma, One Patent" (Arrêté ministériel n° 1275 of 27 September 2022), with documented innovation potential for startup status or software patent registration.

## 1.6 Thesis Structure

The remainder of this thesis is organized as follows. Chapter II reviews the literature on accounting information systems, financial ratio analysis, tax-compliance systems, and AI in finance, and identifies the research gap. Chapter III analyzes the problem and specifies functional and non-functional requirements. Chapter IV presents the proposed architecture and technology choices. Chapter V details the implementation of the core algorithms, database design, security mechanisms, and packaging. Chapter VI reports the testing strategy and results, including the 1800-test suite and performance measurements. Chapter VII evaluates the platform against the objectives and discusses limitations. Chapter VIII concludes and outlines future work, including cloud deployment, mobile access, and e-filing integration.

---

## Key Facts Used in This Chapter (verification sheet)

| Statement | Source |
|---|---|
| SME count 711,832 (2012) → 1,359,803 (2022) | MIM Bulletin n° 42 [Saidat et al., 2024] |
| SMEs ≈95% of enterprises, >70% private workforce | MIM 2022 [Sifer & Guehairia, 2024] |
| 97.6% micro-enterprises; 0.27% medium | Sifer & Guehairia, 2024 |
| Density 28/1000 vs ~45 international | Sifer & Guehairia, 2024 |
| North 69.5% / Highlands 22.1% / South 8.4% | SNAT data, MIM 2022 |
| IBS rates 19/23/26%, min tax 10,000 DZD, 4-year carryforward | Platform tax engine (modules/tax_config.json, v1.0.0) |
| TVA 19/9/6/0%, G50 by day 20 | Platform tax engine |
| IRG 0–35% brackets, 40% proportional deduction | Platform tax engine |
| CNAS 24.5% employer + 9% employee; CNAC 2% | Platform tax engine |
| Penalties 10% + 3%/month | Platform tax engine (cnas.penalties) |
| IBS instalments 20/03, 20/06, 20/11; balance 30/04; DAS 31/01 | Platform tax engine (tax_calendar) |
| Startup/patent mechanism | Arrêté ministériel n° 1275, 27/09/2022 (mod. arrêté n° 008) |
| 35 screens, 37 modules, 1800 tests, 100% coverage, 44 ms startup, ≤45 MB RSS | Project v3.1.7 (docs/, PROJECT_MAP.md) |
