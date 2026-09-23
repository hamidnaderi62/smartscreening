from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf.urls.i18n import i18n_patterns
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "smartscreening"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/set-language/', views.set_language, name='set_language'),
    path('', RedirectView.as_view(url='/fa/', permanent=False), name='language_root'),
    path('legacy/', include(('home.urls', 'legacy_home'), namespace='legacy_home')),
]

# New language-neutral application routes. The old suffixed routes above are
# kept temporarily so existing bookmarks and organization links continue to
# work during the migration.
urlpatterns += i18n_patterns(
    path('', include('home.urls', namespace='home')),
    path('account/', include('account.urls', namespace='account')),
    path('my_model/', include('my_model.urls', namespace='my_model')),
    path('cpanel/', include('cpanel.urls', namespace='cpanel')),
    path('followup/', include('followup.urls', namespace='followup')),
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

