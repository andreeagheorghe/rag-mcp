# Open WebUI

## What it is

Open WebUI is a self-hosted, browser-based interface for interacting with large language models. It looks and feels like ChatGPT but runs entirely on your own infrastructure. It does not run models itself. It connects to whatever model backend you point it at, Ollama, OpenAI-compatible APIs, Anthropic, or any other provider.

## Who builds it

Created and led by Tim J. Baek. Open source, MIT licensed, hosted at github.com/open-webui/open-webui. As of mid-2026 the repository has over 144,000 GitHub stars, making it one of the most widely adopted local AI interface projects.

## What it is for

The core use case is giving you a private, provider-agnostic chat interface where your data does not leave your own machines. You run it on your own server or laptop, connect it to a local Ollama instance or any OpenAI-compatible endpoint, and use it like any commercial chat product.

Beyond basic chat it supports:

- RAG (Retrieval-Augmented Generation): upload documents, build knowledge bases, and let the model retrieve relevant content before answering.
- Tool and MCP integration: connect external services via MCP servers or OpenAPI specs. The project also maintains `mcpo`, a separate tool that wraps any MCP server as an OpenAPI endpoint.
- Multi-user access control: roles, user groups, per-model access permissions, SSO integration.
- Python pipelines: write custom functions that filter, transform, or route messages.
- Voice, image generation, web search, and code execution within the chat interface.

## Relevance to the RAG + MCP project

Open WebUI can serve as a testing interface for your Ollama models while you build the RAG pipeline and MCP server separately. It also has its own built-in RAG support, which is worth understanding conceptually even if the project uses a custom Python pipeline instead.

The `mcpo` project (github.com/open-webui/mcpo) is also worth noting: it is a proxy that exposes MCP servers as OpenAPI endpoints, which would allow Open WebUI itself to call your MCP server as a tool.

## Key facts

- License: MIT
- Install: Docker (recommended), pip, or Kubernetes
- Default port: 8080 internally, commonly mapped to 3000 externally
- Downloads: 353 million as of mid-2026 per the project website
- Enterprise tier available with SLA, audit logs, and long-term support versions
