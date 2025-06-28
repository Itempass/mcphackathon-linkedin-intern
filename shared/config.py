from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Qdrant
    CONTAINERPORT_QDRANT: int = 6333
    EMBEDDING_VECTOR_SIZE: int = 1536

    # MCP Server
    CONTAINERPORT_MCP: int
    BACKEND_BASE_URL: str = "http://localhost:8000"

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"

    # Database Configuration
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str = "db"
    MYSQL_PORT: int = 3306

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'

settings = Settings() 