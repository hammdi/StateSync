import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://statesync:statesync_secret@localhost:5432/education_db",
    )


settings = Settings()
