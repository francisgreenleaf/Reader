from enum import Enum


class Model(Enum):
    GPT3 = "gpt-3.5-turbo"
    GPT4 = "gpt-4o"
    GPT4_MINI = "gpt-4o-mini"
    LLAMA = "llama-3.1"
    GEMMA = "gemma-2"
    MISTRAL_LARGE = "mistral-large"
    QWEN = "qwen-2"

class IndexModel(Enum):
    VECTOR_STORE = "vector_store"
    SUMMARY_INDEX = "summary_index"
