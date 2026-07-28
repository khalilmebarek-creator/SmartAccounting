/* ===== Smart Accounting Platform - Main Script ===== */

document.addEventListener('DOMContentLoaded', () => {

    // ===== AOS (Animate On Scroll) =====
    AOS.init({
        duration: 700,
        easing: 'ease-out-cubic',
        once: true,
        offset: 80,
    });

    // ===== NAVBAR SCROLL EFFECT =====
    const navbar = document.getElementById('navbar');
    const onScroll = () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    // ===== HAMBURGER MENU =====
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');
    hamburger.addEventListener('click', () => {
        const isOpen = navLinks.classList.toggle('active');
        hamburger.classList.toggle('active');
        hamburger.setAttribute('aria-expanded', isOpen);
    });
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            hamburger.classList.remove('active');
            hamburger.setAttribute('aria-expanded', 'false');
        });
    });

    // ===== SMOOTH SCROLL =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', e => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // ===== NUMBER COUNTER =====
    const counters = document.querySelectorAll('.stat-number[data-count]');
    let countersAnimated = false;

    const animateCounters = () => {
        if (countersAnimated) return;
        const statsSection = document.querySelector('.stats-grid');
        if (!statsSection) return;

        const rect = statsSection.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            countersAnimated = true;
            counters.forEach(counter => {
                const target = parseInt(counter.dataset.count);
                const duration = 2000;
                const step = target / (duration / 16);
                let current = 0;

                const update = () => {
                    current += step;
                    if (current >= target) {
                        counter.textContent = target.toLocaleString();
                    } else {
                        counter.textContent = Math.floor(current).toLocaleString();
                        requestAnimationFrame(update);
                    }
                };
                requestAnimationFrame(update);
            });
        }
    };
    window.addEventListener('scroll', animateCounters, { passive: true });

    // ===== CHART BAR ANIMATION =====
    const bars = document.querySelectorAll('.chart-bar');
    let barsAnimated = false;

    const animateBars = () => {
        if (barsAnimated) return;
        const heroCard = document.querySelector('.hero-card-body');
        if (!heroCard) return;

        const rect = heroCard.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            barsAnimated = true;
            bars.forEach((bar, i) => {
                bar.style.height = '0%';
                setTimeout(() => {
                    bar.style.height = bar.style.getPropertyValue('--h');
                }, i * 200);
            });
        }
    };
    window.addEventListener('scroll', animateBars, { passive: true });
    // Trigger immediately if hero is visible
    animateBars();

    // ===== FULL LANGUAGE TRANSLATIONS =====
    const translations = {
        ar: {
            site_name: 'المنصة المحاسبية الذكية',
            nav_about: 'عن المشروع',
            nav_features: 'المميزات',
            nav_modules: 'الوحدات',
            nav_tech: 'الإحصائيات',
            nav_download: 'تحميل',
            nav_updates: 'التحديثات',
            hero_badge: 'v3.1.1 — مشروع تخرج محاسبي',
            hero_title: 'المنصة المحاسبية<br><span class="text-gradient">الذكية</span>',
            hero_desc: 'نظام محاسبي متكامل مبني بالذكاء الاصطناعي — يدعم 3 لغات ويشمل النظام الجبائي الجزائري بأكمله',
            hero_btn1: 'تحميل التطبيق',
            hero_btn2: 'اكتشف المزيد',
            hero_profit: 'نمو الأرباح',
            hero_accuracy: 'دقّة التقارير',
            intro: 'مشروع تخرج محاسبي متكامل يجمع بين <strong>الذكاء الاصطناعي</strong> و<strong>النظام الجبائي الجزائري</strong> — يتضمن 22 شاشة تفاعلية، 28 نسبة مالية، و322 اختبار وحدة ناجح.',
            about_tag: 'عن المشروع',
            about_title: 'ما هي المنصة المحاسبية الذكية؟',
            about_card1_title: 'تطبيق سطح مكتب',
            about_card1_desc: 'تطبيق يعمل على Windows 10/11 — لا يحتاج اتصال بالإنترنت للعمل الأساسي',
            about_card2_title: 'دعم 3 لغات',
            about_card2_desc: 'عربي (RTL) — إنجليزي — فرنسي — مع تبديل فوري بين اللغات',
            about_card3_title: 'بنية معيارية',
            about_card3_desc: '26 وحدة برمجية مستقلة — سهل التوسيع والصيانة والتطوير',
            dev_title: 'من طوّر المشروع',
            dev_name: 'خليل مبارك',
            dev_role: 'طالب محاسبة — مشروع تخرج ماجستير',
            features_tag: 'المميزات الرئيسية',
            features_title: 'لماذا المنصة المحاسبية الذكية؟',
            feat1_title: 'لوحة تحكم ذكية',
            feat1_desc: 'عرض فوري لأهم المؤشرات المالية — رسوم بيانية تفاعلية ومخططات ديناميكية',
            feat2_title: '28 نسبة مالية',
            feat2_desc: 'نسب السيولة، الربحية، الرواج، الدعم — مع تحليل لكل نسبة وتصنيف حسب الأداء',
            feat3_title: 'مساعد ذكاء اصطناعي',
            feat3_desc: 'محادثة ذكية تحلّل البيانات وتقديم توصيات — تعمل أوفلاين وأونلاين',
            feat4_title: 'النظام الجبائي الجزائري',
            feat4_desc: 'حساب TVA، IBS، IRG، CNAS، CNAC — مع تقويم ضريبي وتنبيهات المواعيد النهائية',
            feat5_title: 'التكامل البنكي',
            feat5_desc: 'استيراد كشوفات 6 بنوك جزائرية — كشف حساب CSV + مطابقة تلقائية مع السجلات',
            feat6_title: 'المقارنة الصناعية',
            feat6_desc: 'مقارنة أداء شركتك بـ 7 قطاعات صناعية — رسوم بيانية وتوصيات تحسين',
            feat7_title: 'أمان متعدد الطبقات',
            feat7_desc: 'تشفير AES-256، 4 أدوار مستخدمين، 16 صلاحية، مصادقة ثنائية، سجل نشاط',
            feat8_title: 'طباعة وتصدير احترافي',
            feat8_desc: 'تصدير PDF، Excel، HTML — مع قوالب تقارير جاهزة وقابلة للتخصيص',
            modules_tag: 'الوحدات',
            modules_title: '26 وحدة متكاملة',
            mod1: 'التحليل المالي',
            mod1_desc: 'تحليل DuPont + 28 نسبة + Z-Score',
            mod2: 'التدقيق الذكي',
            mod2_desc: 'كشف الشذوذ + اكتساب النشاط + التحقق',
            mod3: 'التقارير',
            mod3_desc: 'قوالب متعددة + تصدير PDF/Excel/HTML',
            mod4: 'النظام الجبائي',
            mod4_desc: 'TVA + IBS + IRG + CNAS + CNAC',
            mod5: 'التحليل المقارن',
            mod5_desc: 'مقارنة سنوات مالية + تحليل التغيرات',
            mod6: 'التدفقات النقدية',
            mod6_desc: 'قائمة التدفقات + التحليل + الرسوم البيانية',
            mod7: 'التخطيط المالي',
            mod7_desc: 'موازنتات + مراكز تكلفة + نقطة تعادل',
            mod8: 'التوقعات',
            mod8_desc: 'تنبؤ مالي + 3 سيناريوهات + اتجاهات',
            mod9: 'المقارنات الصناعية',
            mod9_desc: '7 قطاعات + معايير + رسوم بيانية',
            mod10: 'التكامل البنكي',
            mod10_desc: '6 بنوك جزائرية + استيراد كشف حساب + مطابقة',
            mod11: 'استيراد البيانات',
            mod11_desc: 'CSV + Excel + معالجة تلقائية للأعمدة',
            mod12: 'مساعد الذكاء الاصطناعي',
            mod12_desc: 'تحليل + توصيات + محادثة ذكية',
            tech_tag: 'إحصائيات المشروع',
            tech_title: 'أرقام المشروع',
            stat1: 'شاشة تفاعلية',
            stat2: 'نسبة مالية',
            stat3: 'اختبار ناجح',
            stat4: 'وحدة برمجية',
            dl_tag: 'تحميل مجاني',
            dl_title: 'حمّل التطبيق الآن',
            dl_desc: 'متوافق مع Windows 10/11 — لا يحتاج تثبيت Python أو أي برامج إضافية',
            dl_inst_title: 'التثبيت السريع',
            dl_inst_desc: 'ملف تثبيت يضيف اختصار سطح المكتب وقائمة Start تلقائياً',
            dl_inst_btn: 'تحميل المُثبّت',
            dl_port_title: 'النسخة المحمولة',
            dl_port_desc: 'ملف مضغوط يحتوي على التطبيق — افتح وأشغّل بدون تثبيت',
            dl_port_btn: 'تحميل المحمول',
            dl_recommended: 'مُوصى به',
            upd_tag: 'آخر التحديثات',
            upd_title: 'ما الجديد؟',
            upd_date: '27 يوليو 2026',
            upd_date2: '28 يوليو 2026',
            upd_date3: '28 يوليو 2026',
            upd_new1: 'إصلاح نظام إشعار التحديثات — يظهر الآن عند توفر إصدار جديد',
            upd_new2: 'إصلاح استعادة كلمة المرور بنظام الرمز الآمن',
            upd_new3: 'الإيميل يملأ تلقائياً بعد التسجيل',
            upd_new4: 'إصلاح تحميل البيانات المالية من أول مرة',
            upd_new5: 'تحسين التنقل بالـ Tab بين الحقول',
            upd_new6: 'إصلاح التقويم الجبائي — اختيار السنة يحدّث العرض فوراً',
            upd_new7: 'إصلاح المعايير المرجعية — تغيير القطاع يحدّث النتائج تلقائياً',
            upd_new8: 'تحميل التحديث مباشرة — نافذة تقدم + تشغيل تلقائي',
            upd1: 'نظام فحص التحديثات التلقائي',
            upd2: '8 ميزات جديدة: طباعة، Excel، تقويم ضريبي، CSV، بنك، مقارنات',
            upd3: 'أيقونة التطبيق + ملف تثبيت احترافي',
            upd4: '22 شاشة — 322 اختبار — 7 قطاعات صناعية',
            footer_rights: 'جميع الحقوق محفوظة',
            footer_project: 'مشروع تخرج ماجستير في المحاسبة',
            toggle: 'EN',
        },
        en: {
            site_name: 'Smart Accounting Platform',
            nav_about: 'About',
            nav_features: 'Features',
            nav_modules: 'Modules',
            nav_tech: 'Stats',
            nav_download: 'Download',
            nav_updates: 'Updates',
            hero_badge: 'v3.1.1 — Master\'s Graduation Project',
            hero_title: 'Smart<br><span class="text-gradient">Accounting Platform</span>',
            hero_desc: 'A complete accounting system powered by AI — supports 3 languages and includes the full Algerian tax system',
            hero_btn1: 'Download App',
            hero_btn2: 'Learn More',
            hero_profit: 'Profit Growth',
            hero_accuracy: 'Report Accuracy',
            intro: 'A complete accounting graduation project combining <strong>Artificial Intelligence</strong> and the <strong>Algerian Tax System</strong> — featuring 22 interactive screens, 28 financial ratios, and 322 passing unit tests.',
            about_tag: 'About',
            about_title: 'What is Smart Accounting Platform?',
            about_card1_title: 'Desktop Application',
            about_card1_desc: 'Runs on Windows 10/11 — no internet connection needed for core features',
            about_card2_title: '3 Languages',
            about_card2_desc: 'Arabic (RTL) — English — French — with instant language switching',
            about_card3_title: 'Modular Architecture',
            about_card3_desc: '26 independent software modules — easy to extend, maintain, and develop',
            dev_title: 'Developer',
            dev_name: 'Khelifi Mebarek',
            dev_role: 'Accounting Student — Master\'s Thesis Project',
            features_tag: 'Key Features',
            features_title: 'Why Smart Accounting Platform?',
            feat1_title: 'Smart Dashboard',
            feat1_desc: 'Instant display of key financial metrics — interactive charts and dynamic diagrams',
            feat2_title: '28 Financial Ratios',
            feat2_desc: 'Liquidity, profitability, leverage, efficiency — with analysis and classification per ratio',
            feat3_title: 'AI Assistant',
            feat3_desc: 'Smart chat that analyzes data and provides recommendations — works offline and online',
            feat4_title: 'Algerian Tax System',
            feat4_desc: 'VAT, IBS, IRG, CNAS, CNAC calculation — with tax calendar and deadline alerts',
            feat5_title: 'Bank Integration',
            feat5_desc: 'Import statements from 6 Algerian banks — CSV + automatic reconciliation with records',
            feat6_title: 'Industry Benchmarking',
            feat6_desc: 'Compare your company performance across 7 industrial sectors — charts and improvement tips',
            feat7_title: 'Multi-Layer Security',
            feat7_desc: 'AES-256 encryption, 4 user roles, 16 permissions, 2FA, activity log',
            feat8_title: 'Professional Print & Export',
            feat8_desc: 'PDF, Excel, HTML export — with ready-made report templates and customization',
            modules_tag: 'Modules',
            modules_title: '26 Integrated Modules',
            mod1: 'Financial Analysis',
            mod1_desc: 'DuPont analysis + 28 ratios + Z-Score',
            mod2: 'Smart Audit',
            mod2_desc: 'Anomaly detection + activity monitoring + verification',
            mod3: 'Reports',
            mod3_desc: 'Multiple templates + PDF/Excel/HTML export',
            mod4: 'Tax System',
            mod4_desc: 'VAT + IBS + IRG + CNAS + CNAC',
            mod5: 'Comparative Analysis',
            mod5_desc: 'Multi-year comparison + trend analysis',
            mod6: 'Cash Flow',
            mod6_desc: 'Cash flow statement + analysis + charts',
            mod7: 'Financial Planning',
            mod7_desc: 'Budgets + cost centers + break-even',
            mod8: 'Forecasting',
            mod8_desc: 'Financial predictions + 3 scenarios + trends',
            mod9: 'Industry Benchmarks',
            mod9_desc: '7 sectors + standards + charts',
            mod10: 'Bank Integration',
            mod10_desc: '6 Algerian banks + statement import + reconciliation',
            mod11: 'Data Import',
            mod11_desc: 'CSV + Excel + automatic column processing',
            mod12: 'AI Assistant',
            mod12_desc: 'Analysis + recommendations + smart chat',
            tech_tag: 'Project Stats',
            tech_title: 'Project Numbers',
            stat1: 'Interactive Screens',
            stat2: 'Financial Ratios',
            stat3: 'Passing Tests',
            stat4: 'Software Modules',
            dl_tag: 'Free Download',
            dl_title: 'Download Now',
            dl_desc: 'Compatible with Windows 10/11 — No Python or additional software needed',
            dl_inst_title: 'Quick Install',
            dl_inst_desc: 'Installer adds desktop shortcut and Start menu automatically',
            dl_inst_btn: 'Download Installer',
            dl_port_title: 'Portable Version',
            dl_port_desc: 'Compressed archive — extract and run without installation',
            dl_port_btn: 'Download Portable',
            dl_recommended: 'Recommended',
            upd_tag: 'Latest Updates',
            upd_title: 'What\'s New?',
            upd_date: 'July 27, 2026',
            upd_date2: 'July 28, 2026',
            upd_date3: 'July 28, 2026',
            upd_new1: 'Fixed update notification — now shows when new version available',
            upd_new2: 'Fixed password recovery with secure code system',
            upd_new3: 'Email auto-filled after registration',
            upd_new4: 'Fixed financial data loading on first open',
            upd_new5: 'Improved Tab navigation between fields',
            upd_new6: 'Fixed Fiscal Calendar — year selection updates view instantly',
            upd_new7: 'Fixed Benchmarks — sector change auto-updates results',
            upd_new8: 'Download update directly — progress window + auto launch',
            upd1: 'Automatic update checker',
            upd2: '8 new features: Printing, Excel, Tax Calendar, CSV, Bank, Benchmarks',
            upd3: 'App icon + professional installer',
            upd4: '22 screens — 351 tests — 7 industrial sectors',
            footer_rights: 'All Rights Reserved',
            footer_project: 'Master\'s Graduation Project in Accounting',
            toggle: 'عر',
        },
        fr: {
            site_name: 'Plateforme Comptable Intelligente',
            nav_about: 'À propos',
            nav_features: 'Fonctionnalités',
            nav_modules: 'Modules',
            nav_tech: 'Statistiques',
            nav_download: 'Télécharger',
            nav_updates: 'Mises à jour',
            hero_badge: 'v3.1.1 — Projet de fin d\'étude Master',
            hero_title: 'Plateforme Comptable<br><span class="text-gradient">Intelligente</span>',
            hero_desc: 'Système comptable complet propulsé par l\'IA — 3 langues et système fiscal algérien complet',
            hero_btn1: 'Télécharger',
            hero_btn2: 'En savoir plus',
            hero_profit: 'Croissance des profits',
            hero_accuracy: 'Précision des rapports',
            intro: 'Projet de fin d\'étude comptable combinant <strong>l\'Intelligence Artificielle</strong> et le <strong>Système Fiscal Algérien</strong> — 22 écrans interactifs, 28 ratios financiers et 322 tests unitaires réussis.',
            about_tag: 'À propos',
            about_title: 'Qu\'est-ce que la Plateforme Comptable Intelligente?',
            about_card1_title: 'Application de bureau',
            about_card1_desc: 'Fonctionne sur Windows 10/11 — pas besoin d\'internet pour les fonctions de base',
            about_card2_title: '3 Langues',
            about_card2_desc: 'Arabe (RTL) — Anglais — Français — changement instantané',
            about_card3_title: 'Architecture Modulaire',
            about_card3_desc: '26 modules logiciels indépendants — facile à étendre et maintenir',
            dev_title: 'Développeur',
            dev_name: 'Khelifi Mebarek',
            dev_role: 'Étudiant en comptabilité — Projet de Master',
            features_tag: 'Fonctionnalités',
            features_title: 'Pourquoi la Plateforme Comptable Intelligente?',
            feat1_title: 'Tableau de bord intelligent',
            feat1_desc: 'Affichage instantané des indicateurs financiers — graphiques interactifs',
            feat2_title: '28 Ratios Financiers',
            feat2_desc: 'Liquidité, rentabilité, levier, efficacité — avec analyse et classification',
            feat3_title: 'Assistant IA',
            feat3_desc: 'Chat intelligent qui analyse les données et fournit des recommandations',
            feat4_title: 'Système Fiscal Algérien',
            feat4_desc: 'TVA, IBS, IRG, CNAS, CNAC — calendrier fiscal et alertes',
            feat5_title: 'Intégration Bancaire',
            feat5_desc: 'Import des relevés de 6 banques algériennes — CSV + rapprochement automatique',
            feat6_title: 'Benchmark Industriel',
            feat6_desc: 'Comparez vos performances sur 7 secteurs industriels — graphiques et conseils',
            feat7_title: 'Sécurité Multi-couches',
            feat7_desc: 'Chiffrement AES-256, 4 rôles, 16 permissions, 2FA, journal d\'activité',
            feat8_title: 'Impression et Export Pro',
            feat8_desc: 'Export PDF, Excel, HTML — modèles de rapports prêts à l\'emploi',
            modules_tag: 'Modules',
            modules_title: '26 Modules Intégrés',
            mod1: 'Analyse Financière',
            mod1_desc: 'Analyse DuPont + 28 ratios + Z-Score',
            mod2: 'Audit Intelligent',
            mod2_desc: 'Détection d\'anomalies + surveillance + vérification',
            mod3: 'Rapports',
            mod3_desc: 'Modèles multiples + export PDF/Excel/HTML',
            mod4: 'Système Fiscal',
            mod4_desc: 'TVA + IBS + IRG + CNAS + CNAC',
            mod5: 'Analyse Comparative',
            mod5_desc: 'Comparaison multi-années + analyse des tendances',
            mod6: 'Trésorerie',
            mod6_desc: 'État de trésorerie + analyse + graphiques',
            mod7: 'Planification Financière',
            mod7_desc: 'Budgets + centres de coûts + point mort',
            mod8: 'Prévisions',
            mod8_desc: 'Prévisions financières + 3 scénarios + tendances',
            mod9: 'Benchmarks Industriels',
            mod9_desc: '7 secteurs + normes + graphiques',
            mod10: 'Intégration Bancaire',
            mod10_desc: '6 banques algériennes + import de relevés + rapprochement',
            mod11: 'Import de Données',
            mod11_desc: 'CSV + Excel + traitement automatique des colonnes',
            mod12: 'Assistant IA',
            mod12_desc: 'Analyse + recommandations + chat intelligent',
            tech_tag: 'Statistiques',
            tech_title: 'Chiffres du Projet',
            stat1: 'Écrans Interactifs',
            stat2: 'Ratios Financiers',
            stat3: 'Tests Réussis',
            stat4: 'Modules Logiciels',
            dl_tag: 'Téléchargement Gratuit',
            dl_title: 'Téléchargez maintenant',
            dl_desc: 'Compatible Windows 10/11 — Pas besoin de Python ou logiciel supplémentaire',
            dl_inst_title: 'Installation Rapide',
            dl_inst_desc: 'L\'installateur ajoute un raccourci bureau et le menu Démarrer automatiquement',
            dl_inst_btn: 'Télécharger l\'Installateur',
            dl_port_title: 'Version Portable',
            dl_port_desc: 'Archive compressée — extrayez et exécutez sans installation',
            dl_port_btn: 'Télécharger Portable',
            dl_recommended: 'Recommandé',
            upd_tag: 'Dernières Mises à Jour',
            upd_title: 'Nouveautés?',
            upd_date: '27 Juillet 2026',
            upd_date2: '28 Juillet 2026',
            upd_date3: '28 Juillet 2026',
            upd_new1: 'Correction de la notification de mise à jour — s\'affiche maintenant',
            upd_new2: 'Récupération du mot de passe avec système de code sécurisé',
            upd_new3: 'Email pré-rempli après inscription',
            upd_new4: 'Correction du chargement des données financières',
            upd_new5: 'Amélioration de la navigation Tab entre les champs',
            upd_new6: 'Correction du Calendrier Fiscal — la sélection de l\'année met à jour l\'affichage',
            upd_new7: 'Correction des Benchmarks — le changement de secteur met à jour les résultats',
            upd_new8: 'Téléchargement direct — fenêtre de progression + lancement automatique',
            upd1: 'Système de vérification automatique des mises à jour',
            upd2: '8 nouvelles fonctionnalités: Impression, Excel, Calendrier fiscal, CSV, Banque, Benchmarks',
            upd3: 'Icône de l\'application + installateur professionnel',
            upd4: '22 écrans — 351 tests — 7 secteurs industriels',
            footer_rights: 'Tous Droits Réservés',
            footer_project: 'Projet de Fin d\'Études Master en Comptabilité',
            toggle: 'ع',
        },
    };

    // ===== LANGUAGE TOGGLE =====
    const langToggle = document.getElementById('langToggle');
    const langOrder = ['ar', 'en', 'fr'];
    let currentLangIndex = 0;

    const applyLang = (lang) => {
        const t = translations[lang];
        if (!t) return;

        // Update button
        langToggle.textContent = t.toggle;

        // Update HTML attributes
        document.documentElement.lang = lang;
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';

        // Update all data-i18n elements
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (t[key]) {
                if (key === 'hero_title' || key === 'intro') {
                    el.innerHTML = t[key];
                } else {
                    el.textContent = t[key];
                }
            }
        });
    };

    langToggle.addEventListener('click', () => {
        currentLangIndex = (currentLangIndex + 1) % langOrder.length;
        applyLang(langOrder[currentLangIndex]);
    });

});
