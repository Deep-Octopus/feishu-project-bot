import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

export const projectsApi = {
  list: () => api.get('/projects/'),
  create: (data) => api.post('/projects/', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
  get: (id) => api.get(`/projects/${id}`),
}

export const tasksApi = {
  list: (projectId) => api.get('/tasks/', { params: { project_id: projectId } }),
  create: (data) => api.post('/tasks/', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
}

export const reportsApi = {
  list: (params) => api.get('/reports/', { params }),
}

export const statisticsApi = {
  overview: (projectId) => api.get('/statistics/overview', { params: { project_id: projectId } }),
  stats: (projectId, period) => api.get('/statistics/stats', { params: { project_id: projectId, period } }),
  weekly: (projectId) => api.get('/statistics/weekly', { params: { project_id: projectId } }),
}

export const configApi = {
  get: () => api.get('/config/'),
}
