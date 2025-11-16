import React from 'react';

const SideEffectCard = ({ sideEffect }) => {
  return (
    <div className="side-effect-card bg-white p-4 rounded-lg shadow-md">
      <h4 className="text-lg font-semibold mb-2">{sideEffect.name}</h4>
      <p className="text-gray-600 mb-2">{sideEffect.description}</p>
      <div className="flex items-center">
        <span className="text-sm text-gray-500 mr-2">Severity:</span>
        <span className={`px-2 py-1 rounded text-xs font-semibold ${
          sideEffect.severity === 'High' ? 'bg-red-100 text-red-800' :
          sideEffect.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
          'bg-green-100 text-green-800'
        }`}>
          {sideEffect.severity}
        </span>
      </div>
    </div>
  );
};

export default SideEffectCard;
