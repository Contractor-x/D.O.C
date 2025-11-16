import React from 'react';
import ResearchCard from './ResearchCard';

const ResearchList = ({ researches }) => {
  return (
    <div className="research-list">
      <h3 className="text-xl font-semibold mb-4">Latest Research</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {researches.map((research, index) => (
          <ResearchCard key={index} research={research} />
        ))}
      </div>
    </div>
  );
};

export default ResearchList;
