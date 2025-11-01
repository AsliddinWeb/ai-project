#!/bin/bash

# ============================================================================
# DJANGO KO'P TILLIK - QISQA BUYRUQLAR
# ============================================================================

echo "🌍 Django Ko'p Tillik - Tezkor O'rnatish"
echo ""

# 1. Locale yaratish
echo "1️⃣ Locale papkasini yaratish..."
mkdir -p locale
echo "✅ Tayyor"
echo ""

# 2. Fayllarni almashtirish
echo "2️⃣ Fayllarni almashtirish (qo'lda bajaring):"
echo "   cp base.py config/settings/base.py"
echo "   cp urls.py config/urls.py"
echo "   cp models_translated.py apps/main_app/models.py"
echo ""

# 3. Template uchun papka
echo "3️⃣ Components papkasini yaratish..."
mkdir -p templates/components
echo "   cp language_switcher.html templates/components/"
echo "✅ Tayyor"
echo ""

# 4. Tarjima fayllarini yaratish
echo "4️⃣ Tarjima fayllarini yaratish..."
echo "   python manage.py makemessages -l uz --ignore=venv"
echo "   python manage.py makemessages -l ru --ignore=venv"
echo "   python manage.py makemessages -l en --ignore=venv"
echo ""

# 5. Tayyor tarjimalarni ko'chirish
echo "5️⃣ Tayyor tarjimalarni ko'chirish..."
echo "   mkdir -p locale/uz/LC_MESSAGES"
echo "   mkdir -p locale/ru/LC_MESSAGES"
echo "   mkdir -p locale/en/LC_MESSAGES"
echo "   cp django_uz.po locale/uz/LC_MESSAGES/django.po"
echo "   cp django_ru.po locale/ru/LC_MESSAGES/django.po"
echo "   cp django_en.po locale/en/LC_MESSAGES/django.po"
echo ""

# 6. Kompilyatsiya
echo "6️⃣ Tarjimalarni kompilyatsiya qilish..."
echo "   python manage.py compilemessages"
echo ""

# 7. Migratsiya
echo "7️⃣ Bazani yangilash..."
echo "   python manage.py makemigrations"
echo "   python manage.py migrate"
echo ""

# 8. Server
echo "8️⃣ Serverni ishga tushurish..."
echo "   python manage.py runserver"
echo ""

echo "======================================================================"
echo "✅ BITTA BUYRUQ BILAN (COPY-PASTE QILING):"
echo "======================================================================"
echo ""
cat << 'EOF'
mkdir -p locale templates/components locale/uz/LC_MESSAGES locale/ru/LC_MESSAGES locale/en/LC_MESSAGES && \
cp base.py config/settings/base.py && \
cp urls.py config/urls.py && \
cp models_translated.py apps/main_app/models.py && \
cp language_switcher.html templates/components/ && \
cp django_uz.po locale/uz/LC_MESSAGES/django.po && \
cp django_ru.po locale/ru/LC_MESSAGES/django.po && \
cp django_en.po locale/en/LC_MESSAGES/django.po && \
python manage.py compilemessages && \
python manage.py makemigrations && \
python manage.py migrate && \
echo "✅ Hammasi tayyor! Endi 'python manage.py runserver' buyrug'ini bering"
EOF

echo ""
echo "======================================================================"
echo "🔗 URL MANZILLAR:"
echo "======================================================================"
echo ""
echo "http://localhost:8000/uz/        → O'zbekcha"
echo "http://localhost:8000/ru/        → Русский"
echo "http://localhost:8000/en/        → English"
echo ""

echo "======================================================================"
echo "📝 TEMPLATE'DA ISHLATISH:"
echo "======================================================================"
echo ""
cat << 'EOF'
{% load i18n %}

<h1>{% trans "Sarlavha" %}</h1>
<p>{% trans "Matn" %}</p>

{% blocktrans with name=user.name %}
    Salom, {{ name }}!
{% endblocktrans %}
EOF

echo ""
echo "======================================================================"
echo "🐍 VIEWS.PY DA ISHLATISH:"
echo "======================================================================"
echo ""
cat << 'EOF'
from django.utils.translation import gettext as _

def my_view(request):
    message = _("Bu tarjima qilinadi")
    return render(request, 'template.html', {'message': message})
EOF

echo ""
echo "======================================================================"
echo "⚠️ HAR SAFAR YANGI MATN QO'SHSANGIZ:"
echo "======================================================================"
echo ""
echo "python manage.py makemessages -a --ignore=venv"
echo "# .po fayllarni tahrirlang"
echo "python manage.py compilemessages"
echo ""

echo "======================================================================"
echo "📖 To'liq qo'llanma: README_MULTILINGUAL.md"
echo "======================================================================"
