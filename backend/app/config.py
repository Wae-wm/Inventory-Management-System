from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "inventory_db"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self) -> str:
        # quote_plus ป้องกันปัญหาเมื่อรหัสผ่านมีอักขระพิเศษ เช่น @ หรือ /
        password = quote_plus(self.db_password)
        return (
            f"mysql+pymysql://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
