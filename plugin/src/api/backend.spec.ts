/**
 * Backend API Specification
 * This file serves as the source of truth for our backend API contract.
 */

export interface APISpec {
  endpoints: {
    sendMessages: {
      method: 'POST';
      path: '/send-messages/';
      request: {
        user_id: string;
        thread_name: string;
        messages: Array<{
          message_id: string;      // hash of sender name, date+time, message content
          sender_name: string;     // name of sender
          date: string;           // date of message sent
          time: string;           // time of message sent
          message_content: string;
        }>;
      };
      response: {
        status: 202;              // ACCEPTED
        body: void;
      };
    };

    processFeedback: {
      method: 'POST';
      path: '/process-feedback/';
      request: {
        user_id: string;
        draft_message_id: string;
        feedback: string;
      };
      response: {
        status: 202;              // ACCEPTED
        body: void;
      };
    };

    rejectDraft: {
      method: 'POST';
      path: '/reject-draft/';
      request: {
        user_id: string;
        draft_message_id: string;
      };
      response: {
        status: 200;              // OK
        body: void;
      };
    };

    getDraftMessages: {
      method: 'GET';
      path: '/draft-messages/';
      queryParams: {              // Changed from body to queryParams since it's GET
        user_id: string;
      };
      response: {
        status: 200;              // OK
        body: {
          draft_messages: Array<{
            thread_name: string;
            draft_message_id: string;
            draft_message_content: string;
          }>;
        };
      };
    };
  };
}

/**
 * Issues found when comparing with current implementation:
 * 1. GET /draft_messages/ should use query parameters, not body
 * 2. Response types match but need explicit void for 202 responses
 * 3. All type names in our implementation match the spec
 */ 