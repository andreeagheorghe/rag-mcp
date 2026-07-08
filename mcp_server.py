# mcp_server.py
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

mcp = FastMCP("rag-server")

CHROMA_DIR = Path(__file__).resolve().parent / "chroma_db"

embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://192.168.66.199:11434")
vectorstore = Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings)


@mcp.tool()
def search_documents(query: str) -> str:
    """Search the local document collection and return relevant excerpts."""

    results = vectorstore.similarity_search(query, k=3)
    output = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "")
        output.append(f"[{i}] Source: {source} (page {page})\n{doc.page_content}")
    return "\n\n".join(output)


if __name__ == "__main__":
    mcp.run(transport="stdio")
