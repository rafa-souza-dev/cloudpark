import axios from 'axios';
import type { LoginCredentials, LoginResponse, Ticket, TicketStatusUpdate } from '@/types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
                        refresh_token: refreshToken,
                    });
                    localStorage.setItem('access_token', response.data.access_token);
                    error.config.headers.Authorization = `Bearer ${response.data.access_token}`;
                    return api.request(error.config);
                } catch (refreshError) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');
                    window.location.href = '/login';
                }
            }
        }
        return Promise.reject(error);
    }
);

export const authService = {
    async login(credentials: LoginCredentials): Promise<LoginResponse> {
        const response = await api.post('/auth/login/', credentials);
        return response.data;
    },

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },

    isAuthenticated(): boolean {
        return !!localStorage.getItem('access_token');
    },

    getCurrentUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    },
};

export const ticketService = {
    async getTickets(params?: {
        status?: string;
        priority?: string;
        search?: string;
    }): Promise<Ticket[]> {
        const response = await api.get('/tickets/', { params });
        return response.data.results || response.data;
    },

    async getTicket(id: number): Promise<Ticket> {
        const response = await api.get(`/tickets/${id}/`);
        return response.data;
    },

    async updateTicketStatus(id: number, statusUpdate: TicketStatusUpdate): Promise<Ticket> {
        const response = await api.patch(`/tickets/${id}/update_status/`, statusUpdate);
        return response.data;
    },
};

export default api; 