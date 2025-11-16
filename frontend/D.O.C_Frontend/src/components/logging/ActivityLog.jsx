import React from 'react';

const ActivityLog = ({ logs }) => {
  return (
    <div className="activity-log">
      <h3 className="text-lg font-semibold mb-4">Activity Log</h3>
      <div className="bg-white rounded-lg shadow-md">
        <div className="max-h-96 overflow-y-auto">
          {logs.map((log, index) => (
            <div key={index} className="p-4 border-b border-gray-200 last:border-b-0">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm font-medium text-gray-900">{log.action}</p>
                  <p className="text-sm text-gray-500">{log.details}</p>
                </div>
                <span className="text-xs text-gray-400">{log.timestamp}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ActivityLog;
