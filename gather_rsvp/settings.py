import os
from pathlib import Path
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured

from .database import database_config_from_url

BASE_DIR = Path(__file__).resolve().parent.parent
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
LOCAL_DEMO_MODE = (
    DEBUG and os.environ.get("DJANGO_LOCAL_DEMO_MODE", "true").lower() == "true"
)
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "insecure-local-prototype-key-do-not-deploy" if DEBUG else "",
)
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost" if DEBUG else ""
    ).split(",")
    if host.strip()
]
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
if RENDER_EXTERNAL_HOSTNAME:
    render_origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)
PUBLIC_BASE_URL = os.environ.get(
    "GATHER_PUBLIC_BASE_URL",
    f"https://{RENDER_EXTERNAL_HOSTNAME}" if RENDER_EXTERNAL_HOSTNAME else "",
).rstrip("/")
_public_url = urlparse(PUBLIC_BASE_URL)
if PUBLIC_BASE_URL and (
    _public_url.scheme != "https"
    or not _public_url.hostname
    or _public_url.username
    or _public_url.password
    or _public_url.query
    or _public_url.fragment
):
    raise ImproperlyConfigured(
        "GATHER_PUBLIC_BASE_URL must be a public HTTPS URL without credentials, query, or fragment."
    )
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN", "").strip()
WHATSAPP_API_VERSION = os.environ.get("WHATSAPP_API_VERSION", "").strip()
WHATSAPP_SEND_INTERVAL = float(os.environ.get("WHATSAPP_SEND_INTERVAL", "0.25"))
if not 0 <= WHATSAPP_SEND_INTERVAL <= 60:
    raise ImproperlyConfigured("WHATSAPP_SEND_INTERVAL must be between 0 and 60 seconds.")
if not DEBUG and (not SECRET_KEY or not ALLOWED_HOSTS):
    raise ImproperlyConfigured(
        "Set DJANGO_SECRET_KEY and DJANGO_ALLOWED_HOSTS before production startup."
    )
if LOCAL_DEMO_MODE and not DEBUG:
    raise ImproperlyConfigured("Local demo mode cannot be enabled outside DEBUG mode.")
if not DEBUG and _public_url.scheme != "https":
    raise ImproperlyConfigured(
        "Set GATHER_PUBLIC_BASE_URL to the public HTTPS site URL before deployment."
    )

BASE_DIR = Path(__file__).resolve().parent.parent
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "guests",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "gather_rsvp.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]
WSGI_APPLICATION = "gather_rsvp.wsgi.application"
ASGI_APPLICATION = "gather_rsvp.asgi.application"
DATABASES = {
    "default": database_config_from_url(
        os.environ.get("DATABASE_URL", "").strip(),
        Path(
            os.environ.get("GATHER_DATABASE_PATH", str(BASE_DIR / "db.sqlite3"))
        ),
    )
}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if not DEBUG
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}
MEDIA_ROOT = Path(
    os.environ.get("GATHER_MEDIA_ROOT", str(BASE_DIR / "media"))
).resolve()
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
