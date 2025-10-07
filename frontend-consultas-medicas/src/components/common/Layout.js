import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Header from './Header';

const Layout = ({ children }) => {
  const { user } = useAuth();

  return (
    <div>
      <Header />
      <div className="main-container">
        {children}
      </div>
    </div>
  );
};

export default Layout;