import React from 'react';

const EmergencyContacts = ({ contacts }) => {
  return (
    <div className="emergency-contacts">
      <h3 className="text-lg font-semibold mb-4">Emergency Contacts</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {contacts.map((contact, index) => (
          <div key={index} className="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
            <h4 className="font-semibold text-red-800">{contact.name}</h4>
            <p className="text-red-700"><strong>Phone:</strong> {contact.phone}</p>
            <p className="text-red-700"><strong>Relationship:</strong> {contact.relationship}</p>
            <button className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
              Call Emergency
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EmergencyContacts;
