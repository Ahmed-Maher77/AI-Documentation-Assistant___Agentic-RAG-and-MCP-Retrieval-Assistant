"""
Local Vector Store Retriever Tool with Context Quality Evaluation (Corrective RAG Pattern).
Evaluates retrieved context for relevance score, total context length, and query coverage.
"""

import os
from typing import List, Tuple
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

_embeddings = None
_vector_store = None


def get_vector_store() -> Chroma:
    """Lazy loader for HuggingFace embeddings and Chroma vector store."""
    global _embeddings, _vector_store
    if _vector_store is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        _vector_store = Chroma(
            collection_name=os.getenv("PINECONE_INDEX_NAME", "langchain-docs-index"),
            embedding_function=_embeddings,
            persist_directory="./chroma_db",
        )
    return _vector_store


def evaluate_retrieved_docs(query: str, docs_with_scores: List[Tuple]) -> dict:
    """
    Evaluates retrieved chunks based on relevance scores, total context volume,
    and query term coverage.

    Returns an evaluation dictionary with quality status, confidence score, and recommendations.
    """
    if not docs_with_scores:
        return {
            "status": "EMPTY",
            "confidence_score": 0.0,
            "is_sufficient": False,
            "reason": "No vector chunks matched the query in the local index.",
            "recommendation": "Prefer calling `fetch_llms_txt_index` first to check official documentation index. If insufficient or specific search is needed, use `fetch_up_to_date_doc`.",
        }

    # Extract scores
    scores = [score for _, score in docs_with_scores]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    max_score = max(scores) if scores else 0.0

    total_chars = sum(len(doc.page_content) for doc, _ in docs_with_scores)

    # Check query term coverage
    query_terms = [t.lower() for t in query.split() if len(t) > 2]
    combined_text = " ".join(doc.page_content.lower() for doc, _ in docs_with_scores)
    matched_terms = [t for t in query_terms if t in combined_text]
    term_coverage = len(matched_terms) / len(query_terms) if query_terms else 1.0

    # Sufficiency criteria
    is_high_relevance = max_score >= 0.4 or avg_score >= 0.3
    is_sufficient_length = total_chars >= 250
    is_term_covered = term_coverage >= 0.5

    if is_high_relevance and is_sufficient_length and is_term_covered:
        status = "SUFFICIENT"
        confidence = round(min(1.0, max(0.5, max_score * 1.2)), 2)
        recommendation = "Local vector documentation is sufficient."
    elif is_high_relevance or is_sufficient_length:
        status = "PARTIALLY_SUFFICIENT"
        confidence = round(max(0.3, avg_score), 2)
        recommendation = "Local docs may be incomplete. Prefer checking `fetch_llms_txt_index` first, or search/verify with `fetch_up_to_date_doc` if extra details are needed."
    else:
        status = "INSUFFICIENT"
        confidence = round(max(0.1, avg_score), 2)
        recommendation = "Local indexed chunks have low relevance. First use `fetch_llms_txt_index` to check official index; if more information is needed, use `fetch_up_to_date_doc` for live search."

    return {
        "status": status,
        "confidence_score": confidence,
        "is_sufficient": status == "SUFFICIENT",
        "avg_score": round(avg_score, 3),
        "max_score": round(max_score, 3),
        "total_chars": total_chars,
        "term_coverage": f"{len(matched_terms)}/{len(query_terms)}" if query_terms else "N/A",
        "recommendation": recommendation,
    }


@tool
def retrieve_relevant_chunks(user_query: str) -> str:
    """
    Retrieve and evaluate relevant chunks from the local indexed LangChain documentation.
    Includes quality evaluation metadata and actionable recommendations if context is insufficient.
    """
    vector_store = get_vector_store()

    try:
        docs_with_scores = vector_store.similarity_search_with_relevance_scores(user_query, k=5)
    except Exception:
        # Fallback if distance metric is unconfigured
        docs = vector_store.similarity_search(user_query, k=5)
        docs_with_scores = [(doc, 0.5) for doc in docs]

    eval_result = evaluate_retrieved_docs(user_query, docs_with_scores)

    if not docs_with_scores:
        return f"[EVALUATION: {eval_result['status']}]\n{eval_result['reason']}\nRecommendation: {eval_result['recommendation']}"

    chunks = []
    for idx, (doc, score) in enumerate(docs_with_scores, 1):
        source = doc.metadata.get("source", "Unknown")
        chunks.append(f"--- Chunk #{idx} (Relevance Score: {score:.2f}) ---\nSource: {source}\n{doc.page_content}")

    header = (
        f"[RETRIEVAL EVALUATION: {eval_result['status']} | Confidence: {eval_result['confidence_score']*100:.0f}% | "
        f"Query Coverage: {eval_result['term_coverage']}]\n"
        f"Recommendation: {eval_result['recommendation']}\n\n"
    )

    return header + "\n\n".join(chunks)
