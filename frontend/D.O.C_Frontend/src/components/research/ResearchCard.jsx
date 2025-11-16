import React from 'react';

const ResearchCard = ({ research }) => {
  return (
    <div className="research-card bg-white p-6 rounded-lg shadow-md">
      <h4 className="text-lg font-semibold mb-2">{research.title}</h4>
      <p className="text-gray-600 mb-2">{research.abstract}</p>
      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>{research.source}</span>
        <span>{research.date}</span>
      </div>
      <div className="mt-4">
        <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
          {research.category}
        </span>
      </div>
      <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Read More
      </button>
    </div>
  );
};

export default ResearchCard;
