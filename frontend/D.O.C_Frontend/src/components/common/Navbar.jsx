import React from 'react';

const Navbar = () => {
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="text-xl font-semibold">D.O.C</div>
          <ul className="flex space-x-6">
            <li><a href="#" className="text-gray-700 hover:text-blue-600">Dashboard</a></li>
            <li><a href="#" className="text-gray-700 hover:text-blue-600">Scan Drug</a></li>
            <li><a href="#" className="text-gray-700 hover:text-blue-600">Side Effects</a></li>
            <li><a href="#" className="text-gray-700 hover:text-blue-600">Research</a></li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
