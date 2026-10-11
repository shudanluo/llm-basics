# RAG Evaluation Harness

A small evaluation harness for a RAG Q&A bot over Microsoft Fabric documentation (ChromaDB + sentence-transformers + Claude).

## Why this exists

Spot-checking a RAG bot by hand does not scale and is not repeatable. After changing a prompt or a chunk size, there is no way to tell whether the system got better or worse. This harness runs a fixed set of questions against the bot and reports a score.

## How it works

- test_cases: each case has a question and a list of keywords a good answer should contain.
- ask(): the RAG pipeline under test (retrieve chunks from ChromaDB, then answer with Claude).
- check_answer(): scores an answer as the share of expected keywords found (case-insensitive).
- run_eval(): runs all cases, prints the average score, the failed cases, and each answer with the keywords it matched.

## Run it

    pip install anthropic sentence-transformers chromadb
    set ANTHROPIC_API_KEY in your environment
    python rag_test.py     (builds the vector store)
    python eval_rag.py     (runs the evaluation)

## What the evaluation caught

The first run scored 0.17. None of the low scores were simply "the model is bad":

1. Stale index. The vector store held 48 chunks instead of the expected 20, and none of them contained the sentence about Dataflow Gen2 being built on Power Query. The bot correctly answered "I cannot answer this", because that text was never in its context. The cause is most likely leftover entries from earlier ingestion runs. Deleting and rebuilding the store fixed it.
2. Language mismatch. The system prompt was written in Chinese, so answers came back in Chinese while the expected keywords were English. Correct answers scored low. Fixed by using an English prompt and answering in the question's language.
3. Brittle keywords. "throttle" does not match "throttling", and "24-hour" does not match "24 hours". Replaced with stems ("throttl", "24").

After these fixes the score is 1.00 on both cases.

## Limitations

- Only 2 test cases, so 1.00 is a sanity check, not evidence of quality.
- Keywords were loosened after inspecting the answers, which biases the result upward.
- There is no unanswerable test case yet (for example an off-topic question) to check that the bot refuses instead of guessing.
- Keyword matching cannot judge meaning. A correct answer phrased differently can still fail.
- Retrieval quality (precision/recall) is not measured separately from answer quality.

## Planned

LLM-as-judge scoring, more test cases including unanswerable ones, and retrieval-level metrics.
