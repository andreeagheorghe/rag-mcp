# query.py
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://192.168.66.199:11434")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = OllamaLLM(model="qwen2.5:7b", base_url="http://192.168.66.199:11434")

template = """Answer the question based on the provided context:

Context: {context}

Question: {question}

Answer:"""

prompt = ChatPromptTemplate.from_template(template)
qa_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

question = "What is the main topic of these documents?"

# Retrieve and display the context chunks
retrieved_docs = retriever.invoke(question)
print("=" * 80)
print("RETRIEVED CONTEXT CHUNKS:")
print("=" * 80)
for i, doc in enumerate(retrieved_docs, 1):
    print(f"\n--- Chunk {i} ---")
    print(doc.page_content)
    print()

# Generate and display the answer
print("=" * 80)
print("ANSWER:")
print("=" * 80)
result = qa_chain.invoke(question)
print(result)
