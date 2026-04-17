import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './styles/main.css'

// Импорт компонентов
import LoginForm from './components/LoginForm.vue'
import Dashboard from './components/Dashboard.vue'
import AccountsList from './components/AccountsList.vue'
import CategoriesList from './components/CategoriesList.vue'
import TransactionsList from './components/TransactionsList.vue'
import TransferForm from './components/TransferForm.vue'
import DebtsList from './components/DebtsList.vue'
import Statistics from './components/Statistics.vue'

const routes = [
  { path: '/', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/login', component: LoginForm },
  { path: '/accounts', component: AccountsList, meta: { requiresAuth: true } },
  { path: '/categories', component: CategoriesList, meta: { requiresAuth: true } },
  { path: '/transactions', component: TransactionsList, meta: { requiresAuth: true } },
  { path: '/transfers', component: TransferForm, meta: { requiresAuth: true } },
  { path: '/debts', component: DebtsList, meta: { requiresAuth: true } },
  { path: '/statistics', component: Statistics, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
