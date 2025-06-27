import { storage } from '../logic/storage';
import { LinkedInThread } from '../logic/html-parser';
import { api } from '../api/backend';

/**
 * Handles the initial setup of the extension.
 */
chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed.');
  // Set up the side panel to open on action click
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  // Initialize storage when extension loads
  storage.initialize().catch(console.error);
});

/**
 * Main message listener for the extension.
 */
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'LINKEDIN_MESSAGES_EXTRACTED') {
    handleMessageExtraction(message.payload).catch(console.error);
  }
});

async function handleMessageExtraction(thread: LinkedInThread) {
  try {
    // Check if collection is already complete (post-onboarding browsing)
    const isComplete = await storage.isComplete();
    
    if (isComplete) {
      // Post-onboarding: Send immediately without storing
      console.log('Post-onboarding browsing: sending thread immediately to backend');
      await sendSingleThreadToBackend(thread);
    } else {
      // Onboarding: Store the thread and get updated count
      const threadsCollected = await storage.storeThread(thread);
      
      // Check if collection just completed
      const isNowComplete = await storage.isComplete();
      
      // Notify all sidepanels about the update
      const message = {
        type: 'COLLECTION_UPDATE',
        payload: {
          threadsCollected,
          isComplete: isNowComplete,
        }
      };
      
      // Broadcast to all extension views
      chrome.runtime.sendMessage(message).catch(() => {
        // Ignore errors from no listeners
      });

      // If we just completed collection, send all collected threads to backend
      if (isNowComplete) {
        // Properly await the backend upload process
        console.log('🚀 Starting onboarding completion: sending all 10 threads to backend...');
        try {
          await sendToBackend();
          
          // Only notify success after all threads are actually sent
          chrome.runtime.sendMessage({
            type: 'UPLOAD_COMPLETE',
            payload: {
              success: true
            }
          }).catch(() => {
            // Ignore errors from no listeners
          });
          
          console.log('✅ Onboarding completion successful: all threads sent to backend');
        } catch (error) {
          console.error('❌ Onboarding completion failed:', error);
          
          // Notify failure if backend upload fails
          chrome.runtime.sendMessage({
            type: 'UPLOAD_COMPLETE',
            payload: {
              success: false,
              error: error instanceof Error ? error.message : 'Unknown error occurred'
            }
          }).catch(() => {
            // Ignore errors from no listeners
          });
        }
      }
    }
    
    // Always forward the thread information to the sidepanel
    chrome.runtime.sendMessage({
      type: 'LINKEDIN_MESSAGES_EXTRACTED',
      payload: thread
    }).catch(() => {
      // Ignore errors from no listeners
    });
    
  } catch (error) {
    console.error('Error handling message extraction:', error);
  }
}

/**
 * Sends a single thread to backend immediately (for post-onboarding browsing)
 */
async function sendSingleThreadToBackend(thread: LinkedInThread) {
  try {
    const userId = await storage.getUserId();
    if (!userId) {
      throw new Error('No user ID available');
    }
    
    console.log(`Sending single thread to backend: ${thread.threadName} with ${thread.messages.length} messages`);
    
    // Convert thread format to match API spec
    const messages = thread.messages.map(msg => ({
      message_id: msg.id,
      sender_name: msg.sender,
      date: msg.date,
      time: msg.time,
      message_content: msg.snippet
    }));
    
    await api.sendMessages({
      user_id: userId,
      thread_name: thread.threadName,
      messages: messages
    });
    
    console.log(`Successfully sent single thread: ${thread.threadName}`);
  } catch (error) {
    console.error('Error sending single thread to backend:', error);
    // Don't throw - we don't want to break the browsing experience
  }
}

/**
 * Sends a single thread with retry logic for server errors
 */
async function sendThreadWithRetry(
  requestPayload: { user_id: string; thread_name: string; messages: any[] },
  threadName: string,
  threadNumber: number,
  totalThreads: number,
  maxRetries: number = 3
): Promise<void> {
  let lastError: Error | null = null;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      if (attempt > 1) {
        console.log(`🔄 Retry attempt ${attempt}/${maxRetries} for thread "${threadName}"`);
      }
      
      await api.sendMessages(requestPayload);
      
      if (attempt > 1) {
        console.log(`✅ Thread "${threadName}" sent successfully on retry attempt ${attempt}`);
      }
      
      return; // Success - exit the retry loop
      
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error');
      
      if (lastError.message.includes('422')) {
        console.warn(`Encountered a 422 error for thread "${threadName}". This thread's data may be malformed. Skipping and continuing.`);
        return; // Don't retry, just continue to the next thread
      }
      
      // Check if it's a server error that we should retry
      const shouldRetry = (
        lastError.message.includes('502') ||
        lastError.message.includes('503') ||
        lastError.message.includes('504') ||
        lastError.message.includes('Server Error') ||
        lastError.message.includes('Backend server is unavailable') ||
        lastError.message.includes('Backend service is temporarily unavailable') ||
        lastError.message.includes('Backend server timeout')
      );
      
      if (shouldRetry && attempt < maxRetries) {
        const retryDelayMs = Math.min(1000 * Math.pow(2, attempt - 1), 10000); // Exponential backoff, max 10s
        console.log(`⚠️  Thread ${threadNumber}/${totalThreads} "${threadName}" failed (attempt ${attempt}/${maxRetries}): ${lastError.message}`);
        console.log(`⏱️  Retrying in ${retryDelayMs}ms...`);
        await new Promise(resolve => setTimeout(resolve, retryDelayMs));
      } else if (!shouldRetry) {
        // Don't retry for client errors (4xx) or non-server errors
        console.error(`❌ Thread ${threadNumber}/${totalThreads} "${threadName}" failed with non-retryable error:`, lastError.message);
        throw lastError;
      } else {
        // Max retries reached
        console.error(`❌ Thread ${threadNumber}/${totalThreads} "${threadName}" failed after ${maxRetries} attempts:`, lastError.message);
        throw lastError;
      }
    }
  }
  
  // This should never be reached, but just in case
  throw lastError || new Error('Unknown error in retry logic');
}

/**
 * Sends all collected threads to backend (for onboarding completion)
 * Includes rate limiting and detailed logging
 */
async function sendToBackend() {
  const userId = await storage.getUserId();
  if (!userId) {
    throw new Error('No user ID available');
  }
  
  const threads = await storage.getCollectedThreads();
  const threadEntries = Object.entries(threads);
  
  console.log('📤 ONBOARDING UPLOAD: Starting bulk thread upload');
  console.log(`📊 Upload Details:`, { 
    userId, 
    totalThreads: threadEntries.length,
    threadNames: threadEntries.map(([name]) => name)
  });
  
  // Send each thread separately with rate limiting
  for (let i = 0; i < threadEntries.length; i++) {
    const [threadName, thread] = threadEntries[i];
    const threadNumber = i + 1;
    
    console.log(`\n🔄 Sending thread ${threadNumber}/${threadEntries.length}: "${threadName}"`);
    console.log(`📝 Thread contains ${thread.messages.length} messages`);
    
    // Convert thread format to match API spec
    const messages = thread.messages.map(msg => ({
      message_id: msg.id,
      sender_name: msg.sender,
      date: msg.date,
      time: msg.time,
      message_content: msg.snippet
    }));
    
    const requestPayload = {
      user_id: userId,
      thread_name: threadName,
      messages: messages
    };
    
    console.log(`🚀 API Request for "${threadName}":`, {
      endpoint: '/send-messages/',
      user_id: userId,
      thread_name: threadName,
      message_count: messages.length
    });
    
    try {
      // Make the API call with retry logic for server errors
      await sendThreadWithRetry(requestPayload, threadName, threadNumber, threadEntries.length);
      
      console.log(`✅ Thread ${threadNumber}/${threadEntries.length} sent successfully: "${threadName}"`);
      
      // Add delay between requests to avoid rate limiting (except for the last one)
      if (i < threadEntries.length - 1) {
        const delayMs = 100; // 0.1 second delay between requests
        console.log(`⏱️  Waiting ${delayMs}ms before sending next thread...`);
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
      
    } catch (error) {
      console.error(`❌ Failed to send thread ${threadNumber}/${threadEntries.length}: "${threadName}"`, error);
      throw new Error(`Failed to send thread "${threadName}": ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  console.log(`\n🎉 ONBOARDING UPLOAD COMPLETE: All ${threadEntries.length} threads sent successfully to backend`);
}

// Note: The onUpdated listener for the side panel is removed as the
// onInstalled listener now handles enabling the side panel globally.
// If you need per-tab logic, you can add it back here. 