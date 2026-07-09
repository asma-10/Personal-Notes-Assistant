# Personal Notes Assistant

A simple conversational assistant built with **LangGraph** and **FastAPI** that remembers facts about the user across conversations, using a local JSON file as long-term memory.

This project was built as a practice exercise to reinforce:
- LangGraph state design and node composition
- Separation between API schemas (Pydantic) and graph state (TypedDict)
- Long-term memory patterns (external store vs. per-session checkpointer)
- Wrapping a LangGraph app behind a FastAPI service
- Containerizing the app with Docker

## How it works

Every time you send a message:

1. **`load_memories`** — loads all previously saved facts for that `user_id` from `memories.json`.
2. **`chat`** — answers the user's message, using known facts as context.
3. **`memorize`** — an LLM call decides whether the message contains a new fact worth remembering, and extracts it as structured JSON.
4. **`save_if_needed`** — saves any extracted facts to `memories.json`.

Facts persist **across conversations** (keyed by `user_id`), while the LangGraph checkpointer manages state **within** a single request/session.

## Project structure

```
.
├── main.py                  # FastAPI app entrypoint
├── api/
│   └── routers/
│       └── chat_endpoint.py # /chat route definition
├── graph/
│   ├── state.py             # TypedDict graph state
│   ├── nodes.py             # Node functions (load_memories, chat, memorize, save_if_needed)
│   └── build_graph.py       # StateGraph wiring + compilation
├── schemas/
│   └── api_schemas.py       # Pydantic request/response models
├── memory_store.py           # Local JSON-based memory read/write functions
├── memories.json             # Local memory storage (created automatically)
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── .env                       # API keys (not committed)
```

## Requirements

- Python 3.11+
- A Groq API key (used via `langchain-groq`)

## Setup (local, no Docker)

1. Clone the project and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_key_here
   ```

3. Run the API:
   ```bash
   uvicorn main:app --reload
   ```

4. The API will be available at `http://localhost:8000`.

## API

### `POST /api/chat`

Send a message and get a response. Facts worth remembering are automatically extracted and saved.


### `GET /health`

Simple health check.

```json
{ "status": "healthy" }
```

## Running with Docker

1. Build the image:
   ```bash
   docker build -t chat_memorizer_img .
   ```

2. Run the container (with your `.env` file and a mounted volume so memories persist across restarts):
   ```bash
   docker run --env-file .env -p 8000:8000 -v $(pwd)/memories.json:/app/memories.json chat_memorizer_img
   ```

3. Test it:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test1", "user_message": "hello, my name is asma !"}'
   ```

## Notes on design decisions

- **No vector search yet.** Memory retrieval is a full pull of everything stored for a `user_id` — simple and readable, but doesn't scale past a small number of facts. This is intentional groundwork before integrating a vector database (e.g. Qdrant) for semantic retrieval.
- **Checkpointer vs. memory store.** The LangGraph checkpointer (`InMemorySaver`) handles short-term, per-thread state. `memories.json` handles long-term, cross-session facts about the user. These are deliberately kept as two separate systems.
- **Schema/state separation.** Pydantic models (`schemas/`) define the API contract; the `TypedDict` (`graph/state.py`) defines internal graph state. They are never passed directly into one another — the router explicitly maps between them.

## Possible next steps

- Replace `memories.json` with Qdrant (semantic search) and/or Supabase (structured storage).
- Add a human-in-the-loop confirmation step before saving new facts.
- Add memory deletion/editing endpoints.
- Persist checkpointer state (e.g. SQLite/Postgres) instead of `InMemorySaver`.
