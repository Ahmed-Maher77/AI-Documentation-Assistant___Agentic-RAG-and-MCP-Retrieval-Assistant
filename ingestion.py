from dotenv import load_dotenv
import os

from langchain_tavily import TavilyCrawl
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_chroma import Chroma


load_dotenv()


# Get LangChain documentation using TavilyCrawl
def get_langchain_docs():
    crawler = TavilyCrawl(
        api_key=os.getenv("TAVILY_API_KEY")
    )

    response = crawler.invoke(
        {
            "url": "https://docs.langchain.com/",
            "max_depth": 2,
            "max_breadth": 10,
        }
    )

    documents = [
        Document(
            page_content=result["raw_content"],
            metadata={
                "source": result["url"]
            }
        )
        for result in response["results"]
        if result.get("raw_content")
    ]

    return documents


# Split documents into smaller chunks
def split_docs_into_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


# Create embedding model
def embed_docs():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embeddings


# Store embeddings in Pinecone
def store_embeddings_in_vector_db(chunks, embeddings):
    # vector_store = PineconeVectorStore.from_documents(
    #     documents=chunks,
    #     embedding=embeddings,
    #     index_name=os.getenv("PINECONE_INDEX_NAME"),
    # )

    vector_store = Chroma(
        collection_name=os.getenv("PINECONE_INDEX_NAME"),
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )

    return vector_store


# Main ingestion pipeline
def main():
    documents = get_langchain_docs()
    print(f"Crawled documents: {len(documents)}")

    chunks = split_docs_into_chunks(documents)
    print(f"Created chunks: {len(chunks)}")

    embeddings = embed_docs()

    vector_store = store_embeddings_in_vector_db(
        chunks,
        embeddings
    )
    vector_store.add_documents(documents)

    print("Data successfully stored in Chroma!")


if __name__ == "__main__":
    main()