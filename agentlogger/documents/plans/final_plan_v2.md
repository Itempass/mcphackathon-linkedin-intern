# Final Plan V2: Table-Based Dashboard

This plan outlines the work to create a single table view for the dashboard, providing an overview of all agent and thread activity.

## Phase 1: Update Data Layer

### 1.1. Establish Data Source for Tool Calls
-   **Task:** Identify the database source for tool call information to calculate `cycles` and `tool chain` per thread.
-   **Decision/Assumption:** Tool call data is stored within the `msg_content` column of the `messages` table as a JSON string. A message is considered a "tool call" if its `msg_content` can be parsed as JSON and contains a top-level `tool_calls` key.

### 1.2. Implement `get_thread_details` Service
-   **Task:** Create a single, powerful function to fetch the data needed for the table view.
-   **Implementation:**
    -   In `src/services/database.ts`, create a new function `getThreadDetails`.
    -   This function will fetch all messages and process them in the application layer (as complex JSON parsing in SQL is difficult and not portable).
    -   It will group messages by `thread_name` and calculate:
        -   `message_count`
        -   `cycles` (tool call count based on the assumption above)
        -   `tool_chain` (list of unique tool names from the content)
        -   `user_id`
        -   `id` (which will be the `thread_name`)

## Phase 2: Refactor UI to Table View

### 2.1. Update the Main API Route
-   **Task:** Point the primary API route to the new database service function.
-   **Implementation:**
    -   Refactor the `/api/assistants` endpoint to call the new `getThreadDetails` service.
    -   Rename the route to `/api/dashboard-data` for clarity.

### 2.2. Implement Dashboard Table
-   **Task:** Rework the main dashboard page to display the new table.
-   **Implementation:**
    -   In `src/app/dashboard/page.tsx`, fetch from the new `/api/dashboard-data` route.
    -   Display a single table with the columns: `id`, `user-id`, `cycles`, `messages`, `tool chain`.
    -   The table rows will represent individual threads.

## Phase 3: Cleanup
-   **Task:** Remove all unused files from previous iterations.
-   **Implementation:**
    -   Delete old workplans.
    -   Remove any components or pages related to the card-based assistant layout. 