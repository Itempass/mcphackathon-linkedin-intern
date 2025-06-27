import React from 'react';
import { ListItem, ListItemButton, ListItemText } from '@mui/material';
import { Intern } from '../types';

interface InternListItemProps {
  intern: Intern;
}

const InternListItem: React.FC<InternListItemProps> = ({ intern }) => {
  const handleClick = () => {
    if (!intern.targetUrl) return;

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const currentTab = tabs[0];
      if (currentTab?.id) {
        try {
          const tabUrl = new URL(currentTab.url || '');

          if (tabUrl.hostname.includes('linkedin.com')) {
            // If on any LinkedIn page
            if (tabUrl.pathname.startsWith('/messaging')) {
              // If already on the messaging page, just switch the panel
              chrome.runtime.sendMessage({ type: 'LINKEDIN_MESSAGING_PAGE_LOADED' });
            } else {
              // If on another LinkedIn page, navigate the current tab
              chrome.tabs.update(currentTab.id, { url: intern.targetUrl });
            }
          } else {
            // If not on LinkedIn, open a new tab
            window.open(intern.targetUrl, '_blank');
          }
        } catch (error) {
          // Fallback for invalid URLs (like chrome:// pages)
          window.open(intern.targetUrl, '_blank');
        }
      } else {
        // Fallback if no tab is found
        window.open(intern.targetUrl, '_blank');
      }
    });
  };

  return (
    <ListItem disablePadding>
      <ListItemButton onClick={handleClick} disabled={!intern.targetUrl}>
        <ListItemText primary={intern.name} />
      </ListItemButton>
    </ListItem>
  );
};

export default InternListItem; 