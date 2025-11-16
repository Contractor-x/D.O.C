import React from 'react';

const FilterOptions = ({ onFilterChange }) => {
  const handleSeverityChange = (e) => {
    onFilterChange({ severity: e.target.value });
  };

  return (
    <div className="filter-options mb-4">
      <label htmlFor="severity-filter" className="block text-sm font-medium text-gray-700 mb-2">
        Filter by Severity
      </label>
      <select
        id="severity-filter"
        onChange={handleSeverityChange}
        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
      >
        <option value="">All Severities</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>
    </div>
  );
};

export default FilterOptions;
