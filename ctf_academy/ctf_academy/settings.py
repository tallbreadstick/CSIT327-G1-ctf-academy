"""
Django settings for ctf_academy project.
"""

import environ
from pathlib import Path
import shutil

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# nodejs package manager
NPM_BIN_PATH = shutil.which('npm')

# Initialize environment reader
env = environ.Env()
# The project's top-level .env lives one directory above BASE_DIR
# (BASE_DIR points at the inner `ctf_academy` package). Use that
# location so variables defined at the repo root are discovered.
environ.Env.read_env(BASE_DIR.parent / '.env')

# Quick-start development settings - unsuitable for production
# Try to read SECRET_KEY from environment/.env. If it's missing (e.g. .env
# not loaded), provide a clearly-marked insecure fallback for local dev so
# the dev server can run. Do NOT use this fallback in production.
SECRET_KEY = env("SECRET_KEY", default="django-insecure-local-dev-secret")
DEBUG = env.bool('DEBUG', default=False)
# Read ALLOWED_HOSTS as a list. Provide a safe development default so
# missing env entries won't crash local startup.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'tailwind',
    'theme',
    'accounts',
]

TAILWIND_APP_NAME = 'theme'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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


# Database (PostgreSQL with psycopg2)
# Uses environment variables from .env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST", default="localhost"),
        'PORT': env("DB_PORT", default="5432"),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Strong password hashing using Argon2
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Strongest, preferred
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files
STATIC_URL = 'static/'

# Optionally include a project-level `static/` directory if it exists.
# Per-app static directories (e.g. `theme/static/...`) are discovered
# automatically by Django so this is only for a top-level static folder.
STATICFILES_DIRS = []
project_static = BASE_DIR / "static"
if project_static.exists():
    STATICFILES_DIRS.append(project_static)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'