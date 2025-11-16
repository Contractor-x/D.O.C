import React from 'react';

const SafetyResult = ({ result }) => {
  const getResultColor = (isSafe) => {
    return isSafe ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100';
  };

  return (
    <div className={`p-4 rounded-md ${getResultColor(result.isSafe)}`}>
      <h3 className="text-lg font-semibold mb-2">Safety Assessment</h3>
      <p className="mb-2">{result.message}</p>
      {result.recommendations && (
        <div>
          <h4 className="font-semibold mb-1">Recommendations:</h4>
          <ul className="list-disc list-inside">
            {result.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SafetyResult;
