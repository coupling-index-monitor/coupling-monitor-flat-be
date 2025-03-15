import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "Graph Generator"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"

    # MongoDB settings
    MONGO_URI: str = os.getenv("MONGO_URI")
    MONGO_DB: str = os.getenv("MONGO_DB")

    # Neo4j settings
    NEO4J_URI: str = os.getenv("NEO4J_URI")
    NEO4J_USER: str = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD")

    JAEGER_URL: str = os.getenv("JAEGER_URL")

    TRACES_DIR: str = "traces"


settings = Settings()
