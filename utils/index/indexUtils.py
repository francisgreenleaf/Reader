''' Utils function related to document index '''
from typing import Callable, Union

from langchain_openai import ChatOpenAI
from llama_index.core import VectorStoreIndex, Document, ServiceContext

from utils.constants import Model, IndexModel


def create_rag_index(content: str, model: str, indexModel: IndexModel) -> Callable[
    [str, IndexModel, float], Union[VectorStoreIndex]]:
    # Create a Document object from the content
    if indexModel == indexModel.VECTOR_STORE:
        return _create_vector_store_rag_index


def _create_vector_store_rag_index(content: str, model: str, temperature: float) -> Callable[
    [str, IndexModel, float], VectorStoreIndex]:
    # Create a Document object from the content
    document = Document(text=content)

    # Create service context with selected model
    llm = ChatOpenAI(model_name=model, temperature=temperature)
    service_context = ServiceContext.from_defaults(llm=llm)

    # Create index
    index = VectorStoreIndex.from_documents([document], service_context=service_context)

    return index
