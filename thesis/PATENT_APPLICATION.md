# Demande de Brevet d'Invention — INAPI

**Date de dépôt :** [à compléter]
**Déposant :** MBKAREK Ahmed Khalil
**Établissement :** Université Ibn Khaldoun — Tiaret
**Spécialité :** Comptabilité et Fiscalité (Master 2)

---

## TITRE DE L'INVENTION

**Système et procédé automatisé d'analyse financière conforme à la fiscalité algérienne, intégrant des capacités d'intelligence artificielle pour les petites et moyennes entreprises**

*(System and automated process for financial analysis compliant with Algerian tax law, integrating artificial intelligence capabilities for small and medium enterprises)*

---

## 1. DOMAINE TECHNIQUE DE L'INVENTION

La présente invention concerne un système informatique et un procédé de traitement automatisé de données financières, plus particulièrement un système d'analyse financière de bureau destiné aux petites et moyennes entreprises (PME) algériennes, intégrant un moteur de conformité fiscale paramétrable selon la législation algérienne en vigueur, des capacités de prédiction et de détection d'anomalies par intelligence artificielle légère, ainsi qu'une interface utilisateur multilingue adaptée au contexte local.

---

## 2. ÉTAT DE L'ART (ANTECEDENTS)

### 2.1 Solutions internationales

Les logiciels de comptabilité et de gestion financière existants sur le marché international (SAP Business One, Oracle NetSuite, Sage, QuickBooks) présentent les limitations suivantes pour les PME algériennes :

- **Coût élevé** : abonnements mensuels de 50 à 500 USD/mois, inaccessibles pour 97,6% des entreprises algériennes (micro-entreprises).
- **Non-conformité fiscale** : aucun intègrement des taux algériens (IBS 19/23/26%, TVA 19/9/6/0%, IRG à barèmes progressifs, CNAS 24,5%+9%, CNAC 2%, VF 2%).
- **Langue et direction** : interfaces exclusivement en anglais/français sans support RTL (droite-à-gauche) pour l'arabe.
- **Absence de calendrier fiscal** : pas de rappels automatiques pour les échéances algériennes (G50 mensuel, IBS trimestriel, DAS annuel).

### 2.2 Solutions locales algériennes

Les logiciels comptables locaux disponibles présentent :

- Architecture fermée (closed-source), mono-utilisateur, sans API.
- Absence d'analyse financière avancée (pas de ratios, DuPont, Z-Score).
- Pas de module de conformité fiscale intégré (calcul IBS/TVA/IRG automatisé).
- Pas de capacités prédictives (forecasting, détection d'anomalies).
- Interfaces en arabe uniquement, sans internacionalisation.

### 2.3 Lacunes identifiées (G1 à G5)

| Lacune | Description |
|--------|-------------|
| G1 — Localisation | Aucun logiciel ne combine arabe RTL + français + anglais avec fiscalité algérienne |
| G2 — Conformité fiscale | Absence de moteur de calcul IBS/TVA/IRG/CNAS automatisé avec calendrier |
| G3 — Accessibilité financière | Les solutions existantes coûtent > 100 USD/mois, inadaptées aux PME algériennes |
| G4 — Profondeur analytique | Pas de combinaison ratios + DuPont + Z-Score + scénarios + benchmarking sectoriel |
| G5 — Vérifiabilité | Aucun logiciel local ne fournit 1800 tests automatisés + 100% de couverture module |

---

## 3. EXPOSÉ DE L'INVENTION

### 3.1 Problème technique résolu

L'invention résout le problème technique de l'absence de système intégré capable de :

1. **Calculer automatiquement** les obligations fiscales algériennes (IBS, TVA, IRG, CNAS, CNAC, VF) à partir des données financières saisies.
2. **Fournir des alertes calendrier** pour 13 échéances fiscales obligatoires (G50 mensuel, acomptes IBS trimestriels, solde IBS annuel, DAS).
3. **Analyser la santé financière** via 20 ratios + décomposition DuPont + score Altman Z-Score.
4. **Prédire l'évolution financière** sur 3 à 6 mois par trois méthodes (régression linéaire, moyenne mobile, lissage exponentiel) avec intervalles de confiance à 95%.
5. **Détecter les anomalies** dans les transactions et les ratios financiers (z-score + IQR).
6. **Fonctionner hors-ligne** sur poste de travail avec base de données locale (SQLite) et synchronisation cloud optionnelle chiffrée (AES-GCM).

### 3.2 Solution technique proposée

L'invention comprend un **système informatique de bureau** (desktop) comprenant les éléments suivants :

#### A. Moteur fiscal paramétrable (TaxEngine)

Un module de calcul configurable via fichier JSON (`tax_config.json`) permettant :

- **IBS** : application du taux selon le type d'activité (production 19%, construction 23%, autres 26%), vérification du minimum légal (10 000 DA), calcul des 3 acomptes trimestriels (20/03, 20/06, 20/11) et du solde (30/04).
- **TVA** : calcul aux 4 taux (19%, 9%, 6%, 0%), suivi du crédit TVA reportable (G N°50), détermination du montant net à payer ou à récupérer.
- **IRG** : application des 4 tranches progressives (0-120 000 DA à 0%, 120 001-360 000 DA à 20%, 360 001-1 440 000 DA à 30%, >1 440 000 DA à 35%) + prélèvement proportionnel à 40%.
- **CNAS** : calcul part patronale (24,5%) et salariale (9%) avec plafond.
- **CNAC** : part patronale (1,5%) et salariale (0,5%).
- **VF** : versement forfaitaire (2% activité standard, 1% construction).
- **Pénalités** : calcul automatique des majorations (10% + 3%/mois de retard).

#### B. Moteur d'analyse financière (CalculationEngine)

Un module calculant en batch **20 ratios financiers** regroupés en 5 familles :

- **Liquidité** : ratio courant, ratio acid-test, ratio de trésorerie.
- **Rentabilité** : marge brute, marge opérationnelle, marge nette, ROA, ROE.
- **Efficacité** : rotation des actifs, rotation des créances (DSO), rotation des stocks (DIO), rotation des dettes (DPO), cycle d'exploitation, cycle de conversion de trésorerie.
- **Solvabilité** : dettes/capitaux propres, ratio d'endettement, ratio d'autonomie financière.
- **Altman Z-Score** : scoring prédictif d'insolvabilité (Z = 1,2×X₁ + 1,4×X₂ + 3,3×X₃ + 0,6×X₄ + 1,0×X₅) avec zones safe/grey/danger.

#### C. Moteur de décomposition DuPont (FinancialAnalyzer)

Décomposition du ROE en trois facteurs multiplicatifs :
- **Marge nette** (net income / chiffre d'affaires)
- **Rotation des actifs** (chiffre d'affaires / actifs totaux)
- **Multiplicateur de capitaux propres** (actifs totaux / capitaux propres)

Avec comparaison sectorielle et recommandations d'optimisation.

#### D. Moteur d'intelligence artificielle légère (AIInsightsEngine)

Un module ne nécessitant que NumPy (sans dépendance scikit-learn) offrant :

1. **Prédiction** (forecasting) sur 3 à 6 mois par trois méthodes :
   - Régression linéaire avec intervalles de confiance à 95%
   - Moyenne mobile (fenêtre glissante de 3 périodes)
   - Lissage exponentiel (α = 0,3)

2. **Détection d'anomalies** par deux méthodes complémentaires :
   - Z-score sur les séries d'profits (seuil z > 2,0)
   - Règle IQR (interquartile) sur les montants de transactions (1,5 × IQR)

3. **Reconnaissance de schémas** :
   - Détection d'inversions profit→perte et inversement
   - Analyse des tendances (hausse/baisse/stable)
   - Calcul du taux de croissance

4. **Alertes intelligentes** classées par sévérité (low/medium/high) couvrant :
   - Liquidité insuffisante
   - Endettement excessif
   - Rentabilité en déclin
   - Anomalies de transactions

#### E. Benchmarking sectoriel (BenchmarkEngine)

Base de données de **7 secteurs d'activité algériens** (commercial, industriel, services, BTP, transport, santé, technologie) avec pour chaque secteur :
- 10 ratios de référence (min/avg/max/idéal)
- Meilleures pratiques dérivées automatiquement (60% de la distance avg→max)
- Standards internationaux de comparaison
- Scores de forces et faiblesses
- Évolution sectorielle multi-périodes
- Classement de concurrents

#### F. Analyse de scénarios (ScenarioAnalyzer)

Simulation financière sur 3 scénarios (mieux/actuel/pire) avec :
- Paramètres de variation configurables (revenus, coûts, efficacité)
- Analyse de sensibilité Tornado (7 paliers de ±20%)
- Comparaison multi-métriques (8 indicateurs)
- Graphiques de comparaison

#### G. Architecture technique innovante

1. **Chargement paresseux des vues** (lazy loading) : les 35 écrans ne sont instanciés que lors de leur première consultation, réduisant le temps de démarrage de 778 ms à 44 ms.

2. **Système de sécurité à plusieurs niveaux** :
   - Dérivation de clé PBKDF2 (100 000 itérations + salt)
   - Coffre-fort de credentials chiffré AES-256
   - Authentification à deux facteurs (2FA)
   - 4 rôles avec 16 permissions granulaires
   - Verrouillage après 5 tentatives échouées (15 min)

3. **Synchronisation cloud chiffrée** :
   - Snapshots avec checksum (SHA-256)
   - Chiffrement optionnel AES-GCM (120 000 itérations PBKDF2)
   - Rotation automatique des sauvegardes (max 20)
   - Journal d'opérations en base de données

4. **Export unifié** : couche d'exportation unique (PDF/Excel/CSV/HTML) avec support arabe (police Amiri), gestion des encodages (UTF-8, cp1252 fallback).

5. **Internationalisation** : 1925 clés i18n × 3 langues (arabe RTL, français, anglais), direction automatique du texte.

6. **Base de données locale** : SQLite en mode WAL avec pool de connexions, opérations batch (executemany), 15 tables relationnelles.

---

## 4. DESCRIPTION DÉTAILLÉE DE L'INVENTION (avec références aux figures)

### 4.1 Figure 1 — Architecture en couches du système

```
┌─────────────────────────────────────────────────┐
│              PRÉSENTATION (UI)                   │
│  35 écrans PyQt5 + thèmes (clair/sombre/moderne) │
│  Direction RTL arabe + raccourcis clavier         │
├─────────────────────────────────────────────────┤
│           CONTRÔLEURS / SERVICES                 │
│  MainWindow + AppState + 35 vues                 │
│  Lazy-loading factory + signaux pyqtSignal       │
├─────────────────────────────────────────────────┤
│          MOTEURS MÉTIER (37 modules)             │
│  TaxEngine │ CalculationEngine │ AIInsights      │
│  FinancialAnalyzer │ ScenarioAnalyzer            │
│  BenchmarkEngine │ CostCenterProfitability       │
│  CloudSync │ UserManager │ Ledger │ Invoicing    │
│  Inventory │ Payroll │ Budgeting │ Currency      │
├─────────────────────────────────────────────────┤
│            PERSISTANCE (Données)                 │
│  SQLite WAL │ Pool connexions │ executemany      │
│  JSON config │ Vault AES-256 │ CSV import        │
└─────────────────────────────────────────────────┘
```

### 4.2 Figure 2 — Flux de traitement d'une analyse fiscale

```
Saisie données financières
        │
        ▼
┌──────────────────┐     ┌──────────────────┐
│ CalculationEngine │────▶│   Ratios (20)    │
│  (batch calcul)   │     │   + Z-Score      │
└──────────────────┘     └────────┬─────────┘
        │                         │
        ▼                         ▼
┌──────────────────┐     ┌──────────────────┐
│    TaxEngine     │     │ FinancialAnalyzer │
│  IBS/TVA/IRG/    │     │   DuPont + Trend  │
│  CNAS/CNAC/VF    │     │   + Comparative   │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│  Tax Calendar    │     │  AIInsights      │
│  13 échéances    │     │  Forecast +      │
│  + rappels auto  │     │  Anomalies       │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         └───────────┬────────────┘
                     ▼
            Rapport consolidé
         (PDF / Excel / HTML)
```

### 4.3 Figure 3 — Schéma de la base de données (15 tables)

| Table | Description |
|-------|-------------|
| financial_data | Données financières saisies (22 champs) |
| ratios | Ratios calculés historisés |
| tax_config | Configuration fiscale paramétrable |
| users | Utilisateurs et rôles |
| sessions | Sessions actives (token + timeout) |
| audit_log | Journal d'audit des opérations |
| cloud_sync_state | État de synchronisation cloud |
| backups | Métadonnées des sauvegardes |
| dashboard_layouts | Dispositions personnalisées du tableau de bord |
| cost_centers | Centres de coûts et allocations |
| partners | Tiers (clients/fournisseurs) |
| invoices | Factures et lignes |
| inventory_items | Articles de stock |
| payroll_data | Données de paie |
| budget_items | Lignes budgétaires |

### 4.4 Figure 4 — Algorithme de détection d'anomalies

```
Entrée: série temporelle S = [s₁, s₂, ..., sₙ]
        ou liste de transactions T = [t₁, t₂, ..., tₘ]

Méthode 1 — Z-score (séries):
  μ = moyenne(S)
  σ = écart-type(S)
  Pour chaque sᵢ:
    z = |sᵢ - μ| / σ
    Si z > 2.0 → anomalie signalée (severity: low/medium/high)

Méthode 2 — IQR (transactions):
  Q1 = percentile(25)
  Q3 = percentile(75)
  IQR = Q3 - Q1
  borne_inf = Q1 - 1.5 × IQR
  borne_sup = Q3 + 1.5 × IQR
  Pour chaque tᵢ:
    Si tᵢ < borne_inf OU tᵢ > borne_sup → anomalie
```

### 4.5 Figure 5 — Algorithme de prédiction (forecasting)

```
Entrée: série S, horizon H (mois), méthode M

Si M = "linear":
  t = [0, 1, ..., n-1]
  pente, origine = polyfit(t, S, 1)
  Pour i = 1 à H:
    prédiction = origine + pente × (n + i)
    erreur_std = √(Σ(résidus²) / n)
    IC95% = [prédiction ± 1.96 × erreur_std × √(1 + 1/n + (x-x̄)²/Sxx)]

Si M = "moving_average":
  moyenne = moyenne(S[-3:])
  IC95% = moyenne ± 1.96 × σ(résidus)

Si M = "exp_smoothing":
  lissage = α × xₜ + (1-α) × lissageₜ₋₁   (α = 0.3)
  IC95% = lissage ± 1.96 × σ(résidus)
```

---

## 5. REVENDICATIONS (CLAIMS)

### Revendication 1 (Indépendante — Système)

Un système informatique de bureau destiné à l'analyse financière et à la conformité fiscale de petites et moyennes entreprises dans un contexte de législation algérienne, comprenant :

a) un **moteur de calcul fiscal paramétrable** (TaxEngine) configuré pour calculer automatiquement la contribution fiscale algérienne comprenant l'impôt sur les bénéfices des sociétés (IBS) selon des taux variables par activité, la taxe sur la valeur ajoutée (TVA) selon des taux multiples avec suivi du crédit reportable, l'impôt sur le revenu global (IRG) selon un barème progressif à quatre tranches, les cotisations de sécurité sociale (CNAS, CNAC) et le versement forfaitaire (VF), ledit moteur étant configuré par un fichier de paramètres JSON extensible permettant la mise à jour des taux sans modification du code source ;

b) un **moteur de calcul de ratios financiers** (CalculationEngine) configuré pour calculer en une seule opération batch au moins vingt ratios financiers regroupés en familles de liquidité, rentabilité, efficacité et solvabilité, incluant un score prédictif d'insolvabilité de type Altman Z-Score, et un indicateur de cycle de conversion de trésorerie ;

c) un **moteur d'intelligence artificielle légère** (AIInsightsEngine) ne nécessitant qu'une seule dépendance de calcul numérique (NumPy), configuré pour effectuer la prédiction de séries financières par au moins trois méthodes distinctes comprenant la régression linéaire, la moyenne mobile et le lissage exponentiel, chacune produisant des intervalles de confiance à 95%, et pour détecter les anomalies dans les séries financières et les transactions individuelles par des méthodes combinées de z-score et de règle interquartile (IQR) ;

d) un **moteur de décomposition multiplicative** (FinancialAnalyzer) configuré pour décomposer le rendement des capitaux propres (ROE) en au moins trois facteurs (marge nette, rotation des actifs, multiplicateur de capitaux propres) avec comparaison à des moyennes sectorielles et génération de recommandations d'optimisation ;

e) une **base de données de benchmarking sectoriel** (BenchmarkEngine) comprenant au moins sept secteurs d'activité économique algériens, chacun doté de valeurs de référence pour au moins dix ratios financiers, de standards internationaux, et de données de concurrents permettant une analyse comparative multi-niveaux ;

f) un **moteur de simulation de scénarios** (ScenarioAnalyzer) configuré pour modéliser au moins trois scénarios (optimiste, de base, pessimiste) avec analyse de sensibilité à au moins sept paliers de variation et production de graphiques comparatifs ;

g) un **système de sécurité multi-niveaux** comprenant une dérivation de clé par PBKDF2 à au moins 100 000 itérations, un coffre-fort de credentials chiffré AES-256, une authentification à deux facteurs, un système de rôles à au moins quatre niveaux avec au moins seize permissions granulaires, et un verrouillage de compte après un nombre configurable de tentatives échouées ;

h) un **moteur de synchronisation cloud** (CloudSync) configuré pour produire des snapshots de données chiffrés par AES-GCM avec checksum d'intégrité SHA-256, gérer la rotation automatique des sauvegardes, et journaliser toutes les opérations dans la base de données ;

i) un **système d'exportation unifié** (ExportLayer) configuré pour produire des rapports dans au moins quatre formats (PDF, Excel, CSV, HTML) avec support de la langue arabe et gestion automatique des encodages ;

j) un **système d'internationalisation** (i18n) comprenant au moins 1900 clés de traduction dans au moins trois langues (arabe, français, anglais) avec prise en charge automatique de la direction du texte de droite à gauche pour la langue arabe ;

k) un **système de chargement différé** (lazy loading) des composants d'interface configuré pour instancier les écrans uniquement lors de leur première consultation, réduisant le temps de démarrage du système à moins de 100 millisecondes ;

l) une **base de données locale** (SQLite) configurée en mode Write-Ahead Logging avec un pool de connexions et des opérations d'insertion groupée (executemany) permettant un gain d'écriture d'au moins quatre fois par rapport à des opérations individuelles.

### Revendication 2 (Dépendante — Calcul fiscal automatisé)

Le système selon la revendication 1, caractérisé en ce que le moteur de calcul fiscal est additionally configuré pour :

a) calculer automatiquement les trois acomptes trimestriels d'IBS (aux dates du 20 mars, 20 juin et 20 novembre) et le solde d'IBS (au 30 avril) ;

b) appliquer automatiquement le minimum légal d'IBS de 10 000 dinars algériens lorsque l'impôt calculé est inférieur à ce montant ;

c) calculer le crédit de TVA reportable d'un mois à l'autre avec détermination du montant net à payer ou du crédit à reporter ;

d) appliquer automatiquement les pénalités de retard de 10% majorées de 3% par mois de retard ;

e) être mis à jour annuellement par simple modification du fichier de configuration JSON sans recompilation du système.

### Revendication 3 (Dépendante — Prédiction financière)

Le système selon la revendication 1, caractérisé en ce que le moteur d'intelligence artificielle est additionally configuré pour :

a) produire des prédictions sur une période configurable de 1 à 12 mois ;

b) fournir pour chaque prédiction un intervalle de confiance à 95% calculé selon la méthode statistique appropriée (intervalle de prédiction pour la régression linéaire, intervalle basé sur l'écart-type pour les autres méthodes) ;

c) calculer automatiquement un indicateur de tendance (hausse/baisse/stable) et un taux de croissance prévisionnel ;

d) classer chaque anomalie détectée selon un niveau de sévérité à trois niveaux (faible/moyen/élevé) basé sur la valeur absolue du z-score ;

e) générer des alertes proactives couvrant au moins les domaines suivants : liquidité insuffisante, endettement excessif, rentabilité en déclin, et anomalies de transactions.

### Revendication 4 (Dépendante — Benchmarking sectoriel)

Le système selon la revendication 1, caractérisé en ce que la base de données de benchmarking est additionally configurée pour :

a) dériver automatiquement des valeurs de « meilleures pratiques » (best practice) pour chaque ratio et chaque secteur en calculant 60% de la distance entre la moyenne sectoriale et la valeur maximale ;

b) calculer automatiquement des standards internationaux de comparaison dépassant les valeurs maximales sectorielles ;

c) produire des scores de forces et faiblesses basés sur la comparaison entre les ratios de l'entreprise et les valeurs sectorielles ;

d) gérer des données de concurrents permettant un classement multi-entreprises au sein du même secteur ;

e) stocker des valeurs d'évolution multi-périodes permettant l'analyse de tendances sectorielles.

### Revendication 5 (Dépendante — Sécurité et synchronisation)

Le système selon la revendication 1, caractérisé en ce que :

a) le coffre-fort de credentials stocke les mots de passe de service (SMTP, API) chiffrés par AES-256, de sorte que les secrets ne sont jamais en texte clair sur le disque ;

b) le système de synchronisation cloud produit un snapshot complet des données financières, calcule un checksum SHA-256 d'intégrité, chiffre optionnellement le contenu par AES-GCM avec une clé dérivée par PBKDF2 (120 000 itérations), et enregistre chaque opération dans un journal de synchronisation en base de données ;

c) le système de sauvegarde automatique gère un nombre configurable de sauvegardes avec rotation automatique (suppression des plus anciennes au dépassement du seuil) ;

d) le système de rôles implémente au moins quatre rôles (administrateur, gestionnaire, comptable, observateur) avec des permissions granulaires couvrant au moins seize actions distinctes.

### Revendication 6 (Dépendante — Architecture et performance)

Le système selon la revendication 1, caractérisé en ce que :

a) le système de chargement différé utilise un pattern de factory combiné à un proxy de module (PEP 562) pour retarder l'instanciation des 35 composants d'interface jusqu'à leur première utilisation ;

b) la base de données locale opère en mode Write-Ahead Logging (WAL) avec un pool de connexions préétablies et des opérations d'insertion groupée (executemany) pour les lots de données ;

c) le temps de démarrage à froid du système est inférieur à 100 millisecondes ;

d) l'occupation mémoire (RSS) du système en fonctionnement normal est inférieure à 100 mégaoctets ;

e) le système est distribué sous forme d'exécutable autonome (standalone) ne nécessitant pas l'installation d'un interpréteur ou d'un framework préalable.

### Revendication 7 (Indépendante — Procédé)

Un procédé automatisé d'analyse financière conforme à la fiscalité algérienne, comprenant les étapes de :

a) **réception** de données financières d'une PME comprenant au moins les champs suivants : actifs courants, stocks, passifs courants, chiffre d'affaires, coût des ventes, résultat net, capitaux propres, et actifs totaux ;

b) **calcul simultané** en une seule opération batch d'au moins vingt ratios financiers couvrant les familles de liquidité, rentabilité, efficacité et solvabilité, incluant un score prédictif d'insolvabilité ;

c) **calcul fiscal automatisé** appliquant les taux algériens en vigueur aux données financières saisies, comprenant au minimum le calcul de l'IBS selon le type d'activité, de la TVA selon le régime applicable, de l'IRG selon le barème progressif, et des cotisations sociales (CNAS, CNAC) ;

d) **génération d'alertes calendrier** pour au moins treize échéances fiscales obligatoires du calendrier fiscal algérien ;

e) **prédiction financière** sur une période configurable par au moins deux méthodes statistiques distinctes, chaque prédiction étant accompagnée d'un intervalle de confiance à 95% ;

f) **détection d'anomalies** dans les séries financières et les transactions par des méthodes statistiques combinées ;

g) **comparaison sectorielle** des ratios calculés avec des valeurs de référence pour au moins sept secteurs d'activité économiques algériens ;

h) **production d'un rapport consolidé** dans un format de sortie parmi PDF, Excel, CSV ou HTML, incluant les résultats des étapes b à g.

### Revendication 8 (Dépendante — Procédé fiscal)

Le procédé selon la revendication 7, caractérisé en ce que l'étape (c) comprend additionally :

a) la vérification et l'application automatique du minimum légal d'IBS (10 000 DA) ;

b) le calcul des trois acomptes trimestriels d'IBS et du solde annuel ;

c) le suivi du crédit de TVA reportable d'une période à l'autre ;

d) le calcul des pénalités de retard applicables en cas de dépassement des délais déclaratifs.

### Revendication 9 (Indépendante — Support informatique)

Un support de stockage de données non transitoire, lisible par ordinateur, stockant des instructions exécutables par un processeur pour mettre en œuvre le procédé selon l'une quelconque des revendications 7 à 8.

### Revendication 10 (Indépendante — Interface multilingue)

Le système selon la revendication 1, caractérisé en ce qu'il comprend additionally un moteur d'internationalisation comprenant :

a) au moins 1900 clés de traduction dans au moins trois langues (arabe, français, anglais) ;

b) un système de direction automatique du texte assurant l'affichage de droite à gauche (RTL) pour la langue arabe et de gauche à droite (LTR) pour les langues française et anglaise ;

c) un système de thèmes visuels comprenant au moins trois thèmes (clair, sombre, moderne) applicables à l'ensemble des composants d'interface ;

d) un système de raccourcis clavier couvrant au moins les 35 écrans du système.

---

## 6. RÉSUMÉ (ABSTRACT)

L'invention concerne un système et un procédé automatisé d'analyse financière destiné aux PME algériennes, intégrant un moteur de conformité fiscale paramétrable (IBS, TVA, IRG, CNAS, CNAC, VF) avec calendrier fiscal automatisé, un moteur d'analyse financière calculant 20 ratios + décomposition DuPont + Altman Z-Score, un moteur d'intelligence artificielle légère (prévision par 3 méthodes + détection d'anomalies par z-score/IQR + alertes), un benchmarking sectoriel sur 7 secteurs algériens avec comparaison concurrentielle, une simulation de scénarios multi-variables, un système de sécurité multi-niveaux (PBKDF2, AES-256, 2FA, 4 rôles), une synchronisation cloud chiffrée (AES-GCM), et une internationalisation trilingue (arabe RTL/français/anglais) avec 1925 clés. Le système fonctionne hors-ligne en tant qu'exécutable autonome avec base SQLite locale, atteignant un temps de démarrage de 44 ms et une occupation mémoire de 45 Mo.

---

## 7. DESSINS (FIGURES)

Les figures sont décrites en annexe et comprennent :

- **Figure 1** : Schéma de l'architecture en couches du système (présentation → contrôleurs → moteurs métier → persistance).
- **Figure 2** : Flux de traitement d'une analyse fiscale complète (saisie → calcul → fiscal → IA → rapport).
- **Figure 3** : Schéma de la base de données (15 tables relationnelles).
- **Figure 4** : Organigramme de l'algorithme de détection d'anomalies (z-score + IQR).
- **Figure 5** : Organigramme de l'algorithme de prédiction financière (3 méthodes + IC 95%).
- **Figure 6** : Capture d'écran du tableau de bord principal (6 KPI + 4 graphiques).
- **Figure 7** : Capture d'écran du moteur fiscal (calcul IBS + TVA + IRG).
- **Figure 8** : Capture d'écran du moteur d'intelligence artificielle (prédiction + anomalies).
- **Figure 9** : Capture d'écran du benchmarking sectoriel (radar chart + comparaison).
- **Figure 10** : Capture d'écran de l'analyse DuPont (shish waterfall chart + recommandations).

---

## 8. DONNÉES TECHNIQUES DU PROTOTYPE

| Paramètre | Valeur |
|-----------|--------|
| Nombre d'écrans | 35 |
| Nombre de modules métier | 37 |
| Nombre de ratios financiers | 20 + Z-Score + DuPont |
| Nombre de tests automatisés | 1 800 |
| Couverture de code module | 100% |
| Temps de démarrage | 44 ms |
| Occupation mémoire (RSS) | 45 Mo |
| Taille de l'exécutable | 143 Mo (standalone Nuitka) |
| Taille de l'installateur | 66,9 Mo (Inno Setup) |
| Langues supportées | 3 (arabe RTL, français, anglais) |
| Clés i18n | 1 925 × 3 langues |
| Secteurs de benchmarking | 7 |
| Tests d'intégration | 37 (workflows + DB + performance) |
| Tests d'interface | 111 (25 classes) |
| Tests d'export | 9 |
| Tests de performance | 4 |
| Date de première version | Juillet 2025 |
| Version du prototype | v3.1.7 |
| Framework d'interface | PyQt5 |
| Base de données | SQLite (WAL mode) |
| Langage de programmation | Python 3.11 |
| Système de build | Nuitka standalone |
| CI/CD | GitHub Actions |

---

## 9. NOVÉAUTÉ ET ACTIVITÉ INVENTIVE

### 9.1 Novéauté

L'invention présente les éléments de novéauté suivants par rapport à l'état de l'art :

1. **Premier système combinant** un moteur fiscal algérien paramétrable + analyse financière complète (20 ratios + DuPont + Z-Score) + IA légère dans un seul produit logiciel.

2. **Première architecture** de benchmarking sectoriel algérien avec 7 secteurs × 10 ratios + dérivation automatique des meilleures pratiques + standards internationaux + données de concurrents.

3. **Premier système d'exportation unifié** pour logiciel comptable algérien supportant PDF arabe (police Amiri) + Excel + CSV + HTML avec gestion automatique des encodages.

4. **Premier système d'internationalisation** trilingue avec 1925 clés × 3 langues et direction automatique RTL dans un contexte de logiciel comptable.

### 9.2 Activité inventive

L'activité inventive réside dans la combinaison synergique des éléments suivants :

- Le moteur fiscal n'est pas simplement un calculateur, il est **paramétrable par fichier JSON** permettant la mise à jour des taux sans recompilation.
- L'IA légère utilise **uniquement NumPy** (sans sklearn), ce qui permet la distribution sous forme d'exécutable autonome de taille réduite.
- Le benchmarking n'est pas un simple comparateur, il **dérive automatiquement** les meilleures pratiques et standards internationaux à partir des données sectorielles.
- Le système de sécurité **combine** PBKDF2 (100k itérations) + AES-256 + 2FA + rôles + verrouillage, ce qui est inhabituel pour un logiciel de bureau comptable.
- Le chargement paresseux **réduit le temps de démarrage de 778 ms à 44 ms** (factoriel 17,7×) sans altérer les fonctionnalités.

---

## 10. APPEL DE PROTECTION

### 10.1 Objet de la protection

La présente demande vise la protection de :

1. Le système informatique de bureau tel que décrit dans les revendications 1 à 6.
2. Le procédé automatisé d'analyse financière tel que décrit dans les revendications 7 à 8.
3. Le support de stockage tel que décrit dans la revendication 9.
4. L'interface multilingue telle que décrit dans la revendication 10.

### 10.2 Domaine d'application

Le système est applicable à toutes les PME algériennes (1,36 million d'entreprises en 2022) et peut être étendu à tout pays disposant d'un système fiscal paramétrable via la configuration JSON.

---

**Déposant :** MBKAREK Ahmed Khalil
**Établissement :** Université Ibn Khaldoun — Tiaret, Algérie
**Date :** [à compléter au moment du dépôt]
