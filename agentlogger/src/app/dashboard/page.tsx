'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ThreadDetail } from '@/types/database';
import LoadingTableRows from '@/components/LoadingTableRows';
import { useRouter } from 'next/navigation';

// Utility to shorten long IDs
const shortenId = (id: string, start = 3, end = 3) => {
  if (id.length <= start + end) {
    return id;
  }
  return `${id.substring(0, start)}...${id.substring(id.length - end)}`;
};

// Format timestamp for display
const formatTimestamp = (isoString: string) => {
  if (!isoString || isoString === new Date(0).toISOString()) {
    return 'N/A';
  }
  return new Date(isoString).toLocaleString();
};

export default function Dashboard() {
  const [data, setData] = useState<ThreadDetail[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const fetchedData = await fetch('/api/dashboard-data').then(res => {
        if (!res.ok) throw new Error(`Failed to fetch: ${res.statusText}`);
        return res.json();
      });
      setData(fetchedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 text-center">
        <div className="text-red-600 text-6xl mb-4">⚠️</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Dashboard</h2>
        <p className="text-gray-600 mb-6">{error}</p>
        <button
          onClick={loadDashboardData}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">MCP Dashboard</h1>
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/12">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/12">User ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-2/12">Created At</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cycles</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Messages</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-6/12">Tool Chain</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {isLoading ? (
              <LoadingTableRows count={10} />
            ) : (
              data.map((thread) => (
                <tr
                  key={thread.id}
                  onClick={() => router.push(`/dashboard/conversation/${thread.id}`)}
                  className="cursor-pointer hover:bg-gray-50"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-blue-600">
                    {shortenId(thread.id)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">{shortenId(thread.user_id)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatTimestamp(thread.created_at)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{thread.cycles}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{thread.messages}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <div className="flex flex-row flex-wrap items-center gap-x-1 gap-y-1">
                      {thread.tool_chain.map((tool, index) => (
                        <div key={tool.id} className="flex items-center">
                          <span
                            className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 font-medium"
                            title={`Tool: ${tool.name}\nResult: ${tool.result}\nDuration: ${tool.duration?.toFixed(2) ?? 'N/A'}s\nModel: ${tool.model ?? 'N/A'}\nTokens: ${tool.tokens ?? 'N/A'}\nPrice: $${tool.price?.toFixed(6) ?? 'N/A'}`}
                          >
                            {tool.name}
                          </span>
                          {index < thread.tool_chain.length - 1 && (
                            <span className="text-gray-400 mx-1.5 font-sans">→</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
} 