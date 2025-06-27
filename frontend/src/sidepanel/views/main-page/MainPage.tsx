import React from 'react';
import { Box, Typography } from '@mui/material';
import InternsList from './components/InternsList';
import { Intern } from './types';
import { v4 as uuidv4 } from 'uuid';

const interns: Intern[] = [
  {
    id: uuidv4(),
    name: 'Email Assistant',
    targetUrl: 'https://gmail.com',
  },
  {
    id: uuidv4(),
    name: 'LinkedIn Connector',
    targetUrl: 'https://www.linkedin.com/messaging/',
  },
  {
    id: uuidv4(),
    name: 'CRM Agent',
  },
];

const MainPage: React.FC = () => {
  return (
    <Box sx={{ pt: 6 }}>
      <Typography variant="h4" sx={{ p: 2 }}>
        Interns
      </Typography>
      <InternsList interns={interns} />
    </Box>
  );
};

export default MainPage; 