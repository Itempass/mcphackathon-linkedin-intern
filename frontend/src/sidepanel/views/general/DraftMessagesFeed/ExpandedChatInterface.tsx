import React from 'react';
import { Box, Typography, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import FeedbackChatbox from './FeedbackChatbox';
import CopyButton from './CopyButton';
import { DraftMessage } from '../../../../api/backend';

interface ExpandedChatInterfaceProps {
  draftMessage: DraftMessage;
  userId: string;
  onClose: () => void;
  onCopySuccess?: () => void;
  onFeedbackSuccess?: () => void;
}

const ExpandedChatInterface: React.FC<ExpandedChatInterfaceProps> = ({
  draftMessage,
  userId,
  onClose,
  onCopySuccess,
  onFeedbackSuccess
}) => {
  console.log('ExpandedChatInterface: Rendering expanded view for:', draftMessage.draft_message_id);
  
  return (
    <Box
      sx={{
        // Expanded card styling - 20% larger height as per specifications
        background: '#ffffff',
        border: '2px solid #3b82f6', // Highlighted border for expanded state
        borderRadius: '8px',
        p: 2,
        mb: 1,
        position: 'relative',
        transition: 'all 0.3s ease-in-out',
        boxShadow: '0 8px 16px rgba(0, 0, 0, 0.15)', // Enhanced shadow for expanded
      }}
    >
      {/* Header with close button */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          mb: 2,
        }}
      >
        <Typography
          variant="h6"
          sx={{
            fontSize: '16px',
            fontWeight: 600,
            color: '#1f2937',
            flex: 1,
            pr: 2,
          }}
        >
          {draftMessage.thread_name}
        </Typography>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <CopyButton
            message={draftMessage.draft_message_content}
            onCopySuccess={onCopySuccess}
          />
          <IconButton
            onClick={onClose}
            size="small"
            sx={{
              width: '32px',
              height: '32px',
              backgroundColor: 'rgba(0, 0, 0, 0.05)',
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
              },
            }}
          >
            <CloseIcon sx={{ fontSize: '16px' }} />
          </IconButton>
        </Box>
      </Box>

      {/* Full message content - no truncation */}
      <Box
        sx={{
          mb: 3,
          p: 2,
          backgroundColor: '#f8f9fa',
          borderRadius: '6px',
          border: '1px solid #e5e7eb',
        }}
      >
        <Typography
          variant="body1"
          sx={{
            fontSize: '15px',
            fontWeight: 400,
            color: '#374151',
            lineHeight: 1.6,
            whiteSpace: 'pre-wrap', // Preserve line breaks
            wordBreak: 'break-word', // Handle long words
          }}
        >
          {draftMessage.draft_message_content}
        </Typography>
      </Box>

      {/* Expanded feedback interface */}
      <Box>
        <Typography
          variant="subtitle2"
          sx={{
            fontSize: '14px',
            fontWeight: 600,
            color: '#374151',
            mb: 1,
          }}
        >
          Provide feedback to improve this draft:
        </Typography>
        
        <FeedbackChatbox
          userId={userId}
          draftMessageId={draftMessage.draft_message_id}
          onFeedbackSuccess={onFeedbackSuccess}
          compact={false} // Full interface, not compact
        />
      </Box>

      {/* Expanded state indicator */}
      <Box
        sx={{
          position: 'absolute',
          top: -1,
          left: 12,
          backgroundColor: '#3b82f6',
          color: 'white',
          px: 1.5,
          py: 0.25,
          borderRadius: '0 0 6px 6px',
          fontSize: '11px',
          fontWeight: 600,
          letterSpacing: '0.5px',
        }}
      >
        IN DRAFT
      </Box>
    </Box>
  );
};

export default ExpandedChatInterface; 