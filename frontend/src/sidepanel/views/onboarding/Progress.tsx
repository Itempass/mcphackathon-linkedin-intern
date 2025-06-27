import { Box, Typography, LinearProgress, Alert } from '@mui/material';

interface ProgressProps {
  threadsCollected: number;
  isComplete: boolean;
  uploadSuccess?: boolean;
  uploadError?: string;
}

export default function Progress({ 
  threadsCollected, 
  isComplete,
  uploadSuccess,
  uploadError,
}: ProgressProps) {
  const progress = Math.min((threadsCollected / 10) * 100, 100);

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2">Progress</Typography>
          <Typography variant="body2">
            {threadsCollected} of 10 threads analyzed
          </Typography>
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ height: 8, borderRadius: 2 }}
        />
      </Box>

      {isComplete && uploadSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Analysis complete! I'm ready to help with messages.
        </Alert>
      )}

      {isComplete && uploadSuccess === false && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {uploadError || 'There was an error processing your messages. Please try again.'}
        </Alert>
      )}

      {!isComplete && (
        <Typography variant="body2" color="text.secondary">
          Keep browsing your LinkedIn messages. I will analyze them as you go.
        </Typography>
      )}
    </Box>
  );
} 