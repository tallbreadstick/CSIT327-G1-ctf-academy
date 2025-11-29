import environ
from pathlib import Path
import shutil
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
NPM_BIN_PATH = shutil.which('npm')
env = environ.Env()
environ.Env.read_env(BASE_DIR.parent / '.env')

SECRET_KEY = env("SECRET_KEY", default="django-insecure-local-dev-secret")
DEBUG = True  # Force debug on for local troubleshooting of 500 errors
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost', 'ctf-academy.onrender.com'])

# Django requires explicit trusted origins for the CSRF checks when the request
# comes from a different origin (scheme + host), for example when deployed to
# Render with HTTPS. Include the scheme (https://) here. You can override this
# via the CSRF_TRUSTED_ORIGINS env var using comma-separated values.
CSRF_TRUSTED_ORIGINS = env.list(
    'CSRF_TRUSTED_ORIGINS',
    default=['https://ctf-academy.onrender.com']
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'tailwind',
    'django_cotton',
    'theme',
    'accounts',
]

TAILWIND_APP_NAME = 'theme'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'accounts.middleware.RequestTimeoutMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ctf_academy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ctf_academy.wsgi.application'
ASGI_APPLICATION = 'ctf_academy.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST", default="localhost"),
        'PORT': env("DB_PORT", default="5432"),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

DATABASES['default']['CONN_MAX_AGE'] = env.int('DB_CONN_MAX_AGE', default=60)
db_options = DATABASES['default'].setdefault('OPTIONS', {})
db_options['connect_timeout'] = env.int('DB_CONNECT_TIMEOUT', default=5)
statement_timeout = env.int('DB_STATEMENT_TIMEOUT_MS', default=5000)
db_options['options'] = f"-c statement_timeout={statement_timeout}"

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = []
project_static = BASE_DIR / "static"
if project_static.exists():
    STATICFILES_DIRS.append(project_static)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SESSION_COOKIE_AGE = 1800  # Session expires after 30 minutes of inactivity.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Logs user out when they close their browser.
LOGIN_URL = 'login_page' # Redirects to this URL name if a user tries to access a protected page.

default_cache_url = env('CACHE_URL', default='')
if default_cache_url:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': default_cache_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'ctf-academy-cache',
        }
    }

CACHE_TTL = env.int('CACHE_TTL', default=60)
REQUEST_TIMEOUT_SECONDS = env.int('REQUEST_TIMEOUT_SECONDS', default=15)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': env('DRF_ANON_RATE', default='30/min'),
        'user': env('DRF_USER_RATE', default='120/min'),
    },
    'EXCEPTION_HANDLER': 'accounts.api.exception_handler',
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15), # Short for security
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1), # Long-lived for getting new access tokens
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Gemini API Configuration
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")