# li_ingest.py
import shutil
from pathlib import Path
from llama_index.core import Settings, SimpleDirectoryReader
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
import chromadb

CHROMA_DIR = Path(__file__).resolve().parent.parent / "li_chroma_db"
shutil.rmtree(CHROMA_DIR, ignore_errors=True)

# Initialize embeddings with Ollama
embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://192.168.66.199:11434",
)

Settings.embed_model = embed_model

# Create ChromaDB client
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
chroma_collection = chroma_client.get_or_create_collection("documents")

# Create vector store
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# Create storage context
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load documents from raw/ directory
raw_dir = Path(__file__).resolve().parent.parent / "raw"
reader = SimpleDirectoryReader(
    input_dir=str(raw_dir),
    required_exts=[".pdf", ".md"],
    recursive=True,
)
documents = reader.load_data()

# Create vector index from documents
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
)

print(f"Ingested {len(documents)} documents")