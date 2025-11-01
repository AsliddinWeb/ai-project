# 🌍 Django Ko'p Tillik (Multilingual) To'liq Qo'llanma

## 📋 Mundarija
1. [Kirish](#kirish)
2. [O'rnatish](#ornatish)
3. [Fayllar tuzilmasi](#fayllar-tuzilmasi)
4. [Qadamma-qadam yo'riqnoma](#qadamma-qadam-yoriqnoma)
5. [Template'larda ishlatish](#templatelarda-ishlatish)
6. [Views va Models da ishlatish](#views-va-models-da-ishlatish)
7. [Xatolarni hal qilish](#xatolarni-hal-qilish)

---

## 🎯 Kirish

Ushbu qo'llanma Django loyihasini 3 tilga (O'zbek, Rus, Ingliz) tarjima qilish uchun to'liq yo'riqnoma.

**Qo'llab-quvvatlanadigan tillar:**
- 🇺🇿 O'zbekcha (uz)
- 🇷🇺 Русский (ru)  
- 🇬🇧 English (en)

---

## 🚀 O'rnatish

### 1. Virtual muhitni faollashtiring

```bash
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 2. Kerakli kutubxonalar allaqachon o'rnatilgan
Django i18n tizim Django bilan birga keladi, qo'shimcha package o'rnatish shart emas.

---

## 📁 Fayllar Tuzilmasi

```
loyihangiz/
├── config/
│   ├── settings/
│   │   └── base.py          ← base.py bilan almashtiring
│   └── urls.py               ← urls.py bilan almashtiring
├── apps/
│   └── main_app/
│       ├── models.py         ← models_translated.py bilan almashtiring
│       └── ...
├── templates/
│   ├── home.html             ← home_example.html dan nusxa oling
│   └── components/
│       └── language_switcher.html  ← Bu faylni qo'shing
├── locale/                   ← Bu papkani yaratish kerak
│   ├── uz/
│   │   └── LC_MESSAGES/
│   │       ├── django.po     ← django_uz.po dan nusxa oling
│   │       └── django.mo     ← compilemessages yaratadi
│   ├── ru/
│   │   └── LC_MESSAGES/
│   │       ├── django.po     ← django_ru.po dan nusxa oling
│   │       └── django.mo
│   └── en/
│       └── LC_MESSAGES/
│           ├── django.po     ← django_en.po dan nusxa oling
│           └── django.mo
└── manage.py
```

---

## 📖 Qadamma-qadam Yo'riqnoma

### 1. Locale papkasini yaratish

```bash
mkdir locale
```

### 2. Fayllarni almashtirish

**MUHIM:** Avval eski fayllardan zaxira nusxa oling!

```bash
# Zaxira
cp config/settings/base.py config/settings/base.py.backup
cp config/urls.py config/urls.py.backup
cp apps/main_app/models.py apps/main_app/models.py.backup

# Almashtirish
cp base.py config/settings/base.py
cp urls.py config/urls.py
cp models_translated.py apps/main_app/models.py
```

### 3. Template'larga til almashtirgich qo'shish

```bash
# Components papkasini yaratish
mkdir -p templates/components

# Til almashtirgichni ko'chirish
cp language_switcher.html templates/components/
```

Har bir template faylida (home.html, about.html, va h.k.):

```html
{% load i18n %}  <!-- Boshida qo'shing -->

<body>
    {% include 'components/language_switcher.html' %}  <!-- Body da qo'shing -->
    <!-- ... qolgan kod ... -->
</body>
```

### 4. Locale katalogini yaratish

```bash
# Barcha tillar uchun
python manage.py makemessages -l uz --ignore=venv
python manage.py makemessages -l ru --ignore=venv
python manage.py makemessages -l en --ignore=venv

# Yoki bitta buyruq bilan
python manage.py makemessages -a --ignore=venv
```

Bu buyruq `locale/uz/LC_MESSAGES/django.po` (va ru, en uchun ham) fayllarini yaratadi.

### 5. Tarjimalarni qo'shish

Agar men tayyorlab bergan `.po` fayllarni ishlatsangiz:

```bash
# Mening tarjimalarimni ko'chirish
cp django_uz.po locale/uz/LC_MESSAGES/django.po
cp django_ru.po locale/ru/LC_MESSAGES/django.po
cp django_en.po locale/en/LC_MESSAGES/django.po
```

Yoki qo'lda tahrirlash:

```bash
# Masalan, nano yoki VS Code da ochish
nano locale/ru/LC_MESSAGES/django.po
```

`.po` fayl namunasi:

```po
msgid "Bosh sahifa"
msgstr "Главная"    # Rus tilida

msgid "Hoziroq boshlash"
msgstr "Начать сейчас"
```

### 6. Tarjimalarni kompilyatsiya qilish

```bash
python manage.py compilemessages
```

Bu buyruq `.po` fayllardan `.mo` fayllar yaratadi.

### 7. Migratsiya

Model field'larini o'zgartirganingiz uchun:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Serverni ishga tushurish

```bash
python manage.py runserver
```

---

## 🎨 Template'larda Ishlatish

### Asosiy ishlatish

```html
{% load i18n %}

<!-- Oddiy matn -->
<h1>{% trans "Sarlavha" %}</h1>
<p>{% trans "Bu matn tarjima qilinadi" %}</p>

<!-- Tugma -->
<button>{% trans "Saqlash" %}</button>

<!-- Link -->
<a href="{% url 'home' %}">{% trans "Bosh sahifa" %}</a>
```

### O'zgaruvchilar bilan

```html
{% load i18n %}

{% blocktrans with name=user.name age=user.age %}
    Salom, {{ name }}! Siz {{ age }} yoshdasiz.
{% endblocktrans %}
```

### Shart bilan

```html
{% load i18n %}

{% if user.is_authenticated %}
    <p>{% trans "Xush kelibsiz" %}, {{ user.username }}!</p>
{% else %}
    <p>{% trans "Iltimos, tizimga kiring" %}</p>
{% endif %}
```

### Ko'p qatorli matn

```html
{% load i18n %}

{% blocktrans %}
    Bu uzun matn bo'lib,
    bir necha qatordan iborat.
    U to'liq tarjima qilinadi.
{% endblocktrans %}
```

---

## 🐍 Views va Models da Ishlatish

### Views.py

```python
from django.utils.translation import gettext as _
from django.shortcuts import render

def my_view(request):
    # Oddiy tarjima
    message = _("Bu xabar tarjima qilinadi")
    
    # Context bilan
    context = {
        'title': _("Sahifa sarlavhasi"),
        'description': _("Tavsif matni"),
        'message': message
    }
    
    return render(request, 'template.html', context)

def another_view(request):
    # Xatolik xabari
    if not request.user.is_authenticated:
        return HttpResponse(_("Iltimos, tizimga kiring"))
    
    # Success xabari
    messages.success(request, _("Muvaffaqiyatli saqlandi!"))
    
    return redirect('home')
```

### Models.py (allaqachon qilgan)

```python
from django.db import models
from django.utils.translation import gettext_lazy as _

class MyModel(models.Model):
    name = models.CharField(_("Ism"), max_length=100)
    description = models.TextField(_("Tavsif"))
    
    class Meta:
        verbose_name = _("Ob'ekt")
        verbose_name_plural = _("Ob'ektlar")
    
    def __str__(self):
        return f"{self.name}"
```

**MUHIM:** Models da `gettext_lazy` ishlatish kerak!

```python
# ✅ To'g'ri
from django.utils.translation import gettext_lazy as _

# ❌ Noto'g'ri
from django.utils.translation import gettext as _
```

---

## 🔗 URL Manzillari

Ko'p tillik yoqilgandan keyin URLlar quyidagicha bo'ladi:

```
http://localhost:8000/uz/               → O'zbekcha bosh sahifa
http://localhost:8000/ru/               → Ruscha bosh sahifa  
http://localhost:8000/en/               → Inglizcha bosh sahifa

http://localhost:8000/uz/diagnose/      → Tashxis (O'zbek)
http://localhost:8000/ru/diagnose/      → Диагностика (Rus)
http://localhost:8000/en/diagnose/      → Diagnosis (Ingliz)

http://localhost:8000/uz/admin/         → Admin (O'zbek)
```

---

## 🔄 Har Safar O'zgartirganda

### 1. Template'larga yangi matn qo'shsangiz:

```bash
# 1. Yangi tarjimalarni topish
python manage.py makemessages -a --ignore=venv

# 2. locale/.../django.po fayllarni tahrirlang

# 3. Kompilyatsiya qiling
python manage.py compilemessages

# 4. Serverni qayta ishga tushuring (yoki faqat yangilang)
```

### 2. Model field'larini o'zgartirsangiz:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py makemessages -a --ignore=venv
python manage.py compilemessages
```

---

## 🛠️ Xatolarni Hal Qilish

### ❌ Xatolik: "No translation files found"

**Sabab:** `locale/` papkasi noto'g'ri joyda yoki yo'q.

**Hal qilish:**
```bash
# 1. locale papkasini to'g'ri joyda yarating
mkdir locale

# 2. LOCALE_PATHS ni tekshiring (base.py da)
LOCALE_PATHS = [
    BASE_DIR / '../locale',
]

# 3. Qayta urinib ko'ring
python manage.py makemessages -l uz --ignore=venv
```

---

### ❌ Xatolik: "Translations not working"

**Sabab:** `.mo` fayllar yaratilmagan.

**Hal qilish:**
```bash
# Kompilyatsiya qiling
python manage.py compilemessages

# Serverni qayta ishga tushuring
python manage.py runserver
```

---

### ❌ Xatolik: "Circular import"

**Sabab:** Models da `gettext` ishlatilgan.

**Hal qilish:**
```python
# ❌ Noto'g'ri
from django.utils.translation import gettext as _

# ✅ To'g'ri
from django.utils.translation import gettext_lazy as _
```

---

### ❌ Xatolik: "LocaleMiddleware not found"

**Sabab:** Middleware qo'shilmagan.

**Hal qilish:**
```python
# config/settings/base.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # BU QATORNI QO'SHING
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

---

### ❌ Xatolik: URLs ishlamayapti

**Sabab:** `i18n_patterns` ishlatilmagan.

**Hal qilish:**
```python
# config/urls.py
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('apps.main_app.urls')),
    prefix_default_language=True
)
```

---

## 📝 Maslahatlar

### 1. gettext vs gettext_lazy

```python
# Views da
from django.utils.translation import gettext as _

# Models va Forms da
from django.utils.translation import gettext_lazy as _
```

### 2. Brauzer tilini avtomatik tanlash

Django avtomatik ravishda foydalanuvchi brauzerining tilini aniqlaydi va shu tilni tanlaydi.

### 3. Cookie orqali tilni eslab qolish

Django avtomatik ravishda foydalanuvchi tanlagan tilni cookie da saqlaydi. Keyingi tashriflarda shu til ishlatiladi.

### 4. .po fayllarni tahrirlash

Poedit dasturidan foydalanishingiz mumkin (qulay interfeys):
- Yuklab olish: https://poedit.net/

Yoki oddiy matn muharrirda (VS Code, Notepad++) tahrirlashingiz mumkin.

---

## ✅ Tekshirish Ro'yxati

Hammasi tayyor bo'lganini tekshirish uchun:

- [ ] `locale/` papkasi mavjud
- [ ] `config/settings/base.py` yangilangan (LANGUAGES, LOCALE_PATHS, LocaleMiddleware)
- [ ] `config/urls.py` i18n_patterns ishlatadi
- [ ] `models.py` da gettext_lazy ishlatilgan
- [ ] Template'larda `{% load i18n %}` va `{% trans %}` ishlatilgan
- [ ] `language_switcher.html` qo'shilgan
- [ ] `.po` fayllar to'ldirilgan
- [ ] `compilemessages` bajrilgan
- [ ] Migratsiya o'tkazilgan
- [ ] Server ishlamoqda va tillar almashmoqda

---

## 🎉 Tayyor!

Endi saytingiz 3 tilda ishlaydi!

**Test qilish:**
1. `http://localhost:8000/uz/` ochib ko'ring
2. Til almashtirgichdan rus tilini tanlang
3. Sahifa `/ru/` ga o'tadi va rus tilida ko'rsatiladi

**Muammolar bo'lsa:**
- Bu README faylni qayta o'qing
- `setup_multilingual.sh` ni ko'ring
- Terminal da xatolarni diqqat bilan o'qing

---

## 📞 Qo'shimcha Resurslar

- Django i18n docs: https://docs.djangoproject.com/en/stable/topics/i18n/
- Poedit (translation editor): https://poedit.net/
- gettext docs: https://www.gnu.org/software/gettext/

---

**Muallif:** Claude AI  
**Sana:** 2025-11-01  
**Versiya:** 1.0
