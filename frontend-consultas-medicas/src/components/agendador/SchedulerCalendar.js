import React, { useState } from 'react';

const SchedulerCalendar = ({ professional, onDateSelect, onCancel }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);

  const navigateMonth = (direction) => {
    const newMonth = new Date(currentMonth);
    newMonth.setMonth(currentMonth.getMonth() + direction);
    setCurrentMonth(newMonth);
  };

  const generateCalendarDays = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    const startDate = new Date(firstDay);
    startDate.setDate(firstDay.getDate() - firstDay.getDay());
    
    const endDate = new Date(lastDay);
    endDate.setDate(lastDay.getDate() + (6 - lastDay.getDay()));
    
    const days = [];
    const currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
      days.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return days;
  };

  const handleDateClick = (date) => {
    // No permitir seleccionar fechas pasadas
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (date >= today) {
      setSelectedDate(date);
      onDateSelect(date.toISOString().split('T')[0]);
    }
  };

  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isSelected = (date) => {
    return selectedDate && date.toDateString() === selectedDate.toDateString();
  };

  const isPast = (date) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  };

  const isCurrentMonth = (date) => {
    return date.getMonth() === currentMonth.getMonth();
  };

  const calendarDays = generateCalendarDays();
  const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

  return (
    <div className="calendar-container">
      <div className="calendar-header d-flex justify-content-between align-items-center mb-4">
        <button 
          className="btn btn-outline-primary btn-sm"
          onClick={() => navigateMonth(-1)}
        >
          <i className="fas fa-chevron-left"></i>
        </button>
        
        <h4 className="mb-0 text-center">
          {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </h4>
        
        <button 
          className="btn btn-outline-primary btn-sm"
          onClick={() => navigateMonth(1)}
        >
          <i className="fas fa-chevron-right"></i>
        </button>
      </div>

      <div className="row mb-2">
        {['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'].map(day => (
          <div key={day} className="col text-center fw-bold text-muted small">
            {day}
          </div>
        ))}
      </div>

      <div className="row">
        {calendarDays.map((date, index) => {
          const dayClass = [
            'col p-2 text-center calendar-day',
            isCurrentMonth(date) ? '' : 'text-muted',
            isToday(date) ? 'today' : '',
            isSelected(date) ? 'selected' : '',
            isPast(date) ? 'past' : ''
          ].filter(Boolean).join(' ');

          return (
            <div key={index} className="col-md-1 p-1">
              <div
                className={dayClass}
                onClick={() => !isPast(date) && handleDateClick(date)}
                style={{
                  cursor: isPast(date) ? 'not-allowed' : 'pointer',
                  opacity: isPast(date) ? 0.5 : 1
                }}
              >
                {date.getDate()}
              </div>
            </div>
          );
        })}
      </div>

      <div className="d-flex justify-content-between mt-4">
        <button className="btn btn-secondary" onClick={onCancel}>
          <i className="fas fa-arrow-left me-2"></i>Volver
        </button>
        
        {selectedDate && (
          <div className="text-success fw-bold">
            <i className="fas fa-calendar-check me-2"></i>
            Fecha seleccionada: {selectedDate.toLocaleDateString('es-ES')}
          </div>
        )}
      </div>
    </div>
  );
};

export default SchedulerCalendar;