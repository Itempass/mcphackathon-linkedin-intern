import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import { api, DraftMessage } from '../../../../api/backend';
import DraftMessageCard from './DraftMessageCard';
import { getMockDrafts } from './mockData';

interface DraftMessagesFeedProps {
  userId: string;
}

const DraftMessagesFeed: React.FC<DraftMessagesFeedProps> = ({ userId }) => {
  // State management as per specifications
  const [drafts, setDrafts] = useState<DraftMessage[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Polling logic - fetch drafts from backend buffer
  useEffect(() => {
    const fetchDrafts = async () => {
      console.log('Fetching drafts from backend buffer...');
      try {
        setError(null);
        
        const response = await api.getDrafts(userId);
        console.log('Draft messages response:', response);
        
        // Data processing: filter and sort drafts
        const validDrafts = response.draft_messages.filter(
          draft => draft.draft_message_content && draft.draft_message_content.trim() !== ''
        );
        
        // Sort by draft_message_id (newest first)
        const sortedDrafts = validDrafts.sort((a, b) => 
          b.draft_message_id.localeCompare(a.draft_message_id)
        );
        
        setDrafts(sortedDrafts);
        
      } catch (err) {
        console.error('Error fetching drafts:', err);
        
        // Check if mock data fallback is enabled via environment variable
        const useMockFallback = import.meta.env.VITE_USE_MOCK_FALLBACK === 'true';
        
        if (useMockFallback) {
          console.log('Backend failed, using mock data for testing (VITE_USE_MOCK_FALLBACK=true)...');
          try {
            const mockResponse = await getMockDrafts();
            const sortedMockDrafts = mockResponse.draft_messages.sort((a, b) => 
              b.draft_message_id.localeCompare(a.draft_message_id)
            );
            setDrafts(sortedMockDrafts);
            setError(null); // Clear error since we have mock data
            return; // Exit early with mock data
          } catch (mockErr) {
            console.error('Mock data also failed:', mockErr);
            // Fall through to normal error handling
          }
        }
        
        // Handle different error types as per specifications (production behavior)
        if (err instanceof Error) {
          if (err.message.includes('fetch') || err.message.includes('network')) {
            setError('Connection failed - please check your internet connection');
          } else if (err.message.includes('404')) {
            setError('Draft service not available');
          } else if (err.message.includes('500') || err.message.includes('Internal Server Error')) {
            setError('Backend server error - the draft service is temporarily unavailable. Please try again later.');
          } else if (err.message.includes('API call failed')) {
            setError('API service error - please try again in a few moments');
          } else {
            setError(`Failed to load drafts: ${err.message}`);
          }
        } else {
          setError('Unknown error occurred');
        }
      } finally {
      }
    };

    // Initial fetch on mount
    fetchDrafts();

    // Set up 5-second interval polling
    const intervalId = setInterval(fetchDrafts, 5000);

    // Cleanup interval on unmount
    return () => {
      console.log('Cleaning up draft polling interval');
      clearInterval(intervalId);
    };
  }, [userId]);

  const handleCopySuccess = () => {
    console.log('Draft message copied successfully');
  };

  const handleFeedbackSuccess = () => {
    console.log('Feedback submitted successfully');
  };

  const handleRejectSuccess = (draftId: string) => {
    console.log('Draft rejected successfully:', draftId);
    
    // Remove the rejected draft from local state immediately
    setDrafts(prevDrafts => 
      prevDrafts.filter(draft => draft.draft_message_id !== draftId)
    );
  };

  const handleRetry = () => {
    setError(null);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {error ? (
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            px: 2,
            py: 4,
            textAlign: 'center',
            boxSizing: 'border-box',
          }}
        >
          <Typography variant="body1" color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
          <button
            onClick={handleRetry}
            className="modern-button"
            style={{
              padding: '12px 24px',
              backgroundColor: '#333333',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: 'pointer',
              fontWeight: 500,
            }}
          >
            Retry
          </button>
        </Box>
      ) : drafts.length > 0 ? (
        <Box sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
          {drafts.map((draft) => (
            <DraftMessageCard
              key={draft.draft_message_id}
              draftMessage={draft}
              userId={userId}
              onCopySuccess={handleCopySuccess}
              onFeedbackSuccess={handleFeedbackSuccess}
              onRejectSuccess={() => handleRejectSuccess(draft.draft_message_id)}
            />
          ))}
        </Box>
      ) : (
        <Box
          sx={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            px: 2,
            py: 4,
            textAlign: 'center',
            boxSizing: 'border-box',
          }}
        >
          <Typography variant="h6" sx={{ mb: 1, color: '#6b7280' }}>
            Once an intern has something for you, they will let you know here
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default DraftMessagesFeed; 