"""Production settings selected with DJANGO_SETTINGS_MODULE."""

from .settings import *  # noqa: F401,F403


DEBUG = False

if SECRET_KEY == 'dev-only-change-this-secret-key':
    raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set for production.')

if not os.environ.get('DJANGO_ALLOWED_HOSTS'):
    raise ImproperlyConfigured('DJANGO_ALLOWED_HOSTS must contain the public hostname.')

if DATABASE_ENGINE != 'postgresql':
    raise ImproperlyConfigured(
        'Production must use PostgreSQL. Set DJANGO_DB_ENGINE=postgresql.'
    )

if not DATABASES['default']['NAME']:
    raise ImproperlyConfigured('DJANGO_DB_NAME must be set for production.')

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
