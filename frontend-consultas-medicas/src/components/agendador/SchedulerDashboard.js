import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { agendadorAPI, pacientesAPI } from '../../services/api';
import ProfessionalSelection from './ProfessionalSelection';
import SchedulerCalendar from './SchedulerCalendar';
import AvailabilityGrid from './AvailabilityGrid';
import AppointmentForm from './AppointmentForm';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';
import { useLocation } from 'react-router-dom';

const SchedulerDashboard = () => {
  const { user } = useAuth();
  const location = useLocation();
  
  const [currentStep, setCurrentStep] = useState('selection'); // selection, calendar, hours, form
  const [selectedProfessional, setSelectedProfessional] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [availableHours, setAvailableHours] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [createdPatient, setCreatedPatient] = useState(null);

  // Efecto para manejar cuando volvemos con un paciente creado
  useEffect(() => {
    if (location.state?.patientCreated && currentStep === 'form') {
      const patient = location.state.patientCreated;
      setCreatedPatient(patient);
      console.log('✅ Paciente creado recibido:', patient);
      
      // Limpiar el estado de location para evitar procesarlo múltiples veces
      window.history.replaceState({}, document.title);
    }
  }, [location, currentStep]);

  // Resetear el proceso
  const resetProcess = () => {
    setCurrentStep('selection');
    setSelectedProfessional(null);
    setSelectedDate(null);
    setSelectedTime(null);
    setAvailableHours([]);
    setCreatedPatient(null);
  };

  // Manejar selección de profesional
  const handleProfessionalSelect = (professional) => {
    setSelectedProfessional(professional);
    setCurrentStep('calendar');
  };

  // Manejar selección de fecha
  const handleDateSelect = async (date) => {
    setSelectedDate(date);
    setLoading(true);
    
    try {
      // Obtener disponibilidad para el profesional y fecha seleccionados
      const response = await agendadorAPI.getDisponibilidad({
        usuario_id: selectedProfessional.id,
        centro_salud_id: user.centro_salud.id,
        fecha: date
      });
      
      setAvailableHours(response.data.horarios_disponibles);
      setCurrentStep('hours');
    } catch (error) {
      setError(error.response?.data?.error || 'Error al cargar disponibilidad');
    } finally {
      setLoading(false);
    }
  };

  // Manejar selección de hora
  const handleTimeSelect = (time) => {
    setSelectedTime(time);
    setCurrentStep('form');
  };

  // Manejar cancelación
  const handleCancel = () => {
    if (currentStep === 'form') {
      setCurrentStep('hours');
      setCreatedPatient(null);
    } else if (currentStep === 'hours') {
      setCurrentStep('calendar');
    } else if (currentStep === 'calendar') {
      resetProcess();
    }
  };

  // Manejar éxito del agendamiento
  const handleAppointmentSuccess = () => {
    resetProcess();
    // Aquí podrías mostrar un mensaje de éxito o recargar datos
    alert('Cita agendada exitosamente');
  };

  // Manejar cuando el AppointmentForm recibe el paciente creado
  const handlePatientCreated = (patient) => {
    setCreatedPatient(patient);
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'selection':
        return (
          <ProfessionalSelection 
            onProfessionalSelect={handleProfessionalSelect}
          />
        );
      
      case 'calendar':
        return (
          <SchedulerCalendar
            professional={selectedProfessional}
            onDateSelect={handleDateSelect}
            onCancel={handleCancel}
          />
        );
      
      case 'hours':
        return (
          <AvailabilityGrid
            professional={selectedProfessional}
            date={selectedDate}
            availableHours={availableHours}
            onTimeSelect={handleTimeSelect}
            onCancel={handleCancel}
            loading={loading}
          />
        );
      
      case 'form':
        return (
          <AppointmentForm
            professional={selectedProfessional}
            date={selectedDate}
            time={selectedTime}
            onSuccess={handleAppointmentSuccess}
            onCancel={handleCancel}
            createdPatient={createdPatient}
            onPatientCreated={handlePatientCreated}
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="main-container">
      {/* Indicador de pasos */}
      <div className="steps-indicator mb-4">
        <div className="d-flex justify-content-center">
          <div className={`step ${currentStep === 'selection' ? 'active' : ''}`}>
            <span className="step-number">1</span>
            <span className="step-label">Profesional</span>
          </div>
          <div className={`step ${currentStep === 'calendar' ? 'active' : ''}`}>
            <span className="step-number">2</span>
            <span className="step-label">Fecha</span>
          </div>
          <div className={`step ${currentStep === 'hours' ? 'active' : ''}`}>
            <span className="step-number">3</span>
            <span className="step-label">Hora</span>
          </div>
          <div className={`step ${currentStep === 'form' ? 'active' : ''}`}>
            <span className="step-number">4</span>
            <span className="step-label">Datos</span>
          </div>
        </div>
      </div>

      {renderCurrentStep()}
    </div>
  );
};

export default SchedulerDashboard;