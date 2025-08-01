import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginForm from '@/components/LoginForm.vue'
import TicketList from '@/components/TicketList.vue'
import TicketDetail from '@/components/TicketDetail.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginForm,
      meta: { requiresAuth: false }
    },
    {
      path: '/tickets',
      name: 'tickets',
      component: TicketList,
      meta: { requiresAuth: true }
    },
    {
      path: '/tickets/:id',
      name: 'ticket-detail',
      component: TicketDetail,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/tickets')
  } else {
    next()
  }
})

export default router
