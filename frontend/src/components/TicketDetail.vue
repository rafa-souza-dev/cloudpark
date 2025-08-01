<template>
  <div class="ticket-detail-container">
    <div class="header">
      <button @click="goBack" class="back-button">← Voltar</button>
      <button @click="logout" class="logout-button">Sair</button>
    </div>

    <div v-if="loading" class="loading">
      Carregando ticket...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="ticket" class="ticket-detail">
      <div class="ticket-header">
        <h1>{{ ticket.title }}</h1>
        <div class="ticket-badges">
          <span :class="['priority-badge', `priority-${ticket.priority}`]">
            {{ getPriorityLabel(ticket.priority) }}
          </span>
          <span :class="['status-badge', `status-${ticket.status}`]">
            {{ getStatusLabel(ticket.status) }}
          </span>
        </div>
      </div>

      <div class="ticket-info">
        <div class="info-section">
          <h3>Descrição</h3>
          <p v-if="ticket.description" class="description">
            {{ ticket.description }}
          </p>
          <p v-else class="no-description">
            Nenhuma descrição fornecida.
          </p>
        </div>

        <div class="info-section">
          <h3>Informações</h3>
          <div class="info-grid">
            <div class="info-item">
              <strong>Atendente:</strong>
              <span>{{ ticket.attendant.email }}</span>
            </div>
            <div class="info-item">
              <strong>Criado em:</strong>
              <span>{{ formatDate(ticket.created_at) }}</span>
            </div>
            <div class="info-item">
              <strong>Última atualização:</strong>
              <span>{{ formatDate(ticket.updated_at) }}</span>
            </div>
          </div>
        </div>

        <div class="info-section">
          <h3>Alterar Status</h3>
          <div class="status-update">
            <select v-model="newStatus" class="status-select">
              <option value="">Selecione um novo status</option>
              <option
                v-for="status in availableStatuses"
                :key="status.value"
                :value="status.value"
              >
                {{ status.label }}
              </option>
            </select>
            
            <button
              @click="updateStatus"
              :disabled="!newStatus || statusUpdating"
              class="update-button"
            >
              {{ statusUpdating ? 'Atualizando...' : 'Atualizar Status' }}
            </button>
          </div>
          
          <div v-if="statusError" class="status-error">
            {{ statusError }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useTicketStore } from '@/stores/tickets';
import type { Ticket } from '@/types';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const ticketStore = useTicketStore();

const newStatus = ref('');
const statusUpdating = ref(false);
const statusError = ref('');

const ticket = computed(() => ticketStore.currentTicket);
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
    hour: '2-digit',
    minute: '2-digit',
  });
};

const availableStatuses = computed(() => {
  if (!ticket.value) return [];
  
  const currentStatus = ticket.value.status;
  const transitions = {
    open: [
      { value: 'in_progress', label: 'Em Atendimento' },
      { value: 'canceled', label: 'Cancelado' },
    ],
    in_progress: [
      { value: 'resolved', label: 'Resolvido' },
      { value: 'canceled', label: 'Cancelado' },
    ],
    resolved: [
      { value: 'in_progress', label: 'Em Atendimento' },
    ],
    canceled: [
      { value: 'open', label: 'Aberto' },
    ],
  };
  
  return transitions[currentStatus as keyof typeof transitions] || [];
});

const updateStatus = async () => {
  if (!newStatus.value || !ticket.value) return;
  
  statusUpdating.value = true;
  statusError.value = '';
  
  const result = await ticketStore.updateTicketStatus(ticket.value.id, {
    status: newStatus.value as Ticket['status'],
  });
  
  if (result.success) {
    newStatus.value = '';
  } else {
    statusError.value = result.error || 'Erro ao atualizar status';
  }
  
  statusUpdating.value = false;
};

const goBack = () => {
  router.push('/tickets');
};

const logout = () => {
  authStore.logout();
  router.push('/login');
};

onMounted(() => {
  const ticketId = parseInt(route.params.id as string);
  if (ticketId) {
    ticketStore.fetchTicket(ticketId);
  }
});
</script>

<style scoped>
.ticket-detail-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.back-button, .logout-button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.back-button {
  background: #6c757d;
  color: white;
}

.back-button:hover {
  background: #5a6268;
}

.logout-button {
  background: #dc3545;
  color: white;
}

.logout-button:hover {
  background: #c82333;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
}

.error {
  color: #dc3545;
}

.ticket-detail {
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 30px;
}

.ticket-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e1e5e9;
}

.ticket-header h1 {
  margin: 0;
  color: #333;
  font-size: 24px;
  flex: 1;
  margin-right: 20px;
}

.ticket-badges {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.priority-badge, .status-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
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

.ticket-info {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.info-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.description {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.no-description {
  color: #999;
  font-style: italic;
  margin: 0;
}

.info-grid {
  display: grid;
  gap: 12px;
}

.info-item {
  display: flex;
  gap: 10px;
}

.info-item strong {
  min-width: 120px;
  color: #333;
}

.info-item span {
  color: #666;
}

.status-update {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.status-select {
  padding: 10px 12px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 14px;
  min-width: 200px;
}

.status-select:focus {
  outline: none;
  border-color: #667eea;
}

.update-button {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.update-button:hover:not(:disabled) {
  background: #218838;
}

.update-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.status-error {
  background: #fee;
  color: #c53030;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  border: 1px solid #fecaca;
  margin-top: 10px;
}
</style> 