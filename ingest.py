# ingest.py
import shutil
from pathlib import Path
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR = Path(__file__).resolve().parent / "chroma_db"
shutil.rmtree(CHROMA_DIR, ignore_errors=True)

docs = []

for file_path in Path("raw/").glob("**/*.md"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        docs.append(Document(page_content=content, metadata={"source": str(file_path)}))

for file_path in Path("raw/").glob("**/*.pdf"):
    reader = PdfReader(file_path)
    for page_num, page in enumerate(reader.pages, 1):
        content = page.extract_text()
        docs.append(Document(page_content=content, metadata={"source": str(file_path), "page": page_num}))

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://192.168.66.199:11434")
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=str(CHROMA_DIR))
print(f"Ingested {len(chunks)} chunks")
