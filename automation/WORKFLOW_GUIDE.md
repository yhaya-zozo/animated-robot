# دليل تشغيل مبسّط (بدون تعقيد)

هذا الدليل مكتوب خطوة بخطوة عشان تشغّل الأتمتة بسهولة.

## 1) جهّز Google Sheet
- اعمل Google Sheet جديد.
- انسخ أول صف (العناوين) من المثال الموجود في `automation/sample_sheet.csv`.
- اكتب بيانات العملاء.

**مهم:** لازم يكون عمود **تم الإرسال؟** موجود.

## 2) جهّز حساب WhatsApp Business API
- استخدم مزود مثل 360dialog أو Twilio.
- خُد القيم الثلاثة:
  - `WHATSAPP_API_BASE_URL`
  - `WHATSAPP_API_TOKEN`
  - `WHATSAPP_SENDER_ID`

## 3) جهّز Google Service Account
- أنشئ Service Account من Google Cloud.
- فعّل Google Sheets API.
- نزّل ملف JSON.
- شارك الـ Sheet مع إيميل الـ Service Account.

## 4) إعداد الملف `.env`
- انسخ `.env.example` إلى `.env`.
- عبّي القيم المطلوبة.

## 5) التشغيل
```bash
pip install -r requirements.txt
python automation/send_whatsapp_reminders.py
```

## 6) أول تشغيل؟ جرّب وضع المحاكاة (بدون إرسال)
- في `.env` ضع:
  - `DRY_RUN=true`
- السكربت هيطبع الرسائل بدل ما يرسلها.

## 7) التعديل على القوالب
- عدّل `automation/templates.json`.
- استخدم المتغيرات: `{{name}}` و `{{event_date}}`.
