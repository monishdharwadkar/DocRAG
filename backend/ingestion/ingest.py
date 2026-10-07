import os
import glob
import argparse
from app.vectorstore.qdrant_client import get_qdrant_store
from ingestion.chunker import MarkdownChunker
from ingestion.embedder import get_embedder

def run_ingestion(docs_dir: str):
    print(f"[*] Starting ingestion from directory: {docs_dir}")
    if not os.path.exists(docs_dir):
        print(f"[!] Directory {docs_dir} does not exist.")
        return

    pattern = os.path.join(docs_dir, "**", "*.md")
    files = glob.glob(pattern, recursive=True)
    if not files:
        # Fallback to direct path search
        files = [os.path.join(docs_dir, f) for f in os.listdir(docs_dir) if f.endswith(".md")]

    print(f"[*] Found {len(files)} markdown documents to process.")

    chunker = MarkdownChunker(chunk_size=600, chunk_overlap=100)
    embedder = get_embedder()
    vectorstore = get_qdrant_store()

    all_chunks = []
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        rel_path = os.path.relpath(file_path, start=os.path.dirname(docs_dir) or ".")
        chunks = chunker.split_text(content, source_path=rel_path)
        all_chunks.extend(chunks)

    print(f"[*] Total chunks created: {len(all_chunks)}")
    if not all_chunks:
        return

    # Extract texts and batch embed
    texts = [f"Heading: {c['heading']}\n{c['text']}" for c in all_chunks]
    print("[*] Generating embeddings...")
    vectors = embedder.encode(texts)

    # Prepare Qdrant payloads
    ids = [c["chunk_id"] for c in all_chunks]
    payloads = [
        {
            "chunk_id": c["chunk_id"],
            "source_path": c["source_path"],
            "heading": c["heading"],
            "text": c["text"]
        }
        for c in all_chunks
    ]

    print("[*] Upserting vectors into Qdrant...")
    vectorstore.upsert_chunks(ids=ids, vectors=vectors, payloads=payloads)
    print(f"[+] Ingestion complete! Successfully indexed {len(all_chunks)} chunks into Qdrant.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documentation into DocRAG vector database.")
    parser.add_argument("--docs-dir", type=str, default="../docs_sample", help="Path to markdown documentation directory.")
    args = parser.parse_args()
    run_ingestion(args.docs_dir)
