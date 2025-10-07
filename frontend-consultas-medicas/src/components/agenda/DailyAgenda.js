import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { agendasAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';

const DailyAgenda = () => {
  const [agendas, setAgendas] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.centro_salud?.id) {
      loadAgendas();
    }
  }, [user, selectedDate]);

  const loadAgendas = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await agendasAPI.getDailyAgenda(
        user.centro_salud.id,
        selectedDate
      );
      console.log('📊 Agendas cargadas:', response.data.agendas);
      setAgendas(response.data.agendas);
    } catch (error) {
      setError(error.response?.data?.error || 'Error al cargar agendas');
      console.error('Error cargando agendas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
  };

  const handleEditConsulta = (agendaId) => {
    navigate(`/consulta/${agendaId}`);
  };

  const getEstadoBadge = (estado) => {
    const estados = {
      'agendada': 'primary',
      'completada': 'success',
      'cancelada': 'danger'
    };
    return <span className={`badge bg-${estados[estado] || 'secondary'}`}>{estado}</span>;
  };

  return (
    <div>
      <div className="row mb-3">
        <div className="col-md-4">
          <label htmlFor="fecha" className="form-label">Seleccione la fecha:</label>
          <input
            type="date"
            className="form-control"
            id="fecha"
            value={selectedDate}
            onChange={handleDateChange}
          />
        </div>
      </div>

      <ErrorAlert error={error} />

      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="table-responsive">
          <table className="table table-bordered table-hover">
            <thead className="table-dark">
              <tr>
                <th>Acción</th>
                <th>Estado Agenda</th>
                <th>Hora</th>
                <th>Estado Atención</th>
                <th>Modalidad de Atención</th>
                <th>Nombre y Apellido</th>
                <th>Nº Ficha</th>
                <th>Nº Carpeta</th>
              </tr>
            </thead>
            <tbody>
              {agendas.map(agenda => (
                <tr key={agenda.agenda_id}>
                  <td>
                     <button
                        className="btn btn-consultation"
                        onClick={() => handleEditConsulta(agenda.agenda_id)}
                        disabled={agenda.estado_agenda === 'completada'}
                        title={
                          agenda.estado_agenda === 'completada'
                            ? 'Consulta ya completada'
                            : agenda.estado_agenda === 'cancelada'
                            ? 'Consulta cancelada'
                            : 'Atender consulta'
                        }
                      >
                        <i className="fas fa-stethoscope"></i>
                        Atender
                      </button>
                  </td>
                  <td>{getEstadoBadge(agenda.estado_agenda)}</td>
                  <td>{agenda.hora}</td>
                  <td>
                    {agenda.consulta && agenda.consulta.estado_atencion ? (
                      <span className={`badge bg-${
                        agenda.consulta.estado_atencion === 'se presentó' ? 'success' : 
                        agenda.consulta.estado_atencion === 'no se presentó' ? 'danger' : 'warning'
                      }`}>
                        {agenda.consulta.estado_atencion}
                      </span>
                    ) : (
                      <span className="badge bg-secondary">N/A</span>
                    )}
                  </td>
                  <td>
                    {agenda.consulta && agenda.consulta.modalidad_atencion ? (
                      <span className="badge bg-info text-dark">{agenda.consulta.modalidad_atencion}</span>
                    ) : (
                      <span className="badge bg-secondary">N/A</span>
                    )}
                  </td>
                  <td>
                    <strong>{agenda.paciente.nombre} {agenda.paciente.apellido}</strong>
                    <br />
                    <small className="text-muted">{agenda.paciente.rut}</small>
                  </td>
                  <td>{agenda.n_ficha}</td>
                  <td>{agenda.n_carpeta}</td>
                </tr>
              ))}
              {agendas.length === 0 && (
                <tr>
                  <td colSpan="8" className="text-center text-muted py-4">
                    <i className="fas fa-calendar-times fa-2x mb-2"></i>
                    <br />
                    No hay agendas para esta fecha
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default DailyAgenda;