import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { consultasAPI, agendasAPI, diagnosticosAPI } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';
import { Notification } from '../../components/common/Notification'; 

const ConsultationForm = () => {
  const { agendaId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [agenda, setAgenda] = useState(null);
  const [paciente, setPaciente] = useState(null);
  const [consulta, setConsulta] = useState(null);
  const [sugerenciasDiagnosticos, setSugerenciasDiagnosticos] = useState([]);
  const [mostrarSugerencias, setMostrarSugerencias] = useState(false);
  const [cargandoDiagnosticos, setCargandoDiagnosticos] = useState(false);
  const [terminoBusquedaDiagnostico, setTerminoBusquedaDiagnostico] = useState('');

  const [formData, setFormData] = useState({
    estado_hora: 'Asignada',
    estado_atencion: 'en espera',
    modalidad_atencion: 'presencial',
    actividad: 'consulta',
    tipo_alta: 'alta',
    diagnostico: '',
    observaciones: '',
    ges: false,
    ingreso_diag: false,
    control_tto: false,
    egreso: false,
    pscv: false,
    morbilidad: false,
    psm: false,
    cns: false,
    lmp_lme: false,
    consejeria_lm: false,
    embarazada: false,
    visita_domic: false,
    dep_severa: false,
    remoto: false
  });

  useEffect(() => {
    if (agendaId) {
      loadAgendaDetail();
    }
  }, [agendaId]);

  // Efecto para buscar diagnósticos cuando el término de búsqueda cambia
  useEffect(() => {
    if (terminoBusquedaDiagnostico.length < 2) {
      setSugerenciasDiagnosticos([]);
      setMostrarSugerencias(false);
      return;
    }

    const buscarDiagnosticos = async () => {
      setCargandoDiagnosticos(true);
      try {
        const response = await consultasAPI.sugerirDiagnosticos(terminoBusquedaDiagnostico, 10);
        setSugerenciasDiagnosticos(response.data.diagnosticos || []);
        setMostrarSugerencias(true);
      } catch (error) {
        console.error('Error al buscar diagnósticos:', error);
        setSugerenciasDiagnosticos([]);
      } finally {
        setCargandoDiagnosticos(false);
      }
    };

    const debounceTimer = setTimeout(buscarDiagnosticos, 300);
    return () => clearTimeout(debounceTimer);
  }, [terminoBusquedaDiagnostico]);

  const loadAgendaDetail = async () => {
    setLoading(true);
    try {
      console.log('🔍 Cargando agenda ID:', agendaId);
      const response = await agendasAPI.getAgendaDetail(agendaId);
      console.log('📊 Respuesta completa de la API:', response.data);
      
      setAgenda(response.data.agenda);
      setPaciente(response.data.paciente);
      setConsulta(response.data.consulta);

      if (response.data.consulta) {
        setFormData(prev => ({
          ...prev,
          estado_hora: response.data.consulta.estado_hora || 'Asignada',
          estado_atencion: response.data.consulta.estado_atencion || 'en espera',
          modalidad_atencion: response.data.consulta.modalidad_atencion || 'presencial',
          actividad: response.data.consulta.actividad || 'consulta',
          tipo_alta: response.data.consulta.tipo_alta || 'alta',
          diagnostico: response.data.consulta.diagnostico || '',
          observaciones: response.data.consulta.observaciones || '',
          ges: response.data.consulta.ges || false,
          ingreso_diag: response.data.consulta.ingreso_diag || false,
          control_tto: response.data.consulta.control_tto || false,
          egreso: response.data.consulta.egreso || false,
          pscv: response.data.consulta.pscv || false,
          morbilidad: response.data.consulta.morbilidad || false,
          psm: response.data.consulta.psm || false,
          cns: response.data.consulta.cns || false,
          lmp_lme: response.data.consulta.lmp_lme || false,
          consejeria_lm: response.data.consulta.consejeria_lm || false,
          embarazada: response.data.consulta.embarazada || false,
          visita_domic: response.data.consulta.visita_domic || false,
          dep_severa: response.data.consulta.dep_severa || false,
          remoto: response.data.consulta.remoto || false
        }));

        // Si hay un diagnóstico, establecer también el término de búsqueda
        if (response.data.consulta.diagnostico) {
          setTerminoBusquedaDiagnostico(response.data.consulta.diagnostico);
        }
      } else {
        setFormData(prev => ({
          ...prev,
          estado_hora: 'Asignada',
          estado_atencion: 'en espera'
        }));
      }
    } catch (error) {
      console.error('❌ Error al cargar la agenda:', error);
      setError(error.response?.data?.error || 'Error al cargar la agenda');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Si cambia el estado_hora, actualizar automáticamente el estado_atencion
    if (name === 'estado_hora') {
      switch (value) {
        case 'Asignada':
          setFormData(prev => ({ ...prev, estado_atencion: 'en espera' }));
          break;
        case 'ejecutada':
          setFormData(prev => ({ ...prev, estado_atencion: 'se presentó' }));
          break;
        case 'no ejecutada':
          setFormData(prev => ({ ...prev, estado_atencion: 'no se presentó' }));
          break;
        default:
          break;
      }
    }

    // Si el campo cambiado es el diagnóstico, actualizar el término de búsqueda
    if (name === 'diagnostico') {
      setTerminoBusquedaDiagnostico(value);
    }
  };

  const handleSelectDiagnostico = (diagnostico) => {
    // Al seleccionar un diagnóstico, actualizar el campo de diagnóstico con el display_text
    setFormData(prev => ({
      ...prev,
      diagnostico: diagnostico.display_text
    }));
    setTerminoBusquedaDiagnostico(diagnostico.display_text);
    setMostrarSugerencias(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      if (!agenda || !paciente || !user) {
        throw new Error('Datos incompletos para guardar la consulta');
      }

      const dataToSend = {
        agenda_id: parseInt(agendaId),
        paciente_id: paciente.id,
        centro_salud_id: user.centro_salud.id,
        ...formData
      };

      console.log('📤 Enviando datos al backend:', dataToSend);
      
      const response = await consultasAPI.saveConsulta(dataToSend);
      console.log('✅ Respuesta del backend:', response.data);
      
      await Notification.success('Consulta guardada exitosamente', '¡Éxito!');
      navigate('/agenda');
    } catch (error) {
      console.error('❌ Error al guardar la consulta:', error);
      setError(error.response?.data?.error || error.message || 'Error al guardar la consulta');
      Notification.error(
        error.response?.data?.error || error.message || 'Error al guardar la consulta',
        'Error');
    } finally {
      setSaving(false);
    }
  };

  // Manejar clic fuera del dropdown para cerrarlo
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!e.target.closest('.diagnostico-autocomplete')) {
        setMostrarSugerencias(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!agenda || !paciente) {
    return (
      <div className="consultation-container">
        <ErrorAlert error={error || "No se pudo cargar la agenda o los datos del paciente"} />
        <button 
          className="btn btn-secondary"
          onClick={() => navigate('/agenda')}
        >
          <i className="fas fa-arrow-left me-2"></i>Volver a la Agenda
        </button>
      </div>
    );
  }

  return (
    <div className="consultation-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Consulta Médica</h2>
        <button 
          className="btn btn-secondary"
          onClick={() => navigate('/agenda')}
        >
          <i className="fas fa-arrow-left me-2"></i>Volver
        </button>
      </div>

      {/* Información del Paciente */}
      <div className="patient-info">
        <h4 className="section-title">Datos del Paciente</h4>
        <div className="row">
          <div className="col-md-6">
            <label className="form-label">RUT</label>
            <p className="form-control-plaintext fw-bold">{paciente.rut}</p>
          </div>
          <div className="col-md-6">
            <label className="form-label">Nombre</label>
            <p className="form-control-plaintext fw-bold">{paciente.nombre} {paciente.apellido}</p>
          </div>
        </div>
        <div className="row">
          <div className="col-md-6">
            <label className="form-label">Teléfono</label>
            <p className="form-control-plaintext">{paciente.telefono}</p>
          </div>
          <div className="col-md-6">
            <label className="form-label">Edad</label>
            <p className="form-control-plaintext">{paciente.edad} años</p>
          </div>
        </div>
        <div className="row">
          <div className="col-md-6">
            <label className="form-label">Género</label>
            <p className="form-control-plaintext">
              {paciente.genero === 'M' ? 'Masculino' : paciente.genero === 'F' ? 'Femenino' : paciente.genero}
            </p>
          </div>
          <div className="col-md-6">
            <label className="form-label">Dirección</label>
            <p className="form-control-plaintext">{paciente.direccion}</p>
          </div>
        </div>
      </div>

      {/* Información de la Agenda */}
      <div className="agenda-info mb-4">
        <h4 className="section-title">Información de la Cita</h4>
        <div className="row">
          <div className="col-md-4">
            <label className="form-label">Fecha</label>
            <p className="form-control-plaintext">{agenda.fecha}</p>
          </div>
          <div className="col-md-4">
            <label className="form-label">Hora</label>
            <p className="form-control-plaintext">{agenda.hora}</p>
          </div>
          <div className="col-md-4">
            <label className="form-label">Médico</label>
            <p className="form-control-plaintext">{agenda.medico.nombre} {agenda.medico.apellido}</p>
          </div>
        </div>
        <div className="row">
          <div className="col-md-6">
            <label className="form-label">Centro de Salud</label>
            <p className="form-control-plaintext">{agenda.centro_salud.nombre}</p>
          </div>
          <div className="col-md-3">
            <label className="form-label">N° Ficha</label>
            <p className="form-control-plaintext">{agenda.n_ficha}</p>
          </div>
          <div className="col-md-3">
            <label className="form-label">N° Carpeta</label>
            <p className="form-control-plaintext">{agenda.n_carpeta}</p>
          </div>
        </div>
      </div>

      {/* Formulario de Consulta */}
      <form onSubmit={handleSubmit}>
        <div className="consultation-data">
          <h4 className="section-title">Datos de la Consulta</h4>
          
          <div className="row">
            <div className="col-md-3 mb-3">
              <label htmlFor="estado_hora" className="form-label">Estado Hora *</label>
              <select
                className="form-select"
                id="estado_hora"
                name="estado_hora"
                value={formData.estado_hora}
                onChange={handleChange}
                required
              >
                <option value="Asignada">Asignada</option>
                <option value="ejecutada">Ejecutada</option>
                <option value="no ejecutada">No Ejecutada</option>
              </select>
            </div>
            <div className="col-md-3 mb-3">
              <label htmlFor="estado_atencion" className="form-label">Estado Atención *</label>
              <select
                className="form-select"
                id="estado_atencion"
                name="estado_atencion"
                value={formData.estado_atencion}
                onChange={handleChange}
                required
              >
                <option value="en espera">En espera</option>
                <option value="se presentó">Se presentó</option>
                <option value="no se presentó">No se presentó</option>
              </select>
            </div>
            <div className="col-md-3 mb-3">
              <label htmlFor="modalidad_atencion" className="form-label">Modalidad Atención *</label>
              <select
                className="form-select"
                id="modalidad_atencion"
                name="modalidad_atencion"
                value={formData.modalidad_atencion}
                onChange={handleChange}
                required
              >
                <option value="presencial">Presencial</option>
                <option value="telemedicina">Telemedicina</option>
              </select>
            </div>
            <div className="col-md-3 mb-3">
              <label htmlFor="actividad" className="form-label">Actividad *</label>
              <select
                className="form-select"
                id="actividad"
                name="actividad"
                value={formData.actividad}
                onChange={handleChange}
                required
              >
                <option value="consulta">Consulta</option>
                <option value="control">Control</option>
                <option value="procedimiento">Procedimiento</option>
              </select>
            </div>
          </div>

          <div className="row">
            <div className="col-md-3 mb-3">
              <label htmlFor="tipo_alta" className="form-label">Tipo Alta *</label>
              <select
                className="form-select"
                id="tipo_alta"
                name="tipo_alta"
                value={formData.tipo_alta}
                onChange={handleChange}
                required
              >
                <option value="alta">Alta</option>
                <option value="derivacion">Derivación</option>
                <option value="seguimiento">Seguimiento</option>
              </select>
            </div>
            <div className="col-md-9 mb-3 diagnostico-autocomplete">
              <label htmlFor="diagnostico" className="form-label">Diagnóstico</label>
              <div className="position-relative">
                <input
                  type="text"
                  className="form-control"
                  id="diagnostico"
                  name="diagnostico"
                  value={formData.diagnostico}
                  onChange={handleChange}
                  placeholder="Ingrese el diagnóstico principal (empezar a escribir para buscar)"
                  autoComplete="off"
                  onFocus={() => {
                    if (terminoBusquedaDiagnostico.length >= 2 && sugerenciasDiagnosticos.length > 0) {
                      setMostrarSugerencias(true);
                    }
                  }}
                />
                {mostrarSugerencias && (
                  <div className="dropdown-menu show w-100" style={{ 
                    maxHeight: '300px', 
                    overflowY: 'auto',
                    zIndex: 1060 
                  }}>
                    {cargandoDiagnosticos ? (
                      <div className="dropdown-item text-muted">
                        <i className="fas fa-spinner fa-spin me-2"></i>
                        Buscando diagnósticos...
                      </div>
                    ) : sugerenciasDiagnosticos.length > 0 ? (
                      sugerenciasDiagnosticos.map(diagnostico => (
                        <button
                          key={diagnostico.id}
                          type="button"
                          className="dropdown-item"
                          onClick={() => handleSelectDiagnostico(diagnostico)}
                          style={{ cursor: 'pointer' }}
                        >
                          <div>
                            <strong>{diagnostico.display_text}</strong>
                            {diagnostico.categoria && (
                              <span className="badge bg-secondary ms-2">{diagnostico.categoria}</span>
                            )}
                            {diagnostico.relevancia && (
                              <small className="text-muted ms-2">({diagnostico.relevancia.toFixed(2)})</small>
                            )}
                          </div>
                        </button>
                      ))
                    ) : (
                      <div className="dropdown-item text-muted">
                        No se encontraron diagnósticos
                      </div>
                    )}
                  </div>
                )}
              </div>
              <small className="form-text text-muted">
                Comience a escribir para buscar en más de 32,000 diagnósticos. Los resultados se ordenan por relevancia.
              </small>
            </div>
          </div>

          <div className="row">
            <div className="col-12 mb-3">
              <label htmlFor="observaciones" className="form-label">Observaciones</label>
              <textarea
                className="form-control"
                id="observaciones"
                name="observaciones"
                rows="3"
                value={formData.observaciones}
                onChange={handleChange}
                placeholder="Observaciones adicionales, evolución, tratamiento, etc."
              ></textarea>
            </div>
          </div>
        </div>

        {/* Checkboxes de Clasificación */}
        <div className="checkbox-section">
          <h4 className="section-title">Clasificación de la Consulta</h4>
          <div className="checkbox-group">
            {[
              { id: 'ges', label: 'GES' },
              { id: 'ingreso_diag', label: 'Ingreso/diag' },
              { id: 'control_tto', label: 'Control/TTO' },
              { id: 'egreso', label: 'Egreso' },
              { id: 'pscv', label: 'PSCV' },
              { id: 'morbilidad', label: 'Morbilidad' },
              { id: 'psm', label: 'PSM' },
              { id: 'cns', label: 'CNS' },
              { id: 'lmp_lme', label: 'LMP/LME' },
              { id: 'consejeria_lm', label: 'Consejeria LM' },
              { id: 'embarazada', label: 'Embarazada' },
              { id: 'visita_domic', label: 'Visita Domic' },
              { id: 'dep_severa', label: 'Dep Severa' },
              { id: 'remoto', label: 'Remoto' }
            ].map(item => (
              <div className="form-check" key={item.id}>
                <input
                  className="form-check-input"
                  type="checkbox"
                  id={item.id}
                  name={item.id}
                  checked={formData[item.id]}
                  onChange={handleChange}
                />
                <label className="form-check-label" htmlFor={item.id}>
                  {item.label}
                </label>
              </div>
            ))}
          </div>
        </div>

        <ErrorAlert error={error} />

        <div className="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
          <button 
            type="button"
            className="btn btn-secondary me-2"
            onClick={() => navigate('/agenda')}
            disabled={saving}
          >
            Cancelar
          </button>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={saving}
          >
            {saving ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                Guardando...
              </>
            ) : (
              <>
                <i className="fas fa-save me-2"></i>
                Guardar Consulta
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ConsultationForm;