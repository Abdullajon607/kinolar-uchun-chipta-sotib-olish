"""
Django settings for the kinolar project.
https://docs.djangoproject.com/en/5.2/topics/settings/
"""

from pathlib import Path
from decouple import Csv, config
from django.urls import reverse_lazy

# Asosiy papka yo'li
BASE_DIR = Path(__file__).resolve().parent.parent

# Xavfsizlik kaliti
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-omj+e!-pzm3420=52!mop^oj*35+7_(ntu5fecwwv$ezw@d_)q",
)

# DIQQAT: Kompyuterda ishlayotganda xatolar ko'rinishi uchun DEBUG=True bo'lishi shart!
DEBUG = config("DEBUG", default=True, cast=bool)

# Ruxsat etilgan domenlar
ALLOWED_HOSTS = list(
    config("ALLOWED_HOSTS", default="127.0.0.1,localhost,*", cast=Csv())
)

# Serverda Admin panel va to'lov qismi ishlashi uchun ruxsat etilgan xavfsiz domenlar
CSRF_TRUSTED_ORIGINS = [
    "https://*.pythonanywhere.com",
    "http://127.0.0.1",
]

# Ilovalar
INSTALLED_APPS = [
    "jazzmin", # Premium dizayn (Har doim eng tepada turadi)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.cinema.apps.CinemaConfig",
    "apps.control.apps.ControlConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # Statik fayllar uchun
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kinolar.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"], # Zamonaviy Path usuliga o'tkazildi
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "kinolar.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Til va vaqt sozlamalari
LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# Statik fayllar (CSS, JS, Rasmlar)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media fayllar (Foydalanuvchi yuklagan fayllar)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Avtorizatsiya manzillari
LOGIN_URL = reverse_lazy("cinema:login")
LOGIN_REDIRECT_URL = reverse_lazy("cinema:home")
LOGOUT_REDIRECT_URL = reverse_lazy("cinema:home")

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600

# Xavfsizlik sozlamalari (Faqat serverda, ya'ni DEBUG=False bo'lganda ishlaydi)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True