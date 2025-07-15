import React, { useState, useEffect } from 'react';
import Lottie from 'lottie-react';
import welcomeAnimation from '../../animations/Welcome.json';
import artistAnimation from '../../animations/Artist.json';
import catsAnimation from '../../animations/Cats in a box.json';
import remoteWorkAnimation from '../../animations/Remote Work and Productivity.json';
import thinkingAnimation from '../../animations/Thinking (colors adapted).json';
import scaredAnimation from '../../animations/Scared 2D character.json';
import musicAnimation from '../../animations/Singing and playing Music with Guitar.json';
import { Sparkles, ArrowRight } from 'lucide-react';

interface WelcomePageProps {
  onComplete: () => void;
  theme: 'light' | 'dark' | 'color';
}

const WelcomePage: React.FC<WelcomePageProps> = ({ onComplete, theme }) => {
  const [showContent, setShowContent] = useState(false);
  const [showButton, setShowButton] = useState(false);
  const [currentAnimation, setCurrentAnimation] = useState(0);

  const animations = [
    { data: welcomeAnimation, title: "Welcome", description: "Ready to discover?" },
    { data: artistAnimation, title: "The Artist", description: "Creative and expressive" },
    { data: catsAnimation, title: "The Explorer", description: "Curious and playful" },
    { data: remoteWorkAnimation, title: "The Professional", description: "Productive and focused" },
    { data: thinkingAnimation, title: "The Thinker", description: "Analytical and thoughtful" },
    { data: scaredAnimation, title: "The Adventurer", description: "Bold and daring" },
    { data: musicAnimation, title: "The Musician", description: "Harmonious and rhythmic" }
  ];

  useEffect(() => {
    // Show content after animation starts
    const timer1 = setTimeout(() => setShowContent(true), 1000);
    const timer2 = setTimeout(() => setShowButton(true), 0);
    
    // Cycle through animations
    const animationInterval = setInterval(() => {
      setCurrentAnimation((prev) => (prev + 1) % animations.length);
    }, 2000);
    
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearInterval(animationInterval);
    };
  }, [animations.length]);

  const themes = {
    light: {
      bg: 'bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100',
      text: 'text-slate-900',
      card: 'bg-white/95 backdrop-blur-sm border-slate-200/60 shadow-xl',
      button: 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg',
      accent: 'text-blue-700',
      subtitle: 'text-slate-700'
    },
    dark: {
      bg: 'bg-gradient-to-br from-black via-gray-900 to-black',
      text: 'text-white',
      card: 'bg-gray-900/90 backdrop-blur-sm border-gray-700/50 shadow-2xl',
      button: 'bg-gradient-to-r from-gray-800 to-gray-900 hover:from-gray-700 hover:to-gray-800 shadow-lg',
      accent: 'text-gray-200',
      subtitle: 'text-gray-300'
    },
    color: {
      bg: 'bg-gradient-to-br from-[#0f0c29] via-[#302b63] to-[#24243e]',
      text: 'text-white',
      card: 'bg-white/10 backdrop-blur-sm border-white/20',
      button: 'bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90',
      accent: 'text-accent',
      subtitle: 'text-white/70'
    }
  };

  const currentTheme = themes[theme];

  return (
    <div className={`min-h-screen ${currentTheme.bg} transition-all duration-500`}>
      {/* Circular Animation Layout */}
      <div className="relative w-full h-[1200px] flex items-center justify-center mb-32" style={{ marginTop: '-50px' }}>
        {/* Center Welcome Animation */}
        <div className="absolute z-20">
          <div className="w-[500px] h-[500px]">
            <Lottie 
              animationData={welcomeAnimation} 
              loop={true}
              autoplay={true}
              style={{ width: '100%', height: '100%' }}
            />
          </div>
        </div>

        {/* Get Started Button - positioned exactly below welcome animation */}
        <div className={`absolute z-20 transition-all duration-1000 ${showButton ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`} style={{ top: '700px' }}>
          <button 
            onClick={onComplete}
            className={`${currentTheme.button} text-white px-8 py-4 rounded-xl font-semibold flex items-center gap-3 mx-auto transition-all duration-300 transform hover:scale-105 hover:shadow-2xl`}
          >
            Get Started <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        {/* Surrounding Animations */}
        {animations.slice(1).map((animation, index) => {
          let angle, radius;
          
          // Map each animation to a specific position
          const positions = [
            { title: "The Professional", angle: 0, radius: 400 },      // Top
            { title: "The Artist", angle: 60, radius: 400 },           // Top-right
            { title: "The Explorer", angle: 120, radius: 400 },        // Right
            { title: "The Thinker", angle: 180, radius: 400 },         // Bottom
            { title: "The Musician", angle: 240, radius: 400 },        // Bottom-left (moved down)
            { title: "The Adventurer", angle: 300, radius: 400 }       // Left
          ];
          
          const position = positions.find(p => p.title === animation.title) || positions[index];
          angle = position.angle;
          radius = position.radius;
          
          const x = Math.cos((angle * Math.PI) / 180) * radius;
          const y = Math.sin((angle * Math.PI) / 180) * radius;
          
          return (
            <div
              key={animation.title}
              className={`absolute z-10 transition-all duration-1000 ${
                showContent ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
              }`}
              style={{
                left: `calc(50% + ${x}px)`,
                top: `calc(50% + ${y}px)`,
                transform: 'translate(-50%, -50%)',
                transitionDelay: `${index * 200}ms`
              }}
            >
              <div className="w-80 h-80">
                <Lottie 
                  animationData={animation.data} 
                  loop={true}
                  autoplay={true}
                  style={{ width: '100%', height: '100%' }}
                />
              </div>
              <div className="text-center mt-4">
                <h3 className={`text-xl font-bold ${currentTheme.text} mb-2`}>
                  {animation.title}
                </h3>
                <p className={`text-sm ${currentTheme.subtitle} max-w-32`}>
                  {animation.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Welcome Text */}
      <div className={`transition-all duration-1000 delay-500 ${showContent ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
        <h1 className={`text-6xl font-bold mb-6 flex items-center justify-center gap-4 ${currentTheme.text}`}>
          Who Are You? <Sparkles className={`w-12 h-12 ${currentTheme.accent} animate-pulse`} />
        </h1>
        
        <p className={`text-xl ${currentTheme.subtitle} mb-8 max-w-3xl mx-auto leading-relaxed`}>
          Discover your true personality through AI analysis. Are you the Artist, the Thinker, the Explorer, 
          or something entirely unique? Let's find out together!
        </p>

        <div className={`${currentTheme.card} rounded-2xl shadow-xl p-8 max-w-3xl mx-auto mb-8`}>
          <h2 className={`text-2xl font-semibold mb-4 ${currentTheme.text}`}>Personality Archetypes</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center mx-auto mb-2">
                <span className="text-white font-bold">🎨</span>
              </div>
              <p className={currentTheme.subtitle}>The Artist</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-xl flex items-center justify-center mx-auto mb-2">
                <span className="text-white font-bold">🧠</span>
              </div>
              <p className={currentTheme.subtitle}>The Thinker</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mx-auto mb-2">
                <span className="text-white font-bold">🏢</span>
              </div>
              <p className={currentTheme.subtitle}>The Professional</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-xl flex items-center justify-center mx-auto mb-2">
                <span className="text-white font-bold">🎵</span>
              </div>
              <p className={currentTheme.subtitle}>The Musician</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage; 