## Project 1: Customer Feedback Analysis Pipeline

A two-layer LLM pipeline for analyzing customer feedback at scale:

1. **Classification layer** — reads feedback from CSV, classifies each entry
   (sentiment / topic / urgency) via individual API calls with few-shot
   prompting, writes results to `classified_feedback.csv`
2. **Analysis layer** — aggregates statistics and critical entries
   (negative + high urgency), sends them in a single call to generate a
   management report (`analysis_report.json`) with top issues, anomalies
   and recommended actions

Handles multilingual input (DE/EN/ZH) and malformed responses (try/except
per row — one bad entry doesn't kill the batch).

**Run:** `python batch_classifier.py` (requires `customer_feedback.csv` in
the same folder and `ANTHROPIC_API_KEY` as environment variable)

## Project 2: RAG Q&A System (Microsoft Fabric docs)

Retrieval-augmented generation pipeline over 5 real Microsoft Fabric 
documentation pages (Lakehouse, Direct Lake, Dataflow Gen2, Capacity/
Throttling, REST APIs).

- Chunking with overlap (hand-written sliding window)
- ChromaDB for vector storage and retrieval (local, persistent)
- sentence-transformers for embeddings (multilingual, local, no API cost)
- Claude API for answer generation grounded in retrieved chunks
- System prompt enforces "say I don't know" instead of hallucinating —
  verified with an out-of-scope test question

**Run:** `python rag_test.py`

## Project: Tool-Calling Agent (calculator + Fabric doc search)

An agent that autonomously decides whether a question needs a tool 
(calculator or the RAG search from Project 2), calls the right one, 
and can iterate — observed re-querying search with adjusted terms 
until it gathered enough context (ReAct pattern in action).

- `agent_test.py` — hand-written agent loop using native Anthropic 
  tool-use API (manual state/history management)
- `agent_langgraph.py` — same agent rebuilt with LangGraph, to compare 
  what the framework handles automatically (state accumulation, 
  routing between "think" and "act" steps) vs the hand-written version

**Run:** `python agent_test.py` or `python agent_langgraph.py`