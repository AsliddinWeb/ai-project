import numpy as np
import tensorflow as tf
import cv2
from PIL import Image
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings
import json

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

    # Model yuklash (compile=False - arxitektura xatoligini e'tiborsiz qoldirish)
    if os.path.exists(MODEL_PATH):
        try:
            # Avval oddiy usulda yuklashga harakat
            model = tf.keras.models.load_model(MODEL_PATH)
            print(f"✅ Model yuklandi: {MODEL_PATH}")
        except ValueError as ve:
            print(f"⚠️ Model arxitektura xatoligi: {ve}")
            print("🔄 Custom loading orqali yuklashga harakat qilinmoqda...")

            # Custom loading - compile=False
            model = tf.keras.models.load_model(MODEL_PATH, compile=False)

            # Modelni qayta compile qilish
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            print(f"✅ Model custom loading bilan yuklandi")
    else:
        print(f"❌ Model topilmadi: {MODEL_PATH}")

    # Scaler yuklash
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
# RASM QAYTA ISHLASH FUNKSIYASI
# ============================================================================
def preprocess_image(image_path):
    """
    Rasmni model uchun tayyorlash (RGB formatda - model 3 kanal kutadi)
    """
    try:
        # OpenCV bilan o'qish (BGR formatda)
        img = cv2.imread(image_path)

        if img is None:
            print(f"❌ Rasm o'qilmadi: {image_path}")
            return None

        # BGR -> RGB konvertatsiya
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # 128x128 ga o'zgartirish (model 128x128 bilan o'rgatilgan)
        img = cv2.resize(img, (128, 128))

        # Normalizatsiya [0, 1]
        img = img / 255.0

        # Batch dimension qo'shish (1, 224, 224, 3)
        img = np.expand_dims(img, axis=0)

        print(f"✅ Rasm qayta ishlandi: {img.shape}")
        return img

    except Exception as e:
        print(f"❌ Rasm qayta ishlashda xatolik: {e}")
        return None


# ============================================================================
# VIEWS
# ============================================================================
def home(request):
    """Home page"""
    return render(request, 'home.html')


def diagnose_thyroid(request):
    """Tashxis qo'yish"""
    if request.method != 'POST':
        return render(request, 'home.html')

    file_name = None

    try:
        print("\n" + "=" * 70)
        print("🏥 YANGI TASHXIS SO'ROVI")
        print("=" * 70)

        # Model tekshiruvi
        if model is None:
            print("❌ Model yuklanmagan!")
            return JsonResponse({
                'success': False,
                'error': 'Model yuklanmagan. Dasturchi bilan bog\'laning va to\'g\'ri model fayllarini oling.'
            }, status=500)

        # Rasm tekshiruvi
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

        # Rasmni qayta ishlash (RGB formatda)
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
        age = float(request.POST.get('age', 0))
        gender = 1 if request.POST.get('gender') == 'Erkak' else 0
        family_history = 1 if request.POST.get('family_history') == 'Ha' else 0
        radiation_exposure = 1 if request.POST.get('radiation_exposure') == 'Ha' else 0
        iodine_deficiency = 1 if request.POST.get('iodine_deficiency') == 'Ha' else 0
        smoking = 1 if request.POST.get('smoking') == 'Ha' else 0
        obesity = 1 if request.POST.get('obesity') == 'Ha' else 0
        diabetes = 1 if request.POST.get('diabetes') == 'Ha' else 0
        tsh_level = float(request.POST.get('tsh_level', 0))
        t3_level = float(request.POST.get('t3_level', 0))
        t4_level = float(request.POST.get('t4_level', 0))
        nodule_size = float(request.POST.get('nodule_size', 0))
        country = int(request.POST.get('country', 0))
        ethnicity = int(request.POST.get('ethnicity', 0))

        # Thyroid Cancer Risk hisoblash (TSH va nodule size asosida)
        if tsh_level > 4.0 or nodule_size > 2.0:
            thyroid_cancer_risk = 2  # High
        elif tsh_level > 2.5 or nodule_size > 1.5:
            thyroid_cancer_risk = 1  # Medium
        else:
            thyroid_cancer_risk = 0  # Low

        print(f"   Yosh: {age}, TSH: {tsh_level}, Tugun: {nodule_size}, Risk: {thyroid_cancer_risk}")

        # Features (15 xususiyat - scaler bilan mos)
        # Tartib: Age, Gender, Country, Ethnicity, Family_History, Radiation_Exposure,
        #         Iodine_Deficiency, Smoking, Obesity, Diabetes, TSH, T3, T4, Nodule_Size, Cancer_Risk
        features = np.array([[
            age, gender, country, ethnicity, family_history,
            radiation_exposure, iodine_deficiency, smoking, obesity,
            diabetes, tsh_level, t3_level, t4_level, nodule_size,
            thyroid_cancer_risk
        ]], dtype=np.float32)

        # Scaling
        if scaler_mean is not None and scaler_scale is not None:
            features_scaled = (features - scaler_mean) / scaler_scale
            print(f"✅ Features scaled")
        else:
            features_scaled = features
            print("⚠️ Scaler topilmadi, scaling bajarilmadi")

        # Bashorat
        print("\n🔮 Bashorat...")
        print(f"   Rasm shape: {processed_image.shape}")
        print(f"   Features shape: {features_scaled.shape}")

        prediction = model.predict([processed_image, features_scaled], verbose=0)

        # Fayl o'chirish
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

        context = {
            'success': True,
            'diagnosis': diagnosis,
            'diagnosis_detail': diagnosis_detail,
            'confidence': round(confidence, 2),
            'risk_level': risk_level,
            'diagnosis_class': diagnosis_class,
            'recommendations': recommendations,
            'patient_data': {
                'age': int(age),
                'gender': 'Erkak' if gender else 'Ayol',
                'tsh': tsh_level,
                't3': t3_level,
                't4': t4_level,
                'nodule_size': nodule_size
            }
        }

        print("✅ Muvaffaqiyatli!\n")
        return render(request, 'diagnosis_result.html', context)

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