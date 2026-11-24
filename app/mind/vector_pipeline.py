from .embeddings_provider import embed_text
from .vector_store import add_vector, search_vectors


def index_text(text, user_id=None, session_id=None):
    add_vector(text, embed_text(text), user_id=user_id, session_id=session_id)


def query_similar(text, top_k=5, user_id=None, session_id=None):
    return search_vectors(embed_text(text), top_k, user_id=user_id, session_id=session_id)
