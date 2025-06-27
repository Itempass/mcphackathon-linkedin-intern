import React, { useState, useEffect } from 'react';
import { IconButton, Tooltip } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckIcon from '@mui/icons-material/Check';
import ErrorIcon from '@mui/icons-material/Error';

interface CopyButtonProps {
  message: string;
  onCopySuccess?: () => void;
}

const CopyButton: React.FC<CopyButtonProps> = ({ message, onCopySuccess }) => {
  // State management as per specifications
  const [copied, setCopied] = useState<boolean>(false);
  const [copyError, setCopyError] = useState<boolean>(false);

  // Reset states after 2-second timeout
  useEffect(() => {
    if (copied || copyError) {
      const timeoutId = setTimeout(() => {
        setCopied(false);
        setCopyError(false);
      }, 2000);

      return () => clearTimeout(timeoutId);
    }
  }, [copied, copyError]);

  // Fallback copy function for older browsers
  const fallbackCopy = (text: string): boolean => {
    try {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      const result = document.execCommand('copy');
      document.body.removeChild(textArea);
      return result;
    } catch (err) {
      console.error('Fallback copy failed:', err);
      return false;
    }
  };

  // Debounced copy function to prevent multiple rapid copies
  const handleCopy = async (event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent card click event
    
    // Reset states
    setCopied(false);
    setCopyError(false);

    try {
      // Modern clipboard API with fallback
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(message);
        console.log('Message copied using modern clipboard API');
      } else {
        // Fallback for older browsers
        const success = fallbackCopy(message);
        if (!success) {
          throw new Error('Fallback copy failed');
        }
        console.log('Message copied using fallback method');
      }

      // Success feedback
      setCopied(true);
      onCopySuccess?.();
      
    } catch (err) {
      console.error('Copy operation failed:', err);
      setCopyError(true);
      
      // Could add toast notification here in the future
      // For now, just visual feedback via error icon
    }
  };

  // Visual feedback logic
  const getIcon = () => {
    if (copied) return <CheckIcon sx={{ fontSize: '16px' }} />;
    if (copyError) return <ErrorIcon sx={{ fontSize: '16px' }} />;
    return <ContentCopyIcon sx={{ fontSize: '16px' }} />;
  };

  const getTooltipText = () => {
    if (copied) return 'Copied!';
    if (copyError) return 'Copy failed - try again';
    return 'Copy message';
  };

  return (
    <Tooltip title={getTooltipText()} arrow placement="left">
      <IconButton
        onClick={handleCopy}
        size="small"
        sx={{
          // 32px x 32px as per specifications
          width: '32px',
          height: '32px',
          // Remove background and border - just the icon
          backgroundColor: 'transparent',
          border: 'none',
          transition: 'all 0.2s ease-in-out',
          // Make icon darker green to fit in the green box
          color: '#2e7d0a', // Dark green that contrasts well with the light green background
          
          '&:hover': {
            backgroundColor: 'transparent',
            // Slightly darker on hover
            color: copied ? 'success.main' : copyError ? 'error.main' : '#1f5a06',
            transform: 'scale(1.1)',
          },
          
          // Disabled state during feedback
          '&:disabled': {
            backgroundColor: 'transparent',
            color: '#6b7280',
          },
        }}
        disabled={copied || copyError}
      >
        {getIcon()}
      </IconButton>
    </Tooltip>
  );
};

export default CopyButton; 