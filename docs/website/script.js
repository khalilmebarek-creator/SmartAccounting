// Smart Accounting Platform — Website Scripts
document.addEventListener('DOMContentLoaded', () => {
    // Language toggle (AR/EN)
    const langBtn = document.getElementById('langToggle');
    const html = document.documentElement;
    const translations = {
        ar: {
            title: 'المنصة المحاسبية الذكية',
            subtitle: 'نظام محاسبي متكامل بالذكاء الاصطناعي — دعم عربي/إنجليزي/فرنسي — النظام الجبائي الجزائري',
            features: 'المميزات الرئيسية',
            modules: 'الوحدات الرئيسية',
            screens: 'الشاشات الـ 18',
            tech: 'التقنيات المستخدمة',
            download: 'تحميل التطبيق',
            langBtn: 'EN',
        },
        en: {
            title: 'Smart Accounting Platform',
            subtitle: 'AI-powered accounting system — Arabic/English/French — Algerian Tax Module',
            features: 'Key Features',
            modules: 'Core Modules',
            screens: '18 Interactive Screens',
            tech: 'Technologies',
            download: 'Download',
            langBtn: 'AR',
        }
    };
    let currentLang = 'ar';
    langBtn.addEventListener('click', () => {
        currentLang = currentLang === 'ar' ? 'en' : 'ar';
        html.lang = currentLang;
        html.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
        langBtn.textContent = translations[currentLang].langBtn;
        document.querySelector('.hero h1').textContent = translations[currentLang].title;
        document.querySelector('.hero-subtitle').textContent = translations[currentLang].subtitle;
        document.querySelectorAll('.section-title').forEach((el, i) => {
            const keys = ['features', 'modules', 'screens', 'tech', 'download'];
            if (keys[i]) el.textContent = translations[currentLang][keys[i]];
        });
    });

    // Hamburger menu
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.querySelector('.nav-links');
    hamburger.addEventListener('click', () => {
        navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        navLinks.style.flexDirection = 'column';
        navLinks.style.position = 'absolute';
        navLinks.style.top = '60px';
        navLinks.style.right = '20px';
        navLinks.style.background = '#fff';
        navLinks.style.padding = '16px';
        navLinks.style.borderRadius = '8px';
        navLinks.style.boxShadow = '0 4px 20px rgba(0,0,0,.1)';
    });

    // Scroll animations
    const fadeEls = document.querySelectorAll('.feature-card, .module-card, .tech-item, .screen-tag');
    fadeEls.forEach(el => el.classList.add('fade-in'));
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('visible');
        });
    }, { threshold: 0.1 });
    fadeEls.forEach(el => observer.observe(el));

    // Counter animation
    const counters = document.querySelectorAll('.stat-number');
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-target'));
                let current = 0;
                const increment = Math.ceil(target / 40);
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) { current = target; clearInterval(timer); }
                    el.textContent = current;
                }, 30);
                counterObserver.unobserve(el);
            }
        });
    }, { threshold: 0.5 });
    counters.forEach(c => counterObserver.observe(c));

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
});
