import React from 'react';

const RecommendationCard = ({ recommendation }) => {
  return (
    <div className="recommendation-card bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
      <h4 className="text-lg font-semibold text-blue-800 mb-2">Recommendation</h4>
      <p className="text-blue-700">{recommendation.text}</p>
      {recommendation.action && (
        <button className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          {recommendation.action}
        </button>
      )}
    </div>
  );
};

export default RecommendationCard;
