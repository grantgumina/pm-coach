from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    JIRA_SERVER: str
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str
    WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 