import numpy as np
import tensorflow as tf
from PIL import Image
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings
import json

# Model fayllar joylashuvi
MODEL_PATH = os.path.join(settings.BASE_DIR, '../thyroid_model_full.h5')
MODEL_ARCHITECTURE_PATH = os.path.join(settings.BASE_DIR, '../thyroid_model_architecture.json')
MODEL_WEIGHTS_PATH = os.path.join(settings.BASE_DIR, '../thyroid_model_weights.h5')
SAVED_MODEL_PATH = os.path.join(settings.BASE_DIR, '../thyroid_model_saved')
SCALER_MEAN_PATH = os.path.join(settings.BASE_DIR, '../scaler_mean.npy')
SCALER_SCALE_PATH = os.path.join(settings.BASE_DIR, '../scaler_scale.npy')

# Global o'zgaruvchilar
model = None
scaler_mean = None
scaler_scale = None


def load_thyroid_model():
    """Modelni turli usullar bilan yuklash"""
    global model, scaler_mean, scaler_scale

    try:
        print("=" * 70)
        print("📦 MODEL YUKLANMOQDA...")
        print("=" * 70)

        # Scaler fayllarini yuklash (bu har doim kerak)
        if os.path.exists(SCALER_MEAN_PATH) and os.path.exists(SCALER_SCALE_PATH):
            scaler_mean = np.load(SCALER_MEAN_PATH)
            scaler_scale = np.load(SCALER_SCALE_PATH)
            print(f"✅ Scaler yuklandi: mean shape={scaler_mean.shape}, scale shape={scaler_scale.shape}")
        else:
            print("❌ Scaler fayllari topilmadi!")
            return False

        # USUL 1: SavedModel formatidan yuklash (ENG YAXSHI)
        if os.path.exists(SAVED_MODEL_PATH):
            print(f"\n🔄 Usul 1: SavedModel formatidan yuklash...")
            try:
                model = tf.keras.models.load_model(SAVED_MODEL_PATH)
                print("✅ SavedModel formatidan yuklandi!")
                print_model_info()
                return True
            except Exception as e:
                print(f"❌ SavedModel yuklashda xatolik: {e}")

        # USUL 2: JSON + Weights dan yuklash
        if os.path.exists(MODEL_ARCHITECTURE_PATH) and os.path.exists(MODEL_WEIGHTS_PATH):
            print(f"\n🔄 Usul 2: JSON arxitektura + og'irliklardan yuklash...")
            try:
                # JSON dan arxitekturani yuklash
                with open(MODEL_ARCHITECTURE_PATH, 'r') as json_file:
                    model_json = json_file.read()

                model = tf.keras.models.model_from_json(model_json)
                print("✅ Model arxitekturasi yuklandi")

                # Og'irliklarni yuklash
                model.load_weights(MODEL_WEIGHTS_PATH)
                print("✅ Og'irliklar yuklandi")

                # Kompilatsiya
                model.compile(
                    optimizer='adam',
                    loss='binary_crossentropy',
                    metrics=['accuracy']
                )
                print("✅ Model kompilatsiya qilindi")
                print_model_info()
                return True
            except Exception as e:
                print(f"❌ JSON+Weights yuklashda xatolik: {e}")

        # USUL 3: H5 fayldan yuklash (compile=False bilan)
        if os.path.exists(MODEL_PATH):
            print(f"\n🔄 Usul 3: H5 fayldan yuklash (compile=False)...")
            try:
                model = tf.keras.models.load_model(MODEL_PATH, compile=False)
                print("✅ Model yuklandi (compile=False)")

                # Qayta kompilatsiya
                model.compile(
                    optimizer='adam',
                    loss='binary_crossentropy',
                    metrics=['accuracy']
                )
                print("✅ Model kompilatsiya qilindi")
                print_model_info()
                return True
            except Exception as e:
                print(f"❌ H5 yuklashda xatolik: {e}")
                import traceback
                print(traceback.format_exc())

        print("\n" + "=" * 70)
        print("❌ MODELNI HECH QANDAY USUL BILAN YUKLAB BO'LMADI!")
        print("=" * 70)
        print("\n💡 YECHIM:")
        print("1. Dasturchi bilan bog'laning")
        print("2. Yuqoridagi 'Dasturchi uchun' kodni Colab da bajaring")
        print("3. Quyidagi fayllarni oling:")
        print("   - thyroid_model_saved/ (SavedModel format)")
        print("   - thyroid_model_architecture.json")
        print("   - thyroid_model_weights.h5")
        print("4. Fayllarni loyihangizga qo'ying")
        print("=" * 70)

        return False

    except Exception as e:
        print("=" * 70)
        print(f"❌ KUTILMAGAN XATOLIK: {e}")
        print("=" * 70)
        import traceback
        print(traceback.format_exc())
        return False


def print_model_info():
    """Model haqida ma'lumot chiqarish"""
    if model is None:
        return

    print("\n📊 MODEL MA'LUMOTLARI:")
    print(f"   Inputlar soni: {len(model.inputs)}")
    for i, inp in enumerate(model.inputs):
        print(f"   Input {i + 1}: {inp.name} - Shape: {inp.shape}")
    print(f"   Outputlar soni: {len(model.outputs)}")
    for i, out in enumerate(model.outputs):
        print(f"   Output {i + 1}: {out.name} - Shape: {out.shape}")


# Django serveri ishga tushganda modelni yuklash
print("\n🚀 Django serveri ishga tushmoqda...")
load_success = load_thyroid_model()

if load_success:
    print("\n" + "=" * 70)
    print("✅ TAYYOR! Model muvaffaqiyatli yuklandi!")
    print("=" * 70 + "\n")
else:
    print("\n" + "=" * 70)
    print("⚠️ OGOHLANTIRISH: Model yuklanmadi!")
    print("Tizim ishlaydi, lekin tashxis qila olmaydi.")
    print("=" * 70 + "\n")


def preprocess_image(image_path):
    """Rasmni qayta ishlash"""
    try:
        print(f"🖼️ Rasm qayta ishlanmoqda: {os.path.basename(image_path)}")

        img = Image.open(image_path)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        img = img.resize((224, 224), Image.LANCZOS)
        img_array = np.array(img, dtype=np.float32)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        print(f"✅ Rasm tayyor: {img_array.shape}")
        return img_array

    except Exception as e:
        print(f"❌ Rasm xatoligi: {e}")
        return None


def home(request):
    """Home sahifa"""
    # Model holatini tekshirish
    model_status = {
        'loaded': model is not None,
        'message': 'Model yuklangan va tayyor' if model is not None else 'Model yuklanmagan - Dasturchi bilan bog\'laning'
    }
    return render(request, 'home.html', {'model_status': model_status})


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

        print(f"   Yosh: {age}, TSH: {tsh_level}, Tugun: {nodule_size}")

        # Features
        features = np.array([[
            age, gender, family_history, radiation_exposure,
            iodine_deficiency, smoking, obesity, diabetes,
            tsh_level, t3_level, t4_level, nodule_size,
            country, ethnicity, 0, 0
        ]], dtype=np.float32)

        # Scaling
        if scaler_mean is not None and scaler_scale is not None:
            features_scaled = (features - scaler_mean) / scaler_scale
        else:
            features_scaled = features

        # Bashorat
        print("\n🔮 Bashorat...")
        prediction = model.predict([processed_image, features_scaled], verbose=0)

        # Fayl o'chirish
        if file_name:
            default_storage.delete(file_name)

        # Natija
        pred_value = float(prediction[0][0])
        confidence = pred_value * 100

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