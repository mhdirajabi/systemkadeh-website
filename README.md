# سیستمکده - فروشگاه تخصصی لوازم صوتی و تصویری خودرو

سیستمکده یک فروشگاه آنلاین کامل و مدرن برای فروش لوازم صوتی، تصویری، مانیتور اندروید و تجهیزات امنیتی خودرو است که با Django و HTMX ساخته شده است.

## ویژگی‌های کلیدی

### 🎯 طراحی و تجربه کاربری
- طراحی کاملاً فارسی و راست‌چین
- ریسپانسیو کامل (موبایل‌فرست)
- دسترس‌پذیری (ARIA)
- فونت ایران یکان
- واحد پول تومان ایران

### 🛒 قابلیت‌های فروشگاهی
- کاتالوگ محصول با دسته‌بندی درختی
- سبد خرید و سفارش با HTMX
- کوپن تخفیف و مدیریت موجودی
- پرداخت آنلاین + خرید اقساطی
- امتیازدهی و نظرات محصول

### 🔐 احراز هویت
- ورود/ثبت‌نام با شماره موبایل و OTP
- ایجاد خودکار حساب کاربری
- پروفایل کاربر با آدرس‌ها و سفارش‌ها

### 💳 پرداخت
- پشتیبانی از زرین‌پال، زیبال
- پرداخت اقساطی (ترب‌پی، اسنپ‌پی، دیجی‌پی)
- لایه abstract PaymentProvider

### 📱 پیامک و بازاریابی
- سیستم ارسال پیامک OTP
- کمپین‌های بازاریابی پیامکی
- خبرنامه و اطلاع‌رسانی

### 🔍 سئو و بهینه‌سازی
- URL تمیز و فارسی
- اسکیما مارک‌آپ
- نقشه سایت و robots.txt
- متا تگ‌های کامل

## تکنولوژی‌ها

### Backend
- **Django 5.x** - فریمورک اصلی
- **Python 3.12** - زبان برنامه‌نویسی
- **PostgreSQL 16** - پایگاه داده
- **Redis** - کش و صف کارها
- **Celery** - تسک‌های پس‌زمینه

### Frontend
- **HTMX** - تعاملات پویا
- **Bootstrap 5 RTL** - فریمورک CSS
- **Vazirmatn Font** - فونت فارسی
- **JavaScript ES6+** - تعاملات پیشرفته

### DevOps
- **Docker & Docker Compose** - کانتینری‌سازی
- **NGINX** - وب سرور و پروکسی
- **Gunicorn** - WSGI سرور
- **WhiteNoise** - فایل‌های استاتیک

## نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (اختیاری)

### راه‌اندازی با Docker (توصیه شده)

1. **کلون کردن پروژه**
```bash
git clone <repository-url>
cd systemkadeh
```

2. **کپی کردن فایل محیط**
```bash
cp .env.example .env
```

3. **ویرایش تنظیمات**
```bash
nano .env
```

4. **راه‌اندازی با Docker Compose**
```bash
docker-compose up -d
```

5. **اجرای مایگریشن‌ها**
```bash
docker-compose exec web python manage.py migrate
```

6. **ایجاد سوپریوزر**
```bash
docker-compose exec web python manage.py createsuperuser
```

7. **بارگذاری داده نمونه**
```bash
docker-compose exec web python manage.py loaddata fixtures/sample_data.json
```

### راه‌اندازی دستی

1. **ایجاد محیط مجازی**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate  # Windows
```

2. **نصب وابستگی‌ها**
```bash
pip install -r requirements.txt
```

3. **تنظیم پایگاه داده**
```bash
createdb systemkadeh
```

4. **اجرای مایگریشن‌ها**
```bash
python manage.py migrate
```

5. **ایجاد سوپریوزر**
```bash
python manage.py createsuperuser
```

6. **اجرای سرور**
```bash
python manage.py runserver
```

## ساختار پروژه

```
systemkadeh/
├── apps/
│   ├── accounts/          # احراز هویت و کاربران
│   ├── blog/              # سیستم وبلاگ
│   ├── cart/              # سبد خرید
│   ├── catalog/           # کاتالوگ محصولات
│   ├── checkout/          # تسویه حساب
│   ├── core/              # هسته سیستم
│   ├── marketing/         # بازاریابی
│   ├── payments/          # پرداخت‌ها
│   ├── seo/               # بهینه‌سازی موتور جستجو
│   └── sms/               # پیامک
├── static/                # فایل‌های استاتیک
├── templates/             # قالب‌های HTML
├── media/                 # فایل‌های رسانه
├── systemkadeh/           # تنظیمات اصلی
├── docker-compose.yml     # کانفیگ Docker
├── Dockerfile            # تصویر Docker
└── requirements.txt      # وابستگی‌های Python
```

## تنظیمات مهم

### پایگاه داده
```python
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:postgres@localhost:5432/systemkadeh'
    )
}
```

### کش Redis
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Celery
```python
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
```

## API و HTMX

### جستجوی زنده
```html
<form hx-get="/catalog/search/" hx-trigger="keyup changed delay:300ms">
    <input type="text" name="q" placeholder="جستجو...">
</form>
```

### افزودن به سبد خرید
```html
<button hx-post="/cart/add/" hx-vals='{"product_id": "123", "quantity": "1"}'>
    افزودن به سبد
</button>
```

### فیلتر محصولات
```html
<select hx-get="/catalog/products/" hx-target="#products">
    <option value="price_asc">قیمت: کم به زیاد</option>
</select>
```

## تست‌ها

```bash
# اجرای تمام تست‌ها
python manage.py test

# تست با پوشش کد
coverage run --source='.' manage.py test
coverage report
coverage html
```

## استقرار (Deployment)

### تولید (Production)

1. **تنظیم متغیرهای محیط**
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-production-secret-key
```

2. **اجرای با Docker**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **تنظیم SSL**
```bash
# کپی گواهی SSL به پوشه ssl/
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem
```

### مانیتورینگ

- **Sentry** برای ردیابی خطاها
- **Google Analytics** برای آمار بازدید
- **Logs** در `/app/logs/`

## مشارکت

1. Fork کنید
2. شاخه جدید بسازید (`git checkout -b feature/amazing-feature`)
3. تغییرات را commit کنید (`git commit -m 'Add amazing feature'`)
4. به شاخه push کنید (`git push origin feature/amazing-feature`)
5. Pull Request بسازید

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای جزئیات بیشتر فایل `LICENSE` را مطالعه کنید.

## پشتیبانی

- **ایمیل**: support@systemkadeh.com
- **تلفن**: 021-12345678
- **وب‌سایت**: https://systemkadeh.com

## تغییرات آینده

- [ ] پنل مدیریت پیشرفته
- [ ] سیستم امتیازدهی و وفاداری
- [ ] چت آنلاین
- [ ] اپلیکیشن موبایل
- [ ] سیستم انبارداری
- [ ] گزارش‌گیری پیشرفته

---

**سیستمکده** - صدایی که همیشه همراهته! 🎵🚗