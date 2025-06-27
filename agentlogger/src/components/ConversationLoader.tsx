'use client';

import { useState, useEffect } from 'react';

const loadingSteps = [
  'Fetching conversation...',
  'Joining thread details...',
  'Analyzing tool calls...',
  'Rendering trace...',
  'Almost there...',
];

export default function ConversationLoader() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prevStep) => (prevStep + 1) % loadingSteps.length);
    }, 1500); // Change step every 1.5 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center">
      <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-6"></div>
      <p className="text-lg font-medium text-gray-700">{loadingSteps[currentStep]}</p>
    </div>
  );
} 