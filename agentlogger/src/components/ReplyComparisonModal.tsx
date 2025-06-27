'use client';

import React, { useState } from 'react';

// A simple diffing function to find differences between two texts
const getDiffLines = (text1: string, text2: string) => {
  const lines1 = text1.split('\n');
  const lines2 = text2.split('\n');
  const maxLines = Math.max(lines1.length, lines2.length);
  
  const diff = [];
  for (let i = 0; i < maxLines; i++) {
    const line1 = lines1[i] || '';
    const line2 = lines2[i] || '';
    diff.push({
      line1,
      line2,
      isDifferent: line1 !== line2
    });
  }
  return diff;
};

interface ReplyComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  generated_draft: string;
  reply_sent_by_user: string;
}

const ReplyComparisonModal: React.FC<ReplyComparisonModalProps> = ({
  isOpen,
  onClose,
  generated_draft,
  reply_sent_by_user,
}) => {
  const [copyStatus, setCopyStatus] = useState('Copy Link');

  if (!isOpen) return null;

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopyStatus('Copied!');
    setTimeout(() => setCopyStatus('Copy Link'), 2000);
  };

  const diffLines = getDiffLines(generated_draft, reply_sent_by_user);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-6xl w-full max-h-[90vh] flex flex-col">
        <div className="flex justify-between items-center mb-6 pb-4 border-b">
          <h2 className="text-2xl font-bold text-gray-800">Compare Draft & Reply</h2>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleCopyLink}
              className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              {copyStatus}
            </button>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-800 text-3xl leading-none">&times;</button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto pr-4 -mr-4">
          <div className="grid grid-cols-2 gap-6">
            <h3 className="font-bold text-lg text-gray-700">Generated Draft</h3>
            <h3 className="font-bold text-lg text-gray-700">Reply Sent by User</h3>
          </div>

          <div className="font-mono text-sm">
            {diffLines.map((diff, index) => (
              <div 
                key={index} 
                className={`grid grid-cols-2 gap-6 border-t ${diff.isDifferent ? 'bg-red-50' : 'bg-white'}`}
              >
                <pre className={`py-2 px-3 whitespace-pre-wrap ${diff.isDifferent ? 'text-red-700' : 'text-gray-600'}`}>
                  {diff.line1}
                </pre>
                <pre className={`py-2 px-3 whitespace-pre-wrap ${diff.isDifferent ? 'text-green-700' : 'bg-green-50'}`}>
                  {diff.line2}
                </pre>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReplyComparisonModal; 