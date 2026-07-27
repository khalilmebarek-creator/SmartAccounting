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
        navLinks.classList.toggle('active');
        hamburger.classList.toggle('active');
    });
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            hamburger.classList.remove('active');
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
        const statsSection = document.querySelector('.stats-col');
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

    // ===== LANGUAGE TOGGLE =====
    const langToggle = document.getElementById('langToggle');
    let currentLang = 'ar';

    const translations = {
        ar: {
            about: 'عن المشروع',
            features: 'المميزات',
            modules: 'الوحدات',
            tech: 'الإحصائيات',
            download: 'تحميل',
            updates: 'التحديثات',
            hero_title_1: 'المنصة المحاسبية',
            hero_title_2: 'الذكية',
            hero_desc: 'نظام محاسبي متكامل مبني بالذكاء الاصطناعي — يدعم 3 لغات ويشمل النظام الجبائي الجزائري بأكمله',
            hero_btn1: 'تحميل التطبيق',
            hero_btn2: 'اكتشف المزيد',
            toggle: 'EN',
        },
        en: {
            about: 'About',
            features: 'Features',
            modules: 'Modules',
            tech: 'Tech',
            download: 'Download',
            updates: 'Updates',
            hero_title_1: 'Smart',
            hero_title_2: 'Accounting Platform',
            hero_desc: 'A complete accounting system powered by AI — supports 3 languages and includes the full Algerian tax system',
            hero_btn1: 'Download App',
            hero_btn2: 'Learn More',
            toggle: 'عر',
        },
    };

    langToggle.addEventListener('click', () => {
        currentLang = currentLang === 'ar' ? 'en' : 'ar';
        const t = translations[currentLang];
        langToggle.textContent = t.toggle;

        document.documentElement.lang = currentLang;
        document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';

        // Update nav links
        document.querySelectorAll('.nav-links a').forEach(a => {
            const key = a.getAttribute('href').replace('#', '');
            if (t[key]) a.textContent = t[key];
        });

        // Update hero
        const heroTitle = document.querySelector('.hero h1');
        if (heroTitle) heroTitle.innerHTML = `${t.hero_title_1}<br><span class="text-gradient">${t.hero_title_2}</span>`;
        const heroDesc = document.querySelector('.hero-desc');
        if (heroDesc) heroDesc.textContent = t.hero_desc;
        const heroBtns = document.querySelectorAll('.hero-buttons .btn');
        if (heroBtns[0]) heroBtns[0].lastChild.textContent = ' ' + t.hero_btn1;
        if (heroBtns[1]) heroBtns[1].textContent = t.hero_btn2;
    });

});
