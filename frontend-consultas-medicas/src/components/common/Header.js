import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import '../../styles/Header.css';
const Header = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <header className="custom-header">
      <div className="container d-flex align-items-center justify-content-between">
        <a className="brand" href="#">
          <i className="fas fa-hospital-alt me-2"></i>
          Sistema de Consultas Médicas
        </a>

        <div className="user-info d-flex align-items-center">
          <span className="user-text me-3">
            {user?.nombre} {user?.apellido} - {user?.centro_salud?.nombre}
          </span>
          <button className="btn logout-btn" onClick={handleLogout}>
            <i className="fas fa-sign-out-alt me-1"></i>
            Cerrar Sesión
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
