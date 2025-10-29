import numpy as np
import tensorflow as tf
import cv2
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
import os
import json

from .models import ThyroidDiagnosis

# ============================================================================
# MODEL VA SCALER YUKLASH
# ============================================================================
MODEL_PATH = os.path.join(settings.BASE_DIR, "../thyroid_model", "thyroid_model_full.h5")
SCALE_MEAN_PATH = os.path.join(settings.BASE_DIR, "../thyroid_model", "scaler_mean.npy")
SCALE_SCALE_PATH = os.path.join(settings.BASE_DIR, "../thyroid_model", "scaler_scale.npy")

# Global o'zgaruvchilar
model = None
scaler_mean = None
scaler_scale = None

try:
    print("=" * 70)
    print("🚀 MODEL YUKLASH BOSHLANDI")
    print("=" * 70)

    if os.path.exists(MODEL_PATH):
        try:
            model = tf.keras.models.load_model(MODEL_PATH)
            print(f"✅ Model yuklandi: {MODEL_PATH}")
        except ValueError as ve:
            print(f"⚠️ Model arxitektura xatoligi: {ve}")
            print("🔄 Custom loading orqali yuklashga harakat qilinmoqda...")
            model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            print(f"✅ Model custom loading bilan yuklandi")
    else:
        print(f"❌ Model topilmadi: {MODEL_PATH}")

    if os.path.exists(SCALE_MEAN_PATH):
        scaler_mean = np.load(SCALE_MEAN_PATH)
        print(f"✅ Scaler mean yuklandi: {scaler_mean.shape}")
    else:
        print(f"❌ Scaler mean topilmadi: {SCALE_MEAN_PATH}")

    if os.path.exists(SCALE_SCALE_PATH):
        scaler_scale = np.load(SCALE_SCALE_PATH)
        print(f"✅ Scaler scale yuklandi: {scaler_scale.shape}")
    else:
        print(f"❌ Scaler scale topilmadi: {SCALE_SCALE_PATH}")

    print("=" * 70)
    print()

except Exception as e:
    print(f"❌ Model yuklashda xatolik: {e}")
    import traceback

    print(traceback.format_exc())


# ============================================================================
# RASM QAYTA ISHLASH
# ============================================================================
def preprocess_image(image_path):
    """Rasmni model uchun tayyorlash"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Rasm o'qilmadi: {image_path}")
            return None

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (128, 128))
        img = img / 255.0
        img = np.expand_dims(img, axis=0)

        print(f"✅ Rasm qayta ishlandi: {img.shape}")
        return img

    except Exception as e:
        print(f"❌ Rasm qayta ishlashda xatolik: {e}")
        return None


# ============================================================================
# TAVSIYALAR
# ============================================================================
def get_recommendations(pred_score, tsh, t3, t4, nodule_size):
    """Tavsiyalar"""
    recs = []

    if pred_score > 0.5:
        recs = [
            "🚨 Zudlik bilan onkolog va endokrinolog bilan bog'laning",
            "📋 Biopsiya va CT/MRI tekshiruvlarini o'tkazing",
            "🔬 To'liq gistologik tahlil qildiring",
            "💊 Davolanish rejasini tuzib oling"
        ]
    else:
        recs = [
            "✅ Yaxshi natija, nazoratda bo'ling",
            "📅 6-12 oyda ultratovush o'tkazing",
            "👨‍⚕️ Yillik shifokor ko'rigidan o'ting",
            "🥗 Sog'lom hayot tarzi"
        ]

    if tsh > 4.0:
        recs.append("⚠️ TSH yuqori - Gipotiroidizm")
    elif tsh < 0.4:
        recs.append("⚠️ TSH past - Gipertiroidizm")

    if nodule_size > 2.0:
        recs.append("⚠️ Tugun katta - Biopsiya kerak")

    return recs


# ============================================================================
# VIEWS
# ============================================================================
def home(request):
    """Home page"""
    return render(request, 'home.html')


def diagnose_thyroid(request):
    """Tashxis qo'yish va saqlash"""
    if request.method != 'POST':
        return render(request, 'home.html')

    file_name = None

    try:
        print("\n" + "=" * 70)
        print("🏥 YANGI TASHXIS SO'ROVI")
        print("=" * 70)

        if model is None:
            print("❌ Model yuklanmagan!")
            return JsonResponse({
                'success': False,
                'error': 'Model yuklanmagan. Dasturchi bilan bog\'laning.'
            }, status=500)

        if 'thyroid_image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Ultratovush rasmini yuklang'
            }, status=400)

        uploaded_file = request.FILES['thyroid_image']
        print(f"📁 Fayl: {uploaded_file.name} ({uploaded_file.size} bytes)")

        if uploaded_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'Rasm 5MB dan kichik bo\'lishi kerak'
            }, status=400)

        # Faylni saqlash
        file_name = default_storage.save(
            f'temp/{uploaded_file.name}',
            ContentFile(uploaded_file.read())
        )
        file_path = default_storage.path(file_name)

        # Rasmni qayta ishlash
        processed_image = preprocess_image(file_path)

        if processed_image is None:
            if file_name:
                default_storage.delete(file_name)
            return JsonResponse({
                'success': False,
                'error': 'Rasmni qayta ishlashda xatolik'
            }, status=400)

        # Form ma'lumotlari
        print("\n📝 Ma'lumotlar:")
        age = int(request.POST.get('age', 0))
        gender = request.POST.get('gender', 'Erkak')
        family_history = request.POST.get('family_history') == 'Ha'
        radiation_exposure = request.POST.get('radiation_exposure') == 'Ha'
        iodine_deficiency = request.POST.get('iodine_deficiency') == 'Ha'
        smoking = request.POST.get('smoking') == 'Ha'
        obesity = request.POST.get('obesity') == 'Ha'
        diabetes = request.POST.get('diabetes') == 'Ha'
        tsh_level = float(request.POST.get('tsh_level', 0))
        t3_level = float(request.POST.get('t3_level', 0))
        t4_level = float(request.POST.get('t4_level', 0))
        nodule_size = float(request.POST.get('nodule_size', 0))
        country = int(request.POST.get('country', 0))
        ethnicity = int(request.POST.get('ethnicity', 0))
        notes = request.POST.get('notes', '')

        # Thyroid Cancer Risk hisoblash
        if tsh_level > 4.0 or nodule_size > 2.0:
            thyroid_cancer_risk = 2
        elif tsh_level > 2.5 or nodule_size > 1.5:
            thyroid_cancer_risk = 1
        else:
            thyroid_cancer_risk = 0

        print(f"   Yosh: {age}, TSH: {tsh_level}, Tugun: {nodule_size}, Risk: {thyroid_cancer_risk}")

        # Features
        gender_numeric = 1 if gender == 'Erkak' else 0
        features = np.array([[
            age, gender_numeric, country, ethnicity, int(family_history),
            int(radiation_exposure), int(iodine_deficiency), int(smoking), int(obesity),
            int(diabetes), tsh_level, t3_level, t4_level, nodule_size,
            thyroid_cancer_risk
        ]], dtype=np.float32)

        # Scaling
        if scaler_mean is not None and scaler_scale is not None:
            features_scaled = (features - scaler_mean) / scaler_scale
            print(f"✅ Features scaled")
        else:
            features_scaled = features
            print("⚠️ Scaler topilmadi")

        # Bashorat
        print("\n🔮 Bashorat...")
        print(f"   Rasm shape: {processed_image.shape}")
        print(f"   Features shape: {features_scaled.shape}")

        prediction = model.predict([processed_image, features_scaled], verbose=0)

        # Vaqtinchalik faylni o'chirish
        if file_name:
            default_storage.delete(file_name)

        # Natija
        pred_value = float(prediction[0][0])
        confidence = pred_value * 100 if pred_value > 0.5 else (1 - pred_value) * 100

        print(f"✅ Natija: {pred_value:.4f} ({confidence:.2f}%)")

        if pred_value > 0.5:
            diagnosis = "Malignant (Xavfli)"
            diagnosis_detail = "Saraton xavfi - Shifokorga murojaat qiling!"
            risk_level = "Yuqori"
            diagnosis_class = "danger"
        else:
            diagnosis = "Benign (Xavfsiz)"
            diagnosis_detail = "Yaxshi sifatli - Nazoratda bo'ling"
            risk_level = "Past"
            diagnosis_class = "success"

        recommendations = get_recommendations(pred_value, tsh_level, t3_level, t4_level, nodule_size)

        # ============================================================================
        # DJANGO MODELGA SAQLASH
        # ============================================================================
        diagnosis_record = ThyroidDiagnosis.objects.create(
            # Rasm
            thyroid_image=uploaded_file,
            # Shaxsiy
            age=age,
            gender=gender,
            country=country,
            ethnicity=ethnicity,
            # Tibbiy tarix
            family_history=family_history,
            radiation_exposure=radiation_exposure,
            iodine_deficiency=iodine_deficiency,
            smoking=smoking,
            obesity=obesity,
            diabetes=diabetes,
            # Laboratoriya
            tsh_level=tsh_level,
            t3_level=t3_level,
            t4_level=t4_level,
            nodule_size=nodule_size,
            # Qo'shimcha
            notes=notes,
            # AI natija
            diagnosis=diagnosis,
            diagnosis_detail=diagnosis_detail,
            confidence=confidence,
            risk_level=risk_level,
            diagnosis_class=diagnosis_class,
            prediction_value=pred_value,
            recommendations=recommendations
        )

        print(f"✅ Ma'lumotlar saqlandi: {diagnosis_record.uuid}")
        print("✅ Muvaffaqiyatli!\n")

        # UUID sahifasiga redirect qilish
        from django.shortcuts import redirect
        return redirect('diagnosis_detail', uuid=diagnosis_record.uuid)

    except Exception as e:
        print(f"❌ Xatolik: {e}")
        import traceback
        print(traceback.format_exc())

        if file_name:
            try:
                default_storage.delete(file_name)
            except:
                pass

        return JsonResponse({
            'success': False,
            'error': f'Xatolik: {str(e)}'
        }, status=500)


def diagnosis_detail(request, uuid):
    """Tashxis detali"""
    diagnosis = get_object_or_404(ThyroidDiagnosis, uuid=uuid)

    context = {
        'success': True,
        'uuid': str(diagnosis.uuid),
        'diagnosis': diagnosis.diagnosis,
        'diagnosis_detail': diagnosis.diagnosis_detail,
        'confidence': diagnosis.confidence,
        'risk_level': diagnosis.risk_level,
        'diagnosis_class': diagnosis.diagnosis_class,
        'recommendations': diagnosis.recommendations,
        'patient_data': {
            'age': diagnosis.age,
            'gender': diagnosis.gender,
            'tsh': diagnosis.tsh_level,
            't3': diagnosis.t3_level,
            't4': diagnosis.t4_level,
            'nodule_size': diagnosis.nodule_size
        },
        'created_at': diagnosis.created_at
    }

    return render(request, 'diagnosis_result.html', context)


def download_diagnosis(request, uuid):
    """Tashxisni yuklab olish (PDF)"""
    diagnosis = get_object_or_404(ThyroidDiagnosis, uuid=uuid)

    # Yuklab olish belgilash
    diagnosis.mark_as_downloaded()

    # HTML ni render qilish
    html_string = render_to_string('diagnosis_pdf.html', {
        'diagnosis': diagnosis,
        'patient_data': {
            'age': diagnosis.age,
            'gender': diagnosis.gender,
            'tsh': diagnosis.tsh_level,
            't3': diagnosis.t3_level,
            't4': diagnosis.t4_level,
            'nodule_size': diagnosis.nodule_size
        }
    })

    # PDF yaratish uchun WeasyPrint ishlatiladi (keyin o'rnatish kerak)
    # Hozircha HTML qaytaramiz
    response = HttpResponse(html_string, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="tashxis_{uuid}.html"'

    return response


def diagnosis_list(request):
    """Barcha tashxislar ro'yxati (Admin panel uchun)"""
    diagnoses = ThyroidDiagnosis.objects.all()[:50]
    return render(request, 'diagnosis_list.html', {'diagnoses': diagnoses})