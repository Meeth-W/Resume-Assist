from langchain.vectorstores.chroma import Chroma
from utils import get_embedding_function, split_documents, load_documents_from_directory
from langchain.schema import Document
from typing import List

CHROMA_PATH = "chroma"

class ChromaDB:
    def __init__(self, persist_directory: str = CHROMA_PATH, embedding_model: str = "amazon.titan-embed-text-v1"):
        self.persist_directory = persist_directory
        self.embedding_function = get_embedding_function(model_name=embedding_model)
        self.vectorstore = Chroma(persist_directory=self.persist_directory, embedding_function=self.embedding_function)

    def add_documents(self, documents: List[Document]):
        """Add documents to the Chroma vector store."""
        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()

    def query(self, query_text: str, top_k: int = 5) -> List[Document]:
        """Query the vector store and return top_k similar documents."""
        results = self.vectorstore.similarity_search(query_text, k=top_k)
        return results

    def clear(self):
        """Clear the entire vector store."""
        self.vectorstore.delete_collection()