import React from 'react';
import SideEffectCard from './SideEffectCard';

const SideEffectList = ({ sideEffects }) => {
  return (
    <div className="side-effect-list">
      <h3 className="text-xl font-semibold mb-4">Side Effects</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sideEffects.map((effect, index) => (
          <SideEffectCard key={index} sideEffect={effect} />
        ))}
      </div>
    </div>
  );
};

export default SideEffectList;
