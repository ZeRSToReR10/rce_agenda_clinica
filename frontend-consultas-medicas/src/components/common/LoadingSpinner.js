import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="text-center">
      <div className="spinner-border" role="status">
        <span className="visually-hidden">Cargando...</span>
      </div>
    </div>
  );
};

export default LoadingSpinner;