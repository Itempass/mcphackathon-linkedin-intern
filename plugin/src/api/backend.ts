// Types for API requests and responses
export interface LinkedInMessage {
  message_id: string;      // hash of sender name, date+time, message content
  sender_name: string;     // name of sender
  date: string;           // date of message sent
  time: string;           // time of message sent
  message_content: string;
}

export interface SendMessagesRequest {
  user_id: string;
  thread_name: string;
  messages: LinkedInMessage[];
}

export interface DraftMessage {
  thread_name: string;
  draft_message_id: string;
  draft_message_content: string;
}

export interface SubmitFeedbackRequest {
  user_id: string;
  draft_message_id: string;
  feedback: string;
}

export interface DraftMessagesResponse {
  draft_messages: DraftMessage[];
}

export interface GetDraftsResponse {
  draft_messages: DraftMessage[];
}

export interface FeedbackRequest {
  user_id: string;
  draft_message_id: string;
  feedback: string;
}

export interface RejectDraftRequest {
  user_id: string;
  draft_message_id: string;
}

// Error handling
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public endpoint?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const DEBUG_LOGGING = import.meta.env.VITE_ENABLE_DEBUG_LOGGING === 'true';

console.log('API Configuration:', {
  API_BASE_URL,
  DEBUG_LOGGING,
  env: import.meta.env
});

// API utilities
async function handleResponse<T>(response: Response, endpoint: string): Promise<T> {
  if (DEBUG_LOGGING) {
    console.log(`API ${endpoint} response:`, {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries()),
    });
  }

  if (!response.ok) {
    // Get the content type to determine how to handle the error
    const contentType = response.headers.get('content-type') || '';
    let errorMessage = '';
    let errorDetails = '';
    
    // Handle different types of error responses
    if (response.status >= 500 && response.status < 600) {
      // 5xx Server Errors
      errorMessage = `Server Error (${response.status}): ${response.statusText}`;
    } else if (response.status === 502) {
      // Specific handling for 502 Bad Gateway
      errorMessage = `Backend server is unavailable (502 Bad Gateway)`;
    } else if (response.status === 503) {
      // Service Unavailable
      errorMessage = `Backend service is temporarily unavailable (503)`;
    } else if (response.status === 504) {
      // Gateway Timeout
      errorMessage = `Backend server timeout (504)`;
    } else {
      // Other errors (4xx, etc.)
      errorMessage = `API call failed (${response.status}): ${response.statusText}`;
    }
    
    try {
      const errorBody = await response.text();
      
      // Check if the response is HTML (common for server errors)
      if (contentType.includes('text/html') || errorBody.trim().startsWith('<!DOCTYPE html>')) {
        console.error(`❌ ${endpoint} returned HTML error page (Status: ${response.status})`);
        console.error('HTML error response preview:', errorBody.substring(0, 200) + '...');
        
        // Extract meaningful error from HTML if possible
        const titleMatch = errorBody.match(/<title>(.*?)<\/title>/i);
        if (titleMatch) {
          errorDetails = `Server returned: ${titleMatch[1]}`;
        } else {
          errorDetails = 'Server returned HTML error page (likely 502/503/504)';
        }
      } else if (contentType.includes('application/json')) {
        // Try to parse JSON error
        try {
          const errorJson = JSON.parse(errorBody);
          errorDetails = errorJson.message || errorJson.error || 'Unknown JSON error';
        } catch {
          errorDetails = errorBody;
        }
      } else {
        // Plain text or other format
        errorDetails = errorBody.substring(0, 200); // Limit to first 200 chars
      }
      
      if (DEBUG_LOGGING) {
        console.error(`API ${endpoint} error body (${contentType}):`, errorBody);
      }
    } catch (e) {
      console.warn('Could not read error response body:', e);
      errorDetails = 'Could not read error details';
    }

    const fullErrorMessage = errorDetails 
      ? `${errorMessage} - ${errorDetails}` 
      : errorMessage;

    throw new APIError(
      fullErrorMessage,
      response.status,
      endpoint
    );
  }

  // For 202 ACCEPTED responses, we don't expect a body
  if (response.status === 202) {
    return undefined as unknown as T;
  }

  try {
    const data = await response.json();
    if (DEBUG_LOGGING) {
      console.log(`API ${endpoint} data:`, data);
    }
    return data;
  } catch (error) {
    throw new APIError(
      'Failed to parse API response as JSON',
      response.status,
      endpoint
    );
  }
}

// API endpoints
export const api = {
  /**
   * Send collected messages to the backend
   * @returns void (202 ACCEPTED)
   */
  async sendMessages(request: SendMessagesRequest): Promise<void> {
    const url = `${API_BASE_URL}/send-messages/`;
    
    console.log('Making API call to:', url);
    console.log('API_BASE_URL:', API_BASE_URL);
    console.log('Send Messages Request:', {
      user_id: request.user_id,
      thread_name: request.thread_name,
      message_count: request.messages.length
    });
    console.log('Full request payload:', request);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      console.log('Raw response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: response.url
      });

      await handleResponse<void>(response, '/send-messages/');
      
      console.log(`Successfully sent messages for thread: ${request.thread_name}`);
    } catch (error) {
      console.error('Fetch error in sendMessages:', error);
      console.error('Failed request details:', {
        url,
        thread_name: request.thread_name,
        user_id: request.user_id,
        message_count: request.messages.length
      });
      throw error;
    }
  },

  /**
   * Get draft messages for a user
   * @returns DraftMessagesResponse (200 OK)
   */
  async getDrafts(userId: string): Promise<GetDraftsResponse> {
    const url = new URL(`${API_BASE_URL}/draft-messages/`);
    url.searchParams.append('user_id', userId);

    console.log('Making API call to:', url.toString());
    console.log('API_BASE_URL:', API_BASE_URL);
    console.log('User ID:', userId);

    try {
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('Raw response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: response.url
      });

      return handleResponse<GetDraftsResponse>(response, '/draft-messages/');
    } catch (error) {
      console.error('Fetch error in getDrafts:', error);
      throw error;
    }
  },

  /**
   * Submit feedback for a draft message
   * @returns void (202 ACCEPTED)
   */
  async submitFeedback(request: FeedbackRequest): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/process-feedback/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    await handleResponse<void>(response, '/process-feedback/');
  },

  /**
   * Reject a draft message and request a new one
   * @returns void (200 OK)
   */
  async rejectDraft(request: RejectDraftRequest): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/reject-draft/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    await handleResponse<void>(response, '/reject-draft/');
  },
};

// Export a singleton instance
export default api; 