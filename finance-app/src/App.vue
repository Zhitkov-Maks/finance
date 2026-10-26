<template>
  <div class="app">
    <!-- Мобильная кнопка меню -->
    <button class="mobile-menu-btn" @click="toggleMobileMenu" v-if="isMobile">
      <i class="fas" :class="mobileMenuOpen ? 'fa-times' : 'fa-bars'"></i>
    </button>

    <div class="sidebar" :class="{ 'mobile-open': mobileMenuOpen }">
      <div class="sidebar-header">
        <div class="logo-wrapper">
          <span class="logo-icon">💰</span>
          <h2>Финансы</h2>
        </div>
      </div>

      <nav class="nav-menu">
        <div class="nav-group">
          <router-link to="/" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-tachometer-alt"></i>
            <span>Дашборд</span>
          </router-link>

          <router-link to="/timesheets" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-calendar-alt"></i>
            <span>Мой график</span>
          </router-link>

          <router-link to="/accounts" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-credit-card"></i>
            <span>Счета</span>
          </router-link>

          <router-link to="/budgets" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-wallet"></i>
            <span>Бюджеты</span>
          </router-link>

          <router-link to="/categories" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-tags"></i>
            <span>Категории</span>
          </router-link>

          <router-link to="/transactions" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-exchange-alt"></i>
            <span>Транзакции</span>
          </router-link>

          <router-link to="/recurring" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-redo"></i>
            <span>Регулярные</span>
          </router-link>

          <router-link to="/debts" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-hand-holding-usd"></i>
            <span>Долги</span>
          </router-link>

          <router-link to="/statistics" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-chart-line"></i>
            <span>Статистика</span>
          </router-link>

          <router-link to="/profile" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-user-circle"></i>
            <span>Профиль</span>
          </router-link>

          <router-link to="/notifications" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-bell"></i>
            <span>Уведомления</span>
            <span v-if="unreadCount > 0" class="nav-badge">
              {{ unreadCount > 99 ? '99+' : unreadCount }}
            </span>
          </router-link>

          <router-link to="/about" class="nav-item" @click="closeMobileMenu">
            <i class="fas fa-info-circle"></i>
            <span>О приложении</span>
          </router-link>
        </div>

        <div class="nav-footer">
          <button @click="toggleTheme" class="nav-item theme-toggle-btn">
            <i class="fas" :class="isDarkMode ? 'fa-sun' : 'fa-moon'"></i>
            <span>{{ isDarkMode ? 'Светлая тема' : 'Тёмная тема' }}</span>
          </button>

          <button @click="logout" class="nav-item logout-btn">
            <i class="fas fa-sign-out-alt"></i>
            <span>Выйти</span>
          </button>
        </div>
      </nav>
    </div>

    <!-- Оверлей для мобильного меню -->
    <div v-if="mobileMenuOpen" class="mobile-overlay" @click="closeMobileMenu"></div>

    <div class="main-content">
      <div class="top-bar" v-if="!isMobile">
        <div class="user-menu" @click="goToProfile">
          <i class="fas fa-user-circle"></i>
          <span>Профиль</span>
        </div>
      </div>
      <router-view />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from './services/api.js'
import { notificationStore } from './stores/notifications.js'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const mobileMenuOpen = ref(false)
    const isMobile = ref(window.innerWidth <= 768)
    const unreadCount = computed(() => notificationStore.unreadCount)

    const isDarkMode = ref(false)

    const applyTheme = (dark) => {
      if (dark) {
        document.documentElement.setAttribute('data-theme', 'dark')
        localStorage.setItem('theme', 'dark')
      } else {
        document.documentElement.removeAttribute('data-theme')
        localStorage.setItem('theme', 'light')
      }
      isDarkMode.value = dark
    }

    const toggleTheme = () => applyTheme(!isDarkMode.value)

    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value
      document.body.style.overflow = mobileMenuOpen.value ? 'hidden' : ''
    }

    const closeMobileMenu = () => {
      mobileMenuOpen.value = false
      document.body.style.overflow = ''
    }

    const handleResize = () => {
      isMobile.value = window.innerWidth <= 768
      if (!isMobile.value) closeMobileMenu()
    }

    const goToProfile = () => {
      router.push('/profile')
      closeMobileMenu()
    }

    const logout = async () => {
      try {
        await apiService.logout()
        localStorage.clear()
        sessionStorage.clear()
        await router.push('/login')
        window.location.href = '/login'
      } catch (error) {
        console.error('Logout error:', error)
        localStorage.clear()
        sessionStorage.clear()
        window.location.href = '/login'
      }
    }

    const handleVisibilityChange = () => {
      if (document.hidden) {
        notificationStore.stopPolling()
      } else {
        notificationStore.startPolling(60000)
      }
    }

    onMounted(() => {
      const savedTheme = localStorage.getItem('theme')
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      applyTheme(savedTheme === 'dark' || (!savedTheme && prefersDark))

      window.addEventListener('resize', handleResize)
      document.addEventListener('visibilitychange', handleVisibilityChange)

      const token = localStorage.getItem('auth_token')
      if (token) notificationStore.startPolling(60000)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      notificationStore.stopPolling()
      document.body.style.overflow = ''
    })

    return {
      mobileMenuOpen, isMobile, unreadCount, isDarkMode,
      toggleTheme, toggleMobileMenu, closeMobileMenu, goToProfile, logout
    }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

/* ============================================================
   ПЕРЕМЕННЫЕ (Светлая тема по умолчанию)
   ============================================================ */
:root {
  --primary-color: #101010;
  --secondary-color: #10b981;
  --danger-color: #ef4444;
  --warning-color: #f59e0b;
  --dark-color: #12135b; /* Основной цвет текста */
  --gray-color: #6b7280; /* Второстепенный текст */
  --light-color: #f3f4f6; /* Фон/бордеры */
  --white: #ffffff;      /* Фон карточек */
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  --radius: 8px;

  /* Переменные для лейаута */
  --bg-body: #f5f5f5;
  --sidebar-bg: #0f172a; /* Глубокий сине-серый (как в Vercel/Linear) */
  --sidebar-hover: rgba(255, 255, 255, 0.05);
  --sidebar-text: #94a3b8;
  --topbar-bg: #ffffff;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: var(--bg-body);
  color: var(--dark-color);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.app { display: flex; min-height: 100vh; position: relative; }

/* ============================================================
   МОБИЛЬНАЯ КНОПКА
   ============================================================ */
.mobile-menu-btn {
  position: fixed; top: 1rem; left: 1rem; z-index: 1000;
  background: #1e293b; color: white; border: 1px solid rgba(255,255,255,0.1);
  width: 45px; height: 45px; border-radius: 12px; cursor: pointer;
  display: none; align-items: center; justify-content: center;
  font-size: 1.25rem; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* ============================================================
   САЙДБАР (СУПЕР-СОВРЕМЕННЫЙ)
   ============================================================ */
.sidebar {
  width: 260px;
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 100;
  transition: transform 0.3s ease, background-color 0.3s ease;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Красивый скроллбар внутри сайдбара */
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

.sidebar-header {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  font-size: 1.5rem;
  filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.4));
}

.sidebar-header h2 {
  font-size: 1.25rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
  background: linear-gradient(to right, #ffffff, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ============================================================
   НАВИГАЦИЯ
   ============================================================ */
.nav-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem 0.75rem;
  gap: 0.25rem;
}

.nav-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.65rem 1rem;
  color: var(--sidebar-text);
  text-decoration: none;
  border-radius: 10px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
  font-size: 0.9rem;
  font-weight: 500;
  position: relative;
}

.nav-item i {
  font-size: 1.1rem;
  width: 22px;
  text-align: center;
  transition: transform 0.25s ease, color 0.25s ease;
}

/* Эффект при наведении */
.nav-item:hover {
  background: var(--sidebar-hover);
  color: #ffffff;
}

.nav-item:hover i {
  transform: scale(1.15);
  color: #3b82f6;
}

/* АКТИВНЫЙ ЭЛЕМЕНТ (Красивая капсула с градиентом) */
.nav-item.router-link-active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.nav-item.router-link-active i {
  color: #ffffff;
}

/* ============================================================
   БЕЙДЖ УВЕДОМЛЕНИЙ (С пульсацией)
   ============================================================ */
.nav-badge {
  margin-left: auto;
  background: #ef4444;
  color: white;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  min-width: 20px;
  text-align: center;
  line-height: 1.4;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.6);
  animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
  70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

/* ============================================================
   НИЖНЯЯ ПАНЕЛЬ (Тема и Выход)
   ============================================================ */
.nav-footer {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding-top: 1rem;
  margin-top: auto;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.theme-toggle-btn {
  color: #fbbf24;
}
.theme-toggle-btn:hover {
  background: rgba(251, 191, 36, 0.1);
  color: #fcd34d;
}

.logout-btn {
  color: #f87171;
  margin-top: 0.25rem;
}
.logout-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* ============================================================
   ОСНОВНОЙ КОНТЕНТ
   ============================================================ */
.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 2rem;
  width: calc(100% - 260px);
  transition: background-color 0.3s ease;
}

.top-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--white);
  border-radius: 9999px; /* Круглые кнопки */
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: var(--shadow);
  border: 1px solid var(--light-color);
}

.user-menu:hover {
  background: var(--light-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.user-menu i {
  font-size: 1.25rem;
  color: var(--primary-color);
}

/* ============================================================
   МОБИЛЬНАЯ ВЕРСИЯ
   ============================================================ */
@media (max-width: 768px) {
  .mobile-menu-btn { display: flex; }

  .sidebar {
    transform: translateX(-100%);
    width: 280px;
    box-shadow: 10px 0 30px rgba(0,0,0,0.5);
  }

  .sidebar.mobile-open { transform: translateX(0); }

  .main-content {
    margin-left: 0;
    padding: 1rem;
    padding-top: 4.5rem;
    width: 100%;
  }

  .mobile-overlay {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px); /* Размытие под оверлеем */
    z-index: 99;
  }
}

/* ============================================================
   ОБЩИЕ СТИЛИ (Карточки, кнопки, формы и т.д.)
   ============================================================ */
.card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
  transition: background-color 0.3s ease;
}

.modal-content {
  background: var(--white);
  border-radius: var(--radius);
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  transition: background-color 0.3s ease;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary { background: var(--primary-color); color: white; }
.btn-primary:hover { background: #4338ca; }
.btn-secondary { background: #6b7280; color: white; }
.btn-secondary:hover { background: #4b5563; }
.btn-success { background: var(--secondary-color); color: white; }
.btn-success:hover { background: #059669; }
.btn-danger { background: var(--danger-color); color: white; }
.btn-danger:hover { background: #dc2626; }
.btn-info { background: #3b82f6; color: white; }
.btn-info:hover { background: #2563eb; }
.btn-sm { padding: 0.25rem 0.75rem; font-size: 0.75rem; }

.form-group { margin-bottom: 1rem; }
.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--dark-color);
}
.form-label.required:after { content: " *"; color: var(--danger-color); }

.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--gray-color);
  border-radius: var(--radius);
  font-size: 0.875rem;
  transition: border-color 0.3s, background-color 0.3s;
  background: var(--white);
  color: var(--dark-color);
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
}

textarea.form-control {
  resize: vertical;
  min-height: 60px;
}

.table { width: 100%; border-collapse: collapse; }
.table th, .table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--light-color);
  color: var(--dark-color);
}
.table th {
  font-weight: 600;
  background: var(--light-color);
}

.modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--light-color);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--gray-color);
  transition: color 0.3s;
}

.modal-close:hover { color: var(--dark-color); }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--light-color);
}

.text-success { color: var(--secondary-color); }
.text-danger { color: var(--danger-color); }
.text-center { text-align: center; }

.alert { padding: 0.75rem 1rem; border-radius: var(--radius); margin-bottom: 1rem; }
.alert-info { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
.alert-danger { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
.alert-warning { background: #fed7aa; color: #92400e; border: 1px solid #fed7aa; }

/* Адаптивность */
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr !important; gap: 1rem; }
  .stat-card { padding: 1rem; }
  .stat-value { font-size: 1.5rem; }
  .quick-actions { flex-direction: column; }
  .quick-actions .btn { width: 100%; justify-content: center; }
  .table-responsive { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .table { min-width: 600px; }
  .card { padding: 1rem; }
  .card-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
  .card-header .btn { width: 100%; }
  .modal-content { width: 95%; margin: 1rem; max-height: 85vh; }
  .form-group select, .form-group input, .form-group textarea { font-size: 16px; }
  .filters { grid-template-columns: 1fr !important; gap: 1rem; }
  .page-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
  .page-header h1 { font-size: 1.5rem; }
  .page-header .btn { width: 100%; }
  .type-tabs { flex-direction: column; }
  .tab-btn { width: 100%; }
  .action-buttons { flex-direction: column; }
  .action-buttons .btn-sm { width: 100%; }
  .pagination { flex-direction: column; gap: 0.5rem; }
  .pagination button { width: 100%; }
}

@media (max-width: 480px) {
  .main-content { padding: 0.75rem; padding-top: 4.5rem; }
  .stat-value { font-size: 1.25rem; }
  .btn { padding: 0.5rem 0.75rem; font-size: 0.8rem; }
  .modal-header h3 { font-size: 1.1rem; }
}

/* Фиксы для уведомлений (темная тема) */
:root[data-theme="dark"] .notification-item {
  background-color: #1f2937 !important;
  border-color: #374151 !important;
}

:root[data-theme="dark"] .notification-item.unread {
  background-color: rgba(59, 130, 246, 0.15) !important;
  border-left-color: #3b82f6 !important;
}

:root[data-theme="dark"] .notification-title-text {
  color: #ffffff !important;
}

:root[data-theme="dark"] .notification-message {
  color: #d1d5db !important;
}

:root[data-theme="dark"] .notification-date {
  color: #9ca3af !important;
}

:root[data-theme="dark"] .notification-icon {
  border-right-color: #374151 !important;
}

:root[data-theme="dark"] .delete-btn {
  color: #6b7280 !important;
}
</style>