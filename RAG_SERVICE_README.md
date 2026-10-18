# RAG Q&A Service (FastAPI + Docker)

Wraps the Fabric-docs RAG bot as an HTTP service and packages it as a Docker image.

## What it does

POST /ask with {"question": "..."} returns {"answer": "..."}.

## Run

    docker build -t rag-api .
    docker run --rm -p 8001:8000 -e ANTHROPIC_API_KEY rag-api

Then open http://127.0.0.1:8001/docs and try the /ask endpoint.

## Design decisions

- The vector index is built at image build time (RUN python rag_test.py) from documents.py. This avoids stale data: an earlier evaluation found a local store with 48 chunks instead of the expected 20, caused by leftover entries from old ingestion runs.
- CPU-only torch is installed first to keep the image smaller.
- The API key is passed at runtime through an environment variable and is never baked into the image.
- The embedding model is loaded once at startup, not per request.
- uvicorn runs with --host 0.0.0.0 so the port mapping works from outside the container.

## Problems hit along the way

- "Cannot connect to the docker API": Docker Desktop was not running yet.
- Port 8000 already in use: an earlier dev server was still running.
- Build failed at the torch step: --index-url replaces PyPI entirely, --extra-index-url adds to it.

## Limitations

- Not deployed to a cloud yet (planned: Azure Container Apps).
- /ask has no authentication. It must not be exposed publicly as is, because anyone calling it would spend the owner's API credits.
- The index is rebuilt on every image build; there is no incremental update.
- The evaluation script still calls ask() directly instead of the HTTP service.
