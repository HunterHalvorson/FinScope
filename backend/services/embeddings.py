from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_text(text)


def embed_text(chunks: list[str]):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    embedded = embeddings.embed_documents(chunks)
    return embedded