import React from 'react';

const DosageComparisonCard = ({ prescribed, recommended }) => {
  const isMatch = prescribed === recommended;

  return (
    <div className={`dosage-comparison-card p-4 rounded-lg border ${isMatch ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}`}>
      <h4 className="text-lg font-semibold mb-2">Dosage Comparison</h4>
      <div className="flex justify-between items-center mb-2">
        <span className="text-gray-600">Prescribed:</span>
        <span className="font-medium">{prescribed} mg</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-gray-600">Recommended:</span>
        <span className="font-medium">{recommended} mg</span>
      </div>
      {!isMatch && (
        <p className="text-red-600 mt-2 text-sm">
          Dosage mismatch detected. Please consult your healthcare provider.
        </p>
      )}
    </div>
  );
};

export default DosageComparisonCard;
