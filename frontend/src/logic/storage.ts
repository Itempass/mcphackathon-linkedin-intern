import { LinkedInThread } from './html-parser';
import { v4 as uuidv4 } from 'uuid';

interface StorageState {
  userId: string | null;
  collectedThreads: {
    [threadName: string]: LinkedInThread;
  };
  threadsCollected: number;
  isComplete: boolean;
}

const INITIAL_STATE: StorageState = {
  userId: null,
  collectedThreads: {},
  threadsCollected: 0,
  isComplete: false,
};

export class StorageManager {
  private static instance: StorageManager;
  
  private constructor() {}

  static getInstance(): StorageManager {
    if (!StorageManager.instance) {
      StorageManager.instance = new StorageManager();
    }
    return StorageManager.instance;
  }

  async initialize(): Promise<void> {
    const state = await this.getState();
    if (!state.userId) {
      await this.setState({
        ...INITIAL_STATE,
        userId: uuidv4(),
      });
    }
  }

  async storeThread(thread: LinkedInThread): Promise<number> {
    const state = await this.getState();
    
    // Don't store if we're already complete and not just updating
    if (state.isComplete && !state.collectedThreads[thread.threadName]) {
      return state.threadsCollected;
    }

    const existingThread = state.collectedThreads[thread.threadName];

    if (existingThread) {
      // Thread exists, merge new messages, avoiding duplicates
      const existingMessageIds = new Set(existingThread.messages.map(m => m.id));
      const newMessages = thread.messages.filter(m => !existingMessageIds.has(m.id));

      if (newMessages.length > 0) {
        const updatedThread = {
          ...existingThread,
          messages: [...existingThread.messages, ...newMessages],
        };

        const newState = {
          ...state,
          collectedThreads: {
            ...state.collectedThreads,
            [thread.threadName]: updatedThread,
          },
        };

        await this.setState(newState);
      }
      return state.threadsCollected; // Return original count as we're just updating
    } else {
      // A new thread is being added
      if(state.isComplete) return state.threadsCollected; // Should not happen based on above logic, but as a safeguard.

      const newState = {
        ...state,
        collectedThreads: {
          ...state.collectedThreads,
          [thread.threadName]: thread,
        },
        threadsCollected: state.threadsCollected + 1,
      };
  
      // Check if we've reached 10 threads
      if (newState.threadsCollected >= 10) {
        newState.isComplete = true;
      }
  
      await this.setState(newState);
      return newState.threadsCollected;
    }
  }

  async isComplete(): Promise<boolean> {
    const state = await this.getState();
    return state.isComplete;
  }

  async getCollectedThreads(): Promise<{ [threadName: string]: LinkedInThread }> {
    const state = await this.getState();
    return state.collectedThreads;
  }

  async getUserId(): Promise<string | null> {
    const state = await this.getState();
    return state.userId;
  }

  private async getState(): Promise<StorageState> {
    return new Promise((resolve) => {
      chrome.storage.local.get('linkedInAssistant', (result) => {
        resolve(result.linkedInAssistant || INITIAL_STATE);
      });
    });
  }

  private async setState(state: StorageState): Promise<void> {
    return new Promise((resolve) => {
      chrome.storage.local.set({ linkedInAssistant: state }, resolve);
    });
  }
}

// Export a singleton instance
export const storage = StorageManager.getInstance(); 