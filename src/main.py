from loguru import logger
from src.retriever import Retriever

if __name__ == "__main__":

    retriever = Retriever()
    logger.info("Retriever initialized.")

    print("\n--- Testing Search ---")
    query = "What was the latest revenue for Tronox?"
    results = retriever.search(query)

    if results:
        print(f"Found {len(results)} results for query: '{query}'")
        for res in results:
            print(f"  - Doc ID: {res.doc_id}")
            print(f"    Metadata: {res.metadata}")
            print(f"    Content: {res.content[:100]}...")
    else:
        print("No results found.")