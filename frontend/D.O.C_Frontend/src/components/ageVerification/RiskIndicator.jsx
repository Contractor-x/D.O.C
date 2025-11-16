import React from 'react';

const RiskIndicator = ({ riskLevel }) => {
  const getRiskColor = (level) => {
    switch (level.toLowerCase()) {
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="risk-indicator flex items-center">
      <div className={`w-4 h-4 rounded-full ${getRiskColor(riskLevel)} mr-2`}></div>
      <span className="text-sm font-medium capitalize">{riskLevel} Risk</span>
    </div>
  );
};

export default RiskIndicator;
