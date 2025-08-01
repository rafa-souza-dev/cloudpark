import { defineStore } from 'pinia';
import { ref } from 'vue';
import { ticketService } from '@/services/api';
import type { Ticket, TicketStatusUpdate } from '@/types';

export const useTicketStore = defineStore('tickets', () => {
    const tickets = ref<Ticket[]>([]);
    const currentTicket = ref<Ticket | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);

    const fetchTickets = async (params?: {
        status?: string;
        priority?: string;
        search?: string;
    }) => {
        loading.value = true;
        error.value = null;

        try {
            const data = await ticketService.getTickets(params);
            tickets.value = data;
        } catch (err: any) {
            error.value = err.response?.data?.error || 'Erro ao carregar tickets';
        } finally {
            loading.value = false;
        }
    };

    const fetchTicket = async (id: number) => {
        loading.value = true;
        error.value = null;

        try {
            const data = await ticketService.getTicket(id);
            currentTicket.value = data;
        } catch (err: any) {
            error.value = err.response?.data?.error || 'Erro ao carregar ticket';
        } finally {
            loading.value = false;
        }
    };

    const updateTicketStatus = async (id: number, statusUpdate: TicketStatusUpdate) => {
        loading.value = true;
        error.value = null;

        try {
            const updatedTicket = await ticketService.updateTicketStatus(id, statusUpdate);

            const index = tickets.value.findIndex(t => t.id === id);
            if (index !== -1) {
                tickets.value[index] = updatedTicket;
            }

            if (currentTicket.value?.id === id) {
                currentTicket.value = updatedTicket;
            }

            return { success: true };
        } catch (err: any) {
            error.value = err.response?.data?.error || 'Erro ao atualizar status';
            return { success: false, error: error.value };
        } finally {
            loading.value = false;
        }
    };

    const clearError = () => {
        error.value = null;
    };

    return {
        tickets,
        currentTicket,
        loading,
        error,
        fetchTickets,
        fetchTicket,
        updateTicketStatus,
        clearError,
    };
}); 