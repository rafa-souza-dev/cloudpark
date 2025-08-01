<template>
  <div class="ticket-list-container">
    <div class="header">
      <h1>Chamados</h1>
      <button @click="logout" class="logout-button">Sair</button>
    </div>

    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Buscar tickets..."
          @input="handleSearch"
        />
      </div>
      
      <div class="filter-buttons">
        <button
          v-for="status in statusOptions"
          :key="status.value"
          @click="filterByStatus(status.value)"
          :class="['filter-button', { active: selectedStatus === status.value }]"
        >
          {{ status.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      Carregando tickets...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="tickets.length === 0" class="empty-state">
      Nenhum ticket encontrado.
    </div>

    <div v-else class="tickets-grid">
      <div
        v-for="ticket in tickets"
        :key="ticket.id"
        class="ticket-card"
        @click="viewTicket(ticket.id)"
      >
        <div class="ticket-header">
          <h3 class="ticket-title">{{ ticket.title }}</h3>
          <div class="ticket-badges">
            <span :class="['priority-badge', `priority-${ticket.priority}`]">
              {{ getPriorityLabel(ticket.priority) }}
            </span>
            <span :class="['status-badge', `status-${ticket.status}`]">
              {{ getStatusLabel(ticket.status) }}
            </span>
          </div>
        </div>
        
        <p v-if="ticket.description" class="ticket-description">
          {{ ticket.description }}
        </p>
        
        <div class="ticket-footer">
          <span class="ticket-date">
            {{ formatDate(ticket.created_at) }}
          </span>
          <span class="ticket-attendant">
            {{ ticket.attendant.email }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useTicketStore } from '@/stores/tickets';
import type { Ticket } from '@/types';

const router = useRouter();
const authStore = useAuthStore();
const ticketStore = useTicketStore();

const searchTerm = ref('');
const selectedStatus = ref('');

const statusOptions = [
  { value: '', label: 'Todos' },
  { value: 'open', label: 'Abertos' },
  { value: 'in_progress', label: 'Em Atendimento' },
  { value: 'resolved', label: 'Resolvidos' },
  { value: 'canceled', label: 'Cancelados' },
];

const tickets = computed(() => ticketStore.tickets);
const loading = computed(() => ticketStore.loading);
const error = computed(() => ticketStore.error);

const getPriorityLabel = (priority: string) => {
  const labels = {
    low: 'Baixa',
    medium: 'Média',
    high: 'Alta',
    critical: 'Crítica',
  };
  return labels[priority as keyof typeof labels] || priority;
};

const getStatusLabel = (status: string) => {
  const labels = {
    open: 'Aberto',
    in_progress: 'Em Atendimento',
    resolved: 'Resolvido',
    canceled: 'Cancelado',
  };
  return labels[status as keyof typeof labels] || status;
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

const handleSearch = () => {
  fetchTickets();
};

const filterByStatus = (status: string) => {
  selectedStatus.value = status;
  fetchTickets();
};

const fetchTickets = () => {
  const params: any = {};
  if (searchTerm.value) params.search = searchTerm.value;
  if (selectedStatus.value) params.status = selectedStatus.value;
  
  ticketStore.fetchTickets(params);
};

const viewTicket = (id: number) => {
  router.push(`/tickets/${id}`);
};

const logout = () => {
  authStore.logout();
  router.push('/login');
};

onMounted(() => {
  fetchTickets();
});

watch([searchTerm], () => {
  fetchTickets();
});
</script>

<style scoped>
.ticket-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h1 {
  margin: 0;
  color: #333;
  font-size: 28px;
}

.logout-button {
  background: #dc3545;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.logout-button:hover {
  background: #c82333;
}

.filters {
  margin-bottom: 30px;
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box input {
  padding: 10px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 14px;
  width: 300px;
}

.search-box input:focus {
  outline: none;
  border-color: #667eea;
}

.filter-buttons {
  display: flex;
  gap: 10px;
}

.filter-button {
  padding: 8px 16px;
  border: 2px solid #e1e5e9;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.filter-button:hover {
  border-color: #667eea;
}

.filter-button.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.loading, .error, .empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
}

.error {
  color: #dc3545;
}

.tickets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.ticket-card {
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ticket-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.ticket-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.ticket-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
  margin-right: 12px;
}

.ticket-badges {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.priority-badge, .status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.priority-low {
  background: #d4edda;
  color: #155724;
}

.priority-medium {
  background: #fff3cd;
  color: #856404;
}

.priority-high {
  background: #f8d7da;
  color: #721c24;
}

.priority-critical {
  background: #f5c6cb;
  color: #721c24;
}

.status-open {
  background: #cce5ff;
  color: #004085;
}

.status-in_progress {
  background: #fff3cd;
  color: #856404;
}

.status-resolved {
  background: #d4edda;
  color: #155724;
}

.status-canceled {
  background: #f8d7da;
  color: #721c24;
}

.ticket-description {
  color: #666;
  font-size: 14px;
  margin: 12px 0;
  line-height: 1.4;
}

.ticket-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
  margin-top: 12px;
}

.ticket-date {
  font-weight: 500;
}

.ticket-attendant {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style> 