from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "opencheiron"


settings = Settings()
