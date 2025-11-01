from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

# Static settings
from django.conf import settings
from django.conf.urls.static import static

# Admin custom
admin.site.site_title = "Admin"
admin.site.site_header = "Tames.Uz"
admin.site.index_title = "Dashboard"

# Til almashtirgich URL (i18n patternsdan tashqarida)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# Ko'p tillik URL'lar
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('apps.main_app.urls')),
    prefix_default_language=True
)

# Static va Media fayllar
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)