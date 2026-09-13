import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


# --- Core -------------------------------------------------------------------

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-communityboard-dev-key")
DEBUG = _env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS", ["*"])

# --- Applications ------------------------------------------------------------

# No django.contrib.admin/sessions/messages: this is a JSON API authenticated
# purely via JWT (see accounts.authentication.JWTAuthentication), so the
# session/admin stack is intentionally left out rather than half-wired.
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "accounts",
    "categories",
    "posts",
    "comments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "communityboard.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ],
        },
    },
]

WSGI_APPLICATION = "communityboard.wsgi.application"
ASGI_APPLICATION = "communityboard.asgi.application"

# --- Database -----------------------------------------------------------------
# CommunityBoard is PostgreSQL-only; see README.md for the schema.

DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/communityboard"),
        conn_max_age=600,
    )
}

# --- Auth ----------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

# --- DRF -------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "UNAUTHENTICATED_USER": "django.contrib.auth.models.AnonymousUser",
}

# --- JWT ---------------------------------------------------------------------
# Mirrors the original Spring/FastAPI service: HS256, "sub" = email, "role" claim.

JWT_SECRET = os.getenv("JWT_SECRET", "communityboard-secret-key-amalitech-2024")
JWT_EXPIRATION_MS = int(os.getenv("JWT_EXPIRATION_MS", 86400000))  # 24h

# --- CORS ----------------------------------------------------------------------
# Defaults to allow-all to match the original SecurityConfig CorsConfiguration bean.
# Set CORS_ALLOWED_ORIGINS (comma-separated) in production to restrict this.

_cors_origins = os.getenv("CORS_ALLOWED_ORIGINS")
if _cors_origins:
    CORS_ALLOWED_ORIGINS = _env_list("CORS_ALLOWED_ORIGINS", [])
else:
    CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["*"]

# --- I18N / static -------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
