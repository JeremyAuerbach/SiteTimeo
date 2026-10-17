from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://timeo:timeo@localhost:5432/timeo"

    # Durée de vie d'une session de compte classique.
    session_ttl_hours: int = 24 * 7
    # Un visiteur sans activité pendant ce délai est considéré comme parti :
    # son compte temporaire est supprimé.
    guest_idle_minutes: int = 10
    # Fréquence de la tâche de nettoyage des sessions / visiteurs expirés.
    cleanup_interval_seconds: int = 300

    # Mettre à true derrière HTTPS.
    cookie_secure: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
