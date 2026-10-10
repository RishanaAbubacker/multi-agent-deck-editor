import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    model_name: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0"))
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "3"))
    artifacts_dir: str = os.getenv("ARTIFACTS_DIR", "artifacts")

settings = Settings()
