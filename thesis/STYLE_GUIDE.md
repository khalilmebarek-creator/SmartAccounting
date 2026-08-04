# Thesis Style Guide (Algerian Master's — English medium)

Companion to `thesis_template.docx` and aligned with the national thesis regulations (Arrêté du 29/12/2014 for master's thesis elaboration/defense) and the innovation framework (Arrêté 1275/2022).

---

## 1. Global Formatting (match the DOCX template)

| Element | Rule |
|---|---|
| Page size | A4 (210 × 297 mm) |
| Margins | Left 3 cm (binding), right 2.5 cm, top 2.5 cm, bottom 2.5 cm |
| Font | Times New Roman 12 pt (body); headings TNR bold, not larger than 14 pt |
| Line spacing | 1.5 for body; single inside tables/figure captions |
| Alignment | Justified body text; left-aligned headings |
| Page numbers | Bottom-center, Arabic numerals starting at Chapter I; front matter numbered i, ii, iii… in lower Roman |
| Chapters | Each chapter starts on a new page |
| Paragraph | First line indent 0.75 cm (or block style with spacing — pick ONE and stay consistent) |
| Language | English body; abstract in Arabic + English (+ French per faculty); quotations >3 lines = indented block, no quotes |
| Numbers | Use "1,000,000" (comma) in English text; "1 000 000" (thin space) in French excerpts |

## 2. Front Matter Order (per Algerian convention)
1. Page de garde (university logo, republic + ministry headers, title, degree, faculty, department, student names, advisor, academic year) — template provided.
2. Dedication (optional).
3. Acknowledgments.
4. Abstract (Arabic) — الملخص.
5. Abstract (English) + keywords.
6. Abstract (French) — Résumé + mots-clés (if faculty requires).
7. Table of contents (auto-generated field).
8. List of figures / list of tables / list of abbreviations.
9. Introduction (Chapter I) begins the Arabic numbering.

## 3. Heading Hierarchy & Capitalization
- **Level 1 (chapter):** "CHAPTER I: INTRODUCTION" — centered, bold, 14 pt.
- **Level 2 (section):** "1.1 Background" — bold, left, 12 pt.
- **Level 3 (subsection):** "1.1.1 Micro-enterprise structure" — italic bold, left, 12 pt.
- Sentence case only (never ALL CAPS for L2/L3). Numbering: chapter.section.subsection.

## 4. Academic Voice & Wording
- Write impersonally: "the platform was evaluated…" / "the experiment shows…" (avoid "I/we" except in acknowledgment).
- Use precise reporting verbs: propose, demonstrate, validate, measure, reveal, contradict.
- Define every acronym at first use (TVA, IBS, IRG, CNAS, CNAC, VF, DAS, AIS, ROE, RSS, UAT, RTL).
- No marketing superlatives ("powerful", "revolutionary"); prefer measurable claims ("cold start 44 ms", "1800/1800 tests pass").
- Claims need a citation or a measurement; distinguish **designed** vs **implemented** vs **measured** vs **verified by test**.

## 5. Figures & Tables
- Numbering: "Figure 2.3" = chapter.figure-index; "Table 4.1" likewise (registers in OUTLINE.md).
- Caption above tables (Table X: …), below figures (Figure X: …), 11 pt, centered, same font.
- Every figure/table must be referenced in text before it appears ("…as shown in Figure 4.1").
- Sources under figures/tables ("Source: Ministry of Industry and Mines, Bulletin n° 42" or "Source: Author (platform output, v3.1.7)").
- Screenshots: capture at 100% zoom, GUI in Arabic version for authenticity + English captions.
- Diagrams: use one consistent notation (UML for architecture/use-cases; flowchart for algorithms).

## 6. Citations & References (APA 7th)
- In-text: (Sifer & Guehairia, 2024); for 3+ authors use (Saidat et al., 2024). Numbered style [n] only if your faculty mandates it — do not mix styles.
- Reference list: alphabetical, hanging indent 0.5 cm, single spacing with 6 pt after.
- Secondary citations: cite only what you actually read; use "as cited in …" otherwise.
- Legal texts: cite as regulations, e.g. *Arrêté ministériel n° 1275 du 27 septembre 2022*, *Journal officiel de la République algérienne*, and use them in-text descriptively.
- Cite the platform's own documentation when describing internals you built: e.g., "Smart Accounting Platform documentation (PROJECT_MAP.md, 2026)" — or simply "Source: Author".

## 7. Writing Checklist per Chapter
- [ ] Chapter opens with 2–4 sentence roadmap ("This chapter…").
- [ ] Every section ends with a bridging sentence to the next.
- [ ] No paragraph longer than ~150 words.
- [ ] Each claim × citation × figure × table cross-checked.
- [ ] Terminology consistent (platform name: *Smart Accounting Platform*; version format v3.1.7).
- [ ] PDF/Word export keeps Arabic rendering intact (embed Arabic-capable font when exporting the bilingual abstract).

## 8. Plagiarism & Integrity
- Quote verbatim only with quotation marks + citation; paraphrase with citation.
- Self-plagiarism: screenshots/numbers from your own reports are fine, but wording must be rewritten for the thesis.
- Use a similarity-check tool; target < 15% overall and < 5% per source.
