# Work Plan: Conversation View Enhancements

This document outlines the plan to improve the user interface and add navigation to the conversation view.

## Phase 1: UI Readability and Styling Improvements

This phase focuses on improving the visual presentation and readability of the conversation messages.

- [x] **Improve Text Contrast:**
    - [x] **Task:** Identify all instances of light gray text within the `ConversationDisplay.tsx` component that have poor contrast.
    - [x] **Implementation:** Adjust the Tailwind CSS classes for these elements to use a darker shade of gray (e.g., `text-gray-700` instead of `text-gray-500`) to ensure they meet accessibility standards and are easier to read.

- [x] **Style Redacted Text:**
    - [x] **Task:** Create a distinct visual style for redacted text to make it immediately recognizable.
    - [x] **Implementation:** In `ConversationDisplay.tsx`, create a helper function that takes the message content, finds all occurrences of `[REDACTED...]`, and wraps them in a `<span>`. This span will be styled with a black background and white text (`bg-black text-white px-1 rounded-sm`).

- [x] **Enhance Message Layout:**
    - [x] **Task:** Refine the layout of individual chat messages in `ConversationDisplay.tsx` for better structure and clarity.
    - [x] **Implementation:** Review and adjust the spacing, alignment, and visual hierarchy within each message block. This may include increasing the margin between the role header and the content, and tidying up the presentation of tool call arguments and results.

## Phase 2: Sidebar Navigation

This phase introduces a new navigation sidebar to the conversation view, inspired by the provided image, to allow for quick navigation between key events in the conversation.

- [x] **Create `TraceSidebar` Component:**
    - [x] **Task:** Develop a new reusable component, `TraceSidebar.tsx`, in the `src/components` directory.
    - [x] **Implementation:** This component will accept a list of navigation items (e.g., messages, tool calls) and render them as a clickable list. The design will be a clean, hierarchical view similar to the example image.

- [x] **Data Processing for Sidebar:**
    - [x] **Task:** Extract and structure the necessary data to populate the sidebar.
    - [x] **Implementation:** In the `src/app/dashboard/conversation/[threadName]/page.tsx` component, process the fetched thread data. Create a new array of objects, where each object contains the necessary information for a sidebar item (e.g., message ID, role, tool name).

- [x] **Integrate Sidebar into Conversation View:**
    - [x] **Task:** Update the conversation page to include the new sidebar.
    - [x] **Implementation:** Modify the layout of `.../[threadName]/page.tsx` to be a two-column grid. The `TraceSidebar` component will be placed in the left column, and the `ConversationDisplay` will be in the right column.

- [x] **Implement Scroll-to-Message Navigation:**
    - [x] **Task:** Enable navigation from the sidebar to the corresponding message in the conversation.
    - [x] **Implementation:** Assign unique `id` attributes to each message container in `ConversationDisplay.tsx`. The `TraceSidebar` component will have click handlers on its items. When an item is clicked, it will use the message ID to scroll the corresponding message into the viewport using `element.scrollIntoView()`.

## Phase 3: Implement Conversation Loader

This phase will introduce a more engaging loading screen when a conversation is being fetched.

- [x] **Task:** Replace the simple "Loading conversation..." text with an animated spinner and a series of dummy loading steps to improve the user experience during long loads.
- [x] **Implementation:**
    - [x] In `src/app/dashboard/conversation/[threadName]/page.tsx`, create a new loading component or inline JSX that includes a spinning wheel icon.
    - [x] Below the spinner, implement a mechanism to cycle through a predefined list of text strings (e.g., "Fetching conversation...", "Analyzing tool calls...", "Rendering trace...") to simulate loading progress.

## Phase 4: Enhance Data Points

This phase will focus on enriching the data displayed for each step in the conversation, particularly for tool calls and assistant messages.

- [x] **Update Data Model:**
    - [x] **Task:** Modify the data types in `src/types/database.ts` to include new data points for performance and cost tracking.
    - [x] **Implementation:** The `ToolCallInfo` and/or `AgentMessage` interfaces will be updated to include fields such as `duration`, `model`, `tokens`, and `price`.

- [x] **Backend Data Extraction:**
    - [x] **Task:** Update the backend service (`src/services/database.ts`) to extract or calculate this new information from the raw message data.
    - [x] **Implementation:** The data processing logic in `getThreadDetails` and `getAgentMessagesById` will be enhanced. This will involve calculating time durations between requests and responses and parsing any available metadata for model, token, and cost information.

- [x] **Frontend Display:**
    - [x] **Task:** Update the UI components (`ConversationDisplay.tsx`, `TraceSidebar.tsx`, and the dashboard page) to display these new data points.
    - [x] **Implementation:** The new data will be integrated into the conversation view, likely next to the relevant message or tool call. The tooltips on the main dashboard will also be updated to include this richer information. 