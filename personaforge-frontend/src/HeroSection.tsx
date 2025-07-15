import React, { useState, useRef, useEffect, useMemo } from 'react';
import { Search, Sparkles, ArrowRight, Sun, Moon, Palette, History, MessageCircle, X, Send } from 'lucide-react';

// Add proper timeout type
type TimeoutID = ReturnType<typeof setTimeout>;

type ChatMessage = {
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
};

type HistoryItem = {
  username: string;
  timestamp: Date;
  data: any;
};

// --- Mock Data Generators ---
// REMOVED: All mock data generators and fake data functions

// --- Chart Color Palette ---
const chartColors = {
  blue: '#60A5FA',
  pink: '#F472B6', 
  green: '#34D399',
  yellow: '#FBBF24',
  violet: '#A78BFA',
  orange: '#FB923C',
  red: '#F87171',
  cyan: '#22D3EE'
};

// --- Glassmorphic Card Wrapper Component ---
const ChartCard = ({ children, title, subtitle, className = '', height = 'h-[360px]', theme = 'dark' }: { 
  children: React.ReactNode; 
  title?: string; 
  subtitle?: string;
  className?: string;
  height?: string;
  theme?: 'light' | 'dark' | 'color';
}) => {
  const themes = {
    light: {
      card: 'bg-white/95 backdrop-blur-sm border-slate-200/60 shadow-xl',
      title: 'text-slate-900',
      subtitle: 'text-slate-700'
    },
    dark: {
      card: 'bg-gray-900/90 backdrop-blur-sm border-gray-700/50 shadow-2xl',
      title: 'text-white',
      subtitle: 'text-gray-300'
    },
    color: {
      card: 'bg-white/10 backdrop-blur-sm border-white/20 shadow-xl',
      title: 'text-white',
      subtitle: 'text-white/70'
    }
  };
  
  const currentTheme = themes[theme];
  
  return (
    <div className={`rounded-2xl ${currentTheme.card} p-6 hover:scale-[1.01] transition-all duration-300 ${className}`}>
    {title && (
      <div className="mb-6">
          <h3 className={`text-xl font-semibold ${currentTheme.title} drop-shadow-glow mb-1`}>{title}</h3>
          {subtitle && <p className={`text-sm ${currentTheme.subtitle}`}>{subtitle}</p>}
      </div>
    )}
    <div className={`${height} w-full flex items-center justify-center`}>
      {children}
    </div>
  </div>
);
};

// --- Tag Chip Component for Raw Stats ---
const TagChip = ({ label, value, color = 'blue', theme = 'dark' }: { 
  label: string; 
  value: number; 
  color?: keyof typeof chartColors;
  theme?: 'light' | 'dark' | 'color';
}) => {
  const themes = {
    light: {
      bg: 'bg-white border-slate-200 hover:bg-slate-50 shadow-md',
      label: 'text-slate-600',
      value: 'text-slate-900'
    },
    dark: {
      bg: 'bg-gray-800 border-gray-600 hover:bg-gray-700 shadow-lg',
      label: 'text-gray-300',
      value: 'text-white'
    },
    color: {
      bg: 'bg-white/15 border-white/30 hover:bg-white/20',
      label: 'text-white/70',
      value: 'text-white'
    }
  };
  
  const currentTheme = themes[theme];
  
  return (
    <div className={`flex items-center justify-between ${currentTheme.bg} px-4 py-3 rounded-full border transition-colors`}>
      <span className={`text-sm ${currentTheme.label}`}>{label}</span>
      <span className={`text-base font-bold ${currentTheme.value}`}>{value}%</span>
  </div>
);
};

// --- Visualization Components ---
const bigFiveColors = [
  'from-pink-400 to-purple-400',
  'from-blue-400 to-cyan-400',
  'from-green-400 to-emerald-400',
  'from-yellow-400 to-orange-400',
  'from-red-400 to-pink-500'
];

const bigFiveSolidColors = [
  '#F472B6', // pink
  '#60A5FA', // blue
  '#34D399', // green
  '#FBBF24', // yellow
  '#A78BFA', // violet
];

const BigFiveBarChart = ({ traits, theme = 'dark' }: { traits: { name: string; value: number; color: string }[]; theme?: 'light' | 'dark' | 'color' }) => {
  // Ensure traits is an array and has valid data
  const validTraits = useMemo(() => 
    Array.isArray(traits) ? traits.filter(trait => 
      trait && typeof trait === 'object' && 
      typeof trait.name === 'string' && 
      typeof trait.value === 'number' &&
      typeof trait.color === 'string'
    ) : [], [traits]
  );
  
  const [animatedValues, setAnimatedValues] = useState(validTraits.map(() => 0));
  const [hovered, setHovered] = useState<number | null>(null);

  useEffect(() => {
    setAnimatedValues(validTraits.map(() => 0));
    const timeouts: TimeoutID[] = [];
    validTraits.forEach((trait, i) => {
      timeouts.push(setTimeout(() => {
        setAnimatedValues(vals => {
          const newVals = [...vals];
          newVals[i] = trait.value;
          return newVals;
        });
      }, 200 + i * 180));
    });
    return () => timeouts.forEach(clearTimeout);
  }, [validTraits]);

  // If no valid data, show a message
  if (validTraits.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">🧠</div>
          <p className="text-gray-500 text-sm">No personality data available</p>
        </div>
      </div>
    );
  }

  const maxBarHeight = 200;
  const chartWidth = 500; // px, increased from 450 to 500 for more space
  const gap = 50; // px gap between bars - back to 50
  const barCount = validTraits.length;
  const barWidth = (chartWidth - gap * (barCount + 1)) / barCount;

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-4">
      <div className="flex w-full h-full items-end justify-between" style={{maxWidth: chartWidth, margin: '0 auto'}}>
        {validTraits.map((trait, i) => (
          <div key={trait.name} className="flex flex-col items-center" style={{width: barWidth + gap}}>
            <div
              className={`relative flex items-end justify-center transition-transform duration-200 ${hovered===i ? 'scale-110 z-20' : ''}`}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              style={{height: maxBarHeight}}
            >
              <div
                className="rounded-b-2xl shadow-2xl border border-white/20 relative transition-all duration-300"
                style={{
                  width: barWidth,
                  height: `${(animatedValues[i]/100)*maxBarHeight}px`,
                  background: bigFiveSolidColors[i],
                  marginLeft: gap / 2,
                  marginRight: gap / 2,
                  boxShadow: hovered===i
                    ? `0 0 48px 16px ${bigFiveSolidColors[i]}88, 0 8px 32px 0 #fff3, 0 0 20px ${bigFiveSolidColors[i]}66`
                    : `0 4px 32px 0 ${bigFiveSolidColors[i]}44, 0 0 15px ${bigFiveSolidColors[i]}33`,
                }}
              >
                <div className="absolute left-0 top-0 w-full h-1/3 rounded-t-2xl bg-white/30 blur-sm opacity-60 pointer-events-none" />
                {hovered===i && (
                  <div className="absolute inset-0 rounded-b-2xl bg-white/20 blur-lg animate-pulse pointer-events-none" />
                )}
              </div>
              <span className="absolute -top-8 left-1/2 -translate-x-1/2 text-base font-bold text-white drop-shadow-glow select-none pointer-events-none">
                {animatedValues[i]}%
              </span>
              {hovered===i && (
                <div
                  className="absolute left-1/2 -translate-x-1/2 w-16 h-1 bg-gradient-to-r from-white via-primary to-accent shadow-lg animate-pulse"
                  style={{bottom: `${(animatedValues[i]/100)*maxBarHeight}px`}}
                />
              )}
            </div>
            <span className={`mt-8 min-w-[120px] px-1 text-xs font-bold text-center whitespace-nowrap ${theme === 'light' ? 'text-red-500' : 'text-white'}`} style={{lineHeight: '1.1'}}>{trait.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const RadarChart = ({ values, theme = 'dark' }: { values: { name: string; value: number }[]; theme?: 'light' | 'dark' | 'color' }) => {
  // Ensure values is an array and has valid data
  const validValues = useMemo(() => 
    Array.isArray(values) ? values.filter(value => 
      value && typeof value === 'object' && 
      typeof value.name === 'string' && 
      typeof value.value === 'number'
    ) : [], [values]
  );
  
  const [animatedVals, setAnimatedVals] = useState(validValues.map(() => 0));
  const [hovered, setHovered] = useState<number | null>(null);
  
  useEffect(() => {
    setAnimatedVals(validValues.map(() => 0));
    setHovered(null);
    const timeouts: TimeoutID[] = [];
    validValues.forEach((v, i) => {
      timeouts.push(setTimeout(() => {
        setAnimatedVals(vals => {
          const newVals = [...vals];
          newVals[i] = v.value;
          return newVals;
        });
      }, 200 + i * 120));
    });
    return () => timeouts.forEach(clearTimeout);
  }, [validValues]);
  
  // If no valid data, show a message
  if (validValues.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">📊</div>
          <p className="text-gray-500 text-sm">No radar data available</p>
        </div>
      </div>
    );
  }
  
  const N = validValues.length;
  const angle = (i: number) => (2 * Math.PI * i) / N;
  const radius = 120;
  const center = 150;
  const points = animatedVals.map((val, i) => {
    const r = radius * (val / 100);
    return [center + r * Math.sin(angle(i)), center - r * Math.cos(angle(i))];
  });
  const polygon = points.map(([x, y]) => `${x},${y}`).join(' ');
  
  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-4">
      <svg width={300} height={300} className="mx-auto relative block">
        {/* Background circle at 100% radius */}
        <circle cx={center} cy={center} r={radius} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth={1} />
        {validValues.map((v, i) => (
          <line key={v.name} x1={center} y1={center} x2={center + radius * Math.sin(angle(i))} y2={center - radius * Math.cos(angle(i))} stroke="#60a5fa" strokeDasharray="4 2" />
        ))}
        <polygon points={polygon} fill="#60a5fa88" stroke="#3b82f6" strokeWidth={4} style={{
          transition: 'all 1s cubic-bezier(.4,2,.6,1)',
          filter: 'drop-shadow(0 0 20px rgba(96, 165, 250, 0.6)) drop-shadow(0 0 10px rgba(59, 130, 246, 0.4))'
        }} />
        {points.map(([x, y], i) => (
          <g key={i}>
            <circle
              cx={x}
              cy={y}
              r={12}
              fill="#3b82f6"
              stroke="#fff"
              strokeWidth={3}
              style={{
                filter: hovered === i ? 'drop-shadow(0 0 28px #60a5fa) drop-shadow(0 0 16px #fff)' : 'none',
                transition: 'filter 0.3s ease',
                transform: hovered === i ? 'scale(1.2)' : 'scale(1)',
                transformOrigin: 'center'
              }}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            />
            {hovered === i && (
              <foreignObject x={x-60} y={y-60} width={120} height={44} style={{pointerEvents: 'none'}}>
                <div className="bg-blue-700/90 text-white text-sm rounded px-2 py-1 shadow-lg text-center animate-fade-in">
                  {validValues[i].name}: <b>{animatedVals[i]}%</b>
                </div>
              </foreignObject>
            )}
          </g>
        ))}
      </svg>
      <div className="flex flex-wrap justify-center gap-3 mt-4 w-full">
        {validValues.map((v, i) => (
          <span key={v.name} className={`text-sm px-3 py-1 text-center font-semibold ${theme === 'light' ? 'text-purple-400' : 'text-white'}`}>{v.name}: <b>{animatedVals[i]}%</b></span>
        ))}
      </div>
    </div>
  );
};

const PieChart = ({ traits, theme = 'dark' }: { traits: { name: string; value: number }[]; theme?: 'light' | 'dark' | 'color' }) => {
  // Ensure traits is an array and has valid data
  const validTraits = useMemo(() => 
    Array.isArray(traits) ? traits.filter(trait => 
      trait && typeof trait === 'object' && 
      typeof trait.name === 'string' && 
      typeof trait.value === 'number'
    ) : [], [traits]
  );
  
  const [animatedVals, setAnimatedVals] = useState(validTraits.map(() => 0));
  const [hovered, setHovered] = useState<number | null>(null);
  
  useEffect(() => {
    setAnimatedVals(validTraits.map(() => 0));
    const timeouts: TimeoutID[] = [];
    validTraits.forEach((t, i) => {
      timeouts.push(setTimeout(() => {
        setAnimatedVals(vals => {
          const newVals = [...vals];
          newVals[i] = t.value;
          return newVals;
        });
      }, 200 + i * 120));
    });
    return () => timeouts.forEach(clearTimeout);
  }, [validTraits]);
  
  // If no valid data, show a message
  if (validTraits.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">🥧</div>
          <p className="text-gray-500 text-sm">No pie chart data available</p>
        </div>
      </div>
    );
  }
  
  const total = validTraits.reduce((sum, t) => sum + t.value, 0);
  const colors = [chartColors.blue, chartColors.pink, chartColors.green, chartColors.yellow, chartColors.violet];
  
  // Increase pie chart size
  const pieSize = 360;
  const pieRadius = 120;
  const center = pieSize / 2;
  const tooltipWidth = 120;
  const tooltipHeight = 60;

  let currentAngle = 0;
  const segments = validTraits.map((trait, i) => {
    const angle = (trait.value / total) * 360;
    const startAngle = currentAngle;
    currentAngle += angle;
    
    const x1 = center + pieRadius * Math.cos((startAngle - 90) * Math.PI / 180);
    const y1 = center + pieRadius * Math.sin((startAngle - 90) * Math.PI / 180);
    const x2 = center + pieRadius * Math.cos((currentAngle - 90) * Math.PI / 180);
    const y2 = center + pieRadius * Math.sin((currentAngle - 90) * Math.PI / 180);
    
    const largeArcFlag = angle > 180 ? 1 : 0;
    // Calculate tooltip position at the edge of the segment
    const tooltipRadius = pieRadius; // edge of the pie
    const tooltipAngle = startAngle + angle / 2;
    let tooltipX = center + tooltipRadius * Math.cos((tooltipAngle - 90) * Math.PI / 180);
    let tooltipY = center + tooltipRadius * Math.sin((tooltipAngle - 90) * Math.PI / 180);
    // Clamp tooltip position to stay within SVG
    tooltipX = Math.max(tooltipWidth / 2, Math.min(pieSize - tooltipWidth / 2, tooltipX));
    tooltipY = Math.max(tooltipHeight / 2, Math.min(pieSize - tooltipHeight / 2, tooltipY));
    
    return {
      ...trait,
      startAngle,
      endAngle: currentAngle,
      angle,
      path: `M ${center} ${center} L ${x1} ${y1} A ${pieRadius} ${pieRadius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`,
      tooltipX,
      tooltipY,
      color: colors[i % colors.length]
    };
  });
  
  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-4">
      <svg width={pieSize} height={pieSize} className="mx-auto relative block">
        {segments.map((segment, i) => (
          <g key={i}>
            <path
              d={segment.path}
              fill={segment.color}
              stroke="#fff"
              strokeWidth={2}
              style={{
                filter: hovered === i 
                  ? `drop-shadow(0 0 25px ${segment.color}cc) drop-shadow(0 0 15px ${segment.color}88)` 
                  : `drop-shadow(0 0 10px ${segment.color}44)`,
                transition: 'all 0.3s ease',
                transform: hovered === i ? 'scale(1.05)' : 'scale(1)'
              }}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            />
            {hovered === i && (
              <foreignObject x={segment.tooltipX - tooltipWidth / 2} y={segment.tooltipY - tooltipHeight / 2} width={tooltipWidth} height={tooltipHeight} style={{pointerEvents: 'none'}}>
                <div className="bg-blue-700/90 text-white text-sm rounded px-2 py-1 shadow-lg text-center animate-fade-in">
                  {segment.name}: <b>{segment.value}%</b>
                </div>
              </foreignObject>
            )}
          </g>
        ))}
        <circle cx={center} cy={center} r={40} fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.3)" strokeWidth={2} />
      </svg>
      
      {/* Labels below the chart */}
      <div className="flex justify-between w-full mt-4 px-8">
        {validTraits.map((trait, i) => (
          <div
            key={`label-${i}`}
            className={`text-center transition-all duration-300 ${
              hovered === i 
                ? 'text-blue-300 font-bold scale-110' 
                : 'text-white font-semibold'
            }`}
            style={{
              width: `${100 / validTraits.length}%`,
              textShadow: hovered === i ? '0 0 8px rgba(96, 165, 250, 0.6)' : 'none'
            }}
          >
            <span className={`text-sm font-semibold ${theme === 'light' ? 'text-orange-400' : 'text-white'}`}>{trait.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const LineChart = ({ events, theme = 'dark' }: { events: { name: string; value: number }[]; theme?: 'light' | 'dark' | 'color' }) => {
  // Ensure events is an array and has valid data
  const validEvents = useMemo(() => 
    Array.isArray(events) ? events.filter(event => 
      event && typeof event === 'object' && 
      typeof event.name === 'string' && 
      typeof event.value === 'number'
    ) : [], [events]
  );
  
  const [animatedVals, setAnimatedVals] = useState(validEvents.map(() => 0));
  const [hovered, setHovered] = useState<number | null>(null);
  
  useEffect(() => {
    setAnimatedVals(validEvents.map(() => 0));
    const timeouts: TimeoutID[] = [];
    validEvents.forEach((e, i) => {
      timeouts.push(setTimeout(() => {
        setAnimatedVals(vals => {
          const newVals = [...vals];
          newVals[i] = e.value;
          return newVals;
        });
      }, 200 + i * 120));
    });
    return () => timeouts.forEach(clearTimeout);
  }, [validEvents]);
  
  // If no valid data, show a message
  if (validEvents.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">📈</div>
          <p className="text-gray-500 text-sm">No timeline data available</p>
        </div>
      </div>
    );
  }
  
  const maxValue = Math.max(...validEvents.map(e => e.value), 100);
  const chartWidth = 400; // Increased from 300
  const chartHeight = 300; // Increased from 240
  const points = validEvents.map((event, i) => ({
    x: (i / (validEvents.length - 1)) * (chartWidth - 60) + 30,
    y: chartHeight - 60 - (animatedVals[i] / maxValue) * (chartHeight - 120)
  }));
  
  const pathData = points.map((point, i) => 
    `${i === 0 ? 'M' : 'L'} ${point.x} ${point.y}`
  ).join(' ');
  
  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-4">
      <svg width={chartWidth} height={chartHeight} className="mx-auto relative block">
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map((value, i) => (
          <line
            key={i}
            x1={30}
            y1={chartHeight - 60 - (value / 100) * (chartHeight - 120)}
            x2={chartWidth - 30}
            y2={chartHeight - 60 - (value / 100) * (chartHeight - 120)}
            stroke="rgba(255,255,255,0.1)"
            strokeWidth={1}
          />
        ))}
        
        {/* Main line path */}
        <path
          d={pathData}
          stroke={chartColors.green}
          strokeWidth={5}
          fill="none"
          style={{
            filter: 'drop-shadow(0 0 20px rgba(52, 211, 153, 0.7)) drop-shadow(0 0 10px rgba(52, 211, 153, 0.4))',
            transition: 'all 1s cubic-bezier(.4,2,.6,1)'
          }}
        />
        
        {/* Data points with hover interactions */}
        {points.map((point, i) => (
          <g key={i}>
          <circle
            cx={point.x}
            cy={point.y}
              r={hovered === i ? 12 : 8}
            fill={chartColors.green}
            stroke="#fff"
              strokeWidth={hovered === i ? 4 : 3}
            style={{
                filter: hovered === i 
                  ? 'drop-shadow(0 0 20px rgba(52, 211, 153, 0.8)) drop-shadow(0 0 10px #fff)' 
                  : 'drop-shadow(0 0 8px rgba(52, 211, 153, 0.6))',
                transition: 'all 0.3s cubic-bezier(.4,2,.6,1)',
                cursor: 'pointer'
              }}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            />
            
            {/* Hover tooltip */}
            {hovered === i && (
              <foreignObject 
                x={point.x - 60} 
                y={point.y - 80} 
                width={120} 
                height={60} 
                style={{pointerEvents: 'none'}}
              >
                <div className="bg-green-700/90 text-white text-sm rounded-lg px-3 py-2 shadow-xl text-center animate-fade-in border border-green-500/50">
                  <div className="font-bold">{validEvents[i].name}</div>
                  <div className="text-green-200">{animatedVals[i]}%</div>
                </div>
              </foreignObject>
            )}
          </g>
        ))}
      </svg>
      
      {/* Labels below the chart */}
      <div className="flex justify-between w-full mt-4 px-8">
        {validEvents.map((event, i) => (
          <div
            key={`label-${i}`}
            className={`text-center transition-all duration-300 ${
              hovered === i 
                ? 'text-green-300 font-bold scale-110' 
                : 'text-white font-semibold'
            }`}
            style={{
              width: `${100 / validEvents.length}%`,
              textShadow: hovered === i ? '0 0 8px rgba(52, 211, 153, 0.6)' : 'none'
            }}
          >
            <span className={`text-sm font-semibold ${theme === 'light' ? 'text-green-400' : 'text-white'}`}>{event.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const RadialProgress = ({ goals }: { goals: { name: string; value: number }[] }) => {
  // Ensure goals is an array and has valid data
  const validGoals = Array.isArray(goals) ? goals.filter(goal => 
    goal && typeof goal === 'object' && 
    typeof goal.name === 'string' && 
    typeof goal.value === 'number'
  ) : [];
  
  const [animatedVals, setAnimatedVals] = useState(validGoals.map(() => 0));
  const [hovered, setHovered] = useState<number | null>(null);
  
  useEffect(() => {
    setAnimatedVals(validGoals.map(() => 0));
    const timeouts: TimeoutID[] = [];
    validGoals.forEach((g, i) => {
      timeouts.push(setTimeout(() => {
        setAnimatedVals(vals => {
          const newVals = [...vals];
          newVals[i] = g.value;
          return newVals;
        });
      }, 200 + i * 120));
    });
    return () => timeouts.forEach(clearTimeout);
  }, [validGoals]);
  
  // If no valid data, show a message
  if (validGoals.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">🎯</div>
          <p className="text-gray-500 text-sm">No goals data available</p>
        </div>
      </div>
    );
  }
  
  const size = 140; // Increased from 120 to 140
  const radius = size / 2.8;
  const circumference = 2 * Math.PI * radius;
  
  return (
    <div className="flex items-center justify-center gap-8">
        {validGoals.map((g, i) => (
        <div 
          key={g.name} 
          className="flex flex-col items-center cursor-pointer transition-all duration-300"
          style={{
            transform: hovered === i ? 'scale(1.1)' : 'scale(1)',
            background: 'transparent',
            border: 'none',
            outline: 'none',
            boxShadow: 'none',
            borderRadius: '0',
            padding: '0',
            margin: '0'
          }}
          onMouseEnter={() => setHovered(i)}
          onMouseLeave={() => setHovered(null)}
        >
            <svg width={size} height={size} className="mb-3" viewBox={`0 0 ${size} ${size}`} style={{background: 'transparent'}}>
              <circle 
                cx={size/2} 
                cy={size/2} 
                r={radius} 
                fill="transparent" 
                stroke="rgba(255,255,255,0.1)" 
                strokeWidth={size/12} 
              />
              <circle
                cx={size/2}
                cy={size/2}
                r={radius}
                fill="none"
                stroke={chartColors.yellow}
                strokeWidth={size/12}
                strokeDasharray={circumference}
                strokeDashoffset={circumference - (animatedVals[i] / 100) * circumference}
                style={{
                  transition: 'stroke-dashoffset 1s cubic-bezier(.4,2,.6,1)', 
                  filter: hovered === i 
                    ? 'drop-shadow(0 0 25px #fbbf24) drop-shadow(0 0 15px #fbbf24cc) drop-shadow(0 0 8px #fff)'
                    : 'drop-shadow(0 0 15px #fbbf24) drop-shadow(0 0 8px #fbbf24cc)'
                }}
                strokeLinecap="round"
              />
              <text 
                x={size/2} 
                y={size/2+6} 
                textAnchor="middle" 
                fill="#fbbf24" 
                fontSize={size/6} 
                fontWeight="bold"
                style={{
                  filter: hovered === i ? 'drop-shadow(0 0 8px #fbbf24)' : 'none',
                  transition: 'all 0.3s ease'
                }}
              >
                {animatedVals[i]}%
              </text>
            </svg>
            <span 
              className={`text-sm font-bold text-center transition-all duration-300 ${
                hovered === i ? 'text-yellow-300 scale-110' : 'text-white'
              }`}
              style={{
                textShadow: hovered === i ? '0 0 8px rgba(251, 191, 36, 0.6)' : 'none',
                background: 'transparent',
                border: 'none',
                outline: 'none'
              }}
            >
              <span className="text-yellow-400 font-semibold">{g.name}</span>
            </span>
          </div>
        ))}
    </div>
  );
};

const BarChart = ({ issues, theme = 'dark' }: { issues: { name: string; value: number }[]; theme?: 'light' | 'dark' | 'color' }) => {
  // Ensure issues is an array and has valid data
  const validIssues = useMemo(() => 
    Array.isArray(issues) ? issues.filter(issue => 
      issue && typeof issue === 'object' && 
      typeof issue.name === 'string' && 
      typeof issue.value === 'number'
    ) : [], [issues]
  );
  
  const [animatedVals, setAnimatedVals] = useState(validIssues.map(() => 0));
  
  useEffect(() => {
    setAnimatedVals(validIssues.map(() => 0));
    const timeouts: TimeoutID[] = [];
    validIssues.forEach((f, i) => {
      timeouts.push(setTimeout(() => {
        setAnimatedVals(vals => {
          const newVals = [...vals];
          newVals[i] = f.value;
          return newVals;
        });
      }, 200 + i * 180));
    });
    return () => timeouts.forEach(clearTimeout);
  }, [validIssues]);

  // If no valid data, show a message
  if (validIssues.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">📊</div>
          <p className="text-gray-500 text-sm">No data available for this chart</p>
        </div>
      </div>
    );
  }

  const max = Math.max(...validIssues.map(f => f.value), 100);
  const chartWidth = 360; // SVG viewBox width
  const chartHeight = 200; // SVG viewBox height
  const barCount = validIssues.length;
  const gapRatio = 0.5; // ratio of gap to bar width
  const totalGap = (barCount + 1) * gapRatio;
  const barWidth = chartWidth / (barCount + totalGap);
  const barGap = barWidth * gapRatio;

  // Beautiful gradient colors for each bar
  const barColors = [
    'from-red-400 to-red-600',
    'from-orange-400 to-orange-600', 
    'from-yellow-400 to-yellow-600',
    'from-pink-400 to-pink-600',
    'from-purple-400 to-purple-600',
    'from-blue-400 to-blue-600'
  ];

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-4">
      <svg width="100%" height={chartHeight} viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="mx-auto relative block">
        <defs>
          {/* Define gradients for each bar */}
          <linearGradient id="barGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#f87171" />
            <stop offset="100%" stopColor="#dc2626" />
          </linearGradient>
          <linearGradient id="barGrad2" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#fb923c" />
            <stop offset="100%" stopColor="#ea580c" />
          </linearGradient>
          <linearGradient id="barGrad3" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#fbbf24" />
            <stop offset="100%" stopColor="#d97706" />
          </linearGradient>
          <linearGradient id="barGrad4" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#f472b6" />
            <stop offset="100%" stopColor="#be185d" />
          </linearGradient>
          <linearGradient id="barGrad5" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#a78bfa" />
            <stop offset="100%" stopColor="#7c3aed" />
          </linearGradient>
          <linearGradient id="barGrad6" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#60a5fa" />
            <stop offset="100%" stopColor="#2563eb" />
          </linearGradient>
        </defs>
        {validIssues.map((f, i) => {
          const barHeight = (animatedVals[i] / max) * 120;
          const x = barGap + i * (barWidth + barGap);
          return (
            <g key={f.name}>
              <rect
                x={x}
                y={160 - barHeight}
                width={barWidth}
                height={barHeight}
                rx={barWidth/2.5}
                fill={`url(#barGrad${(i % 6) + 1})`}
                style={{
                  filter: `drop-shadow(0 0 18px ${i % 6 === 0 ? '#ef4444' : i % 6 === 1 ? '#fb923c' : i % 6 === 2 ? '#fbbf24' : i % 6 === 3 ? '#f472b6' : i % 6 === 4 ? '#a78bfa' : '#60a5fa'}cc) drop-shadow(0 0 6px #fff)`,
                  transition: 'all 0.3s ease',
                  animation: `pulse ${2 + i * 0.2}s infinite`
                }}
              />
              <text 
                x={x + barWidth/2} 
                y={160 - barHeight - 8} 
                textAnchor="middle" 
                fill="#fff" 
                fontSize={12} 
                fontWeight="bold"
                style={{
                  filter: 'drop-shadow(0 0 4px rgba(0,0,0,0.5))'
                }}
              >
                {animatedVals[i]}%
              </text>
              <foreignObject x={x - 16} y={165} width={barWidth + 32} height={30} style={{overflow: 'visible'}}>
                <div style={{
                  textAlign: 'center', 
                  fontSize: 11, 
                  fontWeight: 700, 
                  wordBreak: 'break-word', 
                  lineHeight: 1.1, 
                  width: '100%',
                  color: '#ef4444'
                }}>
                  {f.name}
                </div>
              </foreignObject>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

// --- Main HeroSection ---
const HeroSection = () => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [theme, setTheme] = useState<'light' | 'dark' | 'color'>('dark');
  const [historyOpen, setHistoryOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [analysisHistory, setAnalysisHistory] = useState<HistoryItem[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [maxPosts, setMaxPosts] = useState(25); // Updated to match backend default
  const [maxComments, setMaxComments] = useState(30); // Updated to match backend default
  
  // Memoize chart data to prevent infinite re-renders
  const chartData = useMemo(() => {
    if (!result?.persona?.chart_data) return null;
    return {
      big_five: result.persona.chart_data.big_five || [],
      personality_radar: result.persona.chart_data.personality_radar || [],
      interests_pie: result.persona.chart_data.interests_pie || [],
      community_engagement: result.persona.chart_data.community_engagement || [],
      activity_patterns: result.persona.chart_data.activity_patterns || [],
      sentiment_timeline: result.persona.chart_data.sentiment_timeline || [],
      real_content: result.persona.chart_data.real_content || null
    };
  }, [result?.persona?.chart_data]);
  
  // Memoize individual chart data arrays to prevent infinite re-renders
  const bigFiveData = useMemo(() => chartData?.big_five || [], [chartData?.big_five]);
  const personalityRadarData = useMemo(() => chartData?.personality_radar || [], [chartData?.personality_radar]);
  const interestsPieData = useMemo(() => chartData?.interests_pie || [], [chartData?.interests_pie]);
  const communityEngagementData = useMemo(() => chartData?.community_engagement || [], [chartData?.community_engagement]);
  const activityPatternsData = useMemo(() => chartData?.activity_patterns || [], [chartData?.activity_patterns]);
  const sentimentTimelineData = useMemo(() => chartData?.sentiment_timeline || [], [chartData?.sentiment_timeline]);
  
  // Load history from localStorage on component mount
  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem('personaforge_history');
      if (savedHistory) {
        const parsedHistory = JSON.parse(savedHistory);
        // Convert timestamp strings back to Date objects
        const historyWithDates = parsedHistory.map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }));
        setAnalysisHistory(historyWithDates);
      }
    } catch (error) {
      console.error('Error loading history from localStorage:', error);
    }
  }, []);
  
  // Save history to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('personaforge_history', JSON.stringify(analysisHistory));
    } catch (error) {
      console.error('Error saving history to localStorage:', error);
    }
  }, [analysisHistory]);
  const resultsRef = React.useRef<HTMLDivElement>(null);
  const chatEndRef = React.useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check if this username is already in history
    const existingHistoryItem = analysisHistory.find(item => 
      item.username.toLowerCase() === username.toLowerCase()
    );
    
    if (existingHistoryItem) {
      // Load from history instead of regenerating
      loadHistoryItem(existingHistoryItem);
      return;
    }
    
    setLoading(true);
    
    try {
      // Extract username from Reddit URL or use as-is
      let extractedUsername = username;
      
      // Handle Reddit URLs
      if (username.includes('reddit.com') || username.includes('redd.it')) {
        // Extract username from various Reddit URL formats
        const urlPatterns = [
          /reddit\.com\/user\/([^\/\?]+)/i,
          /reddit\.com\/r\/[^\/]+\/comments\/[^\/]+\/[^\/]+\/comment\/([^\/\?]+)/i,
          /reddit\.com\/r\/[^\/]+\/comments\/[^\/]+\/([^\/\?]+)/i,
          /u\/([^\/\?]+)/i
        ];
        
        for (const pattern of urlPatterns) {
          const match = username.match(pattern);
          if (match) {
            extractedUsername = match[1];
            break;
          }
        }
        
        // If no pattern matched, try to extract from the last part of the URL
        if (extractedUsername === username) {
          const urlParts = username.split('/');
          extractedUsername = urlParts[urlParts.length - 1].split('?')[0];
        }
      }
      
      // Remove any remaining URL parameters or fragments
      extractedUsername = extractedUsername.split('?')[0].split('#')[0];
      
      console.log(`Analyzing Reddit user: ${extractedUsername}`);
      
      // Call the backend API endpoint
      const response = await fetch('http://localhost:8080/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: extractedUsername,
          max_posts: maxPosts,
          max_comments: maxComments,
          save_json: true,
          generate_pdf: true,
          save_visualizations: true
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const apiResult = await response.json();
      
      if (apiResult.error) {
        throw new Error(apiResult.error);
      }
      
      // Transform the API result to match our frontend format
      const transformedResult = {
        // Include real data from the API
        username: apiResult.username, // This is the key field we were missing!
        persona: apiResult.persona,
        analysisMetadata: apiResult.metadata || apiResult.persona?.metadata,
        // Add metadata for display
        metadata: {
          source: apiResult.persona?.metadata?.source || 'Reddit API',
          confidence: apiResult.persona?.metadata?.confidence_overall || 0.6,
          posts_analyzed: apiResult.persona?.metadata?.posts_analyzed || 'Unknown',
          comments_analyzed: apiResult.persona?.metadata?.comments_analyzed || 'Unknown'
        }
      };
      
      setResult(transformedResult);
      
      // Add to history with complete data
      const newHistoryItem = {
        username: extractedUsername,
        timestamp: new Date(),
        data: transformedResult
      };
      
      setAnalysisHistory(prev => {
        const filtered = prev.filter(item => item.username !== extractedUsername);
        return [newHistoryItem, ...filtered.slice(0, 9)];
      });
      
      setLoading(false);
      
      // Scroll to results after a short delay to ensure DOM is updated
    setTimeout(() => {
        resultsRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }, 100);
      
    } catch (error) {
      console.error('Analysis failed:', error);
      setLoading(false);
      
      // Show error message instead of fake data
      let errorMessage = 'Analysis failed. Please try a different username or check if the user exists on Reddit.';
      
      if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Unable to connect to the analysis server. Please make sure the backend is running.';
      } else if (error.message.includes('No data found')) {
        errorMessage = 'No Reddit data found for this user. They might be private or have no public activity.';
      } else if (error.message.includes('Invalid Reddit username')) {
        errorMessage = 'Invalid Reddit username or URL format. Please enter a valid username or Reddit URL.';
      } else {
        errorMessage = `Analysis failed: ${error.message}. Please try a different username or check if the user exists on Reddit.`;
      }
      
      setResult({
        error: errorMessage
      });
    }
  };

  // Theme configurations
  const themes = {
    light: {
      bg: 'bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100',
      text: 'text-slate-900',
      card: 'bg-white/95 backdrop-blur-sm border-slate-200/60 shadow-xl',
      input: 'bg-white border-slate-300 text-slate-900 placeholder-slate-500 focus:border-blue-500',
      button: 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg',
      accent: 'text-blue-700',
      subtitle: 'text-slate-700',
      muted: 'text-slate-600'
    },
    dark: {
      bg: 'bg-gradient-to-br from-black via-gray-900 to-black',
      text: 'text-white',
      card: 'bg-gray-900/90 backdrop-blur-sm border-gray-700/50 shadow-2xl',
      input: 'bg-gray-800 border-gray-600 text-white placeholder-gray-400 focus:border-gray-500',
      button: 'bg-gradient-to-r from-gray-800 to-gray-900 hover:from-gray-700 hover:to-gray-800 shadow-lg',
      accent: 'text-gray-200',
      subtitle: 'text-gray-300',
      muted: 'text-gray-400'
    },
    color: {
      bg: 'bg-gradient-to-br from-[#0f0c29] via-[#302b63] to-[#24243e]',
      text: 'text-white',
      card: 'bg-white/10 backdrop-blur-sm border-white/20',
      input: 'bg-white/15 border-white/30 text-white placeholder-white/60',
      button: 'bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90',
      accent: 'text-accent',
      subtitle: 'text-white/70',
      muted: 'text-white/60'
    }
  };

  const currentTheme = themes[theme];

  // Chat functionality
  const sendMessage = async (message: string) => {
    if (!message.trim()) return;
    
    const userMessage = { type: 'user' as const, content: message, timestamp: new Date() };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsTyping(true);
    
    // Simulate AI response based on persona data
    setTimeout(() => {
      const botResponse = generateBotResponse(message, result);
      const botMessage = { type: 'bot' as const, content: botResponse, timestamp: new Date() };
      setChatMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000);
  };

  const generateBotResponse = (message: string, personaData: any) => {
    const lowerMessage = message.toLowerCase();
    
    // Only work with real persona data
    if (personaData.persona) {
      const persona = personaData.persona;
      
      // Handle "tell me about him in a line" or similar requests
      if (lowerMessage.includes('line') || lowerMessage.includes('brief') || lowerMessage.includes('summary') || lowerMessage.includes('short')) {
        const name = persona.name || 'This user';
        const personalityType = persona.personality?.mbti_type || persona.personality?.type || 'Unknown';
        const archetype = persona.archetype || 'Unknown';
        const age = persona.age || 'Unknown age';
        const occupation = persona.occupation || 'Unknown occupation';
        
        return `${name} is a ${age} ${personalityType} personality type (${archetype}) who works as ${occupation}.`;
      }
      
      if (lowerMessage.includes('personality') || lowerMessage.includes('traits')) {
        const personalityType = persona.personality?.mbti_type || persona.personality?.type || 'Unknown';
        const archetype = persona.archetype || 'Unknown';
        const traits = persona.traits || [];
        const traitList = traits.length > 0 ? traits.slice(0, 3).join(', ') : 'No specific traits identified';
        
        return `Based on the AI analysis, this user has a ${personalityType} personality type and fits the "${archetype}" archetype. Key traits include: ${traitList}.`;
      }
      
      if (lowerMessage.includes('motivation') || lowerMessage.includes('drive')) {
        const motivations = persona.motivations || {};
        if (Object.keys(motivations).length > 0) {
          const topMotivation = Object.entries(motivations)
            .sort(([,a], [,b]) => (b as number) - (a as number))[0];
          return `The user's primary motivation appears to be ${topMotivation?.[0]?.replace('_', ' ')} (${topMotivation?.[1]}%). This drives their decision-making and behavior patterns.`;
        } else {
          return `Motivation data is not available for this user.`;
        }
      }
      
      if (lowerMessage.includes('basic') || lowerMessage.includes('info') || lowerMessage.includes('demographics')) {
        const name = persona.name || 'Unknown name';
        const age = persona.age || 'Unknown age';
        const gender = persona.gender || 'Unknown gender';
        const occupation = persona.occupation || 'Unknown occupation';
        const location = persona.location || 'Unknown location';
        
        return `Here's what I know about this user: ${name}, ${age}, ${gender}, working as ${occupation} in ${location}.`;
      }
      
      if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
        const name = persona.name || 'this user';
        const personalityType = persona.personality?.mbti_type || persona.personality?.type || 'Unknown';
        const archetype = persona.archetype || 'Unknown';
        
        return `Hello! I'm your AI assistant for persona analysis. I have access to a comprehensive personality profile for ${name} generated by GPT-4. They are a ${personalityType} personality type (${archetype}). You can ask me about their personality traits, motivations, demographics, or any other aspect of their profile. What would you like to know?`;
      }
      
      // Default response with specific information
      const name = persona.name || 'this user';
      const personalityType = persona.personality?.mbti_type || persona.personality?.type || 'Unknown';
      const archetype = persona.archetype || 'Unknown';
      const age = persona.age || 'Unknown age';
      const occupation = persona.occupation || 'Unknown occupation';
      
      return `I can help you understand ${name}'s personality analysis. They are a ${age} ${personalityType} personality type (${archetype}) working as ${occupation}. You can ask me about their personality traits, motivations, demographics, or any other aspect of their profile. What specific information would you like to explore?`;
    }
    
    // If no real data available
    return `I don't have any real persona data to analyze. Please try analyzing a valid Reddit username first to get AI-generated insights about their personality.`;
  };

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Helper function to format username for display
  const formatUsername = (username: string) => {
    // If username has slashes, take the last part
    if (username.includes('/')) {
      return username.split('/').pop() || username;
    }
    // If username is longer than 6 characters, truncate
    if (username.length > 6) {
      return username.substring(0, 6) + '...';
    }
    return username;
  };

  // Function to load a history item
  const loadHistoryItem = (historyItem: {username: string, timestamp: Date, data: any}) => {
    setResult(historyItem.data);
    setHistoryOpen(false);
    setLoading(false); // Ensure loading is false when loading from history
    
    // Scroll to results after a short delay to ensure DOM is updated
    setTimeout(() => {
      resultsRef.current?.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
      });
    }, 100);
  };

  // Function to get preview data for history items
  const getHistoryPreview = (data: any) => {
    if (data.error) {
      return {
        type: 'error',
        message: 'Analysis failed',
        color: 'red'
      };
    }
    
    if (data.persona) {
      const persona = data.persona;
      return {
        type: 'success',
        name: persona.name || 'Unknown',
        personality: persona.personality?.mbti_type || persona.personality?.type || 'Unknown',
        archetype: persona.archetype || 'Unknown',
        traits: persona.traits || [],
        color: 'blue'
      };
    }
    
    return {
      type: 'unknown',
      message: 'No data available',
      color: 'gray'
    };
  };

  // Function to remove individual history item
  const removeHistoryItem = (username: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the onClick of the parent div
    setAnalysisHistory(prev => prev.filter(item => item.username !== username));
  };

  // Function to clear all history
  const clearAllHistory = () => {
    if (window.confirm('Are you sure you want to clear all analysis history? This action cannot be undone.')) {
      setAnalysisHistory([]);
    }
  };

  // Initialize chat when opened
  useEffect(() => {
    if (chatOpen && result && chatMessages.length === 0) {
      let welcomeMessage = '';
      
      if (result.persona) {
        const persona = result.persona;
        welcomeMessage = `Hello! I'm your AI assistant for persona analysis. I have access to a comprehensive personality profile for ${persona.name || 'this user'} generated by GPT-4. 

Key details:
• Personality Type: ${persona.personality?.mbti_type || persona.personality?.type || 'Unknown'}
• Archetype: ${persona.archetype || 'Unknown'}
• Age: ${persona.age || 'Unknown'}, Gender: ${persona.gender || 'Unknown'}
• Occupation: ${persona.occupation || 'Unknown'}
• Location: ${persona.location || 'Unknown'}

You can ask me about their personality traits, motivations, demographics, or any other aspect of their profile. What would you like to know?`;
      } else {
        welcomeMessage = `Hello! I'm your AI assistant for persona analysis. I don't have any real persona data to analyze yet. Please try analyzing a valid Reddit username first to get AI-generated insights about their personality.`;
      }
      
      const botMessage = { 
        type: 'bot' as const, 
        content: welcomeMessage, 
        timestamp: new Date() 
      };
      setChatMessages([botMessage]);
    }
  }, [chatOpen, result]);

  // Add this helper function near the top-level of the HeroSection component
  const handleDownloadPDF = async (username: string) => {
    try {
      // Clean the username - remove any 'u/' prefix and ensure it's not empty
      const cleanUsername = username.replace(/^u\//, '').trim();
      if (!cleanUsername || cleanUsername === 'user' || cleanUsername === 'Unknown') {
        // Try to get username from the current result - check the API response structure
        const currentUsername = result?.username || // This is the main username field from API
                               result?.persona?.reddit_username || 
                               result?.persona?.name || 
                               result?.persona?.metadata?.username;
        
        if (!currentUsername || currentUsername === 'user' || currentUsername === 'Unknown') {
          alert('Unable to determine username for PDF download. Please try the analysis again.');
          return;
        }
        
        // Use the current username
        const res = await fetch(`http://localhost:8080/download/pdf/${currentUsername}`);
        if (!res.ok) throw new Error('Failed to generate PDF');
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentUsername}_persona_report.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        // Use the provided username
        const res = await fetch(`http://localhost:8080/download/pdf/${cleanUsername}`);
        if (!res.ok) throw new Error('Failed to generate PDF');
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${cleanUsername}_persona_report.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('PDF download error:', err);
      alert('Failed to download PDF. Please try again.');
    }
  };

  return (
    <main className={`${currentTheme.bg} min-h-screen font-sans ${currentTheme.text} transition-all duration-500`}>
      {/* Theme Switcher */}
      <div className="fixed top-6 right-6 z-50">
        <div className={`backdrop-blur-md rounded-2xl p-2 border shadow-xl ${
          theme === 'light' 
            ? 'bg-white/90 border-slate-200/60' 
            : 'bg-white/10 border-white/20'
        }`}>
          <div className="flex gap-1">
            <button
              onClick={() => setTheme('light')}
              className={`p-3 rounded-xl transition-all duration-300 flex items-center gap-2 ${
                theme === 'light' 
                  ? 'bg-blue-500 text-white shadow-lg' 
                  : theme === 'dark'
                  ? 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
            >
              <Sun className="w-4 h-4" />
            </button>
            <button
              onClick={() => setTheme('color')}
              className={`p-3 rounded-xl transition-all duration-300 flex items-center gap-2 ${
                theme === 'color' 
                  ? 'bg-purple-500 text-white shadow-lg' 
                  : theme === 'light'
                  ? 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
            >
              <Palette className="w-4 h-4" />
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={`p-3 rounded-xl transition-all duration-300 flex items-center gap-2 ${
                theme === 'dark' 
                  ? 'bg-gray-700 text-white shadow-lg' 
                  : theme === 'light'
                  ? 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
            >
              <Moon className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* History Icon */}
      <div className={`fixed top-6 z-50 transition-all duration-300 ease-in-out ${
        historyOpen ? 'left-80' : 'left-6'
      }`}>
        <button
          onClick={() => setHistoryOpen(!historyOpen)}
          className={`p-3 rounded-xl transition-all duration-300 ${currentTheme.card} shadow-xl hover:scale-110 ${
            historyOpen ? 'bg-blue-500 text-white' : `${currentTheme.text} hover:bg-white/10`
          }`}
        >
          <History className="w-5 h-5" />
        </button>
      </div>

      {/* History Sidebar */}
      {historyOpen && (
        <div className="fixed left-0 top-0 h-full w-80 z-40 transition-all duration-300 ease-in-out">
          <div className={`h-full ${currentTheme.card} border-r ${
            theme === 'light' ? 'border-slate-200/60' : 'border-white/20'
          } shadow-xl flex flex-col`}>
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                  <History className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className={`font-semibold ${currentTheme.text}`}>Analysis History</h3>
                  <p className={`text-sm ${currentTheme.subtitle}`}>Recent persona analyses</p>
                </div>
              </div>
              <button
                onClick={() => setHistoryOpen(false)}
                className={`p-2 rounded-lg ${currentTheme.text} hover:bg-white/10 transition-colors`}
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* History List */}
            <div className="flex-1 overflow-y-auto p-4">
              {analysisHistory.length === 0 ? (
                <div className="text-center py-8">
                  <p className={`${currentTheme.subtitle} text-sm`}>No analysis history yet</p>
                  <p className={`${currentTheme.muted} text-xs mt-2`}>Your recent analyses will appear here</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {analysisHistory.map((item, index) => {
                    const preview = getHistoryPreview(item.data);
                    return (
                      <div
                        key={index}
                        onClick={() => loadHistoryItem(item)}
                        className={`p-4 rounded-xl border cursor-pointer transition-all duration-300 hover:scale-105 ${
                          // Highlight if this is the currently viewed item
                          result && result.persona?.name === getHistoryPreview(item.data).name && getHistoryPreview(item.data).type === 'success'
                            ? theme === 'light'
                              ? 'bg-blue-50 border-blue-300 shadow-lg'
                              : 'bg-blue-500/20 border-blue-400 shadow-xl'
                            : theme === 'light' 
                              ? 'bg-white/80 border-slate-200 hover:bg-white hover:shadow-lg' 
                              : 'bg-white/10 border-white/20 hover:bg-white/20 hover:shadow-xl'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <h4 className={`font-semibold ${currentTheme.text}`}>
                              {formatUsername(item.username)}
                            </h4>
                            {/* Show "Currently viewing" indicator */}
                            {result && result.persona?.name === getHistoryPreview(item.data).name && getHistoryPreview(item.data).type === 'success' && (
                              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                                theme === 'light'
                                  ? 'bg-blue-100 text-blue-700'
                                  : 'bg-blue-500/20 text-blue-300'
                              }`}>
                                Viewing
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`text-xs ${currentTheme.subtitle}`}>
                              {item.timestamp.toLocaleDateString()} {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                            {/* Remove button */}
                            <button
                              onClick={(e) => removeHistoryItem(item.username, e)}
                              className={`p-1 rounded-full transition-colors ${
                                theme === 'light'
                                  ? 'text-gray-400 hover:text-red-500 hover:bg-red-50'
                                  : 'text-gray-400 hover:text-red-400 hover:bg-red-500/20'
                              }`}
                              title="Remove from history"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </div>
                        </div>
                        
                        {/* Preview content based on data type */}
                        {preview.type === 'error' && (
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-2 h-2 rounded-full bg-red-400"></div>
                            <span className={`text-xs ${currentTheme.subtitle}`}>
                              {preview.message}
                            </span>
                          </div>
                        )}
                        
                        {preview.type === 'success' && (
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                              <span className={`text-xs font-semibold ${currentTheme.text}`}>
                                {preview.name}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className={`text-xs ${currentTheme.subtitle}`}>
                                {preview.personality} • {preview.archetype}
                              </span>
                            </div>
                            {preview.traits.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {preview.traits.slice(0, 3).map((trait: string, i: number) => (
                                  <span
                                    key={i}
                                    className={`px-2 py-1 rounded-full text-xs font-semibold ${
                                      theme === 'light' 
                                        ? 'bg-blue-100 text-blue-700' 
                                        : 'bg-blue-500/20 text-blue-300'
                                    }`}
                                  >
                                    {trait}
                                  </span>
                                ))}
                                {preview.traits.length > 3 && (
                                  <span className={`text-xs ${currentTheme.muted}`}>
                                    +{preview.traits.length - 3} more
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                        
                        {preview.type === 'unknown' && (
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-gray-400"></div>
                            <span className={`text-xs ${currentTheme.subtitle}`}>
                              {preview.message}
                            </span>
                          </div>
                        )}
                        
                        <p className={`text-xs ${currentTheme.muted} mt-2`}>
                          Click to view full analysis
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-white/10">
              <button
                onClick={clearAllHistory}
                className={`w-full py-2 px-4 rounded-xl text-sm font-medium transition-all duration-300 ${
                  theme === 'light'
                    ? 'bg-red-100 text-red-600 hover:bg-red-200'
                    : 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                }`}
              >
                Clear All History
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Chat Sidebar */}
      {chatOpen && (
        <div className="fixed right-0 top-0 h-full w-96 z-40 transition-all duration-300 ease-in-out">
          <div className={`h-full ${currentTheme.card} border-l ${
            theme === 'light' ? 'border-slate-200/60' : 'border-white/20'
          } shadow-xl flex flex-col`}>
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                  <MessageCircle className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className={`font-semibold ${currentTheme.text}`}>AI Assistant</h3>
                  <p className={`text-sm ${currentTheme.subtitle}`}>Persona Analysis Expert</p>
                </div>
              </div>
              <button
                onClick={() => setChatOpen(false)}
                className={`p-2 rounded-lg ${currentTheme.text} hover:bg-white/10 transition-colors`}
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatMessages.map((message, index) => (
                <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.type === 'user' 
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white' 
                      : `${currentTheme.card} ${currentTheme.text} border border-white/20`
                  }`}>
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    <p className={`text-xs mt-2 ${
                      message.type === 'user' ? 'text-blue-100' : currentTheme.subtitle
                    }`}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}
              
              {/* Typing Indicator */}
              {isTyping && (
                <div className="flex justify-start">
                  <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${currentTheme.card} ${currentTheme.text} border border-white/20`}>
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                      <span className="text-sm">AI is typing...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={chatEndRef} />
            </div>

            {/* Chat Input */}
            <div className="p-4 border-t border-white/10">
              <form onSubmit={(e) => { e.preventDefault(); sendMessage(chatInput); }} className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask about the user's personality..."
                  className={`flex-1 px-4 py-3 rounded-xl border ${currentTheme.input} focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent`}
                  disabled={isTyping}
                />
                <button
                  type="submit"
                  disabled={!chatInput.trim() || isTyping}
                  className={`p-3 rounded-xl transition-all duration-300 ${
                    chatInput.trim() && !isTyping
                      ? 'bg-gradient-to-r from-green-500 to-blue-500 text-white hover:scale-105'
                      : 'bg-gray-500 text-gray-300 cursor-not-allowed'
                  }`}
                >
                  <Send className="w-5 h-5" />
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-screen-xl mx-auto px-6 py-10">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-6 flex items-center justify-center gap-4">
            PersonaForge <Sparkles className={`w-12 h-12 ${currentTheme.accent} animate-pulse`} />
            </h1>
          <p className={`text-xl ${currentTheme.subtitle} mb-8 max-w-3xl mx-auto leading-relaxed`}>
            Transform Reddit usernames and URLs into comprehensive personality profiles using advanced AI analysis. 
            Discover behavioral patterns, motivations, and insights through GPT-4 powered analysis of Reddit activity.
          </p>
          
          {/* Hero Form */}
          <div className="w-full max-w-2xl mx-auto mb-16">
            <form onSubmit={handleSubmit} className={`${currentTheme.card} rounded-2xl shadow-xl p-8`}>
            <div className="flex w-full gap-3">
              <input
                  className={`flex-1 px-4 py-3 rounded-xl border ${currentTheme.input} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                  placeholder="Enter Reddit username or URL (e.g., u/username or https://reddit.com/user/username)..."
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
              />
              <button 
                type="submit" 
                  className={`${currentTheme.button} text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-all duration-300 transform hover:scale-105`}
              >
                Generate <ArrowRight className="w-5 h-5" />
              </button>
            </div>
              
              {/* Advanced Options Toggle */}
              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className={`text-sm ${currentTheme.subtitle} hover:${currentTheme.text} transition-colors flex items-center gap-1`}
                >
                  {showAdvanced ? 'Hide' : 'Show'} Advanced Options
                  <ArrowRight className={`w-3 h-3 transition-transform ${showAdvanced ? 'rotate-90' : ''}`} />
                </button>
              </div>
              
              {/* Advanced Options */}
              {showAdvanced && (
                <div className="mt-4 p-4 rounded-xl border border-white/20 bg-white/5">
                  <h4 className={`text-sm font-semibold mb-3 ${currentTheme.text}`}>Analysis Settings</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className={`block text-xs ${currentTheme.subtitle} mb-1`}>
                        Max Posts to Analyze
                      </label>
                      <input
                        type="number"
                        min="5"
                        max="100"
                        value={maxPosts}
                        onChange={e => setMaxPosts(parseInt(e.target.value) || 25)}
                        className={`w-full px-3 py-2 rounded-lg border text-sm ${currentTheme.input}`}
                      />
                      <p className={`text-xs ${currentTheme.muted} mt-1`}>
                        Higher = more comprehensive analysis
                      </p>
                    </div>
                    <div>
                      <label className={`block text-xs ${currentTheme.subtitle} mb-1`}>
                        Max Comments to Analyze
                      </label>
                      <input
                        type="number"
                        min="5"
                        max="200"
                        value={maxComments}
                        onChange={e => setMaxComments(parseInt(e.target.value) || 30)}
                        className={`w-full px-3 py-2 rounded-lg border text-sm ${currentTheme.input}`}
                      />
                      <p className={`text-xs ${currentTheme.muted} mt-1`}>
                        Higher = better personality insights
                      </p>
                    </div>
                  </div>
                  <div className="mt-3 p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
                    <p className={`text-xs ${currentTheme.subtitle}`}>
                      💡 <strong>Tip:</strong> Higher limits provide more accurate personality analysis but may take longer to process.
                    </p>
                  </div>
                </div>
              )}
          </form>
            
            {/* Chat Icon and Text - Only show when we have real persona data */}
            {result && result.persona && !result.error && !historyOpen && (
              <div className="flex items-center justify-center gap-3 mt-6">
                <button
                  onClick={() => setChatOpen(!chatOpen)}
                  className={`p-3 rounded-xl transition-all duration-300 ${currentTheme.card} shadow-xl hover:scale-105 ${
                    chatOpen ? 'bg-green-500' : `${currentTheme.text} hover:bg-white/10`
                  }`}
                  style={{
                    boxShadow: chatOpen 
                      ? '0 0 20px rgba(34, 197, 94, 0.6), 0 0 40px rgba(34, 197, 94, 0.4), 0 0 60px rgba(34, 197, 94, 0.2)' 
                      : '0 0 20px rgba(59, 130, 246, 0.6), 0 0 40px rgba(59, 130, 246, 0.4), 0 0 60px rgba(59, 130, 246, 0.2)',
                    animation: 'pulse-glow 2s ease-in-out infinite'
                  }}
                >
                  <MessageCircle className={`w-5 h-5 ${chatOpen ? 'text-white' : currentTheme.text}`} />
                </button>
                <span className={`text-base font-semibold ${currentTheme.text} opacity-90 animate-fade-in`}>
                  Want to know more about the user?
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center mt-8 mb-12">
              <div className={`animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 mb-4 ${
                theme === 'light' 
                  ? 'border-blue-600 border-indigo-600' 
                  : theme === 'dark'
                  ? 'border-gray-600 border-gray-700'
                  : 'border-primary border-accent'
              }`} />
              <span className={`text-lg ${currentTheme.text}`}>Analyzing persona...</span>
          </div>
        )}

        {/* Results Dashboard */}
        {result && !loading && (
            <div ref={resultsRef} className="space-y-12 mb-16">
            
            {/* Error State */}
            {result.error && (
            <section className="space-y-8">
              <div className="text-center">
                  <h2 className={`text-3xl font-bold ${currentTheme.text} mb-2 drop-shadow-glow`}>Analysis Failed</h2>
                  <p className={currentTheme.subtitle}>Unable to analyze the provided username</p>
              </div>
                <div className={`${currentTheme.card} rounded-2xl p-8 text-center`}>
                  <div className="text-red-400 text-6xl mb-4">⚠️</div>
                  <h3 className={`text-xl font-semibold mb-4 ${currentTheme.text}`}>Analysis Error</h3>
                  <p className={`${currentTheme.subtitle} mb-6`}>{result.error}</p>
                  <div className="text-sm text-gray-400">
                    <p>• Make sure the username exists on Reddit</p>
                    <p>• Try a different username or Reddit URL</p>
                    <p>• Check if the user has public posts/comments</p>
                  </div>
                </div>
              </section>
            )}

            {/* Real Data Display - Only show if we have actual persona data */}
            {result.persona && !result.error && (
              <>
                {/* Section 1: AI-Generated Persona Profile */}
                <section className="space-y-8">
                  <div className="text-center">
                    <h2 className={`text-3xl font-bold ${currentTheme.text} mb-2 drop-shadow-glow`}>AI-Generated Persona Profile</h2>
                    <p className={currentTheme.subtitle}>Comprehensive personality analysis by GPT-4</p>
                  </div>
                  
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Basic Info */}
                <ChartCard 
                      title="Personal Information" 
                      subtitle="Demographics and basic details"
                      height="h-[300px]"
                      theme={theme}
                    >
                      <div className="w-full h-full flex flex-col justify-center space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className={`text-center p-4 rounded-xl ${currentTheme.card} border border-white/20`}>
                            <div className="text-2xl font-bold text-blue-400 mb-2">{result?.username || result?.persona?.name || 'Unknown'}</div>
                            <div className="text-sm text-gray-400">Username</div>
                          </div>
                          <div className={`text-center p-4 rounded-xl ${currentTheme.card} border border-white/20`}>
                            <div className="text-2xl font-bold text-green-400 mb-2">{result?.persona?.age || 'Unknown'}</div>
                            <div className="text-sm text-gray-400">Age</div>
                          </div>
                          <div className={`text-center p-4 rounded-xl ${currentTheme.card} border border-white/20`}>
                            <div className="text-2xl font-bold text-purple-400 mb-2">{result?.persona?.gender || 'Unknown'}</div>
                            <div className="text-sm text-gray-400">Gender</div>
                          </div>
                          <div className={`text-center p-4 rounded-xl ${currentTheme.card} border border-white/20`}>
                            <div className="text-2xl font-bold text-orange-400 mb-2">{result?.persona?.occupation || 'Unknown'}</div>
                            <div className="text-sm text-gray-400">Occupation</div>
                          </div>
                        </div>
                        <div className={`text-center p-4 rounded-xl ${currentTheme.card} border border-white/20`}>
                          <div className="text-lg font-bold text-yellow-400 mb-2">{result?.persona?.location || 'Unknown'}</div>
                          <div className="text-sm text-gray-400">Location</div>
                        </div>
                      </div>
                </ChartCard>

                    {/* Personality Type */}
                <ChartCard 
                      title="Personality Archetype" 
                      subtitle="MBTI and personality classification"
                      height="h-[300px]"
                      theme={theme}
                    >
                      <div className="w-full h-full flex flex-col justify-center space-y-6">
                        <div className={`text-center p-6 rounded-xl ${currentTheme.card} border border-white/20`}>
                          <div className="text-4xl font-bold text-blue-400 mb-2">
                            {result?.persona?.personality?.mbti_type || result?.persona?.personality?.type || 'Unknown'}
                          </div>
                          <div className="text-sm text-gray-400 mb-4">Personality Type</div>
                          <div className="text-lg font-semibold text-green-400 mb-2">
                            {result?.persona?.archetype || 'The Explorer'}
                          </div>
                          <div className="text-sm text-gray-400">Archetype</div>
                        </div>
                        <div className="flex justify-center space-x-2">
                          {(result?.persona?.traits || []).slice(0, 4).map((trait: string, i: number) => (
                            <span key={i} className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              theme === 'light' 
                                ? 'bg-blue-100 text-blue-700' 
                                : 'bg-blue-500/20 text-blue-300'
                            }`}>
                              {trait}
                            </span>
                          ))}
                        </div>
                      </div>
                </ChartCard>
              </div>

                  {/* Detailed Analysis */}
                  {result?.persona?.formatted_text && (
                    <ChartCard 
                      title="Detailed Personality Analysis" 
                      subtitle="Comprehensive AI-generated insights"
                      height="h-[400px]"
                      theme={theme}
                    >
                      <div className="w-full h-full overflow-y-auto">
                        <div className={`prose prose-sm max-w-none ${theme === 'light' ? 'prose-slate' : 'prose-invert'}`}>
                          <div className="whitespace-pre-wrap text-sm leading-relaxed">
                            {result?.persona?.formatted_text}
                          </div>
                        </div>
                      </div>
                    </ChartCard>
                  )}

                  {/* Analysis Metadata */}
                  {result.metadata && (
                    <div className={`${currentTheme.card} rounded-2xl p-6`}>
                      <h3 className={`text-xl font-semibold mb-4 ${currentTheme.text}`}>Analysis Details</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className={currentTheme.subtitle}>Source: </span>
                          <span className={currentTheme.text}>{result.metadata.source || 'Unknown'}</span>
                        </div>
                        <div>
                          <span className={currentTheme.subtitle}>Confidence: </span>
                          <span className={currentTheme.text}>
                            {result.metadata.confidence ? 
                              `${(result.metadata.confidence * 100).toFixed(1)}%` : 
                              'Unknown'
                            }
                          </span>
                        </div>
                        <div>
                          <span className={currentTheme.subtitle}>Posts Analyzed: </span>
                          <span className={currentTheme.text}>{result.metadata.posts_analyzed || 'Unknown'}</span>
                        </div>
                        <div>
                          <span className={currentTheme.subtitle}>Comments Analyzed: </span>
                          <span className={currentTheme.text}>{result.metadata.comments_analyzed || 'Unknown'}</span>
                        </div>
                      </div>
                    </div>
                  )}
            </section>
              </>
            )}

            {/* Section 2: Comprehensive Text-Based Persona Details - Only show if we have real persona data */}
            {result.persona && !result.error && (
            <section className="space-y-8">
              <div className="text-center">
                  <h2 className={`text-3xl font-bold ${currentTheme.text} mb-2 drop-shadow-glow`}>Detailed Persona Profile</h2>
                  <p className={currentTheme.subtitle}>Comprehensive behavioral analysis and user insights</p>
              </div>
                
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Behaviors & Habits */}
                <ChartCard 
                    title="Behaviors & Habits" 
                    subtitle="Daily patterns and lifestyle choices"
                    height="h-[400px]"
                    theme={theme}
                  >
                    <div className="w-full h-full overflow-y-auto">
                      <div className="space-y-4">
                        {(result.persona?.behaviors || result.persona?.habits || []).map((behavior: string, index: number) => (
                          <div key={index} className={`flex items-start gap-3 p-3 rounded-lg ${
                            theme === 'light' 
                              ? 'bg-blue-50 border border-blue-200' 
                              : 'bg-blue-500/10 border border-blue-500/20'
                          }`}>
                            <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                              theme === 'light' ? 'bg-blue-500' : 'bg-blue-400'
                            }`} />
                            <p className={`text-sm leading-relaxed ${currentTheme.text}`}>
                              {behavior}
                            </p>
                          </div>
                        ))}
                        {(result.persona?.behaviors || result.persona?.habits || []).length === 0 && (
                          <div className={`text-center py-8 ${currentTheme.subtitle}`}>
                            No behavioral data available
                          </div>
                        )}
                      </div>
                    </div>
                </ChartCard>

                  {/* Frustrations & Pain Points */}
                <ChartCard 
                    title="Frustrations & Pain Points" 
                  subtitle="Areas of concern and friction"
                    height="h-[400px]"
                    theme={theme}
                  >
                    <div className="w-full h-full overflow-y-auto">
                      <div className="space-y-4">
                        {(result.persona?.frustrations || result.persona?.pain_points || []).map((frustration: string, index: number) => (
                          <div key={index} className={`flex items-start gap-3 p-3 rounded-lg ${
                            theme === 'light' 
                              ? 'bg-red-50 border border-red-200' 
                              : 'bg-red-500/10 border border-red-500/20'
                          }`}>
                            <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                              theme === 'light' ? 'bg-red-500' : 'bg-red-400'
                            }`} />
                            <p className={`text-sm leading-relaxed ${currentTheme.text}`}>
                              {frustration}
                            </p>
                          </div>
                        ))}
                        {(result.persona?.frustrations || result.persona?.pain_points || []).length === 0 && (
                          <div className={`text-center py-8 ${currentTheme.subtitle}`}>
                            No frustration data available
                          </div>
                        )}
                      </div>
                    </div>
                  </ChartCard>
                </div>

                {/* Goals & Needs */}
                <ChartCard 
                  title="Goals & Needs" 
                  subtitle="Primary objectives and requirements"
                  height="h-[300px]"
                  theme={theme}
                >
                  <div className="w-full h-full overflow-y-auto">
                    <div className="space-y-4">
                      {(result.persona?.goals || result.persona?.needs || []).map((goal: string, index: number) => (
                        <div key={index} className={`flex items-start gap-3 p-3 rounded-lg ${
                          theme === 'light' 
                            ? 'bg-green-50 border border-green-200' 
                            : 'bg-green-500/10 border border-green-500/20'
                        }`}>
                          <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                            theme === 'light' ? 'bg-green-500' : 'bg-green-400'
                          }`} />
                          <p className={`text-sm leading-relaxed ${currentTheme.text}`}>
                            {goal}
                          </p>
                        </div>
                      ))}
                      {(result.persona?.goals || result.persona?.needs || []).length === 0 && (
                        <div className={`text-center py-8 ${currentTheme.subtitle}`}>
                          No goals data available
                        </div>
                      )}
                    </div>
                  </div>
                </ChartCard>

                {/* Motivations & Personality Traits */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Key Motivations */}
                  <ChartCard 
                    title="Key Motivations" 
                    subtitle="Primary driving factors"
                    height="h-[300px]"
                    theme={theme}
                  >
                    <div className="w-full h-full overflow-y-auto">
                      <div className="space-y-4">
                        {Object.entries(result.persona?.motivations || {}).map(([motivation, level]: [string, any], index: number) => (
                          <div key={index} className={`flex items-center justify-between p-3 rounded-lg ${
                            theme === 'light' 
                              ? 'bg-purple-50 border border-purple-200' 
                              : 'bg-purple-500/10 border border-purple-500/20'
                          }`}>
                            <span className={`font-semibold ${currentTheme.text}`}>
                              {motivation.replace('_', ' ')}
                            </span>
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                              theme === 'light' 
                                ? 'bg-purple-100 text-purple-700' 
                                : 'bg-purple-500/20 text-purple-300'
                            }`}>
                              {typeof level === 'number' ? `${level}%` : level}
                            </span>
              </div>
                        ))}
                        {Object.keys(result.persona?.motivations || {}).length === 0 && (
                          <div className={`text-center py-8 ${currentTheme.subtitle}`}>
                            No motivation data available
                          </div>
                        )}
                      </div>
                    </div>
                  </ChartCard>

                  {/* Personality Traits */}
                  <ChartCard 
                    title="Personality Traits" 
                    subtitle="Key characteristics and qualities"
                    height="h-[300px]"
                    theme={theme}
                  >
                    <div className="w-full h-full overflow-y-auto">
                      <div className="space-y-4">
                        {(result.persona?.traits || result.persona?.characteristics || []).map((trait: string, index: number) => (
                          <div key={index} className={`flex items-center justify-between p-3 rounded-lg ${
                            theme === 'light' 
                              ? 'bg-orange-50 border border-orange-200' 
                              : 'bg-orange-500/10 border border-orange-500/20'
                          }`}>
                            <span className={`font-semibold ${currentTheme.text}`}>
                              {trait}
                            </span>
                            <div className={`w-3 h-3 rounded-full ${
                              theme === 'light' ? 'bg-orange-500' : 'bg-orange-400'
                            }`} />
                          </div>
                        ))}
                        {(result.persona?.traits || result.persona?.characteristics || []).length === 0 && (
                          <div className={`text-center py-8 ${currentTheme.subtitle}`}>
                            No personality traits data available
                          </div>
                        )}
                      </div>
                    </div>
                  </ChartCard>
                </div>

                {/* Quote Section */}
                {result.persona?.quote && (
                  <ChartCard 
                    title="Key Quote" 
                    subtitle="Representative statement from the user"
                    height="h-[200px]"
                    theme={theme}
                  >
                    <div className="w-full h-full flex items-center justify-center">
                      <div className={`text-center p-6 rounded-xl border-2 ${
                        theme === 'light' 
                          ? 'bg-red-50 border-red-300' 
                          : 'bg-red-500/10 border-red-500/30'
                      }`}>
                        <p className={`text-lg font-semibold italic ${currentTheme.text}`}>
                          "{result?.persona?.quote}"
                        </p>
                      </div>
                    </div>
                  </ChartCard>
                )}
            </section>
            )}

            {/* Section 3: Charts and Visualizations - Only show if we have chart data */}
            {result?.persona && result.persona.chart_data && !result.error && (
              <section className="space-y-8">
                <div className="text-center">
                  <h2 className={`text-3xl font-bold ${currentTheme.text} mb-2 drop-shadow-glow`}>Data Visualizations</h2>
                  <p className={currentTheme.subtitle}>Interactive charts and analytics from Reddit activity</p>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Personality Radar Chart */}
                  {personalityRadarData.length > 0 &&
                   personalityRadarData.some((item: any) => item.value > 0) && (
                    <ChartCard 
                      title="Personality Radar" 
                      subtitle="MBTI-style personality dimensions"
                      height="h-[400px]"
                      theme={theme}
                    >
                      <RadarChart 
                        values={personalityRadarData}
                        theme={theme}
                      />
                    </ChartCard>
                  )}

                  {/* Interests Pie Chart */}
                  {interestsPieData.length > 0 &&
                   interestsPieData.some((item: any) => item.value > 0) && (
                    <ChartCard 
                      title="Interest Distribution" 
                      subtitle="Top interests and preferences"
                      height="h-[400px]"
                      theme={theme}
                    >
                      <PieChart 
                        traits={interestsPieData}
                        theme={theme}
                      />
                    </ChartCard>
                  )}
                </div>

                {/* Big Five Personality Traits */}
                {bigFiveData.length > 0 &&
                 bigFiveData.some((item: any) => item.value > 0) && (
                  <ChartCard 
                    title="Big Five Personality Traits" 
                    subtitle="OCEAN model analysis"
                    height="h-[400px]"
                    theme={theme}
                  >
                    <BigFiveBarChart 
                      traits={bigFiveData}
                      theme={theme}
                    />
                  </ChartCard>
                )}

                {/* Community Engagement */}
                {communityEngagementData.length > 0 &&
                 communityEngagementData.some((item: any) => item.value > 0) && (
                  <ChartCard 
                    title="Community Engagement" 
                    subtitle="Reddit participation metrics"
                    height="h-[300px]"
                    theme={theme}
                  >
                    <BarChart 
                      issues={communityEngagementData}
                      theme={theme}
                    />
                  </ChartCard>
                )}

                {/* Activity Patterns */}
                {activityPatternsData.length > 0 &&
                 activityPatternsData.some((item: any) => item.value > 0) && (
                  <ChartCard 
                    title="Activity Patterns" 
                    subtitle="User activity metrics"
                    height="h-[300px]"
                    theme={theme}
                  >
                    <BarChart 
                      issues={activityPatternsData}
                      theme={theme}
                    />
                  </ChartCard>
                )}

                {/* Sentiment Timeline */}
                {sentimentTimelineData.length > 0 &&
                 sentimentTimelineData.some((item: any) => item.value > 0) && (
                  <ChartCard 
                    title="Sentiment Timeline" 
                    subtitle="Sentiment over time"
                    height="h-[300px]"
                    theme={theme}
                  >
                    <LineChart 
                      events={sentimentTimelineData}
                      theme={theme}
                    />
                  </ChartCard>
                )}
              </section>
            )}

            {/* Section 4: Mock Data Charts - Only show if we don't have real chart data but have persona */}
            {result?.persona && !result.persona.chart_data && !result.error && (
            <section className="space-y-8">
              <div className="text-center">
                  <h2 className={`text-3xl font-bold ${currentTheme.text} mb-2 drop-shadow-glow`}>Sample Visualizations</h2>
                  <p className={currentTheme.subtitle}>Example charts (real data visualizations will appear when backend charts are generated)</p>
              </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Sample Personality Radar */}
                  <ChartCard 
                    title="Personality Radar" 
                    subtitle="Key personality traits analysis"
                    height="h-[400px]"
                    theme={theme}
                  >
                    <RadarChart 
                      values={[
                        { name: 'Analytical', value: 85 },
                        { name: 'Creative', value: 70 },
                        { name: 'Social', value: 60 },
                        { name: 'Detail-oriented', value: 80 },
                        { name: 'Adaptable', value: 75 }
                      ]}
                      theme={theme}
                    />
                  </ChartCard>

                  {/* Sample Interests Pie */}
                  <ChartCard 
                    title="Interest Distribution" 
                    subtitle="Top interests and preferences"
                    height="h-[400px]"
                    theme={theme}
                  >
                    <PieChart 
                      traits={[
                        { name: 'Technology', value: 30 },
                        { name: 'Gaming', value: 25 },
                        { name: 'Science', value: 20 },
                        { name: 'Entertainment', value: 15 },
                        { name: 'Other', value: 10 }
                      ]}
                      theme={theme}
                    />
                  </ChartCard>
                </div>

                {/* Sample Big Five */}
                <ChartCard 
                  title="Big Five Personality Traits" 
                  subtitle="OCEAN model analysis"
                  height="h-[400px]"
                  theme={theme}
                >
                  <BigFiveBarChart 
                    traits={[
                      { name: 'Openness', value: 75, color: 'blue' },
                      { name: 'Conscientiousness', value: 80, color: 'green' },
                      { name: 'Extraversion', value: 60, color: 'yellow' },
                      { name: 'Agreeableness', value: 70, color: 'purple' },
                      { name: 'Neuroticism', value: 30, color: 'red' }
                    ]}
                    theme={theme}
                  />
                </ChartCard>
              </section>
            )}

            {/* Section 5: Real Reddit Content - Only show if we have real posts/comments */}
            {result?.persona && result.persona.chart_data?.real_content && !result.error && (
              <section className="space-y-8">
                <div className="text-center">
                  <h2 className={`text-3xl font-bold ${currentTheme.text} mb-2 drop-shadow-glow`}>Real Reddit Content</h2>
                  <p className={currentTheme.subtitle}>Actual posts and comments that informed the analysis</p>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Real Posts */}
                  {result?.persona?.chart_data?.real_content?.posts && result.persona.chart_data.real_content.posts.length > 0 && (
                    <ChartCard 
                      title="Sample Posts" 
                      subtitle="Recent Reddit submissions"
                      height="h-[500px]"
                      theme={theme}
                    >
                      <div className="w-full h-full overflow-y-auto space-y-4">
                        {result?.persona?.chart_data?.real_content?.posts.map((post: any, index: number) => (
                          <div key={index} className={`p-4 rounded-lg border ${
                            theme === 'light' 
                              ? 'bg-blue-50 border-blue-200' 
                              : 'bg-blue-500/10 border-blue-500/20'
                          }`}>
                            <div className="flex items-start justify-between mb-2">
                              <h4 className={`font-semibold text-sm ${currentTheme.text}`}>
                                {post.title}
                              </h4>
                              <div className={`text-xs px-2 py-1 rounded ${
                                theme === 'light' 
                                  ? 'bg-green-100 text-green-700' 
                                  : 'bg-green-500/20 text-green-300'
                              }`}>
                                r/{post.subreddit}
                              </div>
                            </div>
                            {post.content && (
                              <p className={`text-sm ${currentTheme.subtitle} mb-2 line-clamp-3`}>
                                {post.content}
                              </p>
                            )}
                            <div className="flex items-center justify-between text-xs text-gray-400">
                              <span>Score: {post.score}</span>
                              <a 
                                href={post.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className={`hover:${currentTheme.text} transition-colors`}
                              >
                                View Post →
                              </a>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ChartCard>
                  )}

                  {/* Real Comments */}
                  {result?.persona?.chart_data?.real_content?.comments && result.persona.chart_data.real_content.comments.length > 0 && (
                    <ChartCard 
                      title="Sample Comments" 
                      subtitle="Recent Reddit comments"
                      height="h-[500px]"
                      theme={theme}
                    >
                      <div className="w-full h-full overflow-y-auto space-y-4">
                        {result?.persona?.chart_data?.real_content?.comments.map((comment: any, index: number) => (
                          <div key={index} className={`p-4 rounded-lg border ${
                            theme === 'light' 
                              ? 'bg-purple-50 border-purple-200' 
                              : 'bg-purple-500/10 border-purple-500/20'
                          }`}>
                            <div className="flex items-start justify-between mb-2">
                              <div className={`text-xs px-2 py-1 rounded ${
                                theme === 'light' 
                                  ? 'bg-purple-100 text-purple-700' 
                                  : 'bg-purple-500/20 text-purple-300'
                              }`}>
                                r/{comment.subreddit}
                              </div>
                              <span className="text-xs text-gray-400">Score: {comment.score}</span>
                            </div>
                            <p className={`text-sm ${currentTheme.text} mb-2 line-clamp-4`}>
                              {comment.content}
                            </p>
                            <div className="flex justify-end">
                              <a 
                                href={comment.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className={`text-xs hover:${currentTheme.text} transition-colors`}
                              >
                                View Comment →
                              </a>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ChartCard>
                  )}
                </div>

                {/* Motivations Chart */}
                {result?.persona?.chart_data?.motivations && 
                 result.persona.chart_data.motivations.length > 0 &&
                 result.persona.chart_data.motivations.some((item: any) => item.value > 0) && (
                  <ChartCard 
                    title="User Motivations" 
                    subtitle="What drives this user's behavior"
                    height="h-[400px]"
                    theme={theme}
                  >
                    <BarChart 
                      issues={result?.persona?.chart_data?.motivations}
                      theme={theme}
                    />
                  </ChartCard>
                )}
            </section>
            )}
          </div>
        )}
      </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className={`${currentTheme.card} rounded-2xl p-6 hover:scale-105 transition-all duration-300`}>
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className={`text-xl font-semibold mb-2 ${currentTheme.text}`}>AI-Powered Analysis</h3>
            <p className={currentTheme.muted}>Advanced machine learning algorithms analyze Reddit activity to extract meaningful personality insights.</p>
          </div>
          
          <div className={`${currentTheme.card} rounded-2xl p-6 hover:scale-105 transition-all duration-300`}>
            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className={`text-xl font-semibold mb-2 ${currentTheme.text}`}>Comprehensive Insights</h3>
            <p className={currentTheme.muted}>Get detailed breakdowns of personality traits, behavioral patterns, and motivational drivers.</p>
          </div>
          
          <div className={`${currentTheme.card} rounded-2xl p-6 hover:scale-105 transition-all duration-300`}>
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className={`text-xl font-semibold mb-2 ${currentTheme.text}`}>Real-time Processing</h3>
            <p className={currentTheme.muted}>Instant analysis with beautiful visualizations and interactive charts for better understanding.</p>
          </div>
        </div>

        {/* How It Works Section */}
        <div className={`${currentTheme.card} rounded-2xl p-8 mb-16`}>
          <h2 className={`text-3xl font-bold text-center mb-8 ${currentTheme.text}`}>How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className={`w-16 h-16 ${currentTheme.button} rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-white`}>
                1
              </div>
              <h3 className={`text-lg font-semibold mb-2 ${currentTheme.text}`}>Enter Username or URL</h3>
              <p className={currentTheme.muted}>Input any Reddit username or paste a Reddit URL to analyze</p>
            </div>
            <div className="text-center">
              <div className={`w-16 h-16 ${currentTheme.button} rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-white`}>
                2
              </div>
              <h3 className={`text-lg font-semibold mb-2 ${currentTheme.text}`}>AI Scrapes & Analyzes</h3>
              <p className={currentTheme.muted}>Our AI scrapes Reddit activity and analyzes behavioral patterns</p>
            </div>
            <div className="text-center">
              <div className={`w-16 h-16 ${currentTheme.button} rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-white`}>
                3
              </div>
              <h3 className={`text-lg font-semibold mb-2 ${currentTheme.text}`}>GPT-4 Generates Profile</h3>
              <p className={currentTheme.muted}>GPT-4 creates a comprehensive personality profile from the data</p>
            </div>
            <div className="text-center">
              <div className={`w-16 h-16 ${currentTheme.button} rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-white`}>
                4
              </div>
              <h3 className={`text-lg font-semibold mb-2 ${currentTheme.text}`}>Explore Real Insights</h3>
              <p className={currentTheme.muted}>Discover detailed charts and AI-generated behavioral analysis</p>
            </div>
          </div>
      </div>

      {/* Add the Download PDF button in the Results Dashboard, after the analysis details section */}
      {result?.persona && !result.error && (
        <div className="flex justify-end mt-4">
          <button
            onClick={() => handleDownloadPDF(result?.username || result?.persona?.reddit_username || result?.persona?.name || result?.persona?.metadata?.username || '')}
            className={`px-6 py-3 rounded-xl font-semibold bg-gradient-to-r from-blue-600 to-green-500 text-white shadow-lg hover:scale-105 transition-all duration-300`}
          >
            Download Full PDF Report
          </button>
        </div>
      )}
    </main>
  );
};

export default HeroSection; 