from dbclients.clients.chroma import get_client, detect_device
from contex.database.obsidian.vault import Vault
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction,
)
from chromadb.api.models.AsyncCollection import AsyncCollection
from typing import Literal
import logging

logger = logging.getLogger(__name__)

COLLECTION_NAME = "obsidian_vault"

## Configure embedding function
embedding_model: Literal["gtr-t5-large", "all-MiniLM-L6-v2"] = "all-MiniLM-L6-v2"
embedding_function = SentenceTransformerEmbeddingFunction(
    model_name=embedding_model, device=detect_device()
)

## Our vault
vault = Vault()


async def get_vault_descriptions_collection() -> AsyncCollection:
    logger.info(
        f"Using embedding model: {embedding_model} on device: {detect_device()}"
    )
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

    await collection.add(
        documents=documents,
        ids=ids,
    )

    return collection


def main():
    import asyncio

    asyncio.run(load_vault(vault))

    # Check the number of items in the collection
    async def check_collection():
        collection = await get_vault_descriptions_collection()
        count = await collection.count()
        logger.info(f"Number of items in the collection: {count}")

    asyncio.run(check_collection())


if __name__ == "__main__":
    main()
