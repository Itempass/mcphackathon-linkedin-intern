import React from 'react';
import { Box, Typography, Avatar, Divider } from '@mui/material';
import CopyButton from './CopyButton';
import RejectButton from './RejectButton';
import FeedbackChatbox from './FeedbackChatbox';
import { DraftMessage } from '../../../../api/backend';

interface DraftMessageCardProps {
  draftMessage: DraftMessage;
  userId: string;
  onCopySuccess?: () => void;
  onFeedbackSuccess?: () => void;
  onRejectSuccess?: () => void;
}

const DraftMessageCard: React.FC<DraftMessageCardProps> = React.memo(({ 
  draftMessage, 
  userId,
  onCopySuccess,
  onFeedbackSuccess,
  onRejectSuccess,
}) => {

  return (
    <Box
      className="modern-card"
      sx={{
        // Modern card styling
        background: '#ffffff',
        borderRadius: '20px',
        border: '1px solid rgba(0, 0, 0, 0.05)',
        boxShadow: '0 2px 12px rgba(0, 0, 0, 0.04)',
        p: 3,
        mb: 3,
        position: 'relative',
        transition: 'all 0.3s ease',
        
        // Hover state
        '&:hover': {
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
          transform: 'translateY(-2px)',
        },
      }}
    >
      {/* Alex attribution and reject button at the same height */}
      <Box 
        sx={{ 
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 2,
        }}
      >
        <Box 
          sx={{ 
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
          }}
        >
          <Avatar 
            src="/intern_headshots/intern_1_pixar.png"
            sx={{ 
              width: 32,
              height: 32,
              bgcolor: '#b2ff59',
              color: '#333333',
              fontSize: '14px',
              fontWeight: 600,
            }}
          >
            A
          </Avatar>
          <Typography 
            sx={{ 
              fontSize: '13px',
              color: '#666666',
              fontWeight: 500,
            }}
          >
            Alex the draft reply intern
          </Typography>
        </Box>

        {/* Reject button aligned to the right */}
        <RejectButton
          userId={userId}
          draftMessageId={draftMessage.draft_message_id}
          onRejectSuccess={onRejectSuccess}
        />
      </Box>

      {/* Divider line */}
      <Divider sx={{ mb: 2 }} />

      {/* Header with contact name */}
      <Box sx={{ mb: 2 }}>
        <Typography
          variant="h6"
          sx={{
            fontSize: '18px',
            fontWeight: 600,
            color: '#1a1a1a',
            lineHeight: 1.2,
          }}
        >
          {draftMessage.thread_name}
        </Typography>
      </Box>

      {/* Draft message content with copy button inside */}
      <Box
        sx={{
          backgroundColor: 'rgba(178, 255, 89, 0.03)',
          borderLeft: '3px solid #b2ff59',
          borderRadius: '12px',
          p: 2.5,
          mb: 3,
          position: 'relative',
        }}
      >
        {/* Copy button positioned inside the green box at top right */}
        <Box
          sx={{
            position: 'absolute',
            top: '12px',
            right: '12px',
            zIndex: 1,
          }}
        >
          <CopyButton
            message={draftMessage.draft_message_content}
            onCopySuccess={onCopySuccess}
          />
        </Box>

        <Typography
          sx={{
            fontSize: '15px',
            fontWeight: 400,
            color: '#333333',
            lineHeight: 1.6,
            whiteSpace: 'pre-wrap',
            pr: 6, // Add right padding to avoid overlap with copy button
          }}
        >
          {draftMessage.draft_message_content}
        </Typography>
      </Box>

      {/* Feedback section without title */}
      <Box 
        sx={{ 
          borderTop: '1px solid rgba(0, 0, 0, 0.05)',
          pt: 2,
        }}
      >
        <FeedbackChatbox
          userId={userId}
          draftMessageId={draftMessage.draft_message_id}
          onFeedbackSuccess={onFeedbackSuccess}
          compact={false}
        />
      </Box>
    </Box>
  );
});

// Add display name for debugging
DraftMessageCard.displayName = 'DraftMessageCard';

export default DraftMessageCard; 