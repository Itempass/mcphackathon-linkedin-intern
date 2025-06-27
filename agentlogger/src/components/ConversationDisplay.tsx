'use client';

import React from 'react';
import { AgentMessage } from '@/types/database';

interface ThreadDisplayProps {
  thread: AgentMessage[];
}

const roleToColorMap: { [key: string]: string } = {
  system: 'bg-gray-200 text-gray-800',
  user: 'bg-blue-100 text-blue-900',
  assistant: 'bg-green-100 text-green-900',
  tool: 'bg-yellow-100 text-yellow-900',
};

// Helper to find and style redacted text
const formatRedactedText = (text: string) => {
  const redactedRegex = /\[REDACTED[^\]]*\]/g;
  return text.split(redactedRegex).map((part, index, array) => (
    <React.Fragment key={index}>
      {part}
      {index < array.length - 1 && (
        <span className="bg-black text-white px-1.5 py-0.5 rounded-sm mx-1">
          {text.match(redactedRegex)?.[index]}
        </span>
      )}
    </React.Fragment>
  ));
};

export default function ThreadDisplay({ thread }: ThreadDisplayProps) {

  if (!thread || thread.length === 0) {
    return (
      <div className="p-8 text-center text-gray-700">
        No messages in this thread.
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">
        Conversation Thread
      </h1>
      <div className="space-y-6">
        {thread.map((message, index) => (
          <div key={index} id={`message-${index}`} className="p-5 border rounded-lg bg-white shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <span className={`font-semibold px-3 py-1 rounded-md text-sm ${roleToColorMap[message.role] || 'bg-gray-100'}`}>
                {message.role === 'tool' ? `tool: ${message.name}` : message.role}
              </span>
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                {message.role === 'assistant' && message.model && <span>Model: {message.model}</span>}
                {message.role === 'assistant' && message.tokens && <span>Tokens: {message.tokens}</span>}
                {message.role === 'assistant' && message.price && <span>Price: ${message.price.toFixed(6)}</span>}
                {message.role === 'tool' && message.duration && <span>Duration: {message.duration.toFixed(2)}s</span>}
              </div>
            </div>
            {message.content && <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">{formatRedactedText(message.content)}</p>}
            {message.tool_calls && (
              <div className="mt-4">
                <h3 className="text-md font-semibold text-gray-800 mb-2">Tool Calls</h3>
                {message.tool_calls.map((toolCall, i) => (
                  <div key={i} className="mt-2 p-3 bg-gray-50 rounded font-mono text-sm">
                    <div className="text-gray-700"><strong>ID:</strong> {toolCall.id}</div>
                    <div className="text-gray-700"><strong>Type:</strong> {toolCall.type}</div>
                    <div className="text-gray-700"><strong>Function:</strong> {toolCall.function.name}</div>
                    <div className="text-gray-700"><strong>Arguments:</strong> <pre className="whitespace-pre-wrap bg-gray-100 p-2 rounded mt-1">{toolCall.function.arguments}</pre></div>
                  </div>
                ))}
              </div>
            )}
             {message.role === 'tool' && (
              <div className="mt-4 font-mono text-sm p-3 bg-yellow-50 rounded">
                <div className="text-gray-700"><strong>Tool Call ID:</strong> {message.tool_call_id}</div>
              </div>
            )}
          </div>
        ))}
      </div>
       {/* Debug Section */}
      <div className="mt-8 bg-gray-100 rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">🐛 Debug: Thread JSON</h2>
        <details className="bg-white rounded p-4">
          <summary className="text-sm font-medium text-gray-700 cursor-pointer hover:text-gray-900">
            Click to expand full JSON data
          </summary>
          <div className="mt-4">
            <pre className="text-xs text-gray-700 bg-gray-50 p-4 rounded overflow-auto max-h-96 whitespace-pre-wrap">
              {JSON.stringify(thread, null, 2)}
            </pre>
          </div>
        </details>
      </div>
    </div>
  );
} 