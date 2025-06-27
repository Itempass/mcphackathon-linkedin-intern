# Final Plan: Assistant-Centric Dashboard

This plan pivots the architecture to align with the final requirements. The dashboard will be driven by a single data source fetching all "assistants" (Agents) and their associated conversation threads.

## Phase 1: Redesign Data Layer (✅ Partially Complete)

### 1.1. Stabilize Database Connection
-   **Task:** ✅ Use environment variables for the database connection.
-   **Implementation:** The code in `src/lib/db.ts` is already configured to use the `MYSQL_DB` environment variable. The user must create the `.env.local` file for this to work.

### 1.2. Create `get_all_assistants` Service
-   **Task:** Create a single function to fetch all agents and their associated thread names.
-   **Implementation:**
    -   In `src/services/database.ts`, create a new function `getAllAssistants`.
    -   This function will first query the `agents` table to get all agents.
    -   Then, for each agent, it will perform a second query on the `messages` table to get a list of unique `thread_name`s associated with that `agent_id`.
    -   The function will return an array of `ProcessedAssistantWithThreads` objects.
    -   Update `src/types/database.ts` with the new `ProcessedAssistantWithThreads` interface.

## Phase 2: Refactor API and UI

### 2.1. Create the `assistants` API Route
-   **Task:** Create the single API endpoint that the dashboard will use.
-   **Implementation:**
    -   Create a new API route at `src/app/api/assistants/route.ts`.
    -   This route will call the `getAllAssistants` function from the database service and return the data.
    -   Delete the old, now-unused API routes: `/api/messages`, `/api/agents`, and `/api/threads`.

### 2.2. Redesign the Main Dashboard
-   **Task:** The main page will now display a list of assistants.
-   **Implementation:**
    -   Refactor `src/app/dashboard/page.tsx`.
    -   It will now fetch data from the `/api/assistants` endpoint.
    -   Instead of a table of messages, it will display a list or grid of assistants. Each item will show the Assistant's ID, system prompt, and a list of the thread names they are involved in.
    -   Clicking on a thread name will navigate the user to the existing conversation view.

### 2.3. Clean up Unused Components
-   **Task:** Remove pages and components that are no longer needed.
-   **Implementation:**
    -   Delete the `/dashboard/agents` directory and its contents, as this page is now redundant.
    -   The `ConversationModal` is likely no longer needed if the main page links directly to the conversation view. I will assess and remove it if it's unused.

## Phase 3: Final Cleanup

-   **Task:** Remove all remaining obsolete files.
-   **Implementation:**
    -   Delete `plans/dashboard_adaptation_plan.md` and `plans/dashboard_adaptation_plan_v2.md`.
    -   Delete any other unused files from previous iterations. 