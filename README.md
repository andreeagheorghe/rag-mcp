# Ollama RAG + MCP Server: Query Your Docs Locally

## Goal

Build a local RAG pipeline over a small document collection, then expose it through an MCP server so a connected AI client (Claude Desktop) can query it as a tool.

This mirrors the following architecture: licensed data prepared for AI use, served through a controlled, auditable interface.

---

## Architecture Overview

```
Documents (PDF/text)
       |
  [Ingestion Script]
       |
  Chunk + Embed (Ollama embeddings)
       |
  ChromaDB (local vector store)
       |
  [MCP Server]  <-- exposes a `search_documents` tool
       |
  Claude Desktop (MCP client)
```

---

## Part 1: RAG Pipeline

### Stack

- **Ollama** — local LLM and embedding model runner
- **ChromaDB** — local vector store, runs in-process, no server needed
- **LangChain** — orchestration: document loading, chunking, embedding, retrieval
- **Python 3.11+**

### Models to use

- Embeddings: `nomic-embed-text` via Ollama (fast, good quality, runs well on Mac)
- Generation: `qwen2.5:7b` via Ollama

### Steps

**1. Install dependencies**

Libraries needed:
- `langchain-text-splitters` — chunking documents
- `langchain-ollama` — Ollama embeddings and LLM wrappers
- `langchain-chroma` — Chroma vector store integration
- `langchain-core` — shared Document type
- `chromadb` — local vector store engine
- `pypdf` — PDF text extraction

```bash
pip install langchain-text-splitters langchain-ollama langchain-chroma langchain-core chromadb pypdf
ollama pull nomic-embed-text
ollama pull qwen2.5:7b
```

**2. Prepare documents**

Pick 5 to 10 PDFs or Markdown/text files.

Place them in a `raw/` folder.

**3. Ingest and embed (`lc/ingest.py`)**

What the script does, in order:
1. Clear out any existing `lc_chroma_db/` directory so re-running the script doesn't duplicate chunks.
2. Load documents from `raw/`: read `.md` files as plain text, and extract text page-by-page from `.pdf` files, tagging each chunk with its source filename (and page number for PDFs).
3. Split the loaded documents into overlapping chunks (~500 characters, 50 character overlap) so retrieval can return focused excerpts instead of whole documents.
4. Create embeddings for each chunk using the `nomic-embed-text` model via Ollama.
5. Create a vector store: persist the chunks and their embeddings to disk in `lc_chroma_db/` using Chroma.
6. Print how many chunks were ingested.

Always resolve `lc_chroma_db/` to an absolute path (relative to the script's own location), since this script and `mcp_server.py` may be launched from different working directories and must both point at the same store.

**4. Query the RAG pipeline (`lc/query.py`)**

What the script does, in order:
1. Create the same embeddings model (`nomic-embed-text`) used during ingestion — queries and documents must be embedded the same way to be comparable. The embeddings model is used to embed the query.
2. Open the existing vector store from `lc_chroma_db/`.
3. Create a retriever from the vector store that, given a query, returns the top-k (e.g. 3) most similar chunks.
4. Create the generation model: `qwen2.5:7b` via Ollama.
5. Build a chain: retriever fetches context for the question → a prompt template combines the question and retrieved context → the LLM generates an answer → the output is parsed to plain text.
6. Invoke the chain with a question and print the answer.

Run `lc/ingest.py` once to build the vector store, then `lc/query.py` to test retrieval.

---

## Part 2: MCP Server

### Stack

- **MCP Python SDK** — `pip install mcp`
- **ChromaDB** — same vector store built in Part 1
- **Transport** — stdio (simplest for local development, works with Claude Desktop)

### What the server exposes

One tool: `search_documents`

Input: a natural language query string.
Output: the top 3 most relevant document chunks with their source filename and page number.

The MCP server does not call the LLM. It only handles retrieval. The connected AI client (Claude Desktop) does the reasoning over what is returned. This is the correct pattern for auditability and access control.

### Steps

**1. Install MCP SDK**

```bash
pip install mcp
```

**2. Build the server (`mcp_server.py`)**

What the script does, in order:
1. Create a FastMCP server instance named `rag-server`.
2. Create the same embeddings model (`nomic-embed-text`) used during ingestion.
3. Open the existing vector store from `lc_chroma_db/`, resolved to an absolute path relative to the script's own location (Claude Desktop may launch this script from an arbitrary working directory, so a relative path would fail or point at the wrong — possibly read-only — location).
4. Register one tool, `search_documents`, that takes a query string, retrieves the top 3 most similar chunks from the vector store, and returns them formatted with their source filename and page number.
5. Run the server over the `stdio` transport when executed directly, so Claude Desktop can spawn it as a subprocess and communicate over stdin/stdout.

Note: the server does not call the generation LLM (`qwen2.5:7b`). It only handles retrieval — the connected AI client (Claude Desktop) does the reasoning over what is returned.

**3. Connect to Claude Desktop**

Claude Desktop's own config file is at `~/Library/Application Support/Claude/claude_desktop_config.json`. Don't hand-edit a copy elsewhere (e.g. under `~/.claude/`) — that directory belongs to Claude Code, a separate tool, and is not read by Claude Desktop.

The easiest way to reach the correct file: open Claude Desktop → **Settings → Developer → Local MCP servers → Edit Config**. This opens the exact file the app reads, avoiding path mix-ups.

Add an `mcpServers` entry, using the Python interpreter from the project's virtualenv (not a bare `python`, which may not resolve correctly for a GUI-launched process) and an absolute path to `mcp_server.py`:

```json
{
  "mcpServers": {
    "rag-server": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

Restart Claude Desktop, or restart just the server from **Settings → Developer**. The `search_documents` tool will appear and Claude can call it during a conversation.

---

## Milestones

1. Ollama running on local network with `nomic-embed-text` and `qwen2.5:7b` pulled.
2. `ingest.py` runs cleanly and ChromaDB persists to disk.
3. `query.py` returns sensible answers from your documents.
4. `mcp_server.py` starts without errors.
5. Claude Desktop connects and can call `search_documents` interactively.

---

## What to research next

- **Chunking strategy**: try different chunk sizes and overlaps, or a semantic/markdown-aware splitter instead of fixed character length. Does retrieval quality change?
- **Embedding model choice**: swap `nomic-embed-text` for another Ollama embedding model and compare retrieved chunks for the same queries.
- **Retrieval evaluation**: build a small set of test questions with known expected chunks, and measure how often the retriever actually returns them (precision/recall at k).
- **Multiple MCP tools**: add a second tool beyond `search_documents` — e.g. one that lists ingested sources, or one that filters by document/date.
- **Transport options**: `mcp_server.py` currently uses `stdio`. Look into the `streamable-http` transport and what changes to run the server as a standalone process reachable over the network.
- **Re-ranking**: after the initial similarity search, add a re-ranking step (cross-encoder or LLM-based) before returning the top chunks.
- **Incremental ingestion**: right now `ingest.py` wipes and rebuilds the whole store. Explore adding/updating only changed documents using stable chunk IDs.
- **Generation model comparison**: swap `qwen2.5:7b` for other local models and compare answer quality/latency on the same retrieved context.
- **Trade-offs worth documenting**: local inference latency vs. hosted API speed, chunk size vs. retrieval precision, retrieval-only MCP tool vs. one that also calls the LLM.

