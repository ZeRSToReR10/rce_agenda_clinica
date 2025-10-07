import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { pacientesAPI } from '../../services/api';
import ErrorAlert from '../common/ErrorAlert';

const PatientForm = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  console.log('📍 PatientForm - Iniciando componente');
  console.log('📍 PatientForm - location.state:', location.state);
  
  // Obtener datos de la cita desde la navegación (si viene del agendamiento)
  const appointmentData = location.state?.appointmentData || {};
  
  console.log('📍 PatientForm - appointmentData:', appointmentData);
  
  const [formData, setFormData] = useState({
    rut: '',
    nombre: '',
    apellido: '',
    telefono: '',
    edad: '',
    genero: '',
    direccion: '',
    fecha_nacimiento: '',
    email: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      console.log('📤 PatientForm - Iniciando envío de formulario');
      
      // Validaciones
      if (!formData.rut || !formData.nombre || !formData.apellido) {
        throw new Error('RUT, nombre y apellido son obligatorios');
      }

      // Preparar datos
      const patientData = {
        rut: formData.rut,
        nombre: formData.nombre.trim(),
        apellido: formData.apellido.trim(),
        telefono: formData.telefono || null,
        edad: formData.edad ? parseInt(formData.edad) : null,
        genero: formData.genero || null,
        direccion: formData.direccion || null,
        fecha_nacimiento: formData.fecha_nacimiento || null,
        email: formData.email || null
      };

      console.log('📤 PatientForm - Datos del paciente:', patientData);
      
      const response = await pacientesAPI.create(patientData);
      
      console.log('✅ PatientForm - Paciente creado:', response.data);
      
      setSuccess('Paciente creado exitosamente');
      
      // Si venimos del agendamiento, redirigir de vuelta con el paciente creado
      if (appointmentData.professional) {
        console.log('🔄 PatientForm - Redirigiendo al agendamiento');
        setTimeout(() => {
          navigate('/agendador', {
            state: {
              patientCreated: response.data.paciente,
              appointmentData: appointmentData
            }
          });
        }, 1500);
      } else {
        // Si no, limpiar el formulario después de 2 segundos
        setTimeout(() => {
          setFormData({
            rut: '',
            nombre: '',
            apellido: '',
            telefono: '',
            edad: '',
            genero: '',
            direccion: '',
            fecha_nacimiento: '',
            email: ''
          });
          setSuccess('');
        }, 2000);
      }
      
    } catch (error) {
      console.error('❌ PatientForm - Error creando paciente:', error);
      setError(error.response?.data?.error || error.message || 'Error al crear el paciente');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    console.log('↩️ PatientForm - Cancelando, volviendo atrás');
    // Si venimos del agendamiento, volver con los datos de la cita
    if (appointmentData.professional) {
      navigate('/agendador', { state: { appointmentData } });
    } else {
      navigate(-1); // equivalente a goBack
    }
  };

  const calculateAge = (fechaNacimiento) => {
    if (!fechaNacimiento) return '';
    
    const today = new Date();
    const birthDate = new Date(fechaNacimiento);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age.toString();
  };

  const handleFechaNacimientoChange = (e) => {
    const fecha = e.target.value;
    setFormData({
      ...formData,
      fecha_nacimiento: fecha,
      edad: calculateAge(fecha)
    });
  };

  console.log('🎨 PatientForm - Renderizando componente');

  return (
    <div className="container mt-4">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">
              <div className="d-flex justify-content-between align-items-center">
                <h3 className="card-title mb-0">
                  <i className="fas fa-user-plus me-2"></i>
                  Crear Nuevo Paciente
                </h3>
                {appointmentData.professional && (
                  <span className="badge bg-info">
                    Volverá al agendamiento después de crear
                  </span>
                )}
              </div>
            </div>
            <div className="card-body">
              {appointmentData.professional && (
                <div className="alert alert-info">
                  <strong>Agendamiento en proceso:</strong><br />
                  Profesional: {appointmentData.professional.nombre} {appointmentData.professional.apellido}<br />
                  Fecha: {new Date(appointmentData.date).toLocaleDateString('es-ES')}<br />
                  Hora: {appointmentData.time}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="rut" className="form-label">RUT *</label>
                    <input
                      type="text"
                      className="form-control"
                      id="rut"
                      name="rut"
                      value={formData.rut}
                      onChange={handleChange}
                      placeholder="12.345.678-9"
                      required
                    />
                    <div className="form-text">Formato: 12.345.678-9 o 12345678-9</div>
                  </div>
                  <div className="col-md-6 mb-3">
                    <label htmlFor="email" className="form-label">Email</label>
                    <input
                      type="email"
                      className="form-control"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="paciente@ejemplo.com"
                    />
                  </div>
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="nombre" className="form-label">Nombre *</label>
                    <input
                      type="text"
                      className="form-control"
                      id="nombre"
                      name="nombre"
                      value={formData.nombre}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="col-md-6 mb-3">
                    <label htmlFor="apellido" className="form-label">Apellido *</label>
                    <input
                      type="text"
                      className="form-control"
                      id="apellido"
                      name="apellido"
                      value={formData.apellido}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="telefono" className="form-label">Teléfono</label>
                    <input
                      type="tel"
                      className="form-control"
                      id="telefono"
                      name="telefono"
                      value={formData.telefono}
                      onChange={handleChange}
                      placeholder="+56912345678"
                    />
                  </div>
                  <div className="col-md-6 mb-3">
                    <label htmlFor="genero" className="form-label">Género</label>
                    <select
                      className="form-select"
                      id="genero"
                      name="genero"
                      value={formData.genero}
                      onChange={handleChange}
                    >
                      <option value="">Seleccione</option>
                      <option value="M">Masculino</option>
                      <option value="F">Femenino</option>
                      <option value="O">Otro</option>
                    </select>
                  </div>
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="fecha_nacimiento" className="form-label">Fecha de Nacimiento</label>
                    <input
                      type="date"
                      className="form-control"
                      id="fecha_nacimiento"
                      name="fecha_nacimiento"
                      value={formData.fecha_nacimiento}
                      onChange={handleFechaNacimientoChange}
                      max={new Date().toISOString().split('T')[0]}
                    />
                  </div>
                  <div className="col-md-6 mb-3">
                    <label htmlFor="edad" className="form-label">Edad (calculada automáticamente)</label>
                    <input
                      type="number"
                      className="form-control"
                      id="edad"
                      name="edad"
                      value={formData.edad}
                      onChange={handleChange}
                      min="0"
                      max="120"
                      readOnly
                    />
                  </div>
                </div>

                <div className="row">
                  <div className="col-12 mb-3">
                    <label htmlFor="direccion" className="form-label">Dirección</label>
                    <input
                      type="text"
                      className="form-control"
                      id="direccion"
                      name="direccion"
                      value={formData.direccion}
                      onChange={handleChange}
                      placeholder="Av. Siempre Viva 123"
                    />
                  </div>
                </div>

                {success && (
                  <div className="alert alert-success">
                    <i className="fas fa-check-circle me-2"></i>
                    {success}
                    {appointmentData.professional && (
                      <div className="mt-2">
                        <small>Redirigiendo al agendamiento...</small>
                      </div>
                    )}
                  </div>
                )}

                <ErrorAlert error={error} />

                <div className="d-flex justify-content-between">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleCancel}
                    disabled={loading}
                  >
                    <i className="fas fa-arrow-left me-2"></i>
                    {appointmentData.professional ? 'Volver al Agendamiento' : 'Cancelar'}
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Creando...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-save me-2"></i>
                        Crear Paciente
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientForm;