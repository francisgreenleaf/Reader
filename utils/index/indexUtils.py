''' Utils function related to document index '''
from typing import Union
import os

from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

from utils.constants import IndexModel


def create_rag_index(content: str, model: str, indexModel: IndexModel) -> Union[VectorStoreIndex, None]:
    """Create a RAG index based on the content and model type."""
    if indexModel == IndexModel.VECTOR_STORE:
        return _create_vector_store_rag_index(content, model)
    return None


def _create_vector_store_rag_index(content: str, model: str, temperature: float = 0.2) -> VectorStoreIndex:
    """Create a vector store RAG index with the given content and model."""
    # Create a Document object from the content
    document = Document(text=content)

    # Configure the LLM and embeddings using the new Settings API
    Settings.llm = OpenAI(
        model=model,
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Use OpenAI embeddings (text-embedding-ada-002 is the default)
    Settings.embed_model = OpenAIEmbedding(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Create and return index using the new API
    return VectorStoreIndex.from_documents([document])
