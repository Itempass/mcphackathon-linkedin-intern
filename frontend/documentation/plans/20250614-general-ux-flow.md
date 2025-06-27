# LinkedIn AI Assistant - General UX Implementation Plan

## Overview
After a user completes the onboarding process (collecting 10 threads), they'll be transitioned to our main interface - the General UX. This interface will be their primary interaction point with our AI assistant when they're using LinkedIn messaging.

## Core Requirements

### Draft Messages Feed
1. **Initial State** ✅
   - ✅ Users will see a clean interface titled "Chat Drafter"
   - ✅ While we're fetching drafts, they'll see a loading indicator with "fetching drafts"
   - ✅ This view only appears when they're actively on a LinkedIn message page

2. **WhatsApp-Style Draft Messages List** ✅
   - ✅ Draft messages are displayed in a WhatsApp-style message list
   - ✅ Each message shows: contact name, message content, and copy button
   - ✅ Messages are fetched from backend draft buffer and lined up in the side panel
   - ✅ Each draft has an easy-to-access copy button for pasting into LinkedIn chat

3. **~~User Feedback System~~** (DEFERRED)
   - ~~At the bottom of the panel, users will find a familiar chat-style input box (similar to Cursor's chat)~~
   - ~~Users have two ways to interact:~~
     1. ~~Send detailed feedback: Type their thoughts and click send~~
     2. ~~Quick regenerate: Click a "regenerate" button when they just want a new draft~~
   - ~~Both actions show appropriate loading states while processing~~

### Technical Integration Points

1. **Message Thread Detection** ✅
   We're leveraging our existing infrastructure:
   - ✅ `dom-watcher.ts` already handles LinkedIn message detection
   - ✅ Automatically extracts thread content when users open messages
   - ✅ Provides clean, structured data we can send to our backend

2. **Backend Communication**
   Here's how our API endpoints work together:

   a. **Sending Messages** ✅ (Already Working)
   - ✅ When we collect a thread, we send it to `/send-messages/`
   - ✅ Includes user ID, thread name, and all message details
   - ✅ Backend acknowledges with 202 ACCEPTED

   b. **Getting Draft Messages** ✅ **COMPLETED**
   - ✅ We fetch all available drafts from backend buffer via `/draft_messages/`
   - ✅ Just need to provide the user's ID
   - ✅ Backend returns an array of drafts with their IDs and content
   - ✅ Display all drafts in WhatsApp-style list format

   c. **~~Handling User Feedback~~** ~~⏳~~ (DEFERRED)
   - ~~When users type feedback, we send it to `/process-feedback/`~~
   - ~~Include user ID, draft ID, and their feedback text~~
   - ~~Backend will process this and generate a new draft~~

   d. **~~Quick Regeneration~~** ~~⏳~~ (DEFERRED)
   - ~~If users click regenerate, we call `/reject-draft/`~~
   - ~~This tells the backend to generate a new version~~
   - ~~Simpler than feedback - just needs user and draft IDs~~

3. **State Management** ✅
   We track everything important about the current session:
   - ✅ All available draft messages from backend buffer
   - ✅ Loading states for draft fetching
   - ✅ Any errors that occur

## Implementation Steps

### Step 1: API Integration Layer ✅
**Commit Message**: "feat: Add API integration layer for draft management"

✅ COMPLETED:
1. ✅ New file `src/api/backend.ts` containing:
   - ✅ Type definitions for all API requests/responses
   - ✅ Functions for each endpoint:
     * ✅ getDrafts(userId)
     * ✅ submitFeedback(userId, draftId, feedback)
     * ✅ rejectDraft(userId, draftId)
   - ✅ Error handling utilities
   - ✅ Response type validation

### Step 2: Base General UX Structure ✅
**Commit Message**: "feat: Add general UX component structure and routing"

✅ COMPLETED:
1. ✅ New directory structure:
   ```
   src/sidepanel/views/general/
   ├── GeneralRoot.tsx
   ├── Header.tsx
   └── EmptyState.tsx
   ```

2. ✅ GeneralRoot contains:
   - ✅ State management setup
   - ✅ API integration hooks
   - ✅ Routing logic from onboarding
   - ✅ Basic layout structure

3. ✅ EmptyState handles:
   - ✅ "Chat Drafter" title display
   - ✅ Loading spinner
   - ✅ Error state displays
   - ✅ Placeholder messages

4. ✅ Header Component:
   - ✅ Dynamic title showing counterparty's name (e.g., "Chat with Sarah Smith")
   - ✅ Elegant typography with gradient or highlight effect
   - ✅ Subtle separator or border below header
   - ✅ Responsive design that handles long names gracefully
   - Optional: Small avatar/icon space for future enhancement
   - Optional: Status indicator (active/typing)

**Why This Second**:
- ✅ Provides the container for all future components
- ✅ Establishes state management patterns
- ✅ Creates smooth transition from onboarding
- Makes the interface more personal and context-aware
- Improves user orientation within the LinkedIn context

### Step 3: Draft Messages Feed Display ✅ **COMPLETED**
**Commit Message**: "feat: Implement WhatsApp-style draft messages display with copy functionality"

✅ **FULLY IMPLEMENTED** - All Technical Specifications Completed:

1. ✅ **DraftMessagesFeed Component Logic**:
   - ✅ **State Management**: 
     * ✅ `drafts: DraftMessage[]` - Array of all draft messages from backend
     * ✅ `loading: boolean` - Loading state during API calls
     * ✅ `error: string | null` - Error state for failed requests
   
   - ✅ **Polling Logic**:
     * ✅ Initialize `useEffect` with 5-second interval using `setInterval`
     * ✅ Call `api.getDrafts(userId)` on mount and every interval
     * ✅ Update `drafts` state with response data
     * ✅ Handle loading states: set `loading: true` before call, `loading: false` after
     * ✅ Clear interval on component unmount
   
   - ✅ **Data Processing**:
     * ✅ Sort drafts by `draft_message_id` or timestamp (newest first)
     * ✅ Filter out empty or invalid draft messages
     * ✅ Map backend response to internal `DraftMessage` interface

2. ✅ **DraftMessageCard Component Specifications**:
   - ✅ **Props Interface**:
     * ✅ `draftMessage: DraftMessage` - Single draft message object
     * ✅ `onCopySuccess?: () => void` - Optional callback for copy success
   
   - ✅ **Visual Elements**:
     * ✅ **Contact Header**: Display `thread_name` as prominent header text (16px, font-weight: 600)
     * ✅ **Message Body**: Display `draft_message_content` with line breaks preserved, max 1 line in preview
     * ✅ **Copy Button**: Floating button (top-right) with copy icon, 32px x 32px
     * ✅ **Card Container**: Rounded corners (8px), subtle shadow, 12px padding, 8px margin between cards
   
   - ✅ **Interaction Logic**:
     * ✅ Hover state: Slight elevation increase (box-shadow)
     * ✅ Copy button hover: Color change to accent color
     * ✅ Click anywhere on card: Optional expand/collapse for long messages

3. ✅ **CopyButton Component Logic**:
   - ✅ **Core Functionality**:
     * ✅ Use `navigator.clipboard.writeText(message)` for copy operation
     * ✅ Implement fallback using `document.execCommand('copy')` for older browsers
     * ✅ Show visual feedback: Icon change (copy → checkmark) for 2 seconds
     * ✅ Handle copy failures with error toast notification
   
   - ✅ **State Management**:
     * ✅ `copied: boolean` - Toggle for showing success state
     * ✅ `copyError: boolean` - Toggle for showing error state
     * ✅ Reset states after 2-second timeout

4. ✅ **API Integration Specifications**:
   - ✅ **Request Flow**:
     * ✅ GET `/draft-messages/` with `userId` parameter
     * ✅ Handle 200 response: Update drafts state
     * ✅ Handle 404/500 errors: Set error state with user-friendly message
     * ✅ Handle network errors: Show "Connection failed" message
   
   - ✅ **Response Processing**:
     * ✅ Validate response structure matches `DraftMessagesResponse` interface
     * ✅ Extract `draft_messages` array from response
     * ✅ Map each item to internal `DraftMessage` format
     * ✅ Handle empty array (no drafts available)

5. ✅ **Loading States Implementation**:
   - ✅ **Initial Load**: Show skeleton cards (3 placeholder cards with shimmer effect)
   - ✅ **Refresh Load**: Show subtle loading indicator at top of feed
   - ✅ **Error State**: Show error message with retry button
   - ✅ **Empty State**: Show "No drafts available" with icon and descriptive text

6. ✅ **Layout & Styling Specifications**:
   - ✅ **Container Layout**:
     * ✅ Full height of sidepanel minus header
     * ✅ Vertical scrolling for overflow
     * ✅ 16px horizontal padding
     * ✅ 8px top/bottom padding
   
   - ✅ **Card Styling**:
     * ✅ Background: `#ffffff` with `border: 1px solid #e5e7eb`
     * ✅ Border radius: `8px`
     * ✅ Box shadow: `0 1px 3px rgba(0, 0, 0, 0.1)`
     * ✅ Hover: `box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1)`
   
   - ✅ **Typography**:
     * ✅ Contact name: `font-size: 16px, font-weight: 600, color: #1f2937`
     * ✅ Message text: `font-size: 14px, font-weight: 400, color: #4b5563, line-height: 1.4`
     * ✅ Truncation: `overflow: hidden, text-overflow: ellipsis, display: -webkit-box, -webkit-line-clamp: 1`

7. ✅ **Performance Considerations**:
   - ✅ **Memo Optimization**: Wrap DraftMessageCard in `React.memo` to prevent unnecessary re-renders
   - ✅ **Virtualization**: If drafts list > 50 items, implement virtual scrolling
   - ✅ **Debouncing**: Debounce copy button clicks to prevent multiple rapid copies
   - ✅ **Memory Management**: Clear polling intervals and timeouts on unmount

✅ **Integration Points**:
- ✅ **GeneralRoot Integration**: Import and render `<DraftMessagesFeed />` in main content area
- ✅ **API Layer**: Use existing `api.getDrafts()` function from `backend.ts`
- ✅ **Error Handling**: Connect to global error boundary for crash recovery
- ✅ **Loading States**: Integrate with existing loading spinner components

✅ **Data Flow**:
1. ✅ User opens sidepanel → GeneralRoot mounts → DraftMessagesFeed mounts
2. ✅ DraftMessagesFeed calls `api.getDrafts(userId)` immediately
3. ✅ Backend returns draft messages array → Update local state
4. ✅ Render DraftMessageCard for each draft message
5. ✅ User clicks copy button → Copy to clipboard → Show success feedback
6. ✅ Polling continues every 5 seconds → Update UI if new drafts available

✅ **Error Handling Logic**:
- ✅ **Network Errors**: Show retry button, maintain last successful data
- ✅ **API Errors**: Show specific error message, option to refresh
- ✅ **Copy Errors**: Show toast notification, fallback to manual selection
- ✅ **Empty Response**: Show empty state with helpful message

### Step 4: Polish & Error Handling ⏳
**Commit Message**: "feat: Add comprehensive error handling and UX polish for draft messages feed"

**What We'll Build**:
1. Error Handling:
   - Global error boundary for draft feed
   - Retry mechanisms for API calls
   - User-friendly error messages
   - Recovery flows when API is down

2. Loading States:
   - Skeleton screens for loading draft cards
   - Progress indicators during fetch
   - Smooth transition animations

3. Edge Cases:
   - Empty draft buffer handling
   - Offline handling
   - Session timeout recovery
   - API rate limiting

### Backend Fallback Strategy ✅
**Issue**: Backend `/draft-messages/` endpoint may return 500 errors or be unavailable
**Solution**: Graceful degradation with proper error handling

**Implementation Strategy**:
- **Primary**: Attempt to fetch drafts from backend API
- **Fallback**: When backend fails (500 errors, network issues), show "No drafts available" message
- **User Experience**: Clear error messaging explaining backend unavailability
- **No Mock Data**: Avoid showing fake/mock data to users in production
- **Retry Functionality**: Provide retry button for users to attempt reconnection

**Error Handling**:
- 500 Internal Server Error → "Backend server error - the draft service is temporarily unavailable. Please try again later."
- Network failures → "Connection failed - please check your internet connection"
- 404 errors → "Draft service not available"
- Generic API failures → "API service error - please try again in a few moments"

**Status**: ✅ Implemented with proper error states and user messaging
**Environment Toggle**: ✅ Added `VITE_USE_MOCK_FALLBACK` environment variable for testing vs production behavior

### Step 5: Interactive Feedback System & Thread Context ⏳
**Commit Message**: "feat: Add feedback system with thread-aware draft prioritization"

**PLANNED IMPLEMENTATION** - Technical Specifications:

1. **Feedback API Integration** ✅:
   - ✅ **Endpoint**: POST `/process-feedback/` (from backend.spec.ts)
   - ✅ **Request Structure**: 
     * ✅ `user_id: string` - Current user identifier
     * ✅ `draft_message_id: string` - Target draft for feedback
     * ✅ `feedback: string` - User's feedback text
   - ✅ **Response Handling**: 202 ACCEPTED with void body
   - ✅ **Error Handling**: Network failures, validation errors, feedback submission status

2. **Feedback UI Components** ✅:
   - **Mini Chatbox Component**: ✅
     * ✅ Appears on topmost draft card by default
     * ✅ Compact input field with send button
     * ✅ Character limit (500 chars) with counter
     * ✅ Auto-resize textarea for longer feedback
     * ✅ Loading state during submission
   
   - **Expandable Chat Interface**: ✅
     * ✅ Click any draft card header → card enlarges (height expansion)
     * ✅ Full chatbox interface appears below message
     * ✅ Send feedback button with loading spinner 
     * ✅ Success/error states with visual feedback
     * ✅ Collapse functionality to return to compact view

3. **Thread Detection & Name Extraction** ✅ (FIXED):
   - **Problem**: LinkedIn thread name extraction currently broken
   - **Solution**: 
     * ✅ Revisited `dom-watcher.ts` LinkedIn message detection
     * ✅ Fixed thread name parsing with multiple fallback selectors
     * ✅ Enhanced counterparty name extraction from various LinkedIn UI elements
     * ✅ Updated Header component processing for "Chat with [Name]" format
   - **Integration**: ✅ Thread detection working with robust fallback system

4. **Thread-Aware Draft Prioritization**:
   - **Thread Matching Logic**:
     * Compare active LinkedIn chat thread name/ID with draft `thread_name`
     * Implement fuzzy matching for thread identification
     * Handle edge cases (name variations, chat formatting differences)
   
   - **Smart Draft Ordering**:
     * **Priority 1**: Drafts matching current active LinkedIn thread
     * **Priority 2**: Recent drafts (by timestamp/ID)
     * **Priority 3**: All other drafts
   
   - **UI Enhancements for Active Thread**:
     * Matched draft appears at top of feed
     * Slightly larger card size (20% height increase)
     * Highlighted border or background accent
     * Chatbox automatically visible (not collapsed)
     * "Active Chat" indicator or badge

5. **State Management Extensions**:
   - **New State Variables**:
     * `activeThreadName: string | null` - Currently active LinkedIn thread
     * `expandedDraftId: string | null` - Which draft card is expanded
     * `feedbackStates: Record<string, FeedbackState>` - Per-draft feedback status
     * `threadMatches: string[]` - Draft IDs matching active thread
   
   - **Feedback State Interface**:
     * `submitting: boolean` - Feedback submission in progress
     * `submitted: boolean` - Feedback successfully sent
     * `error: string | null` - Submission error message
     * `feedbackText: string` - Current feedback input

6. **Component Architecture** ✅ **PARTIALLY COMPLETED**:
   ```
   DraftMessagesFeed/
   ├── index.tsx ✅ (updated with thread matching)
   ├── DraftMessageCard.tsx ✅ (updated with expansion logic)
   ├── CopyButton.tsx ✅ (existing)
   ├── FeedbackChatbox.tsx ✅ (new - compact feedback input)
   ├── ExpandedChatInterface.tsx ✅ (new - full feedback UI)
   ├── mockData.ts ✅ (new - testing fallback data)
   └── ThreadBadge.tsx ⏳ (new - active thread indicator)
   ```

7. **Technical Implementation Flow**:
   
   **Phase 1: Fix Thread Detection** ✅ **COMPLETED**
   - ✅ Debug and repair LinkedIn thread name extraction
   - ✅ Test thread detection across different LinkedIn chat interfaces
   - ✅ Ensure GeneralRoot receives correct counterparty names
   
   **Phase 2: Feedback UI Components** ✅ **COMPLETED**
   - ✅ Create FeedbackChatbox with API integration
   - ✅ Implement card expansion/collapse mechanism
   - ✅ Add feedback submission states and error handling
   
   **Phase 3: Thread Matching & Prioritization** ⏳
   - Implement thread matching algorithm
   - Reorder draft feed based on active thread
   - Add visual indicators for matched drafts
   
   **Phase 4: Integration & Polish** ⏳
   - Connect all components with proper state management
   - Add animations for expand/collapse and reordering
   - Test end-to-end feedback workflow

8. **User Experience Flow**:
   1. User opens LinkedIn chat → Thread name detected → Header updates
   2. DraftMessagesFeed fetches drafts → Thread matching occurs → Relevant draft moves to top
   3. Top draft shows enlarged card with visible chatbox
   4. User types feedback → Clicks send → API call with loading state
   5. Success: Feedback submitted, new draft may appear
   6. User can expand any draft card for detailed feedback interface

9. **API Integration Specifications**:
   - **Request Validation**: Ensure draft_message_id exists in current drafts
   - **Response Handling**: 202 ACCEPTED triggers success state
   - **Error Scenarios**: 
     * 400 Bad Request → "Invalid feedback format"
     * 404 Not Found → "Draft no longer available"
     * 500 Server Error → "Feedback service unavailable"
   - **Retry Logic**: Allow manual retry for failed submissions

10. **Performance Considerations**:
    - **Thread Matching**: Debounce thread detection to avoid excessive matching
    - **Re-rendering**: Optimize draft reordering to minimize layout shifts
    - **Memory**: Clean up feedback states when drafts are removed
    - **Network**: Batch feedback submissions if multiple queued

**Success Criteria**:
- ✅ LinkedIn thread names correctly extracted and displayed
- ✅ Feedback can be submitted for any draft message
- ⏳ Active thread drafts are prioritized and highlighted
- ✅ Smooth expand/collapse animations for draft cards
- ✅ Clear feedback submission states and error handling

**Dependencies**:
- Existing DraftMessagesFeed implementation (Step 3)
- Working dom-watcher.ts thread detection
- Backend `/process-feedback/` endpoint availability

### Step 6: Quick Draft Regeneration System ⏳
**Commit Message**: "feat: Add one-click draft regeneration with reject API"

**PLANNED IMPLEMENTATION** - Technical Specifications:

**Unused API Endpoint**: POST `/reject-draft/` (from backend.spec.ts)

1. **Reject Draft API Integration**:
   - **Endpoint**: POST `/reject-draft/` 
   - **Request Structure**: 
     * `user_id: string` - Current user identifier
     * `draft_message_id: string` - Draft to reject and regenerate
   - **Response Handling**: 200 OK with void body
   - **Purpose**: Quick regeneration without detailed feedback

2. **Regenerate Button Component**:
   - **Placement**: Adjacent to copy button on each draft card
   - **Visual Design**:
     * Refresh/regenerate icon (🔄 or similar)
     * 32px x 32px size matching copy button
     * Distinct color scheme (e.g., orange/amber for "regenerate")
     * Loading spinner during API call
   
   - **Interaction States**:
     * Default: Refresh icon with hover effects
     * Loading: Spinning animation with disabled state
     * Success: Brief checkmark before returning to default
     * Error: Error icon with retry option

3. **User Experience Flow**:
   - **Simple Regeneration**:
     1. User sees draft they don't like
     2. Clicks regenerate button (no feedback required)
     3. API call to `/reject-draft/` with user_id and draft_message_id
     4. Loading state on button while waiting for response
     5. Success: Button shows brief success state
     6. New draft should appear in next polling cycle (5 seconds)
   
   - **Optimistic UI Updates**:
     * Option 1: Keep existing draft until new one arrives
     * Option 2: Show "Generating new draft..." placeholder
     * Option 3: Mark card as "regenerating" with visual indicator

4. **Component Integration**:
   - **DraftMessageCard Updates**:
     * Add regenerate button next to copy button
     * Handle regeneration states (loading, success, error)
     * Visual feedback during regeneration process
   
   - **New Component: RegenerateButton**:
     ```
     DraftMessagesFeed/
     ├── index.tsx (existing)
     ├── DraftMessageCard.tsx (updated)
     ├── CopyButton.tsx (existing)
     ├── RegenerateButton.tsx (new)
     └── ... (Step 5 components)
     ```

5. **State Management**:
   - **Per-Draft Regeneration State**:
     * `regeneratingDrafts: Set<string>` - Track which drafts are being regenerated
     * `regenerationErrors: Record<string, string>` - Per-draft error messages
     * `lastRegeneratedTime: Record<string, number>` - Cooldown tracking
   
   - **Cooldown Logic**:
     * Prevent spam clicking (e.g., 10-second cooldown per draft)
     * Show cooldown timer on button if clicked recently
     * Reset cooldown on successful regeneration

6. **API Error Handling**:
   - **Error Scenarios**:
     * 400 Bad Request → "Cannot regenerate this draft"
     * 404 Not Found → "Draft no longer available"
     * 429 Rate Limited → "Too many requests, please wait"
     * 500 Server Error → "Regeneration service unavailable"
   
   - **Recovery Actions**:
     * Retry button for network errors
     * Clear error state after timeout
     * Fallback to feedback system if regeneration fails

7. **Performance Considerations**:
   - **Rate Limiting**: Client-side cooldown to prevent API abuse
   - **Optimistic Updates**: Consider removing draft immediately vs waiting
   - **Polling Integration**: May need faster polling during active regeneration
   - **Memory Cleanup**: Clear regeneration states when drafts change

8. **Visual Design Specifications**:
   - **Button Layout**:
     * Position: Top-right of card, left of copy button
     * Size: 32px x 32px (matching copy button)
     * Spacing: 8px gap between regenerate and copy buttons
   
   - **Icon States**:
     * Default: Refresh icon (#ff8c00 color)
     * Hover: Darker orange with subtle scale (1.05x)
     * Loading: Spinning animation (360° rotation, 1s duration)
     * Success: Checkmark icon (green, 500ms display)
     * Error: Warning icon (red, with tooltip)
   
   - **Cooldown Indicator**:
     * Circular progress indicator around button
     * Shows remaining cooldown time
     * Fades out when cooldown expires

9. **Integration with Existing Systems**:
   - **Step 3 Compatibility**: Works with current DraftMessagesFeed
   - **Step 5 Coordination**: Regenerate vs. feedback button placement
   - **Polling Enhancement**: Consider faster polling during regeneration
   - **Error Boundaries**: Connect to global error handling

10. **Success Criteria**:
    - ✅ One-click regeneration for any draft message
    - ✅ Clear visual feedback during regeneration process
    - ✅ Rate limiting prevents API abuse
    - ✅ Smooth integration with existing copy functionality
    - ✅ Proper error handling and recovery options
    - ✅ New drafts appear automatically after regeneration

**Technical Implementation Priority**:
1. **RegenerateButton Component**: Core functionality with API integration
2. **State Management**: Add regeneration tracking to DraftMessagesFeed
3. **Visual Integration**: Update DraftMessageCard layout for two buttons
4. **Error Handling**: Comprehensive error states and recovery
5. **Polish**: Cooldown system, animations, and UX enhancements

**Dependencies**:
- Completed Step 3 (DraftMessagesFeed)
- Backend `/reject-draft/` endpoint availability
- Existing API error handling patterns

STEP 5.5 
## Message Sending Implementation Status

### Onboarding Flow (10 Thread Collection) ✅ **FULLY IMPLEMENTED**
**Technical Implementation**:
1. **Thread Detection**: `dom-watcher.ts` extracts LinkedIn messages via `extractMessagesFromDOM()`
2. **Storage Logic**: `storage.ts` tracks collected threads, triggers completion at 10 threads
3. **Backend Submission**: `background/index.ts` sends all 10 threads via `api.sendMessages()` when `isComplete = true`
4. **API Format**: Each thread sent separately with proper message structure per backend.spec.ts

**Code Flow**:
```
LinkedIn Chat → dom-watcher.ts → background/index.ts → storage.storeThread() 
→ [if threadsCollected >= 10] → sendToBackend() → api.sendMessages() per thread
```

**Status**: ✅ Working - sends all 10 collected threads to `/send-messages/` endpoint upon onboarding completion

### Post-Onboarding Browsing ✅ **FULLY IMPLEMENTED**
**Implementation Details**:
- ✅ **Thread Detection**: `handleMessageExtraction()` checks `storage.isComplete()` first
- ✅ **Immediate Send Logic**: Post-onboarding threads trigger `sendSingleThreadToBackend()`
- ✅ **Storage Bypass**: Browsing threads sent directly without storage
- ✅ **Error Handling**: Single thread failures don't break browsing experience

**Code Changes Applied**:
```typescript
// In background/index.ts handleMessageExtraction()
const isComplete = await storage.isComplete();
if (isComplete) {
  // Post-onboarding: Send immediately without storing
  await sendSingleThreadToBackend(thread);
} else {
  // Onboarding: Store the thread and get updated count
  const threadsCollected = await storage.storeThread(thread);
}
```

**New Function Added**:
- ✅ `sendSingleThreadToBackend(thread)`: Sends individual threads immediately
- ✅ Proper API format conversion matching backend.spec.ts
- ✅ Error handling that doesn't interrupt browsing flow

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

## Next Actions (UPDATED)
1. ✅ Create backend.ts file structure
2. ✅ Define API interfaces
3. ✅ Implement getDrafts API function
4. ✅ Create GeneralRoot.tsx component
5. ✅ Create DraftMessagesFeed component structure
6. ✅ Implement WhatsApp-style message cards
7. ✅ Add copy button functionality for easy message copying
8. ✅ Integrate API polling for new drafts
9. ✅ **COMPLETED**: Implement post-onboarding message sending for browsing threads

## Questions to Resolve
1. ✅ Should we add request queuing in Step 1? (Decision: Not needed for initial implementation)
2. ✅ How often should we poll for new drafts? (Decision: Every 5 seconds implemented)
3. ⏳ Should we show timestamps on draft messages?
4. ⏳ Do we need to group drafts by contact/thread?

## Open TODOs
1. ✅ Backend API Definition
2. ✅ Create our API integration layer in `backend.ts`
3. ✅ Implement draft messages feed UI
4. ✅ Add proper copy-to-clipboard functionality
5. ✅ Plan how to handle various API errors

## Next Steps (UPDATED)
1. ✅ Create DraftMessagesFeed component with WhatsApp-style cards
2. ✅ Implement API polling to fetch all drafts from backend buffer
3. ✅ Add copy button functionality for easy message copying
4. ✅ Style components to match WhatsApp message list aesthetic
5. ✅ Add loading and error states

## Questions for Clarification
1. ✅ Should draft messages be grouped by contact or show as one continuous feed? (Decision: Continuous feed implemented)
2. ⏳ What information should we show beyond name and message (timestamp, thread info)?
3. ✅ Should we implement automatic refresh or just manual refresh for now? (Decision: Automatic 5-second polling implemented)

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)

**Updated Header Layout**:
```
[Inbox|Chat Toggle] [Title: "Inbox" OR "Chat with Daren Hua"]
```

#### 3. **State Management Extensions**
- **GeneralRoot Component Updates**: `src/sidepanel/views/general/GeneralRoot.tsx`
- **New State Variables**:
  * `interfaceMode: 'inbox' | 'chat'` - Current interface mode
  * `counterpartyName: string` - Existing (keep for chat mode)
- **State Persistence**: Use localStorage to remember user's preferred mode

#### 4. **Inbox Interface (Current Functionality)**
- **Components**: Keep existing `DraftMessagesFeed` and all sub-components
- **Location**: `src/sidepanel/views/general/DraftMessagesFeed/`
- **Functionality**: No changes - maintains current behavior:
  * Draft messages display in WhatsApp-style cards
  * Copy button functionality  
  * Feedback system (Step 5 components)
  * Polling for new drafts every 5 seconds
- **Title**: Shows "Inbox" instead of "Chat with [Name]"

#### 5. **Chat Interface (New Component)**
- **New Component**: `src/sidepanel/views/general/ChatInterface/`
- **Component Structure**:
```
src/sidepanel/views/general/ChatInterface/
├── index.tsx (main ChatInterface component)
├── MessageBubble.tsx (individual message display)
├── MessageInput.tsx (typing interface)
└── ChatHistory.tsx (conversation history)
```

- **Functionality Specifications**:
  * **Conversational UI**: Chat bubble interface similar to messaging apps
  * **Message History**: Show recent conversation with current contact
  * **Input Interface**: Text input with send button for direct messaging
  * **Thread Context**: Maintain context of current LinkedIn thread
  * **Real-time Updates**: Integrate with existing message detection from `dom-watcher.ts`

#### 6. **Interface Mode Routing**
- **GeneralRoot Component Logic**:
```typescript
const renderContent = () => {
  switch (interfaceMode) {
    case 'inbox':
      return <DraftMessagesFeed userId={userId} />;
    case 'chat':
      return <ChatInterface userId={userId} threadName={counterpartyName} />;
    default:
      return <DraftMessagesFeed userId={userId} />;
  }
};
```

#### 7. **Integration with Existing Systems**

**Thread Detection Integration**:
- **Source**: `dom-watcher.ts` currently extracts LinkedIn thread data
- **Current Flow**: `dom-watcher.ts` → `background/index.ts` → `GeneralRoot.tsx`
- **Enhanced Flow**: Same detection, but ChatInterface can utilize thread context differently than DraftMessagesFeed

**API Integration**:
- **Inbox Mode**: Uses existing `api.getDrafts()` from `src/api/backend.ts`
- **Chat Mode**: May utilize existing message sending APIs or require new endpoints
- **Shared State**: Both modes can access same user context and thread information

#### 8. **User Experience Flow**

**Default Experience (Inbox Mode)**:
1. User opens sidepanel → Toggle defaults to "Inbox"
2. Header shows "Inbox" title
3. Interface shows current draft messages feed
4. All existing functionality remains unchanged

**Switching to Chat Mode**:
1. User clicks "Chat" in toggle → Interface switches
2. Header updates to "Chat with [Current Contact Name]"
3. Interface shows new chat interface with conversation history
4. User can interact directly with conversation context

**Mode Persistence**:
- User's last selected mode saved to localStorage
- Restored on next sidepanel open
- Per-user preference (tied to userId if needed)

#### 9. **Technical Implementation Priority**

**Phase 1: Toggle Infrastructure** ⏳
- Create ModeToggle component
- Update Header component to include toggle
- Add mode state management to GeneralRoot
- Implement basic mode switching (inbox/chat)

**Phase 2: Interface Routing** ⏳
- Implement conditional rendering in GeneralRoot
- Ensure inbox mode maintains current functionality
- Add placeholder ChatInterface component

**Phase 3: Chat Interface Development** ⏳
- Build ChatInterface component structure
- Implement message bubble UI
- Add message input functionality
- Integrate with existing thread detection

**Phase 4: Integration & Polish** ⏳
- Connect ChatInterface with backend APIs
- Add smooth transitions between modes
- Implement state persistence
- Test end-to-end functionality

#### 10. **Component Dependencies**

**Existing Components (No Changes)**:
- `src/sidepanel/views/general/DraftMessagesFeed/` - All existing functionality preserved
- `src/content/dom-watcher.ts` - Thread detection continues to work for both modes
- `src/api/backend.ts` - API functions remain available for both interfaces

**Updated Components**:
- `src/sidepanel/views/general/Header.tsx` - Add toggle and conditional title
- `src/sidepanel/views/general/GeneralRoot.tsx` - Add mode state and routing logic

**New Components**:
- `src/sidepanel/views/general/ModeToggle.tsx` - Toggle switch component
- `src/sidepanel/views/general/ChatInterface/` - Complete new interface for chat mode

#### 11. **Success Criteria**
- ✅ Toggle switch appears in header and functions correctly
- ✅ Inbox mode maintains all current functionality unchanged
- ✅ Chat mode shows new interface with thread context
- ✅ Header title updates correctly based on selected mode
- ✅ Mode preference persists across sessions
- ✅ Smooth transitions between modes without data loss
- ✅ Both modes integrate properly with existing thread detection

#### 12. **Design Specifications**

**Toggle Visual Design**:
- **Size**: 120px width × 32px height
- **Positioning**: 16px from left edge of header
- **Spacing**: 16px gap between toggle and title
- **Active State**: Primary blue (#3b82f6) background
- **Inactive State**: Light gray (#f3f4f6) background
- **Typography**: 14px font size, medium weight

**Header Layout Updates**:
```
[16px] [Toggle: Inbox|Chat] [16px] [Title] [16px]
```

**Responsive Behavior**:
- Toggle remains visible on all screen sizes
- Title truncates if needed to accommodate toggle
- Maintains current header height (no layout shift)

#### 13. **Future Enhancements**
- **Badge System**: Show unread count on toggle options
- **Mode-Specific Settings**: Different preferences for each mode
- **Quick Actions**: Mode-specific shortcuts or actions
- **Keyboard Shortcuts**: Alt+I for Inbox, Alt+C for Chat

## Current Status
✅ COMPLETED Step 1: API Integration Layer
✅ COMPLETED Step 2: Base General UX Structure
✅ COMPLETED Step 3: Draft Messages Feed Display
⏳ PENDING Step 4: Polish & Error Handling
🔄 IN PROGRESS Step 5: Interactive Feedback System & Thread Context
   - ✅ Phase 1: Thread Detection (COMPLETED)
   - ✅ Phase 2: Feedback UI Components (COMPLETED)
   - ⏳ Phase 3: Thread Matching & Prioritization (PENDING)
   - ⏳ Phase 4: Integration & Polish (PENDING)
⏳ PENDING Step 6: Quick Draft Regeneration System
✅ **COMPLETED**: Step 5.5 - Post-Onboarding Message Sending Implementation

### Step 7: Inbox/Chat Toggle Interface ⏳
**Commit Message**: "feat: Add inbox/chat toggle with dual interface modes"

**PLANNED IMPLEMENTATION** - Technical Specifications:

#### Overview
Add a toggle switch to the header that allows users to switch between two distinct interface modes:
- **Inbox Mode**: Current draft messages feed functionality (default)
- **Chat Mode**: New conversational interface for direct interaction

#### Current State Analysis
Based on project research:
- **Header Component**: Located at `src/sidepanel/views/general/Header.tsx` - currently shows dynamic title "Chat with [Name]"
- **GeneralRoot Component**: Located at `src/sidepanel/views/general/GeneralRoot.tsx` - manages counterparty name state and renders header + draft feed
- **Draft Feed**: Located at `src/sidepanel/views/general/DraftMessagesFeed/` - current main interface showing draft messages

#### 1. **Toggle Component Implementation**
- **New Component**: `src/sidepanel/views/general/ModeToggle.tsx`
- **Visual Design**:
  * Segmented control with two options: "Inbox" | "Chat"
  * Position: Top-left of header, before the title
  * Size: Compact toggle (width: 120px, height: 32px)
  * Styling: Material-UI styled toggle buttons
  * Active state: Highlighted with primary color (#3b82f6)

```typescript
interface ModeToggleProps {
  mode: 'inbox' | 'chat';
  onModeChange: (mode: 'inbox' | 'chat') => void;
}
```

#### 2. **Header Component Updates**
- **File**: `src/sidepanel/views/general/Header.tsx`
- **Current Implementation**: Shows "Chat with {counterpartyName}" dynamically
- **New Implementation**:
  * Add toggle component to left side of header
  * Conditional title display based on mode:
    - Inbox mode: "Inbox" (static title)
    - Chat mode: "Chat with {counterpartyName}" (dynamic title)