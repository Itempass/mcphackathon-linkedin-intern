# Development Plan

This document outlines the step-by-step plan to build the backend application based on the provided UML diagrams and API specifications.

### Phase 1: Project Scaffolding & Core Models

**Goal:** Create the basic file structure and define the data shapes that will be used throughout the application.

1.  **Initialize Project Structure:**
    -   Create the `src/` directory for all source code.
    -   Create `documentation/plans/` for project planning documents.
    -   Create `src/main.py`, `src/services.py`, `src/models.py`, and `src/background_tasks.py`.
    -   Create a `tests/` directory.
    -   Create `requirements.txt` and add initial dependencies: `fastapi`, `uvicorn`, `pydantic`, `pytest`.

2.  **Define Data Models (`src/models/`):**
    -   Based on `api_endpoints.md` and `message_class_diagram.puml`, create Pydantic models for all API data in `src/models/api_models.py`.
    -   Create `src/models/internal_models.py` to hold data models for internal use (e.g., database schemas).
    -   This separation ensures that the API contract is decoupled from the internal data representation.

### Phase 2: API Endpoint Implementation

**Goal:** Build the public-facing API that the user will interact with.

1.  **Setup FastAPI App (`src/main.py`):**
    -   Create a basic FastAPI application instance.

2.  **Implement API Endpoints (`src/main.py`):**
    -   **`/send-messages`:** This endpoint will accept a list of messages. Upon receiving a valid request, it will not process them directly. Instead, it will hand off the processing to a background task (defined in Phase 4) and immediately return a `202 Accepted` status to the user.
    -   **`/process-feedback`:** Similar to the messages endpoint, this will accept feedback on a draft, pass the work to a background task, and return `202 Accepted`.
    -   **`/reject-draft`:** This endpoint will directly call a function in `src/services.py` to handle the logic of removing or flagging a draft and return `200 OK`.
    -   **`/draft-messages`:** This endpoint will call a function in `src/services.py` to fetch all available drafts for a user and return them.

3.  **Write API Tests (`tests/test_api.py`):**
    -   Create tests for each endpoint to verify status codes and request/response formats using FastAPI's `TestClient`.

### Phase 3: Core Business Logic

**Goal:** Implement the "brains" of the application as described in the sequence diagrams.

1.  **Implement Service Functions (`src/services.py`):**
    -   **Thread Processing Service Logic:** Create a function that orchestrates creating a draft from a thread of messages. It will be responsible for calling the LLM (from `mcp_servers`), processing the result, and saving it to a database (which we'll mock for now).
    -   **Feedback Service Logic:** Create a function that takes a draft and feedback, communicates with the LLM to get a revised draft, and updates the database.

2.  **Write Unit Tests for Services (`tests/test_services.py`):**
    -   Create unit tests for each function in `src/services.py`. Mock external dependencies (database, LLM calls) to isolate business logic.

### Phase 4: Asynchronous Background Processing

**Goal:** Ensure long-running tasks like LLM calls do not block the API.

1.  **Define Background Tasks (`src/background_tasks.py`):**
    -   Create a `run_thread_processing` function. This function will be called by the `/send-messages` endpoint and will execute the thread processing service logic from `src/services.py`.
    -   Create a `process_feedback_task` function. This will be called by the `/process-feedback` endpoint and execute the feedback service logic.

2.  **Integrate Task Runner:**
    -   Choose and configure a library for managing these background tasks (e.g., Celery with Redis or ARQ).
    -   Connect the endpoints in `src/main.py` to trigger these tasks.

3.  **Write Tests for Background Tasks (`tests/test_background_tasks.py`):**
    -   Create tests to ensure API endpoints correctly trigger background tasks and that tasks execute the right service logic.

### Phase 5: Integration, Persistence & E2E Testing

**Goal:** Replace mock components with real, persistent ones and run end-to-end tests.

1.  **LLM Integration (OpenRouter):**
    -   Add `python-dotenv` and `openai` to `requirements.txt`.
    -   Create a client in `src/llm_client.py` to handle communication with the OpenRouter API.
    -   The client will read the `OPENROUTER_API_KEY` from the `.env` file.
    -   Update the service functions in `src/services.py` (`process_thread_and_create_draft` and `create_revised_draft_from_feedback`) to call the LLM client instead of returning mock data.

2.  **Database Integration:**
    -   Choose a database (e.g., SQLite for simplicity, PostgreSQL for production).
    -   Add a database layer (e.g., using SQLAlchemy) to replace the mock database.
    -   Update the functions in `src/services.py` to interact with the real database for all create, read, update, and delete operations on drafts.

3.  **End-to-End (E2E) Testing:**
    -   Create E2E tests that simulate a full user flow: sending messages, getting a real LLM-generated draft, providing feedback, and seeing the revised result. This validates that all parts of the system work together correctly. 