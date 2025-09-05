from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from typing import List, Optional

DATA_DIR = "data"

def load_documents_from_directory(directory_path: str = DATA_DIR, file_types: List[str] = None) -> List[Document]:
    """Load documents from a specified directory using LangChain's DirectoryLoader."""
    loader = DirectoryLoader(directory_path, glob = file_types)
    documents = loader.load()
    return documents

def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """Split documents into smaller chunks using RecursiveCharacterTextSplitter."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True)
    chunks = text_splitter.split_documents(documents)
    return chunks

# TODO: Swap over to ollame or hugging face embeddings in the future.
def get_embedding_function(model_name: str = "amazon.titan-embed-text-v1") -> BedrockEmbeddings:
    """Get the Bedrock embedding function."""
    embeddings = BedrockEmbeddings(model_name=model_name, region_name="us-east-1")
    return embeddings

