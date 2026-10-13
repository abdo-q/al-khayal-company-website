(() => {
  const loader = document.createElement('div');
  loader.className = 'site-loader';
  loader.setAttribute('role', 'status');
  loader.setAttribute('aria-label', 'جارٍ تحميل الصفحة');
  loader.innerHTML = '<div class="site-loader-inner"><span class="site-loader-mark" aria-hidden="true"></span><span>جارٍ تحميل الصفحة…</span></div>';
  document.documentElement.appendChild(loader);
  const finishLoading = () => window.setTimeout(() => loader.classList.add('is-done'), 180);
  window.addEventListener('load', finishLoading, { once: true });
  window.setTimeout(finishLoading, 2200);


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
})();

// Lightweight, privacy-respecting rating interaction for the services page.
(() => {
  const stars = [...document.querySelectorAll('.rating-star')];
  const copy = document.querySelector('[data-rating-copy]');
  const link = document.querySelector('[data-rating-link]');
  if (!stars.length || !copy || !link) return;
  const labels = ['نحتاج إلى توضيح أكثر', 'الخدمة واضحة جزئيًا', 'المعلومات مفيدة', 'المعلومات واضحة جدًا', 'تجربة قراءة ممتازة'];
  const paint = (value) => {
    stars.forEach((star) => star.classList.toggle('is-selected', Number(star.dataset.rating) <= value));
    copy.textContent = `${labels[value - 1]} — تقييمك: ${value} من 5`;
    link.href = `https://wa.me/966552610151?text=${encodeURIComponent(`السلام عليكم، أقيّم وضوح صفحة الخدمات بـ ${value} من 5 نجوم، وهذه ملاحظتي: `)}`;
  };
  stars.forEach((star) => star.addEventListener('click', () => paint(Number(star.dataset.rating))));
})();
