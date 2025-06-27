import { getFormattedDate, generateId, convertTo24HourFormat } from './linkedin-helpers';

export interface LinkedInMessage {
  id: string;
  sender: string;
  snippet: string;
  date: string;
  time: string;
}

export interface LinkedInThread {
  threadName: string;
  messages: LinkedInMessage[];
}

/**
 * Extracts thread name using multiple fallback selectors for LinkedIn messaging
 */
function extractThreadName(): string {
  console.log('Attempting to extract thread name from LinkedIn messaging interface...');
  
  // Multiple selectors to try for thread name/counterparty name
  const threadSelectors = [
    // Modern LinkedIn messaging selectors
    '.msg-thread-header__participant-name',
    '.msg-conversation-header__participant-name', 
    '.msg-thread-header h2',
    '.msg-conversation-card__participant-name',
    '.conversation-header__participant-name',
    
    // Fallback selectors
    '#thread-detail-jump-target',
    '.thread-detail-header h2',
    '.msg-s-header h2',
    
    // Page title fallback
    'title'
  ];
  
  for (const selector of threadSelectors) {
    try {
      const element = document.querySelector(selector);
      if (element && element.textContent) {
        const rawText = element.textContent.trim();
        console.log(`Found thread name with selector "${selector}": "${rawText}"`);
        
        // If it's the page title, extract the name from "LinkedIn | Messaging | [Name]" format
        if (selector === 'title') {
          const titleMatch = rawText.match(/LinkedIn.*?Messaging.*?\|\s*(.+)$/);
          if (titleMatch && titleMatch[1]) {
            const extractedName = titleMatch[1].trim();
            console.log(`Extracted name from title: "${extractedName}"`);
            return extractedName;
          }
        }
        
        // Clean up common prefixes/suffixes
        let cleanName = rawText
          .replace(/^(Chat with|Conversation with|Message)\s+/i, '')
          .replace(/\s+\([\d\s]+\)$/, '') // Remove "(3)" type suffixes
          .trim();
        
        if (cleanName && cleanName !== 'Unknown' && cleanName.length > 0) {
          console.log(`Final extracted thread name: "${cleanName}"`);
          return cleanName;
        }
      }
    } catch (error) {
      console.warn(`Error with selector "${selector}":`, error);
    }
  }
  
  console.warn('No thread name found with any selector, using fallback');
  return 'Unknown Thread';
}

/**
 * Extracts all messages from the provided LinkedIn chat container element.
 * @param chatContainer The DOM element for '.msg-s-message-list-content'.
 * @returns A promise that resolves to a structured thread object.
 */
export async function extractMessagesFromDOM(chatContainer: HTMLElement): Promise<LinkedInThread> {
  const threadName = extractThreadName();

  const messagePromises: Promise<LinkedInMessage>[] = [];
  let lastSeenDate = getFormattedDate("Today");
  let lastSeenSender = "Unknown";
  let lastSeenTime = "Unknown";

  const messageItems = Array.from(chatContainer.querySelectorAll<HTMLLIElement>(':scope > li'));

  for (const li of messageItems) {
    const dateHeading = li.querySelector('time.msg-s-message-list__time-heading');
    if (dateHeading) {
      lastSeenDate = getFormattedDate(dateHeading.textContent?.trim() ?? '');
    }

    const eventItems = Array.from(li.querySelectorAll<HTMLDivElement>('.msg-s-event-listitem'));

    for (const messageItem of eventItems) {
      const nameElement = messageItem.querySelector('.msg-s-message-group__name');
      const timeElement = messageItem.querySelector('time.msg-s-message-group__timestamp');

      if (nameElement && timeElement) {
        lastSeenSender = nameElement.textContent?.trim() ?? 'Unknown';
        // Convert LinkedIn time format to 24-hour format for backend compatibility
        const rawTime = timeElement.textContent?.trim() ?? 'Unknown';
        lastSeenTime = convertTo24HourFormat(rawTime);
        console.log(`Converted time from "${rawTime}" to "${lastSeenTime}"`);
      }

      const messageBody = messageItem.querySelector('.msg-s-event-listitem__body');
      if (messageBody) {
        const snippet = messageBody.textContent?.trim();
        if (snippet) {
          const messageData = { sender: lastSeenSender, snippet, date: lastSeenDate, time: lastSeenTime };
          const messagePromise = generateId(lastSeenSender, lastSeenDate, lastSeenTime, snippet)
            .then(id => ({ ...messageData, id }));
          messagePromises.push(messagePromise);
        }
      }
    }
  }

  const messages = await Promise.all(messagePromises);
  return { threadName, messages };
} 