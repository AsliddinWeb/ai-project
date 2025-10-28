import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class ThyroidDiagnosis(models.Model):
    """Qalqonsimon bez tashxisi modeli"""

    # UUID asosiy identifikator
    uuid = models.UUIDField(
        _("Identifikator"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    # ============================================================================
    # RASM
    # ============================================================================
    thyroid_image = models.ImageField(
        _("Ultratovush rasmi"),
        upload_to='thyroid_images/%Y/%m/%d/',
        help_text=_("Qalqonsimon bez ultratovush rasmi")
    )

    # ============================================================================
    # SHAXSIY MA'LUMOTLAR
    # ============================================================================
    age = models.PositiveIntegerField(
        _("Yosh"),
        help_text=_("Bemorning yoshi")
    )

    GENDER_CHOICES = [
        ('Erkak', _('Erkak')),
        ('Ayol', _('Ayol')),
    ]
    gender = models.CharField(
        _("Jinsi"),
        max_length=10,
        choices=GENDER_CHOICES
    )

    COUNTRY_CHOICES = [
        (0, _("O'zbekiston")),
        (1, _("Qozog'iston")),
        (2, _("Turkmaniston")),
        (3, _("Tojikiston")),
        (4, _("Qirg'iziston")),
        (5, _("Boshqa")),
    ]
    country = models.IntegerField(
        _("Mamlakat"),
        choices=COUNTRY_CHOICES,
        default=0
    )

    ETHNICITY_CHOICES = [
        (0, _("O'zbek")),
        (1, _("Rus")),
        (2, _("Qozoq")),
        (3, _("Tojik")),
        (4, _("Turkman")),
        (5, _("Boshqa")),
    ]
    ethnicity = models.IntegerField(
        _("Milat"),
        choices=ETHNICITY_CHOICES,
        default=0
    )

    # ============================================================================
    # TIBBIY TARIX
    # ============================================================================
    family_history = models.BooleanField(
        _("Oilaviy kasallik tarixi"),
        default=False,
        help_text=_("Oilada qalqonsimon bez kasalligi bo'lganmi?")
    )

    radiation_exposure = models.BooleanField(
        _("Radiatsiya ta'siri"),
        default=False,
        help_text=_("Radiatsiya ta'siriga uchraganmi?")
    )

    iodine_deficiency = models.BooleanField(
        _("Yod tanqisligi"),
        default=False,
        help_text=_("Yod tanqisligi bormi?")
    )

    smoking = models.BooleanField(
        _("Chekish"),
        default=False,
        help_text=_("Chekadimi?")
    )

    obesity = models.BooleanField(
        _("Semizlik"),
        default=False,
        help_text=_("Semizlik bormi?")
    )

    diabetes = models.BooleanField(
        _("Qandli diabet"),
        default=False,
        help_text=_("Qandli diabet bormi?")
    )

    # ============================================================================
    # LABORATORIYA KO'RSATKICHLARI
    # ============================================================================
    tsh_level = models.FloatField(
        _("TSH darajasi"),
        help_text=_("mIU/L birligida (normal: 0.4-4.0)")
    )

    t3_level = models.FloatField(
        _("T3 darajasi"),
        help_text=_("ng/dL birligida (normal: 80-200)")
    )

    t4_level = models.FloatField(
        _("T4 darajasi"),
        help_text=_("μg/dL birligida (normal: 5.0-12.0)")
    )

    nodule_size = models.FloatField(
        _("Tugun o'lchami"),
        help_text=_("Santimetrda")
    )

    # ============================================================================
    # QO'SHIMCHA MA'LUMOTLAR
    # ============================================================================
    notes = models.TextField(
        _("Qo'shimcha izohlar"),
        blank=True,
        null=True,
        help_text=_("Boshqa muhim ma'lumotlar")
    )

    # ============================================================================
    # AI TASHXIS NATIJALARI
    # ============================================================================
    diagnosis = models.CharField(
        _("Tashxis"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("AI tomonidan berilgan tashxis")
    )

    diagnosis_detail = models.TextField(
        _("Tashxis tafsiloti"),
        blank=True,
        null=True,
        help_text=_("Batafsil tashxis ma'lumoti")
    )

    confidence = models.FloatField(
        _("Ishonch darajasi"),
        blank=True,
        null=True,
        help_text=_("Foizda (0-100)")
    )

    risk_level = models.CharField(
        _("Xavf darajasi"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Past, O'rta, Yuqori")
    )

    DIAGNOSIS_CLASS_CHOICES = [
        ('success', _('Xavfsiz (Benign)')),
        ('warning', _("O'rtacha xavf")),
        ('danger', _('Yuqori xavf (Malignant)')),
    ]
    diagnosis_class = models.CharField(
        _("Tashxis klassi"),
        max_length=20,
        choices=DIAGNOSIS_CLASS_CHOICES,
        blank=True,
        null=True
    )

    prediction_value = models.FloatField(
        _("Model bashorat qiymati"),
        blank=True,
        null=True,
        help_text=_("AI model chiqargan qiymat (0-1)")
    )

    recommendations = models.JSONField(
        _("Tavsiyalar"),
        blank=True,
        null=True,
        help_text=_("Tibbiy tavsiyalar ro'yxati")
    )

    # ============================================================================
    # YUKLAB OLISH VA HOLAT
    # ============================================================================
    is_downloaded = models.BooleanField(
        _("Yuklab olinganmi"),
        default=False,
        help_text=_("Bemor xulosani yuklab olganmi?")
    )

    download_count = models.PositiveIntegerField(
        _("Yuklab olishlar soni"),
        default=0,
        help_text=_("Necha marta yuklab olingan")
    )

    last_downloaded_at = models.DateTimeField(
        _("Oxirgi yuklab olish vaqti"),
        blank=True,
        null=True
    )

    # ============================================================================
    # TIMESTAMPLAR
    # ============================================================================
    created_at = models.DateTimeField(
        _("Yaratilgan vaqti"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _("O'zgartirilgan vaqti"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Qalqonsimon Bez Tashxisi")
        verbose_name_plural = _("Qalqonsimon Bez Tashxislari")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['diagnosis_class']),
            models.Index(fields=['is_downloaded']),
        ]

    def __str__(self):
        return f"{self.age} yoshli {self.gender} - {self.diagnosis or 'Kutilmoqda'} ({self.created_at.strftime('%d.%m.%Y')})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('diagnosis_detail', kwargs={'uuid': self.uuid})

    def mark_as_downloaded(self):
        """Yuklab olingan deb belgilash"""
        from django.utils import timezone
        self.is_downloaded = True
        self.download_count += 1
        self.last_downloaded_at = timezone.now()
        self.save(update_fields=['is_downloaded', 'download_count', 'last_downloaded_at', 'updated_at'])

    @property
    def is_high_risk(self):
        """Yuqori xavfli ekanligini tekshirish"""
        return self.diagnosis_class == 'danger'

    @property
    def formatted_confidence(self):
        """Formatlangan ishonch darajasi"""
        if self.confidence:
            return f"{self.confidence:.1f}%"
        return "N/A"

    @property
    def age_group(self):
        """Yosh guruhi"""
        if self.age < 18:
            return "Voyaga yetmagan"
        elif self.age < 30:
            return "Yosh"
        elif self.age < 50:
            return "O'rta yosh"
        elif self.age < 65:
            return "Keksa"
        else:
            return "Katta yosh"
