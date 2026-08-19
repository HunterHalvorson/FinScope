from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


def chunk_text(text: str):
  splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
  return splitter.split_text(text)

def embed_text(chunks: list[str]):
  model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
  embeddings = model.encode(chunks)
  return embeddings.tolist()

