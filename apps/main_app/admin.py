from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import ThyroidDiagnosis


@admin.register(ThyroidDiagnosis)
class ThyroidDiagnosisAdmin(admin.ModelAdmin):
    """Qalqonsimon bez tashxisi admin paneli"""

    list_display = [
        'uuid_short',
        'patient_info',
        'image_preview',
        'diagnosis_badge',
        'confidence_badge',
        'risk_badge',
        'download_status',
        'created_at',
        'actions_column'
    ]

    list_filter = [
        'diagnosis_class',
        'gender',
        'is_downloaded',
        'created_at',
        'risk_level',
        'country',
        'ethnicity'
    ]

    search_fields = [
        'uuid',
        'diagnosis',
        'notes'
    ]

    readonly_fields = [
        'uuid',
        'created_at',
        'updated_at',
        'image_display',
        'download_count',
        'last_downloaded_at',
        'detailed_info'
    ]

    fieldsets = (
        (_('Identifikator'), {
            'fields': ('uuid', 'created_at', 'updated_at')
        }),
        (_('Rasm'), {
            'fields': ('thyroid_image', 'image_display')
        }),
        (_('Shaxsiy Ma\'lumotlar'), {
            'fields': ('age', 'gender', 'country', 'ethnicity')
        }),
        (_('Tibbiy Tarix'), {
            'fields': (
                'family_history',
                'radiation_exposure',
                'iodine_deficiency',
                'smoking',
                'obesity',
                'diabetes'
            )
        }),
        (_('Laboratoriya Ko\'rsatkichlari'), {
            'fields': ('tsh_level', 't3_level', 't4_level', 'nodule_size')
        }),
        (_('Qo\'shimcha'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('AI Tashxis'), {
            'fields': (
                'diagnosis',
                'diagnosis_detail',
                'confidence',
                'risk_level',
                'diagnosis_class',
                'prediction_value',
                'recommendations'
            )
        }),
        (_('Yuklab Olish'), {
            'fields': ('is_downloaded', 'download_count', 'last_downloaded_at')
        }),
        (_('Batafsil Ma\'lumot'), {
            'fields': ('detailed_info',),
            'classes': ('collapse',)
        })
    )

    def uuid_short(self, obj):
        """Qisqa UUID"""
        return str(obj.uuid)[:8]

    uuid_short.short_description = _('ID')

    def patient_info(self, obj):
        """Bemor ma'lumotlari"""
        return format_html(
            '<strong>{}</strong><br/>'
            '<small>{} yosh | {}</small>',
            obj.gender,
            obj.age,
            obj.get_ethnicity_display()
        )

    patient_info.short_description = _('Bemor')

    def image_preview(self, obj):
        """Rasm ko'rinishi"""
        if obj.thyroid_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />',
                obj.thyroid_image.url
            )
        return '-'

    image_preview.short_description = _('Rasm')

    def image_display(self, obj):
        """Katta rasm ko'rinishi"""
        if obj.thyroid_image:
            return format_html(
                '<img src="{}" style="max-width: 400px; border-radius: 12px;" />',
                obj.thyroid_image.url
            )
        return '-'

    image_display.short_description = _('Ultratovush Rasmi')

    def diagnosis_badge(self, obj):
        """Tashxis badge"""
        if not obj.diagnosis:
            return format_html('<span style="color: gray;">Kutilmoqda</span>')

        colors = {
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444'
        }
        color = colors.get(obj.diagnosis_class, '#6b7280')

        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.diagnosis
        )

    diagnosis_badge.short_description = _('Tashxis')

    def confidence_badge(self, obj):
        """Ishonch darajasi badge"""
        if obj.confidence is None:
            return '-'

        if obj.confidence >= 80:
            color = '#10b981'
        elif obj.confidence >= 60:
            color = '#f59e0b'
        else:
            color = '#ef4444'

        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{:.1f}%</span>',
            color,
            obj.confidence
        )

    confidence_badge.short_description = _('Ishonch')

    def risk_badge(self, obj):
        """Xavf darajasi badge"""
        if not obj.risk_level:
            return '-'

        colors = {
            'Past': '#10b981',
            "O'rta": '#f59e0b',
            'Yuqori': '#ef4444'
        }
        color = colors.get(obj.risk_level, '#6b7280')

        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.risk_level
        )

    risk_badge.short_description = _('Xavf')

    def download_status(self, obj):
        """Yuklab olish holati"""
        if obj.is_downloaded:
            return format_html(
                '<span style="color: #10b981;">✓ {}x</span>',
                obj.download_count
            )
        return format_html('<span style="color: #6b7280;">-</span>')

    download_status.short_description = _('Yuklab olish')

    def actions_column(self, obj):
        """Harakatlar"""
        detail_url = reverse('diagnosis_detail', kwargs={'uuid': obj.uuid})
        return format_html(
            '<a href="{}" target="_blank" class="button" '
            'style="background: #3b82f6; color: white; padding: 6px 12px; '
            'border-radius: 6px; text-decoration: none; font-size: 12px;">'
            'Ko\'rish</a>',
            detail_url
        )

    actions_column.short_description = _('Harakatlar')

    def detailed_info(self, obj):
        """Batafsil ma'lumot"""
        html = '<div style="background: #f9fafb; padding: 16px; border-radius: 8px;">'

        # Laboratoriya
        html += '<h3 style="margin-top: 0;">Laboratoriya Ko\'rsatkichlari</h3>'
        html += f'<p><strong>TSH:</strong> {obj.tsh_level} mIU/L (Normal: 0.4-4.0)</p>'
        html += f'<p><strong>T3:</strong> {obj.t3_level} ng/dL (Normal: 80-200)</p>'
        html += f'<p><strong>T4:</strong> {obj.t4_level} μg/dL (Normal: 5.0-12.0)</p>'
        html += f'<p><strong>Tugun:</strong> {obj.nodule_size} sm</p>'

        # Tibbiy tarix
        html += '<h3>Tibbiy Tarix</h3>'
        html += f'<p><strong>Oilaviy tarix:</strong> {"Ha" if obj.family_history else "Yo\'q"}</p>'
        html += f'<p><strong>Radiatsiya:</strong> {"Ha" if obj.radiation_exposure else "Yo\'q"}</p>'
        html += f'<p><strong>Yod tanqisligi:</strong> {"Ha" if obj.iodine_deficiency else "Yo\'q"}</p>'
        html += f'<p><strong>Chekish:</strong> {"Ha" if obj.smoking else "Yo\'q"}</p>'
        html += f'<p><strong>Semizlik:</strong> {"Ha" if obj.obesity else "Yo\'q"}</p>'
        html += f'<p><strong>Diabet:</strong> {"Ha" if obj.diabetes else "Yo\'q"}</p>'

        # Tavsiyalar
        if obj.recommendations:
            html += '<h3>Tavsiyalar</h3>'
            html += '<ul>'
            for rec in obj.recommendations:
                html += f'<li>{rec}</li>'
            html += '</ul>'

        html += '</div>'
        return format_html(html)

    detailed_info.short_description = _('Batafsil Ma\'lumot')

    def get_queryset(self, request):
        """Optimizatsiya"""
        qs = super().get_queryset(request)
        return qs.select_related()

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }