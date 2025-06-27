import React, { useState, useEffect } from 'react';
import { Box, TextField, IconButton, Typography, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { api } from '../../../../api/backend';

interface FeedbackChatboxProps {
  userId: string;
  draftMessageId: string;
  onFeedbackSuccess?: () => void;
  compact?: boolean; // For mini chatbox vs expanded interface
}

interface FeedbackState {
  submitting: boolean;
  submitted: boolean;
  error: string | null;
  feedbackText: string;
}

const FeedbackChatbox: React.FC<FeedbackChatboxProps> = ({
  userId,
  draftMessageId,
  onFeedbackSuccess,
  compact = false
}) => {
  // Feedback state management as per specifications
  const [feedbackState, setFeedbackState] = useState<FeedbackState>({
    submitting: false,
    submitted: false,
    error: null,
    feedbackText: ''
  });

  const maxCharacters = 500;

  // Reset success state after 3 seconds
  useEffect(() => {
    if (feedbackState.submitted) {
      const timeoutId = setTimeout(() => {
        setFeedbackState(prev => ({ ...prev, submitted: false }));
      }, 3000);

      return () => clearTimeout(timeoutId);
    }
  }, [feedbackState.submitted]);

  const handleSubmitFeedback = async () => {
    if (!feedbackState.feedbackText.trim() || feedbackState.submitting) {
      return;
    }

    console.log('Submitting feedback for draft:', draftMessageId);

    setFeedbackState(prev => ({
      ...prev,
      submitting: true,
      error: null
    }));

    try {
      // API call to /process-feedback/ as per specifications
      await api.submitFeedback({
        user_id: userId,
        draft_message_id: draftMessageId,
        feedback: feedbackState.feedbackText.trim()
      });

      console.log('Feedback submitted successfully');

      // Success state
      setFeedbackState(prev => ({
        ...prev,
        submitting: false,
        submitted: true,
        feedbackText: '', // Clear input after successful submission
        error: null
      }));

      onFeedbackSuccess?.();

    } catch (error) {
      console.error('Failed to submit feedback:', error);

      // Error handling as per specifications
      let errorMessage = 'Failed to submit feedback';
      
      if (error instanceof Error) {
        if (error.message.includes('400')) {
          errorMessage = 'Invalid feedback format';
        } else if (error.message.includes('404')) {
          errorMessage = 'Draft no longer available';
        } else if (error.message.includes('500')) {
          errorMessage = 'Feedback service unavailable';
        } else if (error.message.includes('fetch')) {
          errorMessage = 'Connection failed - please try again';
        }
      }

      setFeedbackState(prev => ({
        ...prev,
        submitting: false,
        submitted: false,
        error: errorMessage
      }));
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    // Submit on Enter (but allow Shift+Enter for new lines)
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmitFeedback();
    }
  };

  const handleTextChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = event.target.value;
    if (newText.length <= maxCharacters) {
      setFeedbackState(prev => ({
        ...prev,
        feedbackText: newText,
        error: null // Clear error when user starts typing
      }));
    }
  };

  const charactersRemaining = maxCharacters - feedbackState.feedbackText.length;
  const isNearLimit = charactersRemaining < 50;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        p: compact ? 1 : 1.5,
        backgroundColor: compact ? 'transparent' : '#f8f9fa',
        borderRadius: compact ? 0 : '8px',
        border: compact ? '1px solid #e5e7eb' : 'none',
      }}
    >
      {/* Success/Error messages */}
      {feedbackState.submitted && (
        <Typography
          variant="caption"
          sx={{
            color: 'success.main',
            fontSize: '12px',
            fontWeight: 500
          }}
        >
          ✓ Feedback submitted successfully!
        </Typography>
      )}

      {feedbackState.error && (
        <Typography
          variant="caption"
          sx={{
            color: 'error.main',
            fontSize: '12px',
            fontWeight: 500
          }}
        >
          {feedbackState.error}
        </Typography>
      )}

      {/* Input area */}
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <TextField
            multiline
            maxRows={compact ? 2 : 4}
            minRows={compact ? 1 : 2}
            fullWidth
            placeholder={compact ? "Quick feedback..." : "Provide feedback"}
            value={feedbackState.feedbackText}
            onChange={handleTextChange}
            onKeyPress={handleKeyPress}
            disabled={feedbackState.submitting}
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                fontSize: compact ? '14px' : '15px',
                lineHeight: 1.4,
                backgroundColor: '#ffffff',
              },
            }}
          />
          
          {/* Character counter */}
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              textAlign: 'right',
              mt: 0.5,
              color: isNearLimit ? 'warning.main' : 'text.secondary',
              fontSize: '11px'
            }}
          >
            {charactersRemaining} characters remaining
          </Typography>
        </Box>

        {/* Send Feedback Button */}
        <IconButton
          onClick={handleSubmitFeedback}
          disabled={
            feedbackState.submitting || 
            !feedbackState.feedbackText.trim() || 
            feedbackState.feedbackText.length > maxCharacters
          }
          size="small"
          color="primary"
          sx={{
            width: '32px',
            height: '32px',
            backgroundColor: 'primary.main',
            color: 'white',
            '&:hover': {
              backgroundColor: 'primary.dark',
            },
            '&:disabled': {
              backgroundColor: '#e0e0e0',
              color: '#9e9e9e',
            },
          }}
        >
          {feedbackState.submitting ? (
            <CircularProgress size={14} color="inherit" />
          ) : (
            <SendIcon sx={{ fontSize: '16px' }} />
          )}
        </IconButton>
      </Box>
    </Box>
  );
};

export default FeedbackChatbox; 