import React from 'react';

const DocumentViewer = ({ document }) => {
  return (
    <div className="document-viewer">
      <h3 className="text-lg font-semibold mb-4">Document Viewer</h3>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h4 className="text-xl font-semibold mb-4">{document.name}</h4>
        <div className="mb-4">
          <p><strong>Type:</strong> {document.type}</p>
          <p><strong>Date:</strong> {document.date}</p>
        </div>
        <div className="border rounded p-4 bg-gray-50">
          {document.content ? (
            <pre className="whitespace-pre-wrap text-sm">{document.content}</pre>
          ) : (
            <div className="text-center text-gray-500">
              <p>Document preview not available</p>
              <p className="text-sm">Click download to view the full document</p>
            </div>
          )}
        </div>
        <div className="mt-4 flex space-x-2">
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            Download
          </button>
          <button className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
            Share
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
