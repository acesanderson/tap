"""
end user example:

def get_similarity_matches(query, limit=5):
    titles = get_titles()
    matches = vector_search(query, titles, limit)
    print(f"Top {limit} similarity matches for '{query}':")
    for match, score in matches:
        print(f"Match: {match}, Similarity Score: {score}")
"""

from dbclients.clients.chroma import get_client, detect_device

client = get_client()
