import React, { useRef, useState } from 'react';

const CameraCapture = ({ onCapture }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = mediaStream;
      setStream(mediaStream);
    } catch (error) {
      console.error('Error accessing camera:', error);
    }
  };

  const captureImage = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');
    onCapture(imageData);
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  return (
    <div className="camera-capture">
      <video ref={videoRef} autoPlay playsInline className="w-full h-64 bg-black"></video>
      <canvas ref={canvasRef} className="hidden" width="640" height="480"></canvas>
      <div className="mt-4 flex justify-center space-x-4">
        <button onClick={startCamera} className="bg-blue-600 text-white px-4 py-2 rounded">Start Camera</button>
        <button onClick={captureImage} className="bg-green-600 text-white px-4 py-2 rounded">Capture</button>
        <button onClick={stopCamera} className="bg-red-600 text-white px-4 py-2 rounded">Stop Camera</button>
      </div>
    </div>
  );
};

export default CameraCapture;
