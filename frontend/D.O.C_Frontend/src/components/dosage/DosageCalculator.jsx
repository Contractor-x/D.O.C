import React, { useState } from 'react';

const DosageCalculator = ({ drug, weight, age }) => {
  const [calculatedDosage, setCalculatedDosage] = useState(null);

  const calculateDosage = () => {
    // Simple mg/kg calculation (this would be more complex in reality)
    const dosage = (drug.dosagePerKg * weight).toFixed(2);
    setCalculatedDosage(dosage);
  };

  return (
    <div className="dosage-calculator bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-semibold mb-4">Dosage Calculator</h3>
      <div className="mb-4">
        <p className="text-gray-600"><strong>Drug:</strong> {drug.name}</p>
        <p className="text-gray-600"><strong>Weight:</strong> {weight} kg</p>
        <p className="text-gray-600"><strong>Age:</strong> {age} years</p>
      </div>
      <button
        onClick={calculateDosage}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 mb-4"
      >
        Calculate Dosage
      </button>
      {calculatedDosage && (
        <div className="bg-green-100 p-4 rounded">
          <p className="text-green-800 font-semibold">Calculated Dosage: {calculatedDosage} mg</p>
        </div>
      )}
    </div>
  );
};

export default DosageCalculator;
