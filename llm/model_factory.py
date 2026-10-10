from langchain_openai import ChatOpenAI
from config.settings import settings


def get_chat_model() -> ChatOpenAI:
    """Create the configured LangChain chat model. OPENAI_API_KEY is read from env."""
    return ChatOpenAI(
        model=settings.model_name,
        temperature=settings.temperature,
    )
