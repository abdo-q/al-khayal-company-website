from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parents[1]
CITY = {
    "abu-arish": "أبو عريش", "bisha": "بيشة", "dawadmi": "الدوادمي", "majmaah": "المجمعة",
    "qurayyat": "القريات", "rafha": "رفحاء", "rass": "الرس", "sabya": "صبيا",
    "shaqra": "شقراء", "turaif": "طريف", "unayzah": "عنيزة", "wadi-al-dawasir": "وادي الدواسر",
}


def set_title(text: str, title: str) -> str:
    return re.sub(r"(<title[^>]*>).*?(</title>)", lambda m: m.group(1) + html.escape(title) + m.group(2), text, count=1, flags=re.I | re.S)


def main() -> None:
    changed = 0
    for path in ROOT.glob("cleaning-*/index.html"):
        slug = path.parent.name.removeprefix("cleaning-")
        if slug not in CITY:
            continue
        text = path.read_text(encoding="utf-8")
        new = set_title(text, f"تنظيف منازل في {CITY[slug]} | الخيال")
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1

    video = ROOT / "video.html"
    text = video.read_text(encoding="utf-8")
    block = '''<section class="section audit-content-section" aria-labelledby="video-guide-title"><div class="container"><div class="section-heading"><span class="eyebrow"><span class="eyebrow-dot"></span> دليل سريع</span><h2 id="video-guide-title">كيف تستفيد من المقطع قبل طلب الخدمة؟</h2><p>المقطع التعريفي يعطي فكرة عن أسلوب العناية بالمنزل، لكنه لا يغني عن وصف احتياجك قبل تحديد الموعد. اذكر المدينة ونوع العقار والمساحة، وحدد إن كان الطلب تنظيفًا دوريًا أو تنظيفًا عميقًا بعد مناسبة أو انتقال. هذه التفاصيل تساعد على ترتيب الأولويات وتوضيح البنود التي تحتاج وقتًا أو مواد خاصة.</p></div><div class="content-grid"><article class="info-card"><h3>قبل التنظيف</h3><p>أبعد الأشياء القابلة للكسر، وحدد الأسطح الحساسة، وصوّر المواضع التي تحتاج متابعة حتى يكون نطاق العمل واضحًا.</p></article><article class="info-card"><h3>أثناء التنسيق</h3><p>اسأل عن المناطق المشمولة والمواد المستخدمة ووقت التنفيذ، ولا تعتمد أي بند إضافي قبل معرفة تكلفته وطريقة إنجازه.</p></article><article class="info-card"><h3>بعد الزيارة</h3><p>راجع النتيجة في الإضاءة المناسبة، وتأكد من تنظيف الحواف والزوايا، ثم أرسل أي ملاحظة عبر واتساب ليتم التعامل معها بوضوح.</p></article></div></div></section>\n'''
    if "id=\"video-guide-title\"" not in text:
        text = text.replace("</main>", block + "</main>", 1)
        video.write_text(text, encoding="utf-8")
        changed += 1

    contact = ROOT / "contact.html"
    text = contact.read_text(encoding="utf-8")
    block = '''<section class="section audit-content-section" aria-labelledby="contact-prep-title"><div class="container"><div class="section-heading"><span class="eyebrow"><span class="eyebrow-dot"></span> تجهيز الطلب</span><h2 id="contact-prep-title">معلومات تساعدنا على الرد بسرعة</h2><p>عند الاتصال أو مراسلتنا عبر واتساب، اذكر المدينة والحي ونوع الخدمة والمساحة التقريبية. وإذا كان الطلب متعلقًا بجهاز أو عطل، اذكر العلامات التي ظهرت ووقت بدايتها وما إذا جرت محاولة إصلاح سابقة. يساعد الوصف المختصر على التحقق من نطاق الخدمة وتوجيهك إلى الخطوة المناسبة دون وعود مسبقة بالتغطية أو الموعد.</p></div><div class="content-grid"><article class="info-card"><h3>التنظيف</h3><p>اذكر عدد الغرف ونوع الأثاث والموعد المناسب، وبيّن إن كان المطلوب تنظيفًا عميقًا أو متابعة دورية.</p></article><article class="info-card"><h3>الصيانة</h3><p>اذكر نوع الجهاز أو العطل والأعراض الظاهرة، ولا تقترب من مصدر كهرباء أو تسرب خطر قبل حضور المختص.</p></article><article class="info-card"><h3>التأكيد</h3><p>لا يُعد الحجز مؤكدًا قبل الرد عليك وتوضيح النطاق والتكلفة والوقت المتوقع للخدمة.</p></article></div></div></section>\n'''
    if "id=\"contact-prep-title\"" not in text:
        text = text.replace("</main>", block + "</main>", 1)
        contact.write_text(text, encoding="utf-8")
        changed += 1

    print(f"changed={changed}")


if __name__ == "__main__":
    main()
