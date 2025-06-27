import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { storage } from '../logic/storage';
import OnboardingRoot from './views/onboarding/OnboardingRoot';
import GeneralRoot from './views/general/GeneralRoot';
import InternCenter from './views/interncenter/InternCenter';

console.log('Sidepanel component loaded');

type View = 'internCenter' | 'onboarding' | 'general';

const Sidepanel = () => {
  const [userId, setUserId] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<View | null>(null);

  useEffect(() => {
    storage.initialize().then(() => {
      console.log('Storage initialized');
      Promise.all([
        storage.getUserId(),
        storage.isComplete()
      ]).then(([userId, complete]) => {
        console.log('Storage checks complete:', { userId, complete });
        setUserId(userId);
        if (complete) {
          setCurrentView('general');
        } else {
          setCurrentView('internCenter');
        }
      });
    });
  }, []);

  useEffect(() => {
    console.log('Setting up message listener');
    const messageListener = (message: any) => {
      if (message.type === 'UPLOAD_COMPLETE' && message.payload.success) {
        setCurrentView('general');
      }
    };

    chrome.runtime.onMessage.addListener(messageListener);

    return () => {
      chrome.runtime.onMessage.removeListener(messageListener);
    };
  }, []);

  const handleNavigateToOnboarding = () => {
    setCurrentView('onboarding');
  };

  const renderContent = () => {
    switch (currentView) {
      case 'internCenter':
        console.log('Rendering InternCenter');
        return <InternCenter onNavigateToOnboarding={handleNavigateToOnboarding} />;
      case 'onboarding':
        console.log('Rendering OnboardingRoot');
        return <OnboardingRoot />;
      case 'general':
        if (!userId) {
          console.log('No userId found, not rendering GeneralRoot');
          return null;
        }
        console.log(`userId ${userId} found, rendering GeneralRoot`);
        return <GeneralRoot userId={userId} />;
      default:
        console.log('No view to render');
        return null; // Or a loading spinner
    }
  }

  return (
    <div className="sidebar-container">
      <div className="sidebar-content">
        <Box sx={{ height: '100vh', bgcolor: 'transparent' }}>
          {renderContent()}
        </Box>
      </div>
    </div>
  );
};

// const Sidepanel = () => {
//   console.log('Sidepanel component rendering');
//   const [userId, setUserId] = useState<string | null>(null);
//   const [isOnboarding, setIsOnboarding] = useState(true);

//   // Check onboarding status on mount
//   useEffect(() => {
//     console.log('Checking onboarding status...');
//     // Initialize storage first to ensure we have a userId
//     storage.initialize().then(() => {
//       console.log('Storage initialized');
//       Promise.all([
//         storage.getUserId(),
//         storage.isComplete()
//       ]).then(([userId, complete]) => {
//         console.log('Storage checks complete:', { userId, complete });
//         setUserId(userId);
//         setIsOnboarding(!userId || !complete);
//       });
//     });
//   }, []);

//   useEffect(() => {
//     console.log('Setting up message listener');
//     const messageListener = (message: any) => {
//       console.log('Received message:', message);
//       if (message.type === 'UPLOAD_COMPLETE' && message.payload.success) {
//         setIsOnboarding(false);
//       }
//     };

//     chrome.runtime.onMessage.addListener(messageListener);
//     return () => {
//       chrome.runtime.onMessage.removeListener(messageListener);
//     };
//   }, []);

//   if (isOnboarding) {
//     console.log('Rendering OnboardingRoot');
//     return <OnboardingRoot />;
//   }

//   // Only render GeneralRoot if we have a userId
//   if (!userId) {
//     console.log('No userId found, not rendering GeneralRoot');
//     return null;
//   } else {
//     console.log(`userId ${userId} found, rendering GeneralRoot`);
//   }

//   return (
//     <Box sx={{ height: '100vh', bgcolor: '#f4f4f9' }}>
//       <GeneralRoot userId={userId} />
//     </Box>
//   );
// };

export default Sidepanel; 