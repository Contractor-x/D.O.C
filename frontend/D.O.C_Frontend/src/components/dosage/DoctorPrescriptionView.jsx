import React from 'react';

const DoctorPrescriptionView = ({ prescription }) => {
  return (
    <div className="doctor-prescription-view bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-semibold mb-4">Doctor's Prescription</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="font-semibold mb-2">Patient Information</h4>
          <p><strong>Name:</strong> {prescription.patientName}</p>
          <p><strong>Age:</strong> {prescription.patientAge}</p>
          <p><strong>Weight:</strong> {prescription.patientWeight} kg</p>
        </div>
        <div>
          <h4 className="font-semibold mb-2">Medication</h4>
          <p><strong>Drug:</strong> {prescription.drugName}</p>
          <p><strong>Dosage:</strong> {prescription.dosage} mg</p>
          <p><strong>Frequency:</strong> {prescription.frequency}</p>
        </div>
      </div>
      <div className="mt-4">
        <h4 className="font-semibold mb-2">Doctor's Notes</h4>
        <p className="text-gray-600">{prescription.notes}</p>
      </div>
    </div>
  );
};

export default DoctorPrescriptionView;
