import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Profile from './components/Profile.vue'
import './styles/main.css'

import LoginForm from './components/LoginForm.vue'
import Dashboard from './components/Dashboard.vue'
import AccountsList from './components/AccountsList.vue'
import CategoriesList from './components/CategoriesList.vue'
import TransactionsList from './components/TransactionsList.vue'
import DebtsList from './components/DebtsList.vue'
import Statistics from './components/Statistics.vue'
import TimesheetsView from './components/TimesheetsView.vue'
import OAuthCallback from './components/OAuthCallback.vue'
import About from './components/About.vue'
import BudgetsView from './components/BudgetsView.vue'
import RecurringView from './components/RecurringView.vue'
import NotificationsView from './components/NotificationsView.vue'  // ← NEW

const routes = [
  { path: '/', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/login', component: LoginForm },
  { path: '/accounts', component: AccountsList, meta: { requiresAuth: true } },
  { path: '/categories', component: CategoriesList, meta: { requiresAuth: true } },
  { path: '/transactions', component: TransactionsList, meta: { requiresAuth: true } },
  { path: '/debts', component: DebtsList, meta: { requiresAuth: true } },
  { path: '/statistics', component: Statistics, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/timesheets', name: 'timesheets', component: TimesheetsView, meta: { requiresAuth: true } },
  { path: '/oauth-callback', component: OAuthCallback, meta: { requiresGuest: true } },
  { path: '/about', name: 'About', component: About, meta: { requiresAuth: true } },
  { path: '/budgets', name: 'Budgets', component: BudgetsView, meta: { requiresAuth: true } },
  { path: '/recurring', name: 'Recurring', component: RecurringView, meta: { requiresAuth: true } },
  { path: '/notifications', name: 'Notifications', component: NotificationsView, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

// Регистрация service worker (для push-уведомлений)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch((err) => {
      console.warn('Service Worker registration failed:', err)
    })
  })
}

const app = createApp(App)
app.use(router)
app.mount('#app')