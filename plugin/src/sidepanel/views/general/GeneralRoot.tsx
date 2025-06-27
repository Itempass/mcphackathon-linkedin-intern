import React, { useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import Header from './Header';
import DraftMessagesFeed from './DraftMessagesFeed';
import ActiveInterns from './ActiveInterns';

interface GeneralRootProps {
  userId: string;
}

export const GeneralRoot: React.FC<GeneralRootProps> = ({ userId }) => {
  // Listen for thread changes from dom-watcher AND draft card clicks
  useEffect(() => {
    const handleMessages = (message: any) => {
      if (message.type === 'LINKEDIN_MESSAGES_EXTRACTED') {
        console.log('GeneralRoot: Received messages from dom-watcher:', message.payload);
        // Thread detection still works, but we don't need to update header title anymore
      } else if (message.type === 'DRAFT_CARD_SELECTED') {
        console.log('GeneralRoot: Draft card selected:', message.payload);
        // Draft card selection still works, but we don't need to update header title anymore
      }
    };

    // Listen for extension messages
    chrome.runtime.onMessage.addListener(handleMessages);

    return () => {
      chrome.runtime.onMessage.removeListener(handleMessages);
    };
  }, []);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: 'transparent',
      }}
    >
      <Header />
      <Box sx={{ flex: '1 1 auto', overflowY: 'auto', p: 2 }}>
        <DraftMessagesFeed userId={userId} />
      </Box>
      <Box 
        sx={{ 
          p: 2, 
          borderTop: '1px solid rgba(0, 0, 0, 0.05)',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(8px)',
        }}
      >
        <Typography 
          variant="caption" 
          sx={{ 
            color: '#666666', 
            display: 'block', 
            mb: 1,
            fontWeight: 500,
            fontSize: '11px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}
        >
          ACTIVE INTERNS
        </Typography>
        <ActiveInterns />
      </Box>
    </Box>
  );
};

export default GeneralRoot; 