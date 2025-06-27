import { NextResponse } from 'next/server';
import { getAgentMessagesById } from '@/services/database';
import { AgentMessage } from '@/types/database';

export async function GET(
  request: Request,
  { params }: { params: { threadName: string } }
) {
  const { threadName: agentId } = params;

  if (!agentId) {
    return NextResponse.json({ error: 'agentId is required' }, { status: 400 });
  }

  try {
    const messages = await getAgentMessagesById(agentId);

    if (!messages || messages.length === 0) {
      return NextResponse.json([]);
    }

    return NextResponse.json(messages);
  } catch (error) {
    console.error(`Error fetching thread for agentId: ${agentId}`, error);
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
