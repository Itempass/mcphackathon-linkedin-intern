/**
 * TypeScript interfaces for the database models.
 * Based on the schema in `documents/external resources/models.py.txt`.
 */

export enum MessageType {
  DRAFT = "DRAFT",
  MESSAGE = "MESSAGE",
}

export interface Message {
  id: string;
  user_id: string;
  msg_content: string;
  type: MessageType;
  thread_name: string;
  sender_name: string;
  timestamp: string; // Stored as ISO 8601 string
  agent_id?: string | null;
}

export interface AgentMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  tool_calls?: any[];
  name?: string;
  tool_call_id?: string;
  timestamp?: string; // ISO 8601 string
  duration?: number; // in seconds, for tool messages
  model?: string;    // for assistant messages
  tokens?: number;   // for assistant messages
  price?: number;    // for assistant messages
}

export interface Agent {
  id: string;
  user_id: string;
  // This 'messages' field is the raw JSON string from the DB
  messages: string; 
}

/**
 * This interface represents the processed Agent data with its associated threads.
 */
export interface ProcessedAssistantWithThreads {
  id: string;
  user_id: string;
  systemPrompt: string | null;
  threads: string[]; // list of thread_name
}

export interface ToolCallInfo {
  id: string;
  name: string;
  arguments: string;
  result: string;
  duration?: number;
  model?: string;
  tokens?: number;
  price?: number;
}

export interface ThreadDetail {
  id: string; // agent_id
  thread_name: string;
  user_id: string;
  created_at: string; // ISO 8601 string
  cycles: number;
  messages: number;
  tool_chain: ToolCallInfo[];
} 