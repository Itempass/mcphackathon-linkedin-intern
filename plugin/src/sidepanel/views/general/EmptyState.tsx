import React from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';

interface EmptyStateProps {
  isLoading?: boolean;
}

const EmptyState: React.FC<EmptyStateProps> = ({ isLoading = true }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 4,
        height: '100%',
        color: 'text.secondary'
      }}
    >
      {isLoading ? (
        <>
          <CircularProgress size={24} sx={{ mb: 2 }} />
          <Typography variant="body1">Fetching draft...</Typography>
        </>
      ) : (
        <Typography variant="body1" sx={{ textAlign: 'center' }}>
          Once an intern has something for you, they will let you know here
        </Typography>
      )}
    </Box>
  );
};

export default EmptyState; 