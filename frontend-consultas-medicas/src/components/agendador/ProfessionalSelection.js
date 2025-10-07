import React, { useState, useEffect } from 'react';
import { agendadorAPI } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';

const ProfessionalSelection = ({ onProfessionalSelect }) => {
  const [especialidades, setEspecialidades] = useState([]);
  const [medicos, setMedicos] = useState([]);
  const [selectedEspecialidad, setSelectedEspecialidad] = useState('');
  const [selectedMedico, setSelectedMedico] = useState('');
  const [loadingEspecialidades, setLoadingEspecialidades] = useState(false);
  const [loadingMedicos, setLoadingMedicos] = useState(false);

  useEffect(() => {
    loadEspecialidades();
  }, []);

  useEffect(() => {
    if (selectedEspecialidad) {
      loadMedicosPorEspecialidad(selectedEspecialidad);
    } else {
      setMedicos([]);
      setSelectedMedico('');
    }
  }, [selectedEspecialidad]);

  const loadEspecialidades = async () => {
    setLoadingEspecialidades(true);
    try {
      const response = await agendadorAPI.getEspecialidades();
      setEspecialidades(response.data.especialidades);
    } catch (error) {
      console.error('Error cargando especialidades:', error);
    } finally {
      setLoadingEspecialidades(false);
    }
  };

  const loadMedicosPorEspecialidad = async (especialidad) => {
    setLoadingMedicos(true);
    try {
      const response = await agendadorAPI.getMedicosPorEspecialidad(especialidad);
      setMedicos(response.data.medicos);
    } catch (error) {
      console.error('Error cargando médicos:', error);
    } finally {
      setLoadingMedicos(false);
    }
  };

  const handleEspecialidadChange = (e) => {
    setSelectedEspecialidad(e.target.value);
  };

  const handleMedicoChange = (e) => {
    const medicoId = e.target.value;
    setSelectedMedico(medicoId);
    
    if (medicoId) {
      const medico = medicos.find(m => m.id == medicoId);
      onProfessionalSelect(medico);
    }
  };

  return (
    <div className="selection-container">
      <h3 className="section-title">Seleccione Profesional</h3>
      
      <div className="row">
        <div className="col-md-6 mb-3">
          <label htmlFor="especialidad" className="form-label">Especialidad</label>
          <select
            className="form-select"
            id="especialidad"
            value={selectedEspecialidad}
            onChange={handleEspecialidadChange}
            disabled={loadingEspecialidades}
          >
            <option value="">Seleccione especialidad</option>
            {especialidades.map(esp => (
              <option key={esp} value={esp}>{esp}</option>
            ))}
          </select>
          {loadingEspecialidades && (
            <div className="mt-2">
              <LoadingSpinner />
            </div>
          )}
        </div>
        
        <div className="col-md-6 mb-3">
          <label htmlFor="medico" className="form-label">Profesional</label>
          <select
            className="form-select"
            id="medico"
            value={selectedMedico}
            onChange={handleMedicoChange}
            disabled={!selectedEspecialidad || loadingMedicos}
          >
            <option value="">Seleccione profesional</option>
            {medicos.map(medico => (
              <option key={medico.id} value={medico.id}>
                {medico.nombre} {medico.apellido} - {medico.especialidad}
              </option>
            ))}
          </select>
          {loadingMedicos && (
            <div className="mt-2">
              <LoadingSpinner />
            </div>
          )}
        </div>
      </div>
      
      {selectedEspecialidad && medicos.length === 0 && !loadingMedicos && (
        <div className="alert alert-warning">
          No se encontraron profesionales para la especialidad seleccionada.
        </div>
      )}
    </div>
  );
};

export default ProfessionalSelection;