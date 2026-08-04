# Chapter II — Literature Review Framework

**Purpose:** a structured search-and-synthesis plan that lets you write Chapter II (6–7 pages) with academic rigor and real citations. Each section lists (a) the search strategy, (b) the synthesis matrix, and (c) the key sources to locate.

---

## 2.0 How to Use This Framework

1. **Search** in the databases below using the keyword triplets per section.
2. **Filter** (2020–2026 preferred; classics kept for theory — DuPont 1920s, Altman 1968, Z-Score revisited 2007).
3. **Log** each paper in the synthesis matrix (table per section): author/year / topic / method / relevant finding / where cited in the thesis / status (read ✓ / skim / drop).
4. **Write** each subsection as: definition → evolution → Algerian/contextual application → relevance to the artifact → one line linking to the design choice you made.

**Databases:** Google Scholar, Scopus, Web of Science, ScienceDirect, IEEE Xplore, SpringerLink, DOAJ (open-access French/Maghreb journals), Université Numérique platforms (CERIST DZ), theses from Algerian universities (DZ theses), Journals USTHB.

**Timebox:** ~1 real working day per subsection; total ~5–6 days for the whole chapter, then tighten to 6–7 pages.

---

## 2.1 Accounting Information Systems (AIS)

**Search terms:** `"accounting information system" AND SME AND (design OR architecture)`, `"AIS" AND "success factors" AND developing countries`, `"ERP" AND SMEs AND (adoption OR cloud)`, `systèmes d'information comptables PME Algérie`.

**Core theory anchors to cite:**
- Romney, M. B., & Steinbart, P. J. — *Accounting Information Systems* (canonical AIS definition + components: people, procedures, data, software, infrastructure, internal controls).
- Beard & Sumner / DeLone & McLean (IS success model) — for stating assessment criteria.
- Spathis & Constantinides — AIS in SMEs.
- Granlund & Mouritsen — ERP introduction in accounting.

**Synthesis matrix columns:** author(yr) | theory/model | components/constructs | empirical context | relevance to our layered architecture (§4.1) | status.

**What to claim in the thesis:** AIS evolved from manual ledgers → spreadsheet islands → integrated ERP → cloud/embedded intelligence; our platform instantiates the classic layered AIS with the modern addition of embedded analytics, and its design is justified by SME resource constraints (avoiding ERP-grade complexity).

---

## 2.2 Financial Ratios & Analysis

**Search terms:** `"financial ratio analysis" AND SMEs`, `"DuPont analysis" AND ROE AND decomposition`, `"Altman Z-Score" AND emerging markets AND SMEs`, `bankruptcy prediction SMEs`, `"horizontal/vertical analysis"`, `ratio analysis limitations SMEs`.

**Core theory anchors:**
- DuPont decomposition (1920s, refined by Collins et al.): ROE = Net margin × Asset turnover × Equity multiplier.
- Altman, E. I. (1968) "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy"; Altman (2007) revisited for emerging markets / private firms; Altman, Hartzell & Peck (1995) emerging-market scoring.
- Beaver (1966) univariate prediction — historical baseline.
- Ratio-families taxonomy (liquidity / solvency / profitability / efficiency / market).
- SME-specific caveats: lack of audited statements, cash-basis reality (note: the platform added the fields **cash, operating expenses, average payables** precisely to make ratios computable from SME reality).

**Deliverable table for the thesis (Table 2.2):** enumerate the 20 implemented ratios grouped by family, with the canonical formula and the source (one of the above anchors).

**Relevance line:** the platform adopts the standard ratio taxonomy but adapts inputs to the sparse data SMEs can actually provide.

---

## 2.3 Tax Compliance Systems

**Search terms:** `"tax compliance" AND automation AND SMEs`, `"fiscal compliance" AND software`, `e-filing adoption developing countries`, `TVA IBS IRG PME Algérie`, `imposition des sociétés algériennes`, `avis d'imposition DGI e-services`.

**Legal/regulatory anchors (cite these directly):**
- Ministry of Industry and Mines statistical bulletins (BIS-PME n° 40, n° 42) — SME statistics.
- Algerian fiscal code (Code des impôts directs et taxes assimilées — CIDTA) for IBS; Code de la TVA; IRG rules (Law of finance updates).
- Arrêté ministériel n° 1275 du 27/09/2022 — "One Diploma, One Startup / One Diploma, One Patent" (innovation-product angle).
- Arrêté du 29/12/2014 — modalités d'élaboration et de soutenance du mémoire de master (formal thesis rules; jury 3–5 members, mentions, public defense).
- loi n° 01-18 du 12/12/2001 — SME promotion framework (context).
- DGI e-services / télédéclaration documentation (compliance digitization trend).

**Practical rates to reuse (already validated in the platform's `modules/tax_config.json`):**
- IBS: production 19%, construction 23%, other 26%; minimum 10,000 DZD; 4-yr loss carryforward; instalments 20/03, 20/06, 20/11; balance 30/04.
- TVA: 19% / 9% / 6% / 0%; monthly G50 by day 20; TVA credit carryover.
- IRG: brackets 0% (≤120,000), 20%, 30%, 35%; 40% proportional deduction (annual min 12,000 / max 18,000 DZD); withholding 10%.
- CNAS: employer 24.5% + employee 9% (total 33.5%), ceiling 8×; CNAC 2%; VF 2% (1% construction), paid monthly by day 20; DAS by 31/01; penalties 10% + 3%/month.

**Synthesis:** international digital-tax literature (e-filing → lower error cost) + Algerian specifics → gap: no SME-oriented offline desktop tool automates this full calendar.

---

## 2.4 AI in Financial Analysis

**Search terms:** `"machine learning" AND "financial forecasting" AND SMEs`, `"time series forecasting" AND (ARIMA OR exponential smoothing OR moving average)`, `"anomaly detection" AND financial transactions AND (z-score OR IQR)`, `explainable AI finance`, `"unsupervised" fraud detection bookkeeping`.

**Core theory anchors:**
- Exponential smoothing (Holt / Holt-Winters), ARIMA (Box-Jenkins) — forecasting baseline; note data-hunger.
- z-score / IQR outlier detection — light, explainable; justified over deep learning for SME scale and for the explainability requirement (Gunning's XAI framing) because advisory outputs must be trusted by non-technical users.
- Recent surveys of AI in accounting/finance (2022–2025) to cite the state of the art and the trend toward embedded, low-cost intelligence.

**Relevance line:** the platform deliberately chooses classical, interpretable methods (linear regression, moving-average, exponential smoothing, z-score, IQR) to satisfy O4 (no external services, explainable outputs, 95% confidence intervals).

---

## 2.5 Current Solutions & Gaps (State of the Art)

**Search terms:** `SAP Business One Algeria roadmap`, `NetSuite SME pricing`, `Sage Algeria PME`, `logiciel comptable algérien PME`, `comptabilité locale ALGOSS LSYS` (verify current vendors), international SME-accounting SaaS (QuickBooks, Zoho Books — note their non-Algerian tax logic).

**Build Table 2.4 (positioning matrix):** criterion rows (price, language, RTL, Algerian tax engine, ratios/analytics, offline mode, testability/openness, install size) × columns (SAP B1, NetSuite, Sage, QuickBooks/Zoho, local Algerian packages, **our platform**). Fill honestly; where a competitor's cell is uncertain, mark "—" rather than guess.

**Identified gaps (carry to Chapter III):**
- **G1** Localization: none embeds the Algerian tax calendar + RTL trilingual UI.
- **G2** Compliance automation: no built-in G50/G57/DAS templates + reminders.
- **G3** Affordability/portability: international suites need servers or licenses; offline free-standing executable matters for SME constraints (intermittent connectivity).
- **G4** Analytics depth: 20 ratios + DuPont + Z-Score + scenarios + benchmarking in one tool.
- **G5** Engineering rigor: open test-driven development (1800 tests, 100% coverage) is absent from proprietary local packages.

---

## 2.6 Literature Review Conclusion (template paragraph)

> "The literature establishes a solid theoretical basis for AIS design (§2.1), ratio-based analysis (§2.2), and compliance automation (§2.3), and shows that lightweight, explainable AI is achievable at SME scale (§2.4). However, no identified solution simultaneously provides (i) native Algerian tax compliance, (ii) advanced financial analysis, and (iii) offline, affordable deployment. This gap (G1–G5) justifies the design-science artifact developed in this thesis."

**Wrap-up checklist before writing the chapter:**
- [ ] ≥ 30 sources logged; classics (DuPont/Altman/Beaver/Romney) present.
- [ ] ≥ 10 sources dated 2020+ (currency).
- [ ] Table 2.4 positioning matrix filled.
- [ ] Each subsection ends with a "relevance to our design" sentence.
- [ ] Paragraph-by-paragraph citation plan avoids orphan references.