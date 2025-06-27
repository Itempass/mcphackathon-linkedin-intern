import React from 'react';
import { List } from '@mui/material';
import InternListItem from './InternListItem';
import { Intern } from '../types';

interface InternsListProps {
  interns: Intern[];
}

const InternsList: React.FC<InternsListProps> = ({ interns }) => {
  return (
    <List>
      {interns.map((intern) => (
        <InternListItem key={intern.id} intern={intern} />
      ))}
    </List>
  );
};

export default InternsList; 