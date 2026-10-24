# تفعيل Google Analytics

بعد إنشاء موقع في Google Analytics 4، انسخ معرّف القياس الذي يبدأ بـ `G-` واستبدل `G-REPLACE_WITH_YOUR_ID` في وسم `analytics.js` الموجود داخل ملفات HTML.

مثال:

```html
<script src="/assets/analytics.js" data-ga-id="G-XXXXXXXXXX"></script>
```

لن يرسل الموقع أي بيانات قبل وضع معرّف حقيقي.
