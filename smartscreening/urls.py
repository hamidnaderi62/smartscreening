from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from . import settings

app_name = "smartscreening"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('account/', include('account.urls', namespace='account')),
    path('my_model/', include('my_model.urls', namespace='my_model')),
    path('ecg/', include('ecg.urls', namespace='ecg')),
    path('pedigree/', include('pedigree.urls', namespace='pedigree')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

