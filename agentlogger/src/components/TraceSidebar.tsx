'use client';

import React from 'react';
import { AgentMessage } from '@/types/database';

// A simplified type for sidebar items
export interface SidebarNavItem {
  id: string;
  role: AgentMessage['role'];
  name: string;
}

interface TraceSidebarProps {
  navItems: SidebarNavItem[];
  onNavItemClick: (id: string) => void;
}

// Icons for different roles
const roleToIconMap: { [key: string]: string } = {
  system: '⚙️',
  user: '👤',
  assistant: '🤖',
  tool: '🛠️',
};

export default function TraceSidebar({ navItems, onNavItemClick }: TraceSidebarProps) {
  return (
    <aside className="w-64 bg-gray-50 p-4 border-r border-gray-200 h-full overflow-y-auto">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Trace Details</h2>
      <nav>
        <ul>
          {navItems.map((item) => (
            <li
              key={item.id}
              onClick={() => onNavItemClick(item.id)}
              className="flex items-center p-2 rounded-md hover:bg-gray-200 cursor-pointer text-sm"
            >
              <span className="mr-2">{roleToIconMap[item.role] || '📄'}</span>
              <span className="truncate">{item.name}</span>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
} 