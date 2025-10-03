#!/usr/bin/env python3.11
import os
import pathway as pw
from pathway.xpacks.llm.question_answering import BaseRAGQuestionAnswerer
from pathway.xpacks.llm.servers import QASummaryRestServer
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.xpacks.llm.llms import OpenAIChat
from pathway.xpacks.llm.embedders import OpenAIEmbedder
from pathway.xpacks.llm.splitters import TokenCountSplitter
from pathway.stdlib.indexing import BruteForceKnnFactory

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

docs = pw.io.fs.read(
    "./json_data/",
    format="binary",
    mode="streaming",
    with_metadata=True
)

embedder = OpenAIEmbedder(model="text-embedding-3-small")
splitter = TokenCountSplitter(max_tokens=400)

doc_store = DocumentStore(
    docs=docs,
    retriever_factory=BruteForceKnnFactory(embedder=embedder, dimensions=1536),
    splitter=splitter
)

llm = OpenAIChat(model="gpt-4o-mini", temperature=0)

question_answerer = BaseRAGQuestionAnswerer(
    llm=llm,
    indexer=doc_store,
    search_topk=3
)

server = QASummaryRestServer(
    host="127.0.0.1",
    port=8080,
    rag_question_answerer=question_answerer
)

if __name__ == "__main__":
    print("Starting Pathway RAG server on http://127.0.0.1:8080")
    print("Query endpoint: POST http://127.0.0.1:8080/v1/pw_ai_answer")
    server.run()
