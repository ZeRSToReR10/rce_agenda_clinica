import React from 'react';

const ErrorAlert = ({ error }) => {
  if (!error) return null;

  return (
    <div className="alert alert-danger alert-dismissible fade show" role="alert">
      {error}
      <button 
        type="button" 
        className="btn-close" 
        onClick={() => {}}
      ></button>
    </div>
  );
};

export default ErrorAlert;