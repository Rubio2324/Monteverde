from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    max_intentos_login: int = 5
    bloqueo_minutos: int = 15

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
