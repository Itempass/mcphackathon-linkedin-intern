import React, { useState, useEffect } from 'react';
import { IconButton, Tooltip } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckIcon from '@mui/icons-material/Check';
import ErrorIcon from '@mui/icons-material/Error';
import { api } from '../../../../api/backend';

interface RejectButtonProps {
  userId: string;
  draftMessageId: string;
  onRejectSuccess?: () => void;
}

const RejectButton: React.FC<RejectButtonProps> = ({ 
  userId, 
  draftMessageId, 
  onRejectSuccess 
}) => {
  // State management similar to CopyButton
  const [rejecting, setRejecting] = useState<boolean>(false);
  const [rejected, setRejected] = useState<boolean>(false);
  const [rejectError, setRejectError] = useState<boolean>(false);

  // Reset states after 2-second timeout
  useEffect(() => {
    if (rejected || rejectError) {
      const timeoutId = setTimeout(() => {
        setRejected(false);
        setRejectError(false);
      }, 2000);

      return () => clearTimeout(timeoutId);
    }
  }, [rejected, rejectError]);

  const handleReject = async (event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent card click event
    
    // Reset states
    setRejected(false);
    setRejectError(false);
    setRejecting(true);

    try {
      console.log(`🗑️  Rejecting draft: ${draftMessageId}`);
      
      // Call the reject-draft API endpoint
      await api.rejectDraft({
        user_id: userId,
        draft_message_id: draftMessageId
      });

      console.log(`✅ Draft rejected successfully: ${draftMessageId}`);
      
      // Success feedback
      setRejected(true);
      setRejecting(false);
      
      // Notify parent component about successful rejection
      onRejectSuccess?.();
      
    } catch (err) {
      console.error('Reject operation failed:', err);
      setRejectError(true);
      setRejecting(false);
      
      // Could add toast notification here in the future
      // For now, just visual feedback via error icon
    }
  };

  // Visual feedback logic
  const getIcon = () => {
    if (rejected) return <CheckIcon sx={{ fontSize: '16px' }} />;
    if (rejectError) return <ErrorIcon sx={{ fontSize: '16px' }} />;
    return <DeleteIcon sx={{ fontSize: '16px' }} />;
  };

  const getColor = () => {
    if (rejected) return 'success';
    if (rejectError) return 'error';
    return 'error'; // Default to error color for delete action
  };

  const getTooltipText = () => {
    if (rejecting) return 'Rejecting draft...';
    if (rejected) return 'Draft rejected!';
    if (rejectError) return 'Reject failed - try again';
    return 'Reject draft';
  };

  return (
    <Tooltip title={getTooltipText()} arrow placement="left">
      <IconButton
        onClick={handleReject}
        size="small"
        color={getColor() as any}
        sx={{
          // 32px x 32px to match CopyButton
          width: '32px',
          height: '32px',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(4px)',
          border: '1px solid rgba(0, 0, 0, 0.1)',
          transition: 'all 0.2s ease-in-out',
          
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 1)',
            // Color change to accent color on hover
            color: rejected ? 'success.main' : rejectError ? 'error.main' : 'error.main',
            transform: 'scale(1.05)',
          },
          
          // Disabled state during operation
          '&:disabled': {
            backgroundColor: 'rgba(255, 255, 255, 0.7)',
          },
        }}
        disabled={rejecting || rejected || rejectError}
      >
        {getIcon()}
      </IconButton>
    </Tooltip>
  );
};

export default RejectButton; 