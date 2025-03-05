''' Utils function related to document index '''
from typing import Union

from langchain_openai import ChatOpenAI
from llama_index.core import VectorStoreIndex, Document, ServiceContext

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

    # Create service context with selected model
    llm = ChatOpenAI(
        model_name=model,
        temperature=temperature
    )
    service_context = ServiceContext.from_defaults(llm=llm)

    # Create and return index
    return VectorStoreIndex.from_documents(
        [document],
        service_context=service_context
    )
