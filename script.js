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
    engagement.setAttribute('aria-label', 'التعليقات');

    const commentsSection = document.createElement('section');
    commentsSection.className = 'article-comments';
    commentsSection.setAttribute('aria-labelledby', 'article-comments-title');
    commentsSection.innerHTML = '<h2 id="article-comments-title">التعليقات</h2><p class="article-comments-intro">يمكنك إرسال سؤالك أو ملاحظتك عبر واتساب مباشرة. تحميل التعليقات الخارجية اختياري حتى لا تتأثر سرعة الصفحة.</p>';

    const commentsRoot = document.createElement('div');
    commentsRoot.className = 'article-hcb';
    commentsRoot.innerHTML = '<p id="HCB_comment_box" dir="rtl" lang="ar">التعليقات متاحة عند الطلب.</p><button type="button" class="button button-secondary article-comments-load">تحميل التعليقات</button><p class="article-comments-status" role="status" aria-live="polite"></p>';
    commentsSection.appendChild(commentsRoot);
    engagement.appendChild(commentsSection);

    const related = article.querySelector('.article-related');
    if (related) related.before(engagement);
    else article.appendChild(engagement);

    let commentsLoaded = false;
    const localizeCommentForm = () => {
      const box = commentsRoot.querySelector('#HCB_comment_box');
      if (!box) return;
      box.setAttribute('dir', 'rtl');
      box.setAttribute('lang', 'ar');
      const nameField = box.querySelector('#hcb_form_name');
      if (nameField) nameField.placeholder = 'اسمك';
      const commentField = box.querySelector('#hcb_form_content');
      if (commentField) commentField.placeholder = 'اكتب تعليقك هنا';
      const submitButton = box.querySelector('#hcb_submit');
      if (submitButton) submitButton.value = 'إرسال التعليق';
      box.querySelectorAll('h2, h3').forEach((heading) => {
        if (/^comments?$/i.test(heading.textContent.trim())) heading.textContent = 'التعليقات';
      });
    };

    const loadComments = () => {
      if (commentsLoaded) return;
      commentsLoaded = true;
      const button = commentsRoot.querySelector('.article-comments-load');
      const status = commentsRoot.querySelector('.article-comments-status');
      if (button) {
        button.disabled = true;
        button.textContent = 'جارٍ تحميل التعليقات…';
      }
      const user = window.hcb_user || (window.hcb_user = {});
      const canonical = document.querySelector('link[rel="canonical"]');
      user.PAGE = canonical ? canonical.href : window.location.href.split('#')[0].split('?')[0];
      let settled = false;
      const fail = () => {
        if (settled) return;
        settled = true;
        const box = commentsRoot.querySelector('#HCB_comment_box');
        if (box) box.textContent = 'تعذر تحميل التعليقات الخارجية الآن. يمكنك التواصل معنا عبر واتساب بدلًا من ذلك.';
        if (status) status.innerHTML = '<a class="text-link" href="https://wa.me/966552610151" target="_blank" rel="noopener noreferrer">إرسال سؤال عبر واتساب</a>';
        if (button) button.remove();
        document.querySelectorAll('script#hcb, link[data-hcb-style]').forEach((node) => node.remove());
      };
      const succeed = () => {
        if (settled) return;
        settled = true;
        if (button) button.remove();
        if (status) status.textContent = '';
        localizeCommentForm();
      };
      const loadWidgetScript = () => {
        if (settled) return;
        const widgetScript = document.createElement('script');
        widgetScript.type = 'text/javascript';
        widgetScript.id = 'hcb';
        widgetScript.async = true;
        const page = encodeURIComponent(user.PAGE).replace(/\+/g, '%2B');
        widgetScript.src = 'https://www.htmlcommentbox.com/jread?page=' + page + '&mod=%241%24wq1rdBcg%24wRuJ5zDkcOgxNS3r%2Fjl3U.&opts=16798&num=10&ts=1792155003900';
        widgetScript.addEventListener('load', () => window.setTimeout(succeed, 300), { once: true });
        widgetScript.addEventListener('error', fail, { once: true });
        document.head.appendChild(widgetScript);
      };
      const css = document.createElement('link');
      css.rel = 'stylesheet';
      css.dataset.hcbStyle = 'true';
      css.href = 'https://www.htmlcommentbox.com/static/skins/bootstrap/twitter-bootstrap.css?v=0';
      css.onload = loadWidgetScript;
      css.onerror = loadWidgetScript;
      document.head.appendChild(css);
      window.setTimeout(fail, 8000);
      const observer = new MutationObserver(localizeCommentForm);
      observer.observe(commentsRoot, { childList: true, subtree: true, attributes: true });
      window.setTimeout(() => observer.disconnect(), 9000);
    };

    const loadButton = commentsRoot.querySelector('.article-comments-load');
    if (loadButton) loadButton.addEventListener('click', loadComments, { once: true });
  }

})();
