from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv


load_dotenv()


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name=os.getenv("PINECONE_INDEX_NAME"),
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)


print(vector_store.get())