import React, { useState } from 'react';
import HeroSection from './HeroSection';
import WelcomePage from './WelcomePage';

const App = () => {
  const [showWelcome, setShowWelcome] = useState(true);
  const [theme, setTheme] = useState<'light' | 'dark' | 'color'>('color');

  const handleWelcomeComplete = () => {
    setShowWelcome(false);
  };

  if (showWelcome) {
    return <WelcomePage onComplete={handleWelcomeComplete} theme={theme} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 relative overflow-hidden">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-20 w-2 h-2 bg-white/20 rounded-full animate-pulse"></div>
        <div className="absolute top-40 right-32 w-1 h-1 bg-purple-300/30 rounded-full animate-bounce"></div>
        <div className="absolute bottom-32 left-1/3 w-3 h-3 bg-blue-300/20 rounded-full animate-ping"></div>
        <div className="absolute top-1/2 right-20 w-1 h-1 bg-indigo-300/40 rounded-full animate-pulse"></div>
      </div>
      
      <div className="relative z-10">
        <HeroSection />
      </div>
    </div>
  );
};

export default App; 