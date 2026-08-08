import React, { useEffect, useState } from 'react';

const HealthScore = ({ score }) => {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 1500;
    const steps = 60;
    const increment = score / steps;
    const stepTime = duration / steps;
    
    const timer = setInterval(() => {
      start += increment;
      if (start >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(start);
      }
    }, stepTime);
    
    return () => clearInterval(timer);
  }, [score]);

  const getColor = (s) => {
    if (s >= 7) return '#00C896'; // accent-success
    if (s >= 4) return '#FF6B35'; // accent-warn
    return '#FF453A'; // critical red
  };

  const color = getColor(score);
  const glowClass = score < 4 ? 'shadow-[0_0_40px_10px_rgba(255,69,58,0.15)]' : 'health-glow';
  
  const circumference = 2 * Math.PI * 90;
  const strokeDashoffset = circumference - (score / 10) * circumference;

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className={`relative w-[200px] h-[200px] rounded-full flex items-center justify-center ${glowClass}`}>
        <svg className="absolute top-0 left-0 w-full h-full transform -rotate-90">
          <circle 
            cx="100" cy="100" r="90" 
            fill="transparent" 
            stroke="#1E2D45" 
            strokeWidth="8" 
          />
          <circle 
            cx="100" cy="100" r="90" 
            fill="transparent" 
            stroke={color} 
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: 'stroke-dashoffset 1.5s ease-out' }}
          />
        </svg>
        <div className="text-center z-10">
          <span className="font-display text-5xl text-text-primary">
            {displayScore.toFixed(1)}
          </span>
          <span className="text-text-muted text-sm block mt-1">/ 10</span>
        </div>
      </div>
      <p className="mt-6 text-text-muted font-medium tracking-wide uppercase text-sm">Financial Health Score</p>
    </div>
  );
};

export default React.memo(HealthScore);
