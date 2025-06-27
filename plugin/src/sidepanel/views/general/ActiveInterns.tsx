import React from 'react';
import { Avatar, Box, IconButton } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { interns } from '../../../logic/interns';

const ActiveInterns: React.FC = () => {
  const activeIntern = interns.find(i => i.id === 1);

  return (
    <Box 
      sx={{ 
        display: 'flex', 
        alignItems: 'center', 
      }}
    >
      {activeIntern && (
        <Avatar src={activeIntern.internPictureUrl}>
          {activeIntern.name.charAt(0)}
        </Avatar>
      )}
      <IconButton 
        sx={{ 
          ml: 1, 
          border: '1px solid',
          borderColor: 'divider',
          width: 40,
          height: 40
        }}
      >
        <AddIcon />
      </IconButton>
    </Box>
  );
};

export default ActiveInterns; 