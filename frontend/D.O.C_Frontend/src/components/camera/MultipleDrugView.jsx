import React from 'react';

const MultipleDrugView = ({ drugs }) => {
  return (
    <div className="multiple-drug-view">
      <h3 className="text-lg font-semibold mb-2">Multiple Drugs Detected</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {drugs.map((drug, index) => (
          <div key={index} className="bg-blue-100 p-4 rounded-md">
            <p className="text-blue-800"><strong>Drug {index + 1}:</strong> {drug.name}</p>
            <p className="text-blue-800"><strong>Confidence:</strong> {drug.confidence}%</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MultipleDrugView;
