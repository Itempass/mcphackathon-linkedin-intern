import { extractMessagesFromDOM } from '../logic/html-parser';
import { debounce } from '../utils/debounce';

chrome.runtime.sendMessage({ type: 'LINKEDIN_MESSAGING_PAGE_LOADED' });

console.log("LinkedIn Message Extractor content script loaded.");

let observedElement: HTMLElement | null = null;

/**
 * Sends a message to the background script with retry logic
 * @param message The message to send
 * @param retries Number of retries left
 * @returns Promise that resolves when message is sent or max retries reached
 */
async function sendMessageWithRetry(message: any, retries = 3): Promise<void> {
  try {
    await chrome.runtime.sendMessage(message);
  } catch (error: any) {
    if (error.message === 'Extension context invalidated.' || !chrome.runtime) {
      console.log('Extension context invalid, reloading content script...');
      // The extension was reloaded/updated, we should stop processing
      messageListObserver.disconnect();
      observedElement = null;
      return;
    }
    
    if (retries > 0) {
      console.log(`Retrying message send, ${retries} attempts left`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s before retry
      return sendMessageWithRetry(message, retries - 1);
    }
    
    console.error('Failed to send message after retries:', error);
  }
}

/**
 * The main function to process messages from the chat container.
 * It calls the parser and sends the structured data to the background script.
 */
async function processMessages() {
  const chatContainer = document.querySelector<HTMLElement>('.msg-s-message-list-content');
  if (!chatContainer) {
    console.warn("Could not find chat container for processing.");
    return;
  }

  try {
    console.log("Processing messages in chat container...");
    const threadData = await extractMessagesFromDOM(chatContainer);

    if (threadData && threadData.messages.length > 0) {
      console.log(`Extracted ${threadData.messages.length} messages. Sending to background.`);
      await sendMessageWithRetry({
        type: 'LINKEDIN_MESSAGES_EXTRACTED',
        payload: threadData,
      });
    } else {
      console.log("No messages found in the current view to process.");
    }
  } catch (error) {
    console.error('Error processing messages:', error);
  }
}

const debouncedProcessMessages = debounce(processMessages, 200);

/**
 * An observer that watches for changes within the message list itself.
 * This triggers reprocessing when new messages are added, etc.
 */
const messageListObserver = new MutationObserver(() => {
  console.log("Message list changed, debouncing message processing.");
  debouncedProcessMessages();
});

/**
 * Sets up the message list observer on the chat container.
 * This function is the core of the "smart watcher".
 */
function setupMessageObserver() {
  try {
    const chatContainer = document.querySelector<HTMLElement>('.msg-s-message-list-content');

    if (chatContainer) {
      // If we're already observing the correct element, do nothing.
      if (observedElement === chatContainer) return;

      console.log("LinkedIn chat container found. Starting message observer.");
      // Disconnect any previous observer before starting a new one.
      messageListObserver.disconnect();
      
      // Process messages once immediately on discovery.
      processMessages().catch(console.error);
      
      // Start observing the container for new messages.
      messageListObserver.observe(chatContainer, { childList: true, subtree: true });
      observedElement = chatContainer;
    } else {
      // If the container is gone, disconnect the observer.
      if (!observedElement) return;
      
      console.log("Chat container not found. Disconnecting message observer.");
      messageListObserver.disconnect();
      observedElement = null;
    }
  } catch (error) {
    console.error('Error in setupMessageObserver:', error);
  }
}

// Initial check in case the script loads after the page is ready.
setupMessageObserver();

// Start observing the whole page for the chat container.
const documentObserver = new MutationObserver(() => {
  if (!chrome.runtime) {
    console.log('Extension context invalid, stopping document observer...');
    documentObserver.disconnect();
    return;
  }
  setupMessageObserver();
});

documentObserver.observe(document.body, {
  childList: true,
  subtree: true
}); 