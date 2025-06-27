import React from 'react';
import { Box, Typography } from '@mui/material';

interface HeaderProps {
  // No props needed for static "Inbox" title
}

export const Header: React.FC<HeaderProps> = () => {
  return (
    <Box
      sx={{
        padding: '20px 24px',
        borderBottom: '1px solid rgba(0, 0, 0, 0.05)',
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(8px)',
        position: 'sticky',
        top: 0,
        zIndex: 10,
      }}
    >
      <Typography
        variant="body1"
        sx={{
          fontSize: '18px',
          fontWeight: 600,
          color: '#1a1a1a',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          letterSpacing: '-0.01em',
        }}
      >
        Inbox
      </Typography>
    </Box>
  );
};

export default Header; 