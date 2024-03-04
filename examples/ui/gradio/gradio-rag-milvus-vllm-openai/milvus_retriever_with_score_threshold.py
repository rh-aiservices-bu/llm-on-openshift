"""Milvus Retriever with Score Threshold"""
import warnings
from typing import Any, Dict, List, Optional

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.pydantic_v1 import root_validator
from langchain_community.vectorstores import Milvus
from langchain_core.retrievers import BaseRetriever

from langchain_community.vectorstores.milvus import Milvus

class MilvusRetrieverWithScoreThreshold(BaseRetriever):
    """`Milvus API` retriever."""

    embedding_function: Embeddings
    collection_name: str = "LangChainCollection"
    collection_description: str = ""
    collection_properties: Optional[Dict[str, Any]] = None
    connection_args: Optional[Dict[str, Any]] = None
    consistency_level: str = "Session"
    search_params: Optional[dict] = None
    k: int = 4
    score_threshold: float = 0.99
    metadata_field: str = "metadata"
    text_field: str = "page_content"

    store: Milvus
    retriever: BaseRetriever

    @root_validator(pre=True)
    def create_retriever(cls, values: Dict) -> Dict:
        """Create the Milvus store and retriever."""
        values["store"] = Milvus(
            embedding_function=values["embedding_function"],
            collection_name=values["collection_name"],
            collection_description=values["collection_description"],
            collection_properties=values["collection_properties"],
            connection_args=values["connection_args"],
            consistency_level=values["consistency_level"],
            metadata_field="metadata",
            text_field="page_content"
        )
        values["retriever"] = values["store"].as_retriever(
            search_kwargs={"param": values["search_params"]}
        )
        return values

    def add_texts(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> None:
        """Add text to the Milvus store

        Args:
            texts (List[str]): The text
            metadatas (List[dict]): Metadata dicts, must line up with existing store
        """
        self.store.add_texts(texts, metadatas)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        **kwargs: Any,
    ) -> List[Document]:
        docs_and_scores = self.store.similarity_search_with_score(query, k=self.k, return_metadata=True)
        docs_and_scores = [(doc, score) for doc, score in docs_and_scores if score < self.score_threshold]
        for doc, score in docs_and_scores:
            doc.metadata = {**doc.metadata, **{"score": score}}
        return [doc for (doc, _) in docs_and_scores]
