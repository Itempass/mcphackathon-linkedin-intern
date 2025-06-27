# Plan to Integrate Anonymization Service

This document outlines the plan to integrate the Python-based `anonymizer_service.py` into the Next.js application dashboard. The goal is to provide a way to view anonymized conversation data in the dashboard.

## Phase 1: Backend API for Anonymization

The existing backend is in TypeScript, and the anonymization service is in Python. We will create a bridge between the two.

- [x] **Create a new API route for anonymization:**
    - [x] Create a new API route at `src/app/api/anonymize/route.ts`.
    - [x] This route will accept a POST request with the conversation data (a list of messages) in the request body.

- [x] **Execute Python script from Node.js:**
    - [x] Inside the new API route, use Node.js's `child_process.spawn` to execute the `anonymizer_service.py` script.
    - [x] The conversation data will be passed to the Python script via `stdin`.
    - [x] The Python script will be modified to read from `stdin`, perform the anonymization, and print the anonymized data to `stdout`.
    - [x] The Node.js route will capture the `stdout` from the Python script.

- [x] **Modify `anonymizer_service.py` for CLI usage:**
    - [x] Add a `if __name__ == "__main__":` block to `anonymizer_service.py`.
    - [x] In this block, read the JSON conversation data from `sys.stdin`.
    - [x] Call the `anonymize_conversation` function with the received data.
    - [x] Print the resulting anonymized JSON data to `sys.stdout`.
    - [x] Handle potential errors and print error messages to `sys.stderr`.

- [x] **Environment Variables:**
    - [x] The `OPENROUTER_API_KEY` and `OPENROUTER_SUMMARY_MODEL` environment variables will need to be available to the Node.js process running the Next.js application. We will use a `.env.local` file to manage these.

## Phase 2: Frontend Integration

With the backend in place, we will update the frontend to use it.

- [x] **Modify the Thread View:**
    - [x] The component that displays the thread messages (likely in `src/app/dashboard/[id]/page.tsx` or a similar component) will be updated.
    - [x] Add an "Anonymize" button or toggle to the UI.

- [x] **Client-side Data Fetching:**
    - [x] When the "Anonymize" button is clicked, the frontend will make a `POST` request to the `/api/anonymize` endpoint.
    - [x] The current conversation messages will be sent in the request body.
    - [x] The response will be the anonymized version of the conversation.

- [x] **State Management:**
    - [x] The component's state will be updated to display the anonymized messages.
    - [x] Add a state variable, e.g., `isAnonymized`, to toggle between the original and anonymized views. This will allow the user to switch back and forth without re-fetching the original data.

## Phase 3: Refinement and Error Handling

- [x] **Loading and Error States:**
    - [x] Implement loading indicators on the frontend while the anonymization is in progress.
    - [x] Display user-friendly error messages if the anonymization fails (e.g., if the Python script returns an error).

- [x] **Configuration Check:**
    - [x] The backend will check if the `anonymizer_service` is configured (i.e., if the required environment variables are set) before attempting to run the script. If not configured, the "Anonymize" button on the frontend could be disabled or hidden. The health check endpoint in the `anonymizer_service` can be used for this. 