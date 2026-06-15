import os


class Settings:
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://statesync:statesync_secret@localhost:5432/gateway_db",
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-secret-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # Ministry service URLs (9 ministries)
    MINISTRY_CIVIL_URL: str = os.getenv("MINISTRY_CIVIL_URL", "http://localhost:8001")
    MINISTRY_EDUCATION_URL: str = os.getenv("MINISTRY_EDUCATION_URL", "http://localhost:8002")
    MINISTRY_DEFENSE_URL: str = os.getenv("MINISTRY_DEFENSE_URL", "http://localhost:8003")
    MINISTRY_HEALTH_URL: str = os.getenv("MINISTRY_HEALTH_URL", "http://localhost:8004")
    MINISTRY_JUSTICE_URL: str = os.getenv("MINISTRY_JUSTICE_URL", "http://localhost:8005")
    MINISTRY_FINANCE_URL: str = os.getenv("MINISTRY_FINANCE_URL", "http://localhost:8006")
    MINISTRY_SOCIAL_URL: str = os.getenv("MINISTRY_SOCIAL_URL", "http://localhost:8007")
    MINISTRY_TRANSPORT_URL: str = os.getenv("MINISTRY_TRANSPORT_URL", "http://localhost:8009")
    MINISTRY_PROPERTY_URL: str = os.getenv("MINISTRY_PROPERTY_URL", "http://localhost:8011")


settings = Settings()
