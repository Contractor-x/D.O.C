import React from 'react';

const DocumentList = ({ documents, onSelect }) => {
  return (
    <div className="document-list">
      <h3 className="text-lg font-semibold mb-4">Medical Documents</h3>
      <div className="space-y-2">
        {documents.map((doc, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100"
            onClick={() => onSelect(doc)}
          >
            <div>
              <p className="font-medium">{doc.name}</p>
              <p className="text-sm text-gray-500">{doc.type} - {doc.date}</p>
            </div>
            <button className="text-blue-600 hover:text-blue-800">View</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentList;
