import { useEffect, useState } from 'react';
import { Box, Typography, Fade, Avatar, Chip, SvgIcon } from '@mui/material';
import { storage } from '../../../logic/storage';
import Progress from './Progress';
import { interns } from '../../../logic/interns';

const LinkedInIcon = (props: React.ComponentProps<typeof SvgIcon>) => (
  <SvgIcon {...props} viewBox="0 0 24 24">
    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
  </SvgIcon>
);

interface CollectionState {
  threadsCollected: number;
  isComplete: boolean;
  uploadSuccess?: boolean;
  uploadError?: string;
}

export default function OnboardingRoot() {
  const intern = interns.find(i => i.id === 1);

  if (!intern) {
    // Handle the case where the intern is not found
    return <Box>Error: Intern with ID 1 not found.</Box>;
  }

  const [collectionState, setCollectionState] = useState<CollectionState>({
    threadsCollected: 0,
    isComplete: false,
  });
  const [showTitle, setShowTitle] = useState(false);
  const [showDescription, setShowDescription] = useState(false);
  const [showProgressBar, setShowProgressBar] = useState(false);
  const [showAvatar, setShowAvatar] = useState(false);
  const [showBadge, setShowBadge] = useState(false);
  const [showCompletionMessage, setShowCompletionMessage] = useState(false);

  // Animation sequence
  useEffect(() => {
    const avatarTimer = setTimeout(() => setShowAvatar(true), 200);
    const titleTimer = setTimeout(() => setShowTitle(true), 400);
    const badgeTimer = setTimeout(() => setShowBadge(true), 1400);
    const descTimer = setTimeout(() => setShowDescription(true), 2400);
    const progressTimer = setTimeout(() => setShowProgressBar(true), 3400);

    return () => {
      clearTimeout(avatarTimer);
      clearTimeout(titleTimer);
      clearTimeout(badgeTimer);
      clearTimeout(descTimer);
      clearTimeout(progressTimer);
    };
  }, []);

  // Handle completion state changes
  useEffect(() => {
    if (collectionState.isComplete) {
      // Show completion message after a 500ms delay
      const messageTimer = setTimeout(() => {
        setShowCompletionMessage(true);
      }, 500);

      // Navigate to general view after a 4-second delay
      const navigationTimer = setTimeout(() => {
        chrome.runtime.sendMessage({
          type: 'UPLOAD_COMPLETE',
          payload: { success: true },
        });
      }, 4000);

      return () => {
        clearTimeout(messageTimer);
        clearTimeout(navigationTimer);
      };
    }
  }, [collectionState.isComplete]);

  // Listen for collection updates
  useEffect(() => {
    const messageListener = (message: any) => {
      if (message.type === 'COLLECTION_UPDATE') {
        setCollectionState(state => ({
          ...state,
          threadsCollected: message.payload.threadsCollected,
          isComplete: message.payload.isComplete,
        }));
      } else if (message.type === 'UPLOAD_COMPLETE') {
        setCollectionState(state => ({
          ...state,
          uploadSuccess: message.payload.success,
          uploadError: message.payload.error,
        }));
      }
    };

    chrome.runtime.onMessage.addListener(messageListener);
    return () => {
      chrome.runtime.onMessage.removeListener(messageListener);
    };
  }, []);

  // Initialize collection state on mount
  useEffect(() => {
    Promise.all([
      storage.getCollectedThreads(),
      storage.isComplete(),
    ]).then(([threads, isComplete]) => {
      setCollectionState({
        threadsCollected: Object.keys(threads).length,
        isComplete,
      });
    });
  }, []);

  return (
    <Box sx={{ p: 4, textAlign: 'center' }}>
      <Fade in={showAvatar} timeout={500}>
        <Avatar 
          src={intern.internPictureUrl} 
          sx={{ 
            width: 64, 
            height: 64, 
            mb: 3, 
            mx: 'auto', 
            bgcolor: '#b2ff59',
            color: '#333333',
            fontWeight: 600,
            fontSize: '24px',
          }}
        >
          {intern.name.charAt(0)}
        </Avatar>
      </Fade>
      
      <Fade in={showTitle} timeout={500}>
        <Typography 
          variant="h5" 
          sx={{ 
            mb: 2,
            fontWeight: 600,
            color: '#1a1a1a',
            fontSize: '24px',
            lineHeight: 1.2,
          }}
        >
          👋 Hi, I'm <span className="highlight-text">{intern.name}</span>!
        </Typography>
      </Fade>
      
      <Fade in={showBadge} timeout={500}>
        <Box sx={{ mb: 3 }}>
          <Chip 
            icon={<LinkedInIcon sx={{ fontSize: 16 }} />} 
            label={intern.internType}
            className="badge"
            sx={{
              backgroundColor: '#f0f0f0',
              color: '#666666',
              fontWeight: 500,
              borderRadius: '20px',
              height: 32,
              '& .MuiChip-icon': {
                color: '#666666',
                fontSize: 16,
              }
            }}
          />
        </Box>
      </Fade>
      
      <Fade in={showDescription && !collectionState.isComplete} timeout={500} unmountOnExit>
        <Typography 
          variant="body1" 
          sx={{ 
            mb: 4,
            color: '#666666',
            fontSize: '16px',
            lineHeight: 1.6,
            maxWidth: '360px',
            margin: '0 auto 32px auto'
          }}
        >
          Let's get to work. To learn your writing style and how you'd like me to respond to certain messages, could you show me 10 relevant messages please?
        </Typography>
      </Fade>
      
      <Fade in={showProgressBar && !collectionState.isComplete} timeout={500} unmountOnExit>
        <Box className="modern-card" sx={{ p: 3, mx: 2 }}>
          <Progress 
            threadsCollected={collectionState.threadsCollected}
            isComplete={collectionState.isComplete}
            uploadSuccess={collectionState.uploadSuccess}
            uploadError={collectionState.uploadError}
          />
        </Box>
      </Fade>

      <Fade in={showCompletionMessage} timeout={500}>
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            minHeight: 150,
            flexDirection: 'column',
            gap: 2
          }}
        >
          <Box className="logo" sx={{ fontSize: '32px' }}>
            ✅
          </Box>
          <Typography 
            variant="body1"
            sx={{
              color: '#1a1a1a',
              fontSize: '18px',
              fontWeight: 500,
              maxWidth: '280px',
              lineHeight: 1.5,
            }}
          >
            Awesome! Once I have a <span className="highlight-text">draft</span> for you, I'll let you know.
          </Typography>
          
          {/* Stats */}
          <Box className="stats" sx={{ justifyContent: 'center', mt: 2 }}>
            <span>🎯</span>
            <Typography component="span">
              Learning your writing style...
            </Typography>
          </Box>
        </Box>
      </Fade>
    </Box>
  );
} 