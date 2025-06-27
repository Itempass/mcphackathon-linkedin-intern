import { NextResponse } from 'next/server';
import { getThreadDetails } from '@/services/database';

export async function GET() {
  try {
    const threadDetails = await getThreadDetails();
    return NextResponse.json(threadDetails);
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
} 