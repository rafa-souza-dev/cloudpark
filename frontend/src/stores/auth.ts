import { defineStore } from 'pinia';
import { ref } from 'vue';
import { authService } from '@/services/api';
import type { User, LoginCredentials } from '@/types';

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null);
    const isAuthenticated = ref(false);

    const initializeAuth = () => {
        const savedUser = localStorage.getItem('user');
        if (savedUser && authService.isAuthenticated()) {
            user.value = JSON.parse(savedUser);
            isAuthenticated.value = true;
        }
    };

    const login = async (credentials: LoginCredentials) => {
        try {
            const response = await authService.login(credentials);

            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token);
            localStorage.setItem('user', JSON.stringify(response.user));

            user.value = response.user;
            isAuthenticated.value = true;

            return { success: true };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.error || 'Erro ao fazer login'
            };
        }
    };

    const logout = () => {
        authService.logout();
        user.value = null;
        isAuthenticated.value = false;
    };

    const isTechnician = () => {
        return user.value?.profile === 'technician';
    };

    initializeAuth();

    return {
        user,
        isAuthenticated,
        login,
        logout,
        isTechnician,
    };
}); 