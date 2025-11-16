import React from 'react';

const IdentificationResult = ({ result }) => {
  return (
    <div className="identification-result">
      <h3 className="text-lg font-semibold mb-2">Identification Result</h3>
      {result ? (
        <div className="bg-green-100 p-4 rounded-md">
          <p className="text-green-800"><strong>Drug:</strong> {result.name}</p>
          <p className="text-green-800"><strong>Confidence:</strong> {result.confidence}%</p>
        </div>
      ) : (
        <div className="bg-yellow-100 p-4 rounded-md">
          <p className="text-yellow-800">No drug identified. Please try again.</p>
        </div>
      )}
    </div>
  );
};

export default IdentificationResult;
