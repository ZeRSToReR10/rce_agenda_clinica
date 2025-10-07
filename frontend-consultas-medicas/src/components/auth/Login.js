import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { authAPI } from '../../services/api';
import logoSalud from '../../assets/logo_salud_lautaro.png';
import '../../styles/Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    rut: '',
    password: '',
    centro_salud_id: '',
  });
  const [centros, setCentros] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuth();

  useEffect(() => {
    loadCentros();
  }, []);

  const loadCentros = async () => {
    try {
      const response = await authAPI.getCentros();
      setCentros(response.data);
    } catch (error) {
      console.error('Error cargando centros:', error);
      setError('Error al cargar centros de salud');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login(formData);
      const { token, user, centro_salud, sesion } = response.data;
      
      login({ ...user, centro_salud, sesion }, token);
      
      // Redirigir según el rol
      if (user.rol === 'health-worker') {
        window.location.href = '/agenda';
      } else if (user.rol === 'scheduler') {
        window.location.href = '/agendador';
      } else if (user.rol === 'admin') {
        window.location.href = '/admin';
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Error en el login');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="login-container">
      <div className="logo">
        <img 
          src={logoSalud} 
          alt="Departamento de Salud Lautaro" 
          className="logo-img"
        />
        <p className="text-muted">Departamento de Salud</p>
      </div>
      
      <form onSubmit={handleSubmit}>
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}
        
        <div className="mb-3">
          <label htmlFor="rut" className="form-label">RUT Usuario</label>
          <input
            type="text"
            className="form-control"
            id="rut"
            name="rut"
            placeholder="12.345.678-9"
            value={formData.rut}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="mb-3">
          <label htmlFor="centro_salud_id" className="form-label">Centro Médico</label>
          <select
            className="form-select"
            id="centro_salud_id"
            name="centro_salud_id"
            value={formData.centro_salud_id}
            onChange={handleChange}
            required
          >
            <option value="" disabled>Seleccione un centro médico</option>
            {centros.map(centro => (
              <option key={centro.id} value={centro.id}>
                {centro.nombre}
              </option>
            ))}
          </select>
        </div>
        
        <div className="mb-3">
          <label htmlFor="password" className="form-label">Contraseña</label>
          <input
            type="password"
            className="form-control"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        
        <button 
          type="submit" 
          className="btn btn-primary w-100"
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status"></span>
              Ingresando...
            </>
          ) : 'Ingresar'}
        </button>
      </form>
    </div>
  );
};

export default Login;