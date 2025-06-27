interface LoadingStatusProps {
  message?: string;
  showSpinner?: boolean;
  details?: string;
}

export default function LoadingStatus({ 
  message = "Loading conversations and extracting tool statuses...", 
  showSpinner = true,
  details 
}: LoadingStatusProps) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div className="flex items-center space-x-3">
        {showSpinner && (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
        )}
        <div className="flex-1">
          <p className="text-sm font-medium text-blue-800">{message}</p>
          {details ? (
            <p className="text-xs text-blue-600 mt-1">{details}</p>
          ) : (
            <p className="text-xs text-blue-600 mt-1">
              This may take a moment as we process conversation data and extract tool response statuses...
            </p>
          )}
        </div>
      </div>
    </div>
  );
} 