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
            hero_badge: 'v3.1.4 — مشروع تخرج محاسبي',
            hero_title: 'المنصة المحاسبية<br><span class="text-gradient">الذكية</span>',
            hero_desc: 'نظام محاسبي متكامل مبني بالذكاء الاصطناعي — يدعم 3 لغات ويشمل النظام الجبائي الجزائري بأكمله',
            hero_btn1: 'تحميل التطبيق',
            hero_btn2: 'اكتشف المزيد',
            hero_profit: 'نمو الأرباح',
            hero_accuracy: 'دقّة التقارير',
            intro: 'مشروع تخرج محاسبي متكامل يجمع بين <strong>الذكاء الاصطناعي</strong> و<strong>النظام الجبائي الجزائري</strong> — يتضمن 26 شاشة تفاعلية، 20 نسبة مالية + Z-Score، و560 اختبار وحدة ناجح.',
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
            feat2_title: '20 نسبة مالية + Z-Score',
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
            modules_title: '27 وحدة متكاملة',
            mod1: 'التحليل المالي',
            mod1_desc: 'تحليل DuPont + 20 نسبة + Z-Score',
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
            mod13: 'الرؤى الذكية',
            mod13_desc: 'تنبؤ + كشف شذوذ + أنماط + توصيات + تنبيهات',
            mod14: 'ربحية مراكز التكلفة',
            mod14_desc: 'توزيع التكاليف + ربحية المراكز + مقارنات + اتجاه',
            mod15: 'تعدد العملات',
            mod15_desc: '7 عملات + أسعار صرف + محول + تقرير متعدد العملات',
            mod16: 'المزامنة السحابية',
            mod16_desc: 'وجهات مزامنة + نسخ احتياطي تلقائي + استرجاع مشفّر',
            mod17: 'الشركات التجريبية',
            mod17_desc: '4 شركات نموذجية + معاملات شهرية + تقارير مُعدّة + قوالب CSV',
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
            dl_note_sac: '<strong>ملاحظة لمستخدمي Windows 11:</strong> إذا ظهرت رسالة "An Application Control policy has blocked this file" عند فتح التطبيق، فالمشكلة من ميزة <em>Smart App Control</em> — يُحل بإيقافها من: <code>Windows Security ← App &amp; browser control ← Smart App Control settings ← Off</code> (التطبيق يدعم Windows 10 و 11، والمشكلة خاصة ببعض أجهزة Windows 11 فقط).',
            upd_tag: 'آخر التحديثات',
            upd_title: 'ما الجديد؟',
            upd_date: '27 يوليو 2026',
            upd_date2: '28 يوليو 2026',
            upd_date3: '28 يوليو 2026',
            upd_date4: '30 يوليو 2026',
            upd_date5: '31 يوليو 2026',
            upd_date6: '1 أغسطس 2026',
            upd_date7: '1 أغسطس 2026',
            upd_new19: 'تحسين أداء شامل: إقلاع أسرع 15× (778→49ms) + ذاكرة أقل (128→45MB) + تجمّع اتصالات قاعدة البيانات (حفظ أسرع 88×) + لوحة تحكم بدون إعادة رسم زائدة',
            upd_new20: 'تعدد العملات: 7 عملات افتراضية + أسعار صرف + محول + تقرير متعدد العملات + تصدير CSV',
            upd_new21: 'المزامنة السحابية والنسخ الاحتياطي: وجهات مزامنة (Dropbox/OneDrive/Drive) + نسخ احتياطي تلقائي + تشفير اختياري + استرجاع + سجل عمليات',
            upd_new22: 'الشركات التجريبية: 4 شركات (تجارية/خدمات/إنتاج/استيراد-تصدير) + معاملات شهرية نموذجية (12 شهراً) + تقارير مُعدّة مسبقاً + قوالب استيراد/تصدير CSV',
            upd_new23: 'تجربة مستخدم محسّنة: اختصارات كاملة لكل الشاشات 28 (Ctrl+1..0، Ctrl+Shift+1..0، F2..F8، Ctrl+T للثيم) + قائمة "عرض" ديناميكية + رسائل خطأ موحّدة مع إجراء مقترح + انتقالات تلاشي + مؤشر تحميل + تحسينات تباين وإتاحة في الثيمات الثلاثة',
            upd_new24: 'التغطية الشاملة للوحدات: 1229 اختباراً ناجحاً + تغطية 99% للوحدات البرمجية (كانت 73%) — اختبارات edge/error لكل وحدة + إصلاح خطأ generate_report في المقارنات + قائمة أخطاء موثّقة',
            upd_new25: 'اختبار التكامل والأداء: 1266 اختباراً ناجحاً + 3 أخطاء منتج أُصلحت (تخزين رأس المال العامل، الحذف الترابطي للـ notes، نسخ احتياطي يفقد بيانات WAL) — إدراج 1200 معاملة خلال 4ms + 2000 حساب نسب خلال 0.11s + 8 مستخدمين متزامنين بلا أخطاء',
            upd_date8: '1 أغسطس 2026',
            upd_date9: '1 أغسطس 2026',
            upd_new26: 'شاشة اختبار المستخدمين (29): 4 مجموعات مستخدمين × 5 سيناريوهات + ملاحظات/مقترحات/أعطال مع تصنيفات وأولويات وحالات + درجة رضا وتحليل تفصيلي + تقارير (تعقيبات/قائمة أعطال/طلبات تحسين/ملخص) + بيانات تجريبية + تصدير/استيراد JSON + تصدير CSV/Excel/PDF + حفظ/تحميل قاعدة بيانات — 1332 اختباراً ناجحاً + تغطية user_testing 100%',
            upd_date10: '1 أغسطس 2026',
            upd_new27: 'التصحيحات النهائية + مراجعة الأمان: إصلاح 13 خللاً (طباعة Landscape + كشف رأس ملف البنك + حماية القوالب الافتراضية + تصدير عربي واضح عند غياب خط Amiri + تنزيل التحديثات بملف جزئي آمن + استعادة نسخ احتياطية تشمل vault + رفض جداول محجوزة في SQLite) + مراجعة أمان شاملة (PBKDF2 100k + تخزين مشفّر لأسرار SMTP/API + HTTPS فقط) — 1350 اختباراً ناجحاً + تغطية وحدات 100%',
            upd_new13: 'إصلاح مشكلة عدم فتح التطبيق بعد التحديث',
            upd_new14: 'إصلاح ظهور نافذة cmd عند التحديث — التحديث يعمل الآن بشكل مخفي تماماً',
            upd_new15: 'تحديث المثبّت إلى نسخة محسّنة وأصغر حجماً',
            upd_new1: 'إصلاح نظام إشعار التحديثات — يظهر الآن عند توفر إصدار جديد',
            upd_new2: 'إصلاح استعادة كلمة المرور بنظام الرمز الآمن',
            upd_new3: 'الإيميل يملأ تلقائياً بعد التسجيل',
            upd_new4: 'إصلاح تحميل البيانات المالية من أول مرة',
            upd_new5: 'تحسين التنقل بالـ Tab بين الحقول',
            upd_new6: 'إصلاح التقويم الجبائي — اختيار السنة يحدّث العرض فوراً',
            upd_new7: 'إصلاح المعايير المرجعية — تغيير القطاع يحدّث النتائج تلقائياً',
            upd_new8: 'تحميل التحديث مباشرة — نافذة تقدم + تشغيل تلقائي',
            upd_new9: 'إضافة 8 نسب مالية جديدة — Cash Ratio، هامش الربح التشغيلي، فترة المخزون، دوران الموردين، فترة سداد الموردين، الدورة التشغيلية، دورة التحويل النقدي، نسبة حقوق الملكية',
            upd_new10: 'إضافة 3 حقول إدخال جديدة — النقدية، المصاريف التشغيلية، متوسط الموردين',
            upd_new11: 'إصلاح مشكلة عرض الشرطة السفلية (_) في كلمة السر عند الوضع العربي',
            upd_new12: 'شاشة النسب المالية تعرض الآن 20 نسبة في 4 فئات',
            upd_new16: 'ميزة المعايير المرجعية المتقدمة: أفضل الممارسات + معيار دولي + نقاط قوة/ضعف + تحليل اتجاه + مقارنة منافسين',
            upd_new17: 'لوحة التحكم المتقدمة: 6 بطاقات KPI بحالة لونية + 4 رسوم + تنبيهات (شذوذ/أداء/معايير/إجراءات) + تخصيص كامل + تصدير PDF/Excel',
            upd_new18: 'تحليل ربحية مراكز التكلفة: مراكز (قسم/مشروع/فرع/خط إنتاج) + توزيع مباشر/غير مباشر + ربحية + مقارنات + اتجاه + تقارير + تصدير PDF/Excel',
            upd1: 'نظام فحص التحديثات التلقائي',
            upd2: '8 ميزات جديدة: طباعة، Excel، تقويم ضريبي، CSV، بنك، مقارنات',
            upd3: 'أيقونة التطبيق + ملف تثبيت احترافي',
            upd4: '26 شاشة — 560 اختبار — 7 قطاعات صناعية',
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
            hero_badge: 'v3.1.4 — Master\'s Graduation Project',
            hero_title: 'Smart<br><span class="text-gradient">Accounting Platform</span>',
            hero_desc: 'A complete accounting system powered by AI — supports 3 languages and includes the full Algerian tax system',
            hero_btn1: 'Download App',
            hero_btn2: 'Learn More',
            hero_profit: 'Profit Growth',
            hero_accuracy: 'Report Accuracy',
            intro: 'A complete accounting graduation project combining <strong>Artificial Intelligence</strong> and the <strong>Algerian Tax System</strong> — featuring 26 interactive screens, 20 financial ratios + Z-Score, and 560 passing unit tests.',
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
            feat2_title: '20 Ratios + Z-Score',
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
            modules_title: '27 Integrated Modules',
            mod1: 'Financial Analysis',
            mod1_desc: 'DuPont analysis + 20 ratios + Z-Score',
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
            mod13: 'AI Insights',
            mod13_desc: 'Forecasting + anomalies + patterns + recommendations + alerts',
            mod14: 'Cost Center Profitability',
            mod14_desc: 'Cost allocation + center profitability + comparisons + trends',
            mod15: 'Multi-Currency',
            mod15_desc: '7 currencies + exchange rates + converter + multi-currency report',
            mod16: 'Cloud Sync',
            mod16_desc: 'Sync destinations + automatic backups + encrypted restore',
            mod17: 'Demo Companies',
            mod17_desc: '4 sample companies + monthly transactions + pre-made reports + CSV templates',
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
            dl_note_sac: '<strong>Note for Windows 11 users:</strong> If you see "An Application Control policy has blocked this file" when opening the app, it\'s caused by the <em>Smart App Control</em> feature — fix it by turning it off: <code>Windows Security ← App &amp; browser control ← Smart App Control settings ← Off</code> (the app supports Windows 10 &amp; 11; this only affects some Windows 11 devices).',
            upd_tag: 'Latest Updates',
            upd_title: 'What\'s New?',
            upd_date: 'July 27, 2026',
            upd_date2: 'July 28, 2026',
            upd_date3: 'July 28, 2026',
            upd_date4: 'July 30, 2026',
            upd_date5: 'July 31, 2026',
            upd_date6: 'August 1, 2026',
            upd_date7: 'August 1, 2026',
            upd_new19: 'Comprehensive performance: 15× faster startup (778→49ms) + less memory (128→45MB) + database connection pooling (88× faster saves) + dashboard without redundant redraws',
            upd_new20: 'Multi-currency: 7 default currencies + exchange rates + converter + multi-currency report + CSV export',
            upd_new21: 'Cloud sync & backup: sync destinations (Dropbox/OneDrive/Drive) + automatic backups + optional encryption + restore + operations log',
            upd_new22: 'Demo companies: 4 sample companies (Retail/Services/Manufacturing/Import-Export) + monthly transactions (12 months) + pre-made reports + CSV import/export templates',
            upd_new23: 'Improved UX: complete keyboard shortcuts for all 28 screens (Ctrl+1..0, Ctrl+Shift+1..0, F2..F8, Ctrl+T for theme) + dynamic "View" menu + unified error messages with suggested actions + fade transitions + loading indicator + contrast/accessibility improvements in all three themes',
            upd_new24: 'Comprehensive module coverage: 1229 passing tests + 99% module coverage (up from 73%) — edge/error tests for every module + fixed generate_report bug in comparisons + documented error list',
            upd_new25: 'Integration & performance testing: 1266 passing tests + 3 product bugs fixed (working capital not stored, broken notes cascade delete, backup losing WAL data) — 1200-row bulk insert in 4ms + 2000 ratio calculations in 0.11s + 8 concurrent users with zero errors',
            upd_date8: 'August 1, 2026',
            upd_date9: 'August 1, 2026',
            upd_new26: 'User testing screen (29): 4 user groups × 5 scenarios + feedback/suggestions/bugs with categories, priorities and statuses + satisfaction score with detailed breakdown + reports (feedback/issue list/enhancement requests/summary) + demo data + JSON export/import + CSV/Excel/PDF export + database save/load — 1332 passing tests + 100% user_testing coverage',
            upd_date10: 'August 1, 2026',
            upd_new27: 'Final fixes + security review: fixed 13 bugs (Landscape printing + bank file header detection + default template protection + clear Arabic PDF export when the Amiri font is missing + safe partial-file update download + backups restoring vault.enc + SQLite reserved table name rejection) + comprehensive security review (PBKDF2 100k + encrypted SMTP/API secrets + HTTPS only) — 1350 passing tests + 100% module coverage',
            upd_new13: 'Fixed app not opening after update',
            upd_new14: 'Fixed cmd window appearing during update — update now runs fully hidden',
            upd_new15: 'Improved installer — smaller and faster',
            upd_new1: 'Fixed update notification — now shows when new version available',
            upd_new2: 'Fixed password recovery with secure code system',
            upd_new3: 'Email auto-filled after registration',
            upd_new4: 'Fixed financial data loading on first open',
            upd_new5: 'Improved Tab navigation between fields',
            upd_new6: 'Fixed Fiscal Calendar — year selection updates view instantly',
            upd_new7: 'Fixed Benchmarks — sector change auto-updates results',
            upd_new8: 'Download update directly — progress window + auto launch',
            upd_new9: 'Added 8 new financial ratios — Cash Ratio, Operating Profit Margin, DIO, Payables Turnover, DPO, Operating Cycle, CCC, Equity Ratio',
            upd_new10: 'Added 3 new input fields — Cash, Operating Expenses, Average Payables',
            upd_new11: 'Fixed underscore (_) not displaying in password fields in Arabic RTL mode',
            upd_new12: 'Ratios screen now shows 20 ratios in 4 categories',
            upd_new16: 'Advanced reference standards: Best Practice + International + Strengths/Weaknesses + Trend Analysis + Competitor Comparison',
            upd_new17: 'Advanced Dashboard: 6 color-coded KPI cards + 4 charts + smart alerts + full customization + PDF/Excel export',
            upd_new18: 'Cost Center Profitability: centers (department/project/branch/production line) + direct/indirect allocation + profitability + comparisons + trends + reports + PDF/Excel export',
            upd1: 'Automatic update checker',
            upd2: '8 new features: Printing, Excel, Tax Calendar, CSV, Bank, Benchmarks',
            upd3: 'App icon + professional installer',
            upd4: '26 screens — 560 tests — 7 industrial sectors',
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
            hero_badge: 'v3.1.4 — Projet de fin d\'étude Master',
            hero_title: 'Plateforme Comptable<br><span class="text-gradient">Intelligente</span>',
            hero_desc: 'Système comptable complet propulsé par l\'IA — 3 langues et système fiscal algérien complet',
            hero_btn1: 'Télécharger',
            hero_btn2: 'En savoir plus',
            hero_profit: 'Croissance des profits',
            hero_accuracy: 'Précision des rapports',
            intro: 'Projet de fin d\'étude comptable combinant <strong>l\'Intelligence Artificielle</strong> et le <strong>Système Fiscal Algérien</strong> — 26 écrans interactifs, 20 ratios financiers + Z-Score et 560 tests unitaires réussis.',
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
            feat2_title: '20 Ratios + Z-Score',
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
            modules_title: '27 Modules Intégrés',
            mod1: 'Analyse Financière',
            mod1_desc: 'Analyse DuPont + 20 ratios + Z-Score',
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
            mod13: 'Insights IA',
            mod13_desc: 'Prévision + anomalies + tendances + recommandations + alertes',
            mod14: 'Rentabilité Centres de Coûts',
            mod14_desc: 'Répartition des coûts + rentabilité des centres + comparaisons + tendances',
            mod15: 'Devises Multiples',
            mod15_desc: '7 devises + taux de change + convertisseur + rapport multidevises',
            mod16: 'Sync Cloud',
            mod16_desc: 'Destinations de sync + sauvegardes automatiques + restauration chiffrée',
            mod17: 'Entreprises Démo',
            mod17_desc: '4 entreprises d\'exemple + transactions mensuelles + rapports préétablis + modèles CSV',
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
            dl_note_sac: '<strong>Note pour les utilisateurs de Windows 11 :</strong> Si le message "An Application Control policy has blocked this file" s\'affiche à l\'ouverture de l\'application, c\'est dû à la fonction <em>Smart App Control</em> — désactivez-la : <code>Windows Security ← App &amp; browser control ← Smart App Control settings ← Off</code> (l\'application prend en charge Windows 10 et 11 ; ce problème ne touche que certains appareils Windows 11).',
            upd_tag: 'Dernières Mises à Jour',
            upd_title: 'Nouveautés?',
            upd_date: '27 Juillet 2026',
            upd_date2: '28 Juillet 2026',
            upd_date3: '28 Juillet 2026',
            upd_date4: '30 Juillet 2026',
            upd_date5: '31 Juillet 2026',
            upd_date6: '1 Août 2026',
            upd_date7: '1 Août 2026',
            upd_new19: 'Performance complète : démarrage 15× plus rapide (778→49ms) + moins de mémoire (128→45MB) + pool de connexions base de données (sauvegardes 88× plus rapides) + tableau de bord sans redessin excessif',
            upd_new20: 'Devises multiples : 7 devises par défaut + taux de change + convertisseur + rapport multidevises + export CSV',
            upd_new21: 'Sync cloud et sauvegarde : destinations (Dropbox/OneDrive/Drive) + sauvegardes automatiques + chiffrement optionnel + restauration + journal',
            upd_new22: 'Entreprises démo : 4 entreprises d\'exemple (Commerce/Services/Production/Import-Export) + transactions mensuelles (12 mois) + rapports préétablis + modèles d\'import/export CSV',
            upd_new23: 'Expérience utilisateur améliorée : raccourcis clavier complets pour les 28 écrans (Ctrl+1..0, Ctrl+Maj+1..0, F2..F8, Ctrl+T pour le thème) + menu "Affichage" dynamique + messages d\'erreur unifiés avec action suggérée + transitions fondues + indicateur de chargement + améliorations de contraste/accessibilité dans les trois thèmes',
            upd_new24: 'Couverture complète des modules : 1229 tests réussis + couverture des modules à 99% (contre 73%) — tests edge/erreur pour chaque module + correction du bug generate_report dans les comparaisons + liste d\'erreurs documentée',
            upd_new25: 'Tests d\'intégration et de performance : 1266 tests réussis + 3 bugs produit corrigés (fonds de roulement non stocké, cascade de suppression notes cassée, sauvegarde perdant les données WAL) — insertion groupée de 1200 lignes en 4ms + 2000 calculs de ratios en 0.11s + 8 utilisateurs simultanés sans erreur',
            upd_date8: '1 Août 2026',
            upd_date9: '1 Août 2026',
            upd_new26: 'Écran tests utilisateurs (29) : 4 groupes × 5 scénarios + retours/suggestions/bugs avec catégories, priorités et statuts + score de satisfaction avec analyse détaillée + rapports (retours/liste bugs/demandes d\'amélioration/résumé) + données de démo + export/import JSON + export CSV/Excel/PDF + sauvegarde/chargement base de données — 1332 tests réussis + couverture user_testing 100%',
            upd_date10: '1 Août 2026',
            upd_new27: 'Correctifs finaux + revue de sécurité : correction de 13 bugs (impression paysage + détection d\'en-tête des fichiers bancaires + protection des modèles par défaut + export PDF arabe clair quand la police Amiri manque + téléchargement de mise à jour avec fichier partiel sûr + restauration de sauvegarde incluant vault.enc + rejet des noms de tables réservés SQLite) + revue de sécurité complète (PBKDF2 100k + secrets SMTP/API chiffrés + HTTPS uniquement) — 1350 tests réussis + couverture des modules 100%',
            upd_new13: 'Correction du problème d\'ouverture de l\'application après la mise à jour',
            upd_new14: 'Correction de la fenêtre cmd pendant la mise à jour — elle s\'exécute maintenant en toute discrétion',
            upd_new15: 'Installateur amélioré — plus petit et plus rapide',
            upd_new1: 'Correction de la notification de mise à jour — s\'affiche maintenant',
            upd_new2: 'Récupération du mot de passe avec système de code sécurisé',
            upd_new3: 'Email pré-rempli après inscription',
            upd_new4: 'Correction du chargement des données financières',
            upd_new5: 'Amélioration de la navigation Tab entre les champs',
            upd_new6: 'Correction du Calendrier Fiscal — la sélection de l\'année met à jour l\'affichage',
            upd_new7: 'Correction des Benchmarks — le changement de secteur met à jour les résultats',
            upd_new8: 'Téléchargement direct — fenêtre de progression + lancement automatique',
            upd_new9: 'Ajout de 8 nouveaux ratios financiers — Cash Ratio, Marge opérationnelle, DIO, Rotation fournisseurs, DPO, Cycle opérationnel, CCC, Ratio des capitaux propres',
            upd_new10: 'Ajout de 3 nouveaux champs — Trésorerie, Charges opérationnelles, Fournisseurs moyens',
            upd_new11: 'Correction du trait de soulignement (_) dans les mots de passe en mode arabe RTL',
            upd_new12: 'L\'écran des ratios affiche maintenant 20 ratios en 4 catégories',
            upd_new16: 'Références sectorielles avancées : Meilleure pratique + Norme internationale + Forces/Faiblesses + Analyse de tendance + Comparaison concurrents',
            upd_new17: 'Tableau de bord avancé : 6 cartes KPI à code couleur + 4 graphiques + alertes intelligentes + personnalisation complète + export PDF/Excel',
            upd_new18: 'Rentabilité des centres de coûts : centres (département/projet/succursale/ligne de production) + répartition directe/indirecte + rentabilité + comparaisons + tendances + rapports + export PDF/Excel',
            upd1: 'Système de vérification automatique des mises à jour',
            upd2: '8 nouvelles fonctionnalités: Impression, Excel, Calendrier fiscal, CSV, Banque, Benchmarks',
            upd3: 'Icône de l\'application + installateur professionnel',
            upd4: '26 écrans — 560 tests — 7 secteurs industriels',
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
                if (key === 'hero_title' || key === 'intro' || key === 'dl_note_sac') {
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

