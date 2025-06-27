'use client';

import { useState, useEffect, useMemo } from 'react';
import { useParams } from 'next/navigation';
import { AgentMessage } from '@/types/database';
import ThreadDisplay from '@/components/ConversationDisplay';
import TraceSidebar, { SidebarNavItem } from '@/components/TraceSidebar';
import ConversationLoader from '@/components/ConversationLoader';

const ThreadPage = () => {
  const [thread, setThread] = useState<AgentMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const params = useParams();
  const threadName = params.threadName as string;

  useEffect(() => {
    if (!threadName) return;

    const fetchThread = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/threads/${threadName}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch thread: ${response.status}`);
        }
        const data = await response.json();
        setThread(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load thread');
      } finally {
        setIsLoading(false);
      }
    };

    fetchThread();
  }, [threadName]);

  const navItems = useMemo((): SidebarNavItem[] => {
    return thread.map((message, index) => ({
      id: `message-${index}`,
      role: message.role,
      name: message.name || message.role,
    }));
  }, [thread]);

  const handleNavItemClick = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <ConversationLoader />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center text-red-600">
        <p>Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen">
      <TraceSidebar navItems={navItems} onNavItemClick={handleNavItemClick} />
      <main className="flex-1 overflow-y-auto">
        <ThreadDisplay thread={thread} />
      </main>
    </div>
  );
};

export default ThreadPage; 