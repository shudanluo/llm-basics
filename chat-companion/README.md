# AI Chat Companion with Long-Term Memory

A command-line chat companion that remembers past conversations across sessions, using vector search to recall relevant context — not just the current conversation window.

## Why this project

This is a personal project, separate from my work (I'm an Analytics Engineer, so this was a deliberate change of pace from business/SaaS-metric topics). The goal was to design and build a small agent end-to-end myself — from architecture decisions to debugging — rather than follow a pre-scripted tutorial.

## How it works

Each turn of conversation (user message + AI reply) is treated as a single unit:

1. **Storage**: After every turn, the turn is embedded (`sentence-transformers`, multilingual model) and stored in ChromaDB, along with a timestamp. Storage happens immediately after each turn rather than batched at the end of a session, so no data is lost if the program is closed abruptly.
2. **Retrieval trigger**: Rather than searching memory on every single message (which would add latency/cost for no benefit on simple exchanges), retrieval is only triggered by keyword rules — e.g. the user says "remember", "before", "last time". If triggered, the most relevant past turns are retrieved via vector similarity search and injected into the prompt as context.
3. **Reply generation**: The user's message (plus retrieved context, if any) is sent to Claude, which generates a reply.
4. **Storage, again**: The new turn (including the reply) is saved back into memory, so it's available for future retrieval.



## Stack

- Claude API (`anthropic`) for the chat model
- `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`) for embeddings
- ChromaDB (persistent, local) for vector storage

## Known limitations (v1)

- **No short-term memory within a session.** Retrieval is keyword-triggered, so if the user references something from a few turns ago *without* using a trigger word, the model won't recall it — even within the same conversation. Verified this directly during testing: asking "who did Xiaohong marry?" right after mentioning "Xiaohong and Xiaoming got married" failed, because no keyword was present to trigger a memory lookup. Planned for v2: maintain a short rolling window of recent turns that's always included in the prompt, independent of the long-term keyword-triggered retrieval.
- **Keyword-based retrieval trigger is brittle.** It only catches explicit references ("remember", "before"), not semantically related follow-ups that don't use those words. A more robust approach (e.g. a relevance-score threshold on every query, or letting the LLM decide whether to look up memory) is a planned upgrade.
- **No topic classification yet.** Each memory is tagged `"unclassified"`; the plan was to have Claude generate a short topic label per turn, not yet implemented.
- **Command-line only.** No web interface or deployment yet — both are planned as later stages (v2: simple web UI; v3: cloud deployment).

## Running it

```bash
pip install anthropic sentence-transformers chromadb
export ANTHROPIC_API_KEY=your_key_here
python memory_test.py
```

Chat normally. To test memory recall, mention something, then later refer back to it using a word like "remember" or "before".