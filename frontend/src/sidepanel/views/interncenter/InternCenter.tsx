import React, { useState } from 'react';
import { Box, Typography, Card, CardHeader, Avatar, Collapse, CardContent, CardActions, Button } from '@mui/material';
import { interns } from '../../../logic/interns';

interface InternCenterProps {
  onNavigateToOnboarding: () => void;
}

const InternCenter: React.FC<InternCenterProps> = ({ onNavigateToOnboarding }) => {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const handleMouseEnter = (id: number) => {
    setExpandedId(id);
  };

  const handleMouseLeave = () => {
    setExpandedId(null);
  };

  return (
    <Box sx={{ p: 4, textAlign: 'center' }}>
      
      <Typography 
        variant="h4" 
        sx={{ 
          mb: 2,
          fontWeight: 600,
          color: '#1a1a1a',
          fontSize: '28px',
          lineHeight: 1.2,
        }}
      >
        Your <span className="highlight-text">interns</span> are ready for you
      </Typography>
      
      <Typography 
        sx={{ 
          mb: 4,
          color: '#666666',
          fontSize: '16px',
          lineHeight: 1.5,
          maxWidth: '320px',
          margin: '0 auto 32px auto'
        }}
      >
        Choose from our talented interns to help streamline your workflow.
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {interns.map((intern) => (
          <Card
            key={intern.id}
            className="modern-card"
            onMouseEnter={() => handleMouseEnter(intern.id)}
            onMouseLeave={handleMouseLeave}
            sx={{
              textAlign: 'left',
              overflow: 'visible',
              borderRadius: '24px',
              cursor: 'pointer',
              '&:hover': {
                transform: 'translateY(-3px)',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
              }
            }}
          >
            <Box 
              sx={{ 
                transition: 'all 0.2s ease',
                borderRadius: '24px',
                '&:hover': { 
                  backgroundColor: 'rgba(178, 255, 89, 0.02)' 
                } 
              }}
            >
              <CardHeader
                avatar={
                  <Avatar 
                    src={intern.internPictureUrl} 
                    sx={{ 
                      bgcolor: '#b2ff59',
                      color: '#333333',
                      width: 52,
                      height: 52,
                      fontWeight: 600,
                      fontSize: '18px',
                    }}
                  >
                    {intern.name.charAt(0)}
                  </Avatar>
                }
                title={
                  <Typography sx={{ fontWeight: 600, color: '#1a1a1a', fontSize: '16px' }}>
                    {intern.name}
                  </Typography>
                }
                subheader={
                  <Typography sx={{ color: '#666666', fontSize: '14px', mt: 0.5 }}>
                    {intern.subtitle}
                  </Typography>
                }
                sx={{ p: 3 }}
              />
            </Box>
            <Collapse in={expandedId === intern.id} timeout={300} unmountOnExit>
              <CardContent sx={{ pt: 0, px: 3, pb: 2 }}>
                <Box
                  sx={{
                    backgroundColor: 'rgba(178, 255, 89, 0.05)',
                    borderLeft: '4px solid #b2ff59',
                    borderRadius: '12px',
                    p: 2.5,
                    position: 'relative',
                    '&::before': {
                      content: '"\"',
                      position: 'absolute',
                      top: '8px',
                      left: '12px',
                      fontSize: '24px',
                      color: '#b2ff59',
                      fontWeight: 'bold',
                      fontFamily: 'Georgia, serif',
                    },
                    '&::after': {
                      content: '"\"',
                      position: 'absolute',
                      bottom: '8px',
                      right: '12px',
                      fontSize: '24px',
                      color: '#b2ff59',
                      fontWeight: 'bold',
                      fontFamily: 'Georgia, serif',
                    }
                  }}
                >
                  <Typography 
                    sx={{ 
                      color: '#333333', 
                      lineHeight: 1.6,
                      fontStyle: 'italic',
                      fontSize: '15px',
                      px: 2,
                      py: 1,
                    }}
                  >
                    {intern.description}
                  </Typography>
                </Box>
              </CardContent>
              <CardActions sx={{ justifyContent: 'center', p: 3, pt: 1 }}>
                <Button 
                  variant="contained" 
                  onClick={onNavigateToOnboarding}
                  sx={{
                    textTransform: 'none',
                    fontWeight: 600,
                    borderRadius: '20px',
                    px: 4,
                    py: 1.5,
                    fontSize: '15px',
                    backgroundColor: '#00C851',
                    color: '#ffffff',
                    boxShadow: '0 4px 16px rgba(0, 200, 81, 0.3)',
                    '&:hover': {
                      backgroundColor: '#007E33',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 24px rgba(0, 200, 81, 0.4)',
                    }
                  }}
                >
                  🚀 Hire me
                </Button>
              </CardActions>
            </Collapse>
          </Card>
        ))}
      </Box>
      
      {/* Stats */}
      <Box className="stats" sx={{ justifyContent: 'center', mt: 4 }}>
        <span>🔥</span>
        <Typography component="span">
          {interns.length} talented interns available
        </Typography>
      </Box>
    </Box>
  );
};

export default InternCenter;
