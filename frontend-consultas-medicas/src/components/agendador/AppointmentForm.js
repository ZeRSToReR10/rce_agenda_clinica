import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // Cambiado: useHistory → useNavigate
import { agendadorAPI, pacientesAPI } from '../../services/api';
import ErrorAlert from '../common/ErrorAlert';
import { useAuth } from '../../contexts/AuthContext';
import { Notification } from '../../components/common/Notification';

const AppointmentForm = ({ professional, date, time, onSuccess, onCancel, createdPatient, onPatientCreated }) => {
  const { user } = useAuth();
  const navigate = useNavigate(); // Cambiado: useHistory → useNavigate
  
  const [formData, setFormData] = useState({
    paciente_rut: '',
    paciente_nombre: '',
    paciente_apellido: '',
    paciente_telefono: '',
    paciente_edad: '',
    paciente_genero: '',
    paciente_direccion: '',
    n_ficha: '',
    n_carpeta: '',
    tipo_consulta: 'consulta'
  });
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);

  // Efecto para manejar cuando recibimos un paciente creado desde el dashboard
  useEffect(() => {
    if (createdPatient) {
      console.log('🔄 AppointmentForm recibió paciente creado:', createdPatient);
      selectPatient(createdPatient);
      if (onPatientCreated) {
        onPatientCreated(createdPatient);
      }
    }
  }, [createdPatient, onPatientCreated]);

  // Buscar paciente SOLO por RUT
  const searchPatient = async () => {
    console.log('🎯 searchPatient ejecutándose...');
    
    if (!formData.paciente_rut) {
      setError('Ingrese RUT para buscar');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const rutLimpio = formData.paciente_rut.replace(/\./g, '').replace(/-/g, '');
      console.log('🔍 Buscando por RUT:', rutLimpio);
      
      // Usar la función search existente pero solo con RUT (apellido vacío)
      const response = await pacientesAPI.search('', rutLimpio);
      
      console.log('✅ Respuesta recibida:', response);
      console.log('📋 Datos de la respuesta:', response.data);
      
      setSearchResults(response.data.pacientes || []);
      setShowSearchResults(true);
      
      if (response.data.pacientes.length === 0) {
        setError('Paciente no encontrado con ese RUT');
        console.log('❌ No se encontraron pacientes');
      } else {
        console.log(`✅ Encontrados ${response.data.pacientes.length} pacientes`);
      }
    } catch (error) {
      console.error('❌ Error buscando paciente:', error);
      console.error('❌ Detalles del error:', error.response);
      setError(error.response?.data?.error || 'Error al buscar paciente');
    } finally {
      setLoading(false);
    }
  };

  // Manejar la tecla Enter en el campo RUT
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      searchPatient();
    }
  };

  // Seleccionar paciente de los resultados
  const selectPatient = (patient) => {
    console.log('✅ Paciente seleccionado:', patient);
    setSelectedPatient(patient);
    setFormData({
      ...formData,
      paciente_rut: patient.rut,
      paciente_nombre: patient.nombre,
      paciente_apellido: patient.apellido,
      paciente_telefono: patient.telefono || '',
      paciente_edad: patient.edad || '',
      paciente_genero: patient.genero || '',
      paciente_direccion: patient.direccion || ''
    });
    setShowSearchResults(false);
    setSearchResults([]);
    setError('');
  };

  // Función para redirigir a la creación de paciente
  const handleCreateNewPatient = () => {
    // Pasamos los datos de la cita actual para poder volver
    navigate('/pacientes/nuevo', {
      state: {
        appointmentData: {
          professional,
          date,
          time
        }
      }
    });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Función para buscar paciente por RUT (usada antes de agendar)
  const findPatientByRut = async (rut) => {
    try {
      console.log('🔍 Buscando paciente por RUT antes de agendar:', rut);
      const response = await pacientesAPI.search('', rut);
      console.log('📋 Resultados búsqueda RUT:', response.data);
      return response.data.pacientes?.[0] || null;
    } catch (error) {
      console.error('❌ Error buscando paciente por RUT:', error);
      return null;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      // Validaciones básicas
      if (!formData.paciente_rut) {
        throw new Error('El RUT del paciente es obligatorio');
      }

      let pacienteFinal = selectedPatient;

      // Si no hay paciente seleccionado, buscar por RUT
      if (!pacienteFinal) {
        const rutLimpio = formData.paciente_rut.replace(/\./g, '').replace(/-/g, '');
        const existingPatient = await findPatientByRut(rutLimpio);
        
        if (existingPatient) {
          pacienteFinal = existingPatient;
          console.log('✅ Paciente encontrado:', pacienteFinal);
        } else {
          throw new Error('No se encontró el paciente con ese RUT. Debe buscar y seleccionar un paciente existente o crear uno nuevo.');
        }
      }

      // Validar que tenemos un paciente con ID
      if (!pacienteFinal || !pacienteFinal.id) {
        throw new Error('No se pudo obtener el ID del paciente');
      }

      // Obtener centro_salud_id del contexto de usuario
      const centroSaludId = user?.centro_salud?.id || 1;

      // Crear la agenda
      const appointmentData = {
        paciente_id: pacienteFinal.id,
        usuario_id: professional.id,
        centro_salud_id: centroSaludId,
        fecha: date,
        hora: time.includes(':') ? time : `${time}:00`,
        tipo_consulta: formData.tipo_consulta,
        n_ficha: formData.n_ficha || null,
        n_carpeta: formData.n_carpeta || null
      };

      console.log('📤 Creando agenda con datos:', appointmentData);
      
      const response = await agendadorAPI.createAgenda(appointmentData);
      console.log('✅ Agenda creada:', response.data);
      
      await Notification.success('Consulta guardada exitosamente', '¡Éxito!');
      window.location.reload();
    } catch (error) {
      console.error('❌ Error en handleSubmit:', error);
      setError(error.message || 'Error al agendar la cita');
      Notification.error(
        error.response?.data?.error || error.message || 'Error al guardar la consulta',
        'Error'
      );
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="scheduling-form">
      <h3 className="section-title">Agendar Consulta</h3>

      {/* Resumen de la cita */}
      <div className="alert alert-info">
        <h6 className="alert-heading">Resumen de la Cita</h6>
        <p className="mb-1"><strong>Profesional:</strong> {professional.nombre} {professional.apellido}</p>
        <p className="mb-1"><strong>Fecha:</strong> {formatDate(date)}</p>
        <p className="mb-0"><strong>Hora:</strong> {time}</p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Búsqueda de paciente SOLO por RUT */}
        <div className="patient-search mb-4">
          <h5>Buscar Paciente por RUT</h5>
          <div className="row">
            <div className="col-md-8 mb-3">
              <label htmlFor="paciente_rut" className="form-label">RUT *</label>
              <div className="input-group">
                <input
                  type="text"
                  className="form-control"
                  id="paciente_rut"
                  name="paciente_rut"
                  value={formData.paciente_rut}
                  onChange={handleChange}
                  onKeyPress={handleKeyPress}
                  placeholder="12.345.678-9 o 123456789"
                  required
                  disabled={!!selectedPatient}
                />
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={searchPatient}
                  disabled={loading || !formData.paciente_rut || !!selectedPatient}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Buscando...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-search me-2"></i>
                      Buscar por RUT
                    </>
                  )}
                </button>
              </div>
              <div className="form-text">
                Ingrese el RUT con o sin formato: 123456789 o 12.345.678-9
              </div>
            </div>
          </div>

          {/* Botón para crear nuevo paciente */}
          <div className="row mb-3">
            <div className="col-12">
              <button
                type="button"
                className="btn btn-outline-success"
                onClick={handleCreateNewPatient}
              >
                <i className="fas fa-user-plus me-2"></i>
                Crear Nuevo Paciente
              </button>
              <div className="form-text text-muted mt-1">
                Si el paciente no existe en el sistema, puede crear uno nuevo
              </div>
            </div>
          </div>

          {/* Resultados de búsqueda */}
          {showSearchResults && (
            <div className="search-results mt-3">
              <div className="card">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <h6 className="mb-0">Resultados de búsqueda por RUT</h6>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline-secondary"
                    onClick={() => setShowSearchResults(false)}
                  >
                    <i className="fas fa-times me-1"></i>
                    Cerrar
                  </button>
                </div>
                <div className="card-body">
                  {searchResults.length > 0 ? (
                    <div className="list-group">
                      {searchResults.map(patient => (
                        <button
                          key={patient.id}
                          type="button"
                          className="list-group-item list-group-item-action"
                          onClick={() => selectPatient(patient)}
                        >
                          <div className="d-flex justify-content-between align-items-start">
                            <div>
                              <strong>{patient.rut}</strong><br />
                              {patient.nombre} {patient.apellido}
                              {patient.telefono && <><br />Tel: {patient.telefono}</>}
                              {patient.edad && <><br />Edad: {patient.edad}</>}
                              {patient.genero && <><br />Género: {patient.genero === 'M' ? 'Masculino' : patient.genero === 'F' ? 'Femenino' : patient.genero}</>}
                            </div>
                            <span className="badge bg-success">Seleccionar</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-3">
                      <p className="text-muted">No se encontraron pacientes con ese RUT.</p>
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={handleCreateNewPatient}
                      >
                        <i className="fas fa-user-plus me-2"></i>
                        Crear Nuevo Paciente
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Información del paciente seleccionado */}
          {selectedPatient && (
            <div className="alert alert-success mt-3">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <i className="fas fa-check-circle me-2"></i>
                  <strong>Paciente seleccionado:</strong> {selectedPatient.nombre} {selectedPatient.apellido} ({selectedPatient.rut})
                  {createdPatient && <span className="badge bg-warning text-dark ms-2">Nuevo</span>}
                </div>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => {
                    setSelectedPatient(null);
                    setFormData({
                      ...formData,
                      paciente_rut: '',
                      paciente_nombre: '',
                      paciente_apellido: '',
                      paciente_telefono: '',
                      paciente_edad: '',
                      paciente_genero: '',
                      paciente_direccion: ''
                    });
                  }}
                >
                  <i className="fas fa-times me-1"></i>
                  Cambiar
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Datos del paciente (solo lectura cuando está seleccionado) */}
        <div className="patient-info">
          <h5>
            Datos del Paciente 
            {selectedPatient && (
              <span className="badge bg-success ms-2">
                {createdPatient ? 'Nuevo' : 'Existente'}
              </span>
            )}
          </h5>
          <div className="row">
            <div className="col-md-6 mb-3">
              <label htmlFor="paciente_nombre" className="form-label">Nombre *</label>
              <input
                type="text"
                className="form-control"
                id="paciente_nombre"
                name="paciente_nombre"
                value={formData.paciente_nombre}
                onChange={handleChange}
                required
                readOnly={!!selectedPatient}
              />
            </div>
            <div className="col-md-6 mb-3">
              <label htmlFor="paciente_apellido" className="form-label">Apellido *</label>
              <input
                type="text"
                className="form-control"
                id="paciente_apellido"
                name="paciente_apellido"
                value={formData.paciente_apellido}
                onChange={handleChange}
                required
                readOnly={!!selectedPatient}
              />
            </div>
          </div>

          <div className="row">
            <div className="col-md-6 mb-3">
              <label htmlFor="paciente_telefono" className="form-label">Teléfono</label>
              <input
                type="tel"
                className="form-control"
                id="paciente_telefono"
                name="paciente_telefono"
                value={formData.paciente_telefono}
                onChange={handleChange}
                readOnly={!!selectedPatient}
              />
            </div>
            <div className="col-md-3 mb-3">
              <label htmlFor="paciente_edad" className="form-label">Edad</label>
              <input
                type="number"
                className="form-control"
                id="paciente_edad"
                name="paciente_edad"
                value={formData.paciente_edad}
                onChange={handleChange}
                min="0"
                max="120"
                readOnly={!!selectedPatient}
              />
            </div>
            <div className="col-md-3 mb-3">
              <label htmlFor="paciente_genero" className="form-label">Género</label>
              <select
                className="form-select"
                id="paciente_genero"
                name="paciente_genero"
                value={formData.paciente_genero}
                onChange={handleChange}
                disabled={!!selectedPatient}
              >
                <option value="">Seleccione</option>
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
                <option value="O">Otro</option>
              </select>
            </div>
          </div>

          <div className="row">
            <div className="col-12 mb-3">
              <label htmlFor="paciente_direccion" className="form-label">Dirección</label>
              <input
                type="text"
                className="form-control"
                id="paciente_direccion"
                name="paciente_direccion"
                value={formData.paciente_direccion}
                onChange={handleChange}
                readOnly={!!selectedPatient}
              />
            </div>
          </div>
        </div>

        {/* Datos de la consulta */}
        <div className="row mb-4">
          <div className="col-md-4 mb-3">
            <label htmlFor="tipo_consulta" className="form-label">Tipo de Consulta</label>
            <select
              className="form-select"
              id="tipo_consulta"
              name="tipo_consulta"
              value={formData.tipo_consulta}
              onChange={handleChange}
            >
              <option value="consulta">Consulta</option>
              <option value="control">Control</option>
              <option value="procedimiento">Procedimiento</option>
            </select>
          </div>
          <div className="col-md-4">
            <label htmlFor="n_ficha" className="form-label">Nº Ficha</label>
            <input
              type="text"
              className="form-control"
              id="n_ficha"
              name="n_ficha"
              value={formData.n_ficha}
              onChange={handleChange}
            />
          </div>
          <div className="col-md-4">
            <label htmlFor="n_carpeta" className="form-label">Nº Carpeta</label>
            <input
              type="text"
              className="form-control"
              id="n_carpeta"
              name="n_carpeta"
              value={formData.n_carpeta}
              onChange={handleChange}
            />
          </div>
        </div>

        <ErrorAlert error={error} />

        <div className="d-grid gap-2 d-md-flex justify-content-md-end">
          <button 
            type="button"
            className="btn btn-secondary me-2"
            onClick={onCancel}
            disabled={saving}
          >
            <i className="fas fa-times me-2"></i>Cancelar
          </button>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={saving || !selectedPatient}
          >
            {saving ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                Agendando...
              </>
            ) : (
              <>
                <i className="fas fa-calendar-plus me-2"></i>
                Confirmar Cita
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AppointmentForm;