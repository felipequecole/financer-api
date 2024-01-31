from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pg_user: str
    pg_password: str
    pg_host: str
    pg_db_name: str

    @computed_field
    @property
    def pg_connect_string(self) -> str:
        return f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}/{self.pg_db_name}"


app_settings = Settings(_env_file='.env')
