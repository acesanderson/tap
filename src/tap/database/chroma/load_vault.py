from dbclients.clients.chroma import get_client
from conduit.embeddings.generate_embeddings import generate_embeddings, quick_embedding
from tap.database.vault import Vault
from chromadb.api.models.AsyncCollection import AsyncCollection
import logging

logger = logging.getLogger(__name__)

COLLECTION_NAME = "obsidian_vault"


async def get_vault_collection() -> AsyncCollection:
    client = await get_client()
    return await client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=embedding_function
    )


async def load_vault(vault: Vault) -> AsyncCollection:
    logger.info(f"Loading vault from path: {vault.obsidian_path}")
    client = await get_client()

    # Delete the entire collection if it exists
    try:
        await client.delete_collection(name=COLLECTION_NAME)
        logger.info(f"Deleted existing collection: {COLLECTION_NAME}")
    except Exception:
        pass  # Collection didn't exist, that's fine

    # Create fresh collection
    collection = await client.create_collection(
        name=COLLECTION_NAME, embedding_function=embedding_function
    )

    # Add new data
    documents = vault.documents
    ids = vault.titles
    embeddings = generate_embeddings(ids=ids, documents=documents)

    await collection.add(
        documents=documents,
        ids=ids,
        embeddings=embeddings,
    )

    return collection


def query_collection(query: str, top_k: int = 5):
    """
    Query the vault collection for similar documents.
    """
    import asyncio

    async def _query():
        collection = await get_vault_collection()
        query_embedding = quick_embedding(query)
        results = await collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        return results

    return asyncio.run(_query())


def main():
    import asyncio

    vault = Vault()

    asyncio.run(load_vault(vault))

    # Check the number of items in the collection
    async def check_collection():
        collection = await get_vault_collection()
        count = await collection.count()
        logger.info(f"Number of items in the collection: {count}")

    asyncio.run(check_collection())


if __name__ == "__main__":
    main()
