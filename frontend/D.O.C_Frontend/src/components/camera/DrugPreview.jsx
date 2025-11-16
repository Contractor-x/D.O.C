import React from 'react';

const DrugPreview = ({ image }) => {
  return (
    <div className="drug-preview">
      <h3 className="text-lg font-semibold mb-2">Captured Image</h3>
      {image ? (
        <img src={image} alt="Captured drug" className="w-full h-64 object-cover rounded-md" />
      ) : (
        <div className="w-full h-64 bg-gray-200 flex items-center justify-center rounded-md">
          <p className="text-gray-500">No image captured</p>
        </div>
      )}
    </div>
  );
};

export default DrugPreview;
