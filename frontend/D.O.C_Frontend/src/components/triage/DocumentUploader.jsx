import React, { useState } from 'react';

const DocumentUploader = ({ onUpload }) => {
  const [files, setFiles] = useState([]);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
  };

  const handleUpload = () => {
    if (files.length > 0) {
      onUpload(files);
    }
  };

  return (
    <div className="document-uploader">
      <h3 className="text-lg font-semibold mb-4">Upload Medical Documents</h3>
      <div className="mb-4">
        <input
          type="file"
          multiple
          accept="image/*,.pdf,.doc,.docx"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
      </div>
      {files.length > 0 && (
        <div className="mb-4">
          <h4 className="font-semibold mb-2">Selected Files:</h4>
          <ul className="list-disc list-inside">
            {files.map((file, index) => (
              <li key={index}>{file.name}</li>
            ))}
          </ul>
        </div>
      )}
      <button
        onClick={handleUpload}
        disabled={files.length === 0}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        Upload Documents
      </button>
    </div>
  );
};

export default DocumentUploader;
