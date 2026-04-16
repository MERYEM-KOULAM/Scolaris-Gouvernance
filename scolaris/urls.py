from django.contrib import admin
from django.urls import path, include
from django.conf import settings               # <--- Important
from django.conf.urls.static import static     # <--- Important
from core.views import home_redirect
from scolarite import views as scolarite_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('professeur/', include('academique.urls')),
    path('rh/', include('rh.urls')),
    path('scolarite/', include('scolarite.urls')),
    path('candidature/', scolarite_views.page_candidature, name='candidature'),
    path('candidature-succes/', scolarite_views.candidature_succes, name='candidature_succes'),
    path('', home_redirect, name='home'),
]

# C'est ce bloc qui permet d'afficher les images et les supports
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)