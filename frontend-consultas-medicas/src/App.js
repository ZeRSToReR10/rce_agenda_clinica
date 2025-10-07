import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './components/auth/Login';
import DailyAgenda from './components/agenda/DailyAgenda';
import ConsultationForm from './components/consultas/ConsultationForm';
import SchedulerDashboard from './components/agendador/SchedulerDashboard';
import PrivateRoute from './components/auth/PrivateRoute';
import Layout from './components/common/Layout';
import './App.css';
import PatientForm from './components/patients/PatientForm';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<Login />} />
            
            {/* Rutas para health-worker */}
            <Route path="/agenda" element={
              <PrivateRoute requiredRole="health-worker">
                <Layout>
                  <DailyAgenda />
                </Layout>
              </PrivateRoute>
            } />
            
            <Route path="/consulta/:agendaId" element={
              <PrivateRoute requiredRole="health-worker">
                <Layout>
                  <ConsultationForm />
                </Layout>
              </PrivateRoute>
            } />

            {/* Rutas para agendador */}
            <Route path="/agendador" element={
              <PrivateRoute requiredRole="scheduler">
                <Layout>
                  <SchedulerDashboard />
                </Layout>
              </PrivateRoute>
            } />

            {/* Ruta para crear nuevo paciente */}
            <Route path="/pacientes/nuevo" element={
              <PrivateRoute requiredRole="scheduler">
                <Layout>
                  <PatientForm />
                </Layout>
              </PrivateRoute>
            } />

            {/* Ruta por defecto */}
            <Route path="/" element={<Navigate to="/login" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;