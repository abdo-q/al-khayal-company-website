(() => {
  // Brief branded loading veil; always removed on load or after a short safety timeout.
  const pageLoader = document.createElement('div');
  pageLoader.className = 'site-page-loader';
  pageLoader.setAttribute('role', 'status');
  pageLoader.setAttribute('aria-live', 'polite');
  pageLoader.innerHTML = '<span class="site-page-loader__spinner" aria-hidden="true"></span><span>جارٍ تجهيز الصفحة…</span>';
  document.body.appendChild(pageLoader);
  let loaderDismissed = false;
  const hidePageLoader = () => {
    if (loaderDismissed) return;
    loaderDismissed = true;
    window.setTimeout(() => {
      pageLoader.classList.add('is-hidden');
      window.setTimeout(() => pageLoader.remove(), 320);
    }, 120);
  };
  if (document.readyState === 'complete') hidePageLoader();
  else window.addEventListener('load', hidePageLoader, { once: true });
  window.setTimeout(hidePageLoader, 1600);

  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav-links');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('click', (event) => {
      if (!nav.contains(event.target) && !toggle.contains(event.target)) {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  const revealItems = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('is-visible'));
  }

  const form = document.querySelector('#contact-form');
  if (form) {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const data = new FormData(form);
      const lines = [
        'السلام عليكم، أرغب بالاستفسار عن خدمات الخيال للخدمات المنزلية.',
        `الاسم: ${data.get('name')}`,
        `رقم التواصل: ${data.get('phone')}`,
        `الخدمة المطلوبة: ${data.get('service') || 'استفسار عام'}`,
        `التفاصيل: ${data.get('message')}`
      ];
      const status = form.querySelector('.form-status');
      if (status) status.textContent = 'سيتم فتح واتساب لإرسال رسالتك. أرسلها من التطبيق لإتمام التواصل.';
      window.open(`https://wa.me/966552610151?text=${encodeURIComponent(lines.join('\n'))}`, '_blank', 'noopener,noreferrer');
    });
  }

  document.querySelectorAll('[data-year]').forEach((node) => {
    node.textContent = new Date().getFullYear();
  });

  const article = document.querySelector('.article-detail');
  if (article && document.body.classList.contains('article-page')) {
    const engagement = document.createElement('section');
    engagement.className = 'article-engagement';
    engagement.setAttribute('aria-label', 'التواصل بشأن المقال');
    engagement.innerHTML = '<section class="article-comments" aria-labelledby="article-comments-title"><h2 id="article-comments-title">هل لديك سؤال؟</h2><p class="article-comments-intro">التعليقات الخارجية متوقفة لتجنب بطء الصفحة. أرسل سؤالك مباشرة عبر واتساب وسنساعدك في اختيار الخدمة المناسبة.</p><a class="button button-secondary" href="https://wa.me/966552610151" target="_blank" rel="noopener noreferrer">إرسال سؤال عبر واتساب</a></section>';
    const related = article.querySelector('.article-related');
    if (related) related.before(engagement);
    else article.appendChild(engagement);
  }
})();
