# Smart Accounting Platform — Video Tutorial Script + Production Guide

**Product:** Smart Accounting Platform v3.1.7
**Target audience:** Algerian SMEs, Accountants, Entrepreneurs, Investors
**Language:** English narration + Arabic/English UI
**Target duration:** 12–15 minutes
**Output:** Full script, shot list, storyboard, B-roll suggestions

---

## Video Structure Overview

| # | Section | Duration | Screen | Action |
|---|---------|----------|--------|--------|
| 1 | Opening + Value Proposition | 0:00–0:30 | Splash / intro slide | Brand intro, key numbers |
| 2 | Getting Started | 0:30–1:30 | Login → Dashboard | First login + password change |
| 3 | Data Entry | 1:30–3:30 | Data Entry screen | Enter financial data, calculate |
| 4 | Financial Dashboard | 3:30–5:00 | Dashboard + Ratios | Charts, ratios, KPIs |
| 5 | Advanced Analysis | 5:00–7:00 | DuPont + Z-Score + Scenarios | Walk-through each |
| 6 | Tax Compliance | 7:00–9:00 | Tax + Calendar | IBS/TVA/IRG calculators + reminders |
| 7 | AI & Forecasting | 9:00–10:30 | AI Insights + Forecast | Predictions + anomaly detection |
| 8 | Productivity Features | 10:30–11:30 | Cloud + Import + Export | Backup, CSV import, PDF/Excel |
| 9 | Closing + CTA | 11:30–12:00 | Closing slide | Download link, patent info |

---

## SECTION 1: Opening (0:00–0:30)

**VISUAL:** Animated logo reveal → key stats overlay (dark theme, gold accents)
```
[0:00] LOGO REVEAL — Smart Accounting Platform
[0:02] STAT 1: "35 Interactive Screens"
[0:04] STAT 2: "20 Financial Ratios + DuPont + Z-Score"
[0:06] STAT 3: "100% Algerian Tax Compliance"
[0:08] STAT 4: "AI-Powered Insights"
[0:10] STAT 5: "3 Languages — Arabic, English, French"
[0:12] STAT 6: "1800 Automated Tests"
[0:15] Voice-over begins
```

**VOICE-OVER (VO):**
> "Meet Smart Accounting Platform — the first Algerian-built accounting solution that combines full tax compliance with advanced financial analysis and AI-powered insights. Built for Algerian SMEs, designed for the world."

---

## SECTION 2: Getting Started (0:30–1:30)

**VISUAL:** App launch → Login screen

```
[0:30] LAUNCH — Double-click SmartAccounting.exe
        → Window appears in <1 second (44ms cold start)
        → Arabic RTL interface loads
[0:35] LOGIN SCREEN
        → Default admin: admin / Admin@1234
        → Type credentials → Login
[0:40] PASSWORD CHANGE DIALOG (first-time demo)
        → "You must change your password"
        → Enter old + new password → OK
[0:50] SIDEBAR APPEARS — 35 screens organized in groups
        → Highlight the sidebar width (250px, fixed)
        → Show the language selector (AR/EN/FR)
        → Show the theme toggle button (dark/light)
[1:00] THEME TOGGLE — Ctrl+T
        → Click → instant dark mode
        → Click again → light mode
        → Highlight: "All 3 themes built-in — no restart needed"
[1:10] SHORTCUTS DIALOG — F1
        → Show all keyboard shortcuts
        → Highlight: Ctrl+1 through Ctrl+Shift+D
[1:20] STATUS BAR
        → Shows "Welcome: admin (Admin)" + current theme
        → Auto-save indicator
```

**VO:**
> "Launch takes under one second. Log in with the default admin account — on first login, you'll be prompted to set a new password. The sidebar gives you instant access to all 35 screens. Press F1 to see every keyboard shortcut. Toggle between light and dark themes with Ctrl+T — no restart needed. The platform supports Arabic right-to-left, English, and French."

---

## SECTION 3: Data Entry (1:30–3:30)

**VISUAL:** Data Entry screen (the core input screen)

```
[1:30] NAVIGATE TO DATA ENTRY — Ctrl+1
        → Screen loads in <100ms
[1:35] FIELD TOUR — Tour the input fields
        → Revenue (إيرادات) — enter 5,000,000
        → COGS (تكلفة البضاعة) — enter 3,000,000
        → Operating Expenses (مصاريف تشغيل) — enter 800,000
        → Cash (صندوق) — enter 500,000
        → Average Payables (متوسط الذمم المدينة) — enter 200,000
        → Total Assets (إجمالي الأصول) — enter 4,000,000
        → Total Equity (رأس المال) — enter 2,500,000
        → Total Liabilities (الخصوم) — enter 1,500,000
[1:50] SPIN BOXES — Highlight empty-before-input feature
        → Show: fields display "أدخل المبلغ" (Enter amount) not 0.00
        → Type a number → it replaces the placeholder
[2:00] MULTI-YEAR COMPARISON
        → Click "Add Year" → Year 2 columns appear
        → Enter Year 1 and Year 2 data side by side
        → Show: "Horizontal analysis compares year-over-year"
[2:20] CALCULATE — Ctrl+R
        → Click "Calculate Ratios" button
        → Loading indicator → Results appear instantly
        → Show: the ratios section updates with 20 ratios
[2:40] SAVE TO DATABASE — Ctrl+S
        → Click "Save" → success message
        → Show: data is persisted to SQLite
[2:50] EXPORT — Ctrl+E
        → Click Export → PDF dialog opens
        → Choose location → PDF generated
        → Show: Arabic content renders in PDF
[3:10] PRINT — Ctrl+P
        → Print dialog opens
        → Cancel → back to data entry
[3:20] NAVIGATION SHORTCUTS
        → Ctrl+2 = Dashboard
        → Ctrl+3 = Ratios
        → Ctrl+4 = DuPont
        → Show: sidebar highlights change
```

**VO:**
> "Data Entry is your command center. Enter revenue, costs, assets, and equity — notice the fields show a placeholder instead of zero, so you always know what's been entered. Add multiple years for horizontal comparison. Hit Ctrl+R to calculate all 20 financial ratios instantly. Save to the database with Ctrl+S — everything persists locally in SQLite. Export any view to PDF with Ctrl+E or print with Ctrl+P. Navigate between screens with Ctrl+1 through Ctrl+0."

---

## SECTION 4: Financial Dashboard (3:30–5:00)

**VISUAL:** Dashboard (screen 2) + Ratios (screen 3)

```
[3:30] DASHBOARD — Ctrl+2
        → Revenue chart (monthly bar chart)
        → Expense breakdown (pie chart)
        → KPI cards (Net Profit, ROE, Current Ratio)
        → Show: "No data" state vs "with data" state
[3:50] RATIOS — Ctrl+3
        → Full table of 20 ratios
        → Liquidity: Current Ratio, Quick Ratio, Cash Ratio
        → Profitability: ROE, ROA, Net Margin, Gross Margin
        → Solvency: Debt-to-Equity, Interest Coverage
        → Efficiency: Asset Turnover, Inventory Turnover
        → Highlight: each ratio has a benchmark color (green/yellow/red)
[4:10] INTERACTIVE BARS
        → Click on a ratio → detail view opens
        → Show: formula explanation + benchmark comparison
[4:30] EXPORT RATIOS
        → Click Export → Excel workbook opens
        → Show: 5 sheets (Ratios, Ranking, Comparisons, Standards, Recommendations)
        → Show: header styling (1F4E79 blue, white text)
[4:50] PDF EXPORT
        → Click Export PDF → charts embedded
        → Show: multi-page PDF with charts + tables
```

**VO:**
> "The Dashboard gives you an instant overview — revenue trends, expense breakdown, and key performance indicators. Dive deeper into the Ratios screen: 20 financial ratios organized by family — liquidity, profitability, solvency, and efficiency. Each ratio is color-coded against industry benchmarks. Export everything to Excel with properly formatted sheets, or to PDF with embedded charts."

---

## SECTION 5: Advanced Analysis (5:00–7:00)

**VISUAL:** DuPont (4) + Z-Score (13) + Scenarios (22)

```
[5:00] DUPONT ANALYSIS — Ctrl+4
        → Waterfall chart showing ROE decomposition
        → ROE = Net Margin × Asset Turnover × Equity Multiplier
        → Bar chart comparison across years
        → Gauge indicator showing current ROE
        → Highlight: "This is the most advanced DuPont implementation in any Algerian accounting tool"
[5:30] SECTOR COMPARISON
        → Select sector from dropdown (General/Manufacturing/Services/Trade)
        → Show: comparison bars (your company vs sector average)
        → Recommendation text appears below
[5:50] Z-SCORE — Ctrl+Shift+3
        → Altman Z-Score gauge (red/yellow/green zones)
        → Score: 2.7 → "Grey Zone" warning
        → Historical trend chart
        → Risk assessment text
[6:10] SCENARIO ANALYSIS — F3
        → Three scenarios: Optimistic / Normal / Pessimistic
        → Tornado sensitivity chart
        → Line chart showing all three trajectories
        → "What-if" sliders for key variables
        → Export scenarios to JSON / PDF
[6:40] BREAK-EVEN — Ctrl+Shift+7
        → Break-even chart with fixed/variable costs
        → Break-even point highlighted
        → Margin of safety calculation
[6:50] BUDGET vs ACTUAL — Ctrl+Shift+5
        → Side-by-side comparison
        → Variance analysis
        → Color-coded over/under budget
```

**VO:**
> "DuPont Analysis decomposes Return on Equity into three drivers — profitability, efficiency, and leverage — with a waterfall chart and sector comparison. The Z-Score gauge shows bankruptcy risk at a glance: green means safe, red means danger. Scenario Analysis lets you model optimistic, normal, and pessimistic outcomes with a Tornado sensitivity chart. Break-even analysis shows exactly when your business becomes profitable."

---

## SECTION 6: Tax Compliance (7:00–9:00)

**VISUAL:** Tax screen (9) + Tax Calendar (19)

```
[7:00] TAX SYSTEM — Ctrl+0
        → Tax calculator tabs: IBS, TVA, IRG, CNAS, CNAC, VF
[7:05] IBS CALCULATOR
        → Select activity type: "نشاط إنتاجي" (Manufacturing)
        → Rate: 19% auto-selected
        → Enter taxable income: 3,000,000
        → Calculate: IBS = 570,000
        → Show: minimum tax 10,000 DZD applied
        → Show: loss carryforward option (4 years)
        → Show: reinvested profit deduction (10%)
[7:20] TVA CALCULATOR
        → Standard rate 19% / Reduced 9% / Intermediate 6% / Zero 0%
        → Enter sales + purchases
        → Calculate: TVA due = (Sales × 19%) - (Purchases × 19%)
        → Show: TVA credit carryover logic
[7:35] IRG CALCULATOR
        → Progressive brackets displayed:
          • 0 – 120,000: 0%
          • 120,001 – 360,000: 20%
          • 360,001 – 1,440,000: 30%
          • > 1,440,000: 35%
        → Enter monthly salary: 150,000
        → Show: 40% proportional deduction applied
        → Result: IRG = 0 (within exempt bracket)
[7:50] CNAS
        → Employer: 24.5% (Social 12.5% + Work Accident 1.25% + Retirement 10.5% + Early Ret. 0.25%)
        → Employee: 9% (Social 1.5% + Retirement 6.75% + Unemployment 0.75%)
        → Ceiling: 8 × SMIG
        → Enter base salary → auto-calculate both shares
[8:05] TAX CALENDAR — Ctrl+Shift+9
        → Monthly obligations: TVA, IRG, CNAS, CNAC, VF → due day 20
        → Quarterly: IBS instalments (Mar 20, Jun 20, Nov 20)
        → Annual: DAS (Jan 31), IBS Balance (Apr 30)
        → Visual calendar with color-coded deadlines
        → Alert banner at top: "3 obligations due in 5 days"
[8:20] DECLARATIONS
        → G50 (TVA monthly) template
        → G57 (TVA annual) template
        → DAS (salary declaration) template
        → Export to PDF/Excel
[8:40] TAX REMINDERS
        → Notification system for upcoming deadlines
        → Show: popup when deadline is near
        → Show: penalty calculation (10% + 3%/month)
```

**VO:**
> "The Tax System is the heart of compliance. Six calculators built into one screen — IBS with activity-based rates from 19 to 26 percent, TVA with four rate tiers, IRG with progressive brackets and the 40 percent proportional deduction, CNAS with employer and employee shares, CNAC, and Versement Forfaitaire. The Tax Calendar shows all your monthly, quarterly, and annual obligations with color-coded deadlines. Never miss a filing — the platform reminds you before each due date."

---

## SECTION 7: AI & Forecasting (9:00–10:30)

**VISUAL:** AI Insights (24) + Forecasting (14)

```
[9:00] AI INSIGHTS — F5
        → Method selector: Linear Regression / Moving Average / Exponential Smoothing
        → Enter forecast period: 6 months
        → Click "Analyze"
[9:10] FORECASTING RESULTS
        → Line chart: historical data + forecast + 95% confidence interval
        → Revenue, Expenses, Profit forecast lines
        → Growth rate displayed
[9:30] ANOMALY DETECTION
        → Z-score anomalies on profit data
        → IQR anomalies on transactions
        → Severity levels: Critical / Warning / Info
        → Show: flagged transaction highlighted in red
[9:50] RISK PATTERNS
        → Trend analysis (upward/downward/stable)
        → Seasonality detection
        → Risk score gauge
[10:00] SMART RECOMMENDATIONS
        → AI-generated suggestions
        → Priority levels (High / Medium / Low)
        → Action items with category tags
[10:10] EXPORT AI REPORT
        → PDF with charts + recommendations
        → Excel with forecast data
[10:20] FORECASTING SCREEN — Ctrl+Shift+4
        → Dedicated forecasting with 3 methods side by side
        → Compare: Linear vs Moving Average vs Exponential Smoothing
        → Show: which method fits best for different data patterns
```

**VO:**
> "AI Insights combines three forecasting methods — linear regression, moving average, and exponential smoothing — with 95% confidence intervals. Anomaly detection flags unusual profits and transactions using z-score and IQR rules. Risk patterns identify trends and seasonality. Smart recommendations give you actionable advice, prioritized by impact. All insights are explainable — no black box."

---

## SECTION 8: Productivity Features (10:30–11:30)

**VISUAL:** Cloud Sync (27) + Data Import (20) + Demo Data (28)

```
[10:30] CLOUD SYNC — Ctrl+Shift+8
        → Sync destinations: Dropbox / OneDrive / Google Drive
        → Snapshot with checksum verification
        → Optional AES-GCM encryption (password-protected)
        → Auto-backup schedule (daily/weekly)
        → Sync log showing recent operations
[10:50] DATA IMPORT — Ctrl+Shift+0
        → CSV import wizard
        → Map columns to fields
        → Validation preview
        → Import → success message
[11:00] DEMO DATA — F9
        → 4 pre-built companies:
          • Trading Company (تجارية)
          • Services Company (خدمات)
          • Manufacturing (إنتاج)
          • Import/Export (استيراد-تصدير)
        → Click "Load" → all data populates instantly
        → Show: full financial statements + ratios calculated
[11:15] EXPORT ANY SCREEN
        → Every screen has Export PDF / Export Excel
        → Show: consistent formatting across all exports
        → Highlight: unified export layer (3 screens share same code)
[11:25] MULTI-CURRENCY — F6
        → 7 default currencies with exchange rates
        → Convert amounts between currencies
        → Multi-currency report
```

**VO:**
> "Cloud Sync backs up your data with optional AES encryption. Data Import handles CSV files with a mapping wizard. Demo Data gives you four pre-built companies — load one and see the full platform in action instantly. Every screen exports to PDF and Excel with consistent formatting. Multi-currency support handles exchange rates and conversions."

---

## SECTION 9: Closing (11:30–12:00)

**VISUAL:** Closing slide with download links

```
[11:30] SUMMARY SLIDE
        → "35 screens • 20 ratios • 6 tax calculators • AI insights"
        → "100% Algerian tax compliance"
        → "3 languages: Arabic, English, French"
        → "1800 automated tests"
[11:40] DOWNLOAD OPTIONS
        → Installer: 66.9 MB (Inno Setup, silent install)
        → Portable: 109 MB (no installation needed)
        → Standalone: 143 MB (Nuitka compiled)
[11:50] PATENT / STARTUP INFO
        → "Developed under Arrêté 1275 — One Diploma, One Startup"
        → "Eligible for startup status and patent registration"
[11:55] CALL TO ACTION
        → "Download now: [github.com/...]"
        → "Star us on GitHub"
        → "Questions? Open an issue"
[12:00] LOGO + END
```

**VO:**
> "Smart Accounting Platform — built for Algerian SMEs, powered by AI, fully compliant with Algerian tax law. Download the installer or portable version from GitHub. Developed under the national 'One Diploma, One Startup' mechanism. Thank you for watching."

---

## PRODUCTION GUIDE

### Recording Setup
- **Screen recorder:** OBS Studio (free) or Camtasia
- **Resolution:** 1920×1080 (1080p)
- **Frame rate:** 30fps (sufficient for UI)
- **Mouse cursor:** Use highlight/zoom effect on click
- **Audio:** USB microphone, quiet room, record in WAV
- **Font size:** Increase app font to 14pt before recording (Settings → Font Size)

### Recording Checklist
- [ ] Clean desktop (no personal files visible)
- [ ] App set to Arabic mode (for authentic look)
- [ ] Demo data loaded (Company: Trading Company)
- [ ] Dark theme enabled (more professional)
- [ ] Notifications disabled (no pop-ups during recording)
- [ ] Test all keyboard shortcuts work
- [ ] Close other apps (reduce visual noise)

### Post-Production
- **Software:** DaVinci Resolve (free) or Adobe Premiere
- **Transitions:** Cut-only (no fancy transitions — keep professional)
- **Text overlays:** Use for keyboard shortcuts (show "Ctrl+R" when calculating)
- **Lower thirds:** Section titles at bottom-left
- **Music:** Subtle background (royalty-free, low volume)
- **Captions:** Add English subtitles (SRT file)
- **Thumbnail:** App screenshot + "Smart Accounting Platform v3.1.7"

### B-Roll Suggestions
- Algerian SME office scenes (stock footage)
- Calculator/accounting footage
- Charts and graphs animation
- Code editor showing the 1800 tests passing
- GitHub repo page with stars
- Mobile phone showing the GitHub release page

### Publishing
- **Platform:** YouTube (primary), LinkedIn (secondary)
- **Title:** "Smart Accounting Platform v3.1.7 — Full Demo for Algerian SMEs"
- **Description:** Feature list + download links + timestamps
- **Tags:** accounting, Algeria, SME, tax compliance, financial analysis, DuPont, Z-Score, AI
- **Thumbnail:** Clean, professional, app screenshot with key stats

### Keyboard Shortcut Quick Reference (for overlays)

| Shortcut | Action |
|----------|--------|
| Ctrl+1–0 | Screens 1–10 |
| Ctrl+Shift+1–0 | Screens 11–20 |
| F2–F12 | Screens 21–35 |
| Ctrl+R | Calculate Ratios |
| Ctrl+S | Save to Database |
| Ctrl+E | Export PDF |
| Ctrl+P | Print |
| Ctrl+T | Toggle Theme |
| Ctrl+L | Logout |
| F1 | Shortcuts Dialog |
