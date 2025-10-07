import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Interceptor para agregar el token a las requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  getCentros: () => api.get('/auth/centros'),
  logout: () => api.post('/auth/logout'),
};

export const agendasAPI = {
  getDailyAgenda: (centroSaludId, fecha) => 
    api.get('/agendas/dia', { params: { centro_salud_id: centroSaludId, fecha } }),
  getAgendaDetail: (agendaId) => api.get(`/agendas/${agendaId}`),
  updateAgendaStatus: (agendaId, estado) => 
    api.put(`/agendas/${agendaId}/estado`, { estado }),
};

export const consultasAPI = {
  getConsultaDetail: (agendaId) => api.get(`/consultas/detalle/${agendaId}`),
  saveConsulta: (data) => api.post('/consultas/guardar', data),
  sugerirDiagnosticos: (termino, limite = 10) => 
    api.get('/consultas/diagnostico/sugerir', { params: { q: termino, limit: limite } }),
};

export const diagnosticosAPI = {
  buscar: (termino, limite = 20) => 
    api.get('/diagnosticos/buscar', { params: { q: termino, limit: limite } }),
  obtenerSugerencias: (limite = 50) => 
    api.get('/diagnosticos/sugerencias', { params: { limit: limite } }),
  obtenerCategorias: () => api.get('/diagnosticos/categorias'),
  obtenerPorCodigo: (codigo) => api.get(`/diagnosticos/por-codigo/${codigo}`),
  obtenerPorId: (id) => api.get(`/diagnosticos/${id}`),
};

export const pacientesAPI = {
  search: (apellido = '', rut = '') => {
    const params = {};
    if (apellido) params.apellido = apellido;
    if (rut) params.rut = rut;
    
    return api.get('/pacientes/buscar', { params });
  },
  create: (pacienteData) => api.post('/pacientes/', pacienteData)
};

export const agendadorAPI = {
  getAgendas: (params) => api.get('/agendador/agendas', { params }),
  createAgenda: (data) => api.post('/agendador/agendas', data),
  updateAgenda: (agendaId, data) => api.put(`/agendador/agendas/${agendaId}`, data),
  cancelAgenda: (agendaId) => api.delete(`/agendador/agendas/${agendaId}`),
  getDisponibilidad: (params) => api.get('/agendador/disponibilidad', { params }),
  getMedicos: (params) => api.get('/agendador/medicos', { params }),
  getEspecialidades: () => api.get('/agendador/especialidades'),
  getMedicosPorEspecialidad: (especialidad) => 
    api.get('/agendador/medicos-especialidad', { params: { especialidad } }),
};

export const usuariosAPI = {
  create: (data) => api.post('/usuarios/usuarios', data),
  list: (params) => api.get('/usuarios/usuarios', { params }),
  createAdmin: (data) => api.post('/usuarios/create-admin', data),
};

export default api;