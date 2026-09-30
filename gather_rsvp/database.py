from urllib.parse import parse_qs, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured


def database_config_from_url(database_url, sqlite_path):
    if not database_url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": sqlite_path,
        }

    parsed = urlparse(database_url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ImproperlyConfigured(
            "DATABASE_URL must use the postgres or postgresql scheme."
        )
    database_name = unquote(parsed.path.lstrip("/"))
    if not database_name or not parsed.hostname:
        raise ImproperlyConfigured(
            "DATABASE_URL must include a PostgreSQL host and database name."
        )
    try:
        port = parsed.port
    except ValueError as error:
        raise ImproperlyConfigured("DATABASE_URL has an invalid port.") from error

    query = parse_qs(parsed.query)
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": database_name,
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname,
        "PORT": str(port or ""),
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {
            "sslmode": query.get("sslmode", ["require"])[0],
        },
    }
