from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_aud: str = "authenticated"
    supabase_storage_bucket: str = "documents"

    gemini_api_key: str
    gemini_model: str = "gemini-1.5-flash"
    embedding_model: str = "text-embedding-004"

    chunk_size_words: int = 600
    chunk_overlap_words: int = 75

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
