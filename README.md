# Multi-Format Search Engine

محرك بحث متعدد الصيغ بواجهة ويب حديثة باستخدام Python وWhoosh وNLTK

---

## فكرة المشروع
محرك بحث ذكي يدعم البحث في ملفات PDF, TXT, CSV, Excel, JSON وصفحات الويب (Web Pages) من خلال واجهة ويب سهلة وحديثة.

---

## المميزات
- دعم البحث في: PDF, TXT, CSV, Excel, JSON, Web Pages
- واجهة مستخدم حديثة مع فلتر لاختيار نوع الملف
- دعم استعلامات البحث المتقدمة: AND, OR, Phrase, Wildcard, Fuzzy
- معالجة نصوص باستخدام NLTK
- حساب Precision / Recall / F1-Score
- تنظيم الكود وسهولة التوسعة
- دعم اللغة العربية والإنجليزية
- أيقونة موقع (favicon) تعبر عن البحث

---

## المتطلبات
- Python 3.8+
- pip
- المتطلبات البرمجية:
  ```bash
  pip install -r requirements.txt
  ```
- Tesseract OCR (لـ PDF)
- Poppler (لـ PDF)

---

## خطوات التشغيل
1. ضع ملفاتك في `data/documents`
2. ضع روابط صفحات الويب في `indexer/web_urls.txt` (كل رابط في سطر)
3. شغل التطبيق:
   ```bash
   python app.py
   ```
4. افتح المتصفح على: [http://localhost:5000](http://localhost:5000)
5. ابحث وحدد نوع الملف من القائمة المنسدلة

---

## أمثلة استعلامات البحث
- كلمة واحدة: `python`
- جملة: `information retrieval`
- عبارة: `"search engine"`
- استعلام AND: `python AND search`
- استعلام OR: `python OR java`
- Wildcard: `pyth*`
- Fuzzy: `retrival~`

---

## بنية المشروع
```
.
├── app.py              # التطبيق الرئيسي
├── config.py           # الإعدادات
├── requirements.txt    # المتطلبات
├── data/
│   ├── documents/     # ملفات البحث
│   └── indexes/       # الفهارس
├── indexer/
│   ├── pdf_indexer.py
│   ├── txt_indexer.py
│   ├── csv_indexer.py
│   ├── excel_indexer.py
│   ├── json_indexer.py
│   ├── web_indexer.py
│   └── web_urls.txt    # روابط صفحات الويب
├── templates/
│   └── index.html     # الواجهة
└── static/
    └── 1f50d.png      # أيقونة الموقع (عدسة بحث)
```

---

## المساهمة
مرحبًا بأي اقتراحات أو تحسينات! 