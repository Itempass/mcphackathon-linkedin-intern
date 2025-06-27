import { Box, Typography, Button } from '@mui/material';
import { storage } from '../../../logic/storage';

interface WelcomeProps {
  onComplete: () => void;
}

export default function Welcome({ onComplete }: WelcomeProps) {
  const handleStart = async () => {
    await storage.initialize();
    onComplete();
  };

  return (
    <Box sx={{ textAlign: 'center', py: 4, px: 3 }}>
      {/* Logo */}
      <Box className="logo" sx={{ margin: '0 auto 32px auto' }}>
        🚀
      </Box>
      
      <Typography 
        variant="h4" 
        component="h1" 
        sx={{
          mb: 2,
          fontWeight: 600,
          color: '#1a1a1a',
          fontSize: '28px',
          lineHeight: 1.2,
        }}
      >
        Welcome to <span className="highlight-text">LinkedIn</span> AI Assistant
      </Typography>
      
      <Typography 
        variant="body1" 
        sx={{ 
          mb: 3,
          color: '#666666',
          fontSize: '16px',
          lineHeight: 1.6,
          maxWidth: '340px',
          margin: '0 auto 24px auto'
        }}
      >
        To get started, we'll need to learn your communication style. 
        We'll analyze 10 of your LinkedIn message threads to understand 
        how you typically interact with others.
      </Typography>

      <Typography 
        variant="body2" 
        sx={{ 
          mb: 4,
          color: '#888888',
          fontSize: '14px',
          lineHeight: 1.5,
          maxWidth: '320px',
          margin: '0 auto 32px auto'
        }}
      >
        This will help us provide more personalized message suggestions 
        that match your tone and style.
      </Typography>

      <Button 
        variant="contained" 
        size="large"
        onClick={handleStart}
        className="modern-button"
        sx={{
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: '12px',
          px: 4,
          py: 1.5,
          fontSize: '16px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          '&:hover': {
            boxShadow: '0 6px 20px rgba(0, 0, 0, 0.2)',
          }
        }}
      >
        Let's Get Started
      </Button>
      
      {/* Stats */}
      <Box className="stats" sx={{ justifyContent: 'center', mt: 4 }}>
        <span>⚡</span>
        <Typography component="span">
          Powered by advanced AI technology
        </Typography>
      </Box>
    </Box>
  );
} 