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
    engagement.setAttribute('aria-label', 'تقييم المقال والتعليقات');

    const ratingSection = document.createElement('section');
    ratingSection.className = 'article-rating';
    ratingSection.setAttribute('aria-labelledby', 'article-rating-title');
    ratingSection.innerHTML = '<h2 id="article-rating-title">ما رأيك في هذا المقال؟</h2><p class="article-rating-note">قيّم فائدته من نجمة إلى خمس نجوم. يُحفظ تقييمك في هذا المتصفح فقط ولا يُعرض كمتوسط عام.</p>';
    const ratingGroup = document.createElement('div');
    ratingGroup.className = 'article-rating-stars';
    ratingGroup.setAttribute('role', 'group');
    ratingGroup.setAttribute('aria-label', 'اختر تقييمًا من نجمة إلى خمس نجوم');
    const ratingStatus = document.createElement('p');
    ratingStatus.className = 'article-rating-status';
    ratingStatus.setAttribute('aria-live', 'polite');

    const ratingKey = `alkhayal:article-rating:${window.location.pathname}`;
    let savedRating = 0;
    try {
      const value = Number(window.localStorage.getItem(ratingKey));
      if (Number.isInteger(value) && value >= 1 && value <= 5) savedRating = value;
    } catch (_) {
      // Local storage can be unavailable in private/restricted browsing modes.
    }

    const starButtons = [];
    const paintRating = (value) => {
      starButtons.forEach((button, index) => {
        button.classList.toggle('is-selected', index < value);
        button.setAttribute('aria-pressed', String(index + 1 === value));
      });
    };
    for (let score = 1; score <= 5; score += 1) {
      const button = document.createElement('button');
      button.className = 'article-rating-star';
      button.type = 'button';
      button.textContent = '★';
      button.setAttribute('aria-label', `${score} ${score === 1 ? 'نجمة' : 'نجوم'}`);
      button.setAttribute('aria-pressed', 'false');
      button.addEventListener('click', () => {
        savedRating = score;
        paintRating(score);
        try {
          window.localStorage.setItem(ratingKey, String(score));
          ratingStatus.textContent = `شكرًا لك؛ حُفظ تقييمك (${score} من 5) في هذا المتصفح.`;
        } catch (_) {
          ratingStatus.textContent = `شكرًا لك على تقييم المقال (${score} من 5). تعذّر حفظه في هذا المتصفح.`;
        }
      });
      starButtons.push(button);
      ratingGroup.appendChild(button);
    }
    paintRating(savedRating);
    ratingStatus.textContent = savedRating
      ? `تقييمك المحفوظ في هذا المتصفح: ${savedRating} من 5.`
      : 'لن يظهر تقييم عام؛ يمكنك تغيير اختيارك في أي وقت.';
    ratingSection.append(ratingGroup, ratingStatus);

    const commentsSection = document.createElement('section');
    commentsSection.className = 'article-comments';
    commentsSection.setAttribute('aria-labelledby', 'article-comments-title');
    commentsSection.innerHTML = '<h2 id="article-comments-title">النقاش والتعليقات</h2><p class="article-comments-intro">شارك سؤالًا أو تجربة تساعد القرّاء. تُدار التعليقات عبر GitHub Discussions.</p>';
    const giscusContainer = document.createElement('div');
    giscusContainer.className = 'article-giscus';
    const fallback = document.createElement('p');
    fallback.className = 'article-comments-fallback';
    fallback.innerHTML = 'إذا لم تظهر مساحة التعليقات، <a href="https://github.com/abdo-q/al-khayal-home-services/discussions" target="_blank" rel="noopener noreferrer">افتح النقاشات على GitHub</a>.';
    const giscusScript = document.createElement('script');
    giscusScript.src = 'https://giscus.app/client.js';
    giscusScript.async = true;
    giscusScript.crossOrigin = 'anonymous';
    giscusScript.setAttribute('data-repo', 'abdo-q/al-khayal-home-services');
    giscusScript.setAttribute('data-repo-id', 'R_kgDOVG-KiQ');
    giscusScript.setAttribute('data-category', 'General');
    giscusScript.setAttribute('data-category-id', 'DIC_kwDOVG-Ki4DIkXy');
    giscusScript.setAttribute('data-mapping', 'pathname');
    giscusScript.setAttribute('data-strict', '0');
    giscusScript.setAttribute('data-reactions-enabled', '1');
    giscusScript.setAttribute('data-emit-metadata', '0');
    giscusScript.setAttribute('data-input-position', 'top');
    giscusScript.setAttribute('data-theme', 'light');
    giscusScript.setAttribute('data-lang', 'ar');
    giscusScript.addEventListener('error', () => fallback.classList.add('is-visible'), { once: true });
    giscusContainer.append(giscusScript, fallback);
    commentsSection.appendChild(giscusContainer);
    engagement.append(ratingSection, commentsSection);

    const related = article.querySelector('.article-related');
    if (related) related.before(engagement);
    else article.appendChild(engagement);
  }
})();
