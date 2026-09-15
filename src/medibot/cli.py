"""CLI entry point for Nura.

Uses the service layer (``medibot.services``) for ingestion, retrieval, and
RAG.  The streamlit UI and HTTP backend share these same services.
"""

import logging
import sys

from medibot.core.config import settings
from medibot.services.ingestion import chunk_documents, load_pdfs
from medibot.services.rag import build_rag_chain
from medibot.services.retrieval import (
    build_and_save_vectorstore,
    load_vectorstore,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

USAGE = """\
Usage:
  medibot ingest     - Build FAISS index from PDFs in data/
  medibot query      - Interactive CLI query mode
  medibot evaluate   - Run the evaluation suite (see --help)
  medibot web        - Launch Streamlit web interface
"""


def cmd_ingest() -> None:
    """Build the FAISS vector store from PDF source documents."""
    logger.info("Starting ingestion pipeline")
    documents = load_pdfs()
    if not documents:
        logger.error("No PDF documents found in data/")
        sys.exit(1)

    chunks = chunk_documents(documents)
    build_and_save_vectorstore(chunks, settings.FAISS_INDEX_PATH)
    logger.info(
        "Ingestion complete. Index saved to %s",
        settings.FAISS_INDEX_PATH,
    )


def cmd_query() -> None:
    """Run interactive CLI query loop against the RAG chain."""
    vectorstore = load_vectorstore()
    rag_chain = build_rag_chain(vectorstore)

    print("Nura CLI - type 'quit' to exit")
    while True:
        try:
            query = input("Query: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not query or query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        response = rag_chain.invoke({"input": query})
        print(f"\nAnswer: {response['answer']}")
        print("\nSources:")
        for i, doc in enumerate(response["context"], 1):
            snippet = doc.page_content[:200].replace("\n", " ")
            print(f"  [{i}] {snippet}...\n")


def cmd_evaluate() -> None:
    """Run the evaluation suite (retrieval, accuracy, memory, citation, safety)."""
    from medibot.evaluation.runner import main as evaluation_main

    evaluation_main(sys.argv[2:])


def cmd_web() -> None:
    """Launch the Streamlit web interface."""
    import subprocess

    app_path = str(
        __import__("pathlib").Path(__file__).resolve().parent / "app.py"
    )
    logger.info("Launching Streamlit app: %s", app_path)
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], check=True)


def main() -> None:
    """CLI entry point dispatcher."""
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    command = sys.argv[1].lower()

    commands = {
        "ingest": cmd_ingest,
        "query": cmd_query,
        "evaluate": cmd_evaluate,
        "web": cmd_web,
    }

    handler = commands.get(command)
    if handler is None:
        print(f"Unknown command: {command}")
        print(USAGE)
        sys.exit(1)

    handler()


if __name__ == "__main__":
    main()
