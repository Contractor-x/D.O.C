import React from 'react';

const DoctorContactCard = ({ doctor }) => {
  return (
    <div className="doctor-contact-card bg-white p-6 rounded-lg shadow-md">
      <div className="flex items-center mb-4">
        <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-lg mr-4">
          {doctor.name.charAt(0)}
        </div>
        <div>
          <h4 className="text-lg font-semibold">{doctor.name}</h4>
          <p className="text-gray-600">{doctor.specialty}</p>
        </div>
      </div>
      <div className="mb-4">
        <p className="text-sm text-gray-600"><strong>Clinic:</strong> {doctor.clinic}</p>
        <p className="text-sm text-gray-600"><strong>Phone:</strong> {doctor.phone}</p>
        <p className="text-sm text-gray-600"><strong>Email:</strong> {doctor.email}</p>
      </div>
      <div className="flex space-x-2">
        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 flex-1">
          Call
        </button>
        <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 flex-1">
          Message
        </button>
      </div>
    </div>
  );
};

export default DoctorContactCard;
