from enum import Enum

class Model(Enum):
    GPT3 = "gpt-3.5-turbo"
    GPT4 = "gpt-4o"
    GPT4_MINI = "gpt-4o-mini"

class IndexModel(Enum):
    VECTOR_STORE = "vector_store"
    SUMMARY_INDEX = "summary_index"