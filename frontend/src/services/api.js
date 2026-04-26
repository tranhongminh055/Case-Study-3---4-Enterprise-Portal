import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const api = axios.create({ baseURL, timeout: 10000 });

// initialize auth header if token present
const storedToken = localStorage.getItem('auth_token');
if (storedToken) api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;

// Add interceptor to always include token from localStorage
api.interceptors.request.use((config) => {
	const token = localStorage.getItem('auth_token');
	if (token) {
		config.headers.Authorization = `Bearer ${token}`;
	}
	return config;
});

export const setAuthToken = (token) => {
	if (token) {
		api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
		localStorage.setItem('auth_token', token);
	} else {
		delete api.defaults.headers.common['Authorization'];
		localStorage.removeItem('auth_token');
	}
};

export const getEmployees = () => api.get('/employees');
export const getEmployeesWithPayroll = () => api.get('/employees/with-payroll');
export const createEmployee = (payload) => api.post('/employees', payload);
export const updateEmployee = (id, payload) => api.put(`/employees/${id}`, payload);
export const deleteEmployee = (id) => api.delete(`/employees/${id}`);
export const getReports = () => api.get('/reports');
export const getAlerts = () => api.get('/alerts');
export const getSalaries = () => api.get('/salaries');
export const getAttendance = () => api.get('/attendance');
export const createSalary = (payload) => api.post('/salaries', payload);
export const updateSalary = (id, payload) => api.put(`/salaries/${id}`, payload);
export const deleteSalary = (id) => api.delete(`/salaries/${id}`);
export const createAttendance = (payload) => api.post('/attendance', payload);
export const updateAttendance = (id, payload) => api.put(`/attendance/${id}`, payload);
export const deleteAttendance = (id) => api.delete(`/attendance/${id}`);

export default api;
