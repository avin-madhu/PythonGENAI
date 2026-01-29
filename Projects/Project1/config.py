from pydantic_settings import BaseSettings

"""
 this actually gets the value from the .env and inject into the variables and set 
 the env variables automatically 
"""


class Settings(BaseSettings):
    app_name: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    database_url: str

    class Config:
        env_file = ".env"


# like load_dotenv() now we can use this object to access the env vars
settings = Settings()
