export interface User {
    id: number;
    email: string;
    profile: 'attendant' | 'technician';
    is_staff: boolean;
    is_superuser: boolean;
}

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    user: User;
}

export interface Ticket {
    id: number;
    title: string;
    priority: 'low' | 'medium' | 'high' | 'critical';
    status: 'open' | 'in_progress' | 'resolved' | 'canceled';
    description: string | null;
    attendant: User;
    created_at: string;
    updated_at: string;
}

export interface TicketStatusUpdate {
    status: Ticket['status'];
}

export interface LoginCredentials {
    email: string;
    password: string;
} 