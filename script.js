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

  // Cache local pages after the first visit so repeated keyword navigation is instant.
  if ('serviceWorker' in navigator && window.isSecureContext) {
    navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' }).catch(() => {});
  }

  const prefetched = new Set();
  const prefetchLocalPage = (link) => {
    if (!link || link.target === '_blank' || link.hasAttribute('download')) return;
    const url = new URL(link.href, window.location.href);
    if (url.origin !== window.location.origin || prefetched.has(url.href)) return;
    prefetched.add(url.href);
    const hint = document.createElement('link');
    hint.rel = 'prefetch';
    hint.as = 'document';
    hint.href = url.href;
    document.head.appendChild(hint);
  };
  document.addEventListener('pointerover', (event) => {
    const link = event.target.closest('a');
    if (link) prefetchLocalPage(link);
  }, { passive: true });
  document.addEventListener('focusin', (event) => {
    const link = event.target.closest('a');
    if (link) prefetchLocalPage(link);
  });


})();
