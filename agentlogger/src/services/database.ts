import pool from '@/lib/db';
import { Agent, AgentMessage, Message, ThreadDetail, ToolCallInfo } from '@/types/database';

/**
 * Fetches all agents and processes their message JSON to generate thread details.
 */
export async function getThreadDetails(): Promise<ThreadDetail[]> {
  const query = `
    SELECT
      a.id,
      a.user_id,
      a.messages,
      a.created_at
    FROM agents a
    ORDER BY a.created_at DESC
  `;

  const [rows] = await pool.query(query);
  const agents = rows as (Agent & { created_at: string | null })[];

  if (!agents.length) {
    return [];
  }

  return agents.map(agent => {
    let messages: AgentMessage[] = [];
    try {
      if (agent.messages) {
        messages = JSON.parse(agent.messages);
      }
    } catch (e) {
      console.error(`Failed to parse messages for agent ${agent.id}:`, e);
    }

    const toolChain: ToolCallInfo[] = messages
      .filter(msg => msg.role === 'assistant' && msg.tool_calls)
      .flatMap(assistantMsg => 
        (assistantMsg.tool_calls ?? []).map((toolCall: any) => {
          const toolResultMsg = messages.find(
            msg => msg.role === 'tool' && msg.tool_call_id === toolCall.id
          );
          return {
            id: toolCall.id || 'N/A',
            name: toolCall.function?.name || 'unknown_tool',
            arguments: toolCall.function?.arguments || '{}',
            result: toolResultMsg?.content || 'No result found',
            duration: toolResultMsg?.duration,
            model: assistantMsg.model,
            tokens: assistantMsg.tokens,
            price: assistantMsg.price,
          };
        })
      );

    let threadName = agent.id; // Fallback to agent ID
    const userMessageWithThreadName = messages.find(m => m.role === 'user' && m.content?.includes("in the thread"));
    if (userMessageWithThreadName) {
      const match = userMessageWithThreadName.content.match(/in the thread '([^']+)'/);
      if (match && match[1]) {
        threadName = match[1];
      }
    }

    return {
      id: agent.id,
      thread_name: threadName,
      user_id: agent.user_id,
      created_at: agent.created_at || new Date(0).toISOString(),
      cycles: toolChain.length,
      messages: messages.length,
      tool_chain: toolChain,
    };
  });
}

/**
 * Gets all messages for an agent by the agent's ID.
 * @param agentId The ID of the agent.
 */
export async function getAgentMessagesById(agentId: string): Promise<AgentMessage[]> {
  const [rows] = await pool.query('SELECT messages FROM agents WHERE id = ?', [agentId]);
  const agents = rows as Pick<Agent, 'messages'>[];

  if (agents.length === 0) {
    return [];
  }

  try {
    return JSON.parse(agents[0].messages) as AgentMessage[];
  } catch (e) {
    console.error(`Failed to parse messages for agent ${agentId}`, e);
    return [];
  }
}

/**
 * Gets all messages in a thread by the thread's name.
 * @param threadName The name of the thread.
 */
export async function getThreadByName(threadName: string): Promise<Message[]> {
  const [threadRows] = await pool.query(
    'SELECT * FROM messages WHERE thread_name = ? ORDER BY timestamp ASC',
    [threadName]
  );
  
  return threadRows as Message[];
} 