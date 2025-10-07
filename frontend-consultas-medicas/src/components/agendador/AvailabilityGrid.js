import React from 'react';
import LoadingSpinner from '../common/LoadingSpinner';

const AvailabilityGrid = ({ professional, date, availableHours, onTimeSelect, onCancel, loading }) => {
  const generateTimeSlots = () => {
    const slots = [];
    for (let hour = 8; hour < 18; hour++) {
      for (let minute = 0; minute < 60; minute += 30) {
        const time = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        slots.push(time);
      }
    }
    return slots;
  };

  const allTimeSlots = generateTimeSlots();

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="hours-container">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="hours-container">
      <h3 className="section-title">
        Horarios Disponibles
      </h3>
      
      <div className="mb-4">
        <p className="mb-1">
          <strong>Profesional:</strong> {professional.nombre} {professional.apellido}
        </p>
        <p className="mb-1">
          <strong>Fecha:</strong> {formatDate(date)}
        </p>
        <p className="mb-0 text-muted">
          {availableHours.length} horarios disponibles
        </p>
      </div>

      <div className="row">
        {allTimeSlots.map(time => {
          const isAvailable = availableHours.includes(time);
          const timeEnd = `${(parseInt(time.split(':')[0]) + (time.endsWith('30') ? 1 : 0)).toString().padStart(2, '0')}:${time.endsWith('30') ? '00' : '30'}`;
          
          return (
            <div key={time} className="col-md-4 mb-3">
              <div
                className={`hour-block p-3 text-center ${
                  isAvailable ? 'available' : 'booked'
                }`}
                onClick={() => isAvailable && onTimeSelect(time)}
                style={{
                  cursor: isAvailable ? 'pointer' : 'not-allowed',
                  opacity: isAvailable ? 1 : 0.6
                }}
              >
                <div className="fw-bold">{time} - {timeEnd}</div>
                <small className={isAvailable ? 'text-success' : 'text-danger'}>
                  {isAvailable ? 'Disponible' : 'Ocupado'}
                </small>
                {isAvailable && (
                  <div className="mt-2">
                    <button className="btn btn-sm btn-primary">
                      Agendar
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {availableHours.length === 0 && (
        <div className="alert alert-warning text-center">
          <i className="fas fa-exclamation-triangle me-2"></i>
          No hay horarios disponibles para esta fecha.
        </div>
      )}

      <div className="d-flex justify-content-between mt-4">
        <button className="btn btn-secondary" onClick={onCancel}>
          <i className="fas fa-arrow-left me-2"></i>Volver
        </button>
        
        <div className="text-muted">
          Horario de atención: 8:00 - 18:00
        </div>
      </div>
    </div>
  );
};

export default AvailabilityGrid;