<template>
  <div class="app">
    <!-- Мобильная кнопка меню -->
    <button class="mobile-menu-btn" @click="toggleMobileMenu" v-if="isMobile">
      <i class="fas" :class="mobileMenuOpen ? 'fa-times' : 'fa-bars'"></i>
    </button>

    <div class="sidebar" :class="{ 'mobile-open': mobileMenuOpen }">
      <div class="sidebar-header">
        <h2>💰 Финансы</h2>
      </div>
      
      <nav class="nav-menu">
        <router-link to="/" class="nav-item" @click="closeMobileMenu">
          <i class="fas fa-tachometer-alt"></i>
          <span>Дашборд</span>
        </router-link>
        
        <router-link to="/accounts" class="nav-item" @click="closeMobileMenu">
          <i class="fas fa-credit-card"></i>
          <span>Счета</span>
        </router-link>
        
        <router-link to="/categories" class="nav-item" @click="closeMobileMenu">
          <i class="fas fa-tags"></i>
          <span>Категории</span>
        </router-link>
        
        <router-link to="/transactions" class="nav-item" @click="closeMobileMenu">
          <i class="fas fa-exchange-alt"></i>
          <span>Транзакции</span>
        </router-link>
        
        <router-link to="/debts" class="nav-item" @click="closeMobileMenu">
          <i class="fas fa-hand-holding-usd"></i>
          <span>Долги</span>
        </router-link>
        
        <router-link to="/statistics" class="nav-item" @click="closeMobileMenu">
          <i class="fas fa-chart-line"></i>
          <span>Статистика</span>
        </router-link>
        
        <button @click="logout" class="nav-item logout-btn">
          <i class="fas fa-sign-out-alt"></i>
          <span>Выйти</span>
        </button>
      </nav>
    </div>

    <!-- Оверлей для мобильного меню -->
    <div v-if="mobileMenuOpen" class="mobile-overlay" @click="closeMobileMenu"></div>
    
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from './services/api.js'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const mobileMenuOpen = ref(false)
    const isMobile = ref(window.innerWidth <= 768)
    
    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value
      // Блокируем прокрутку body при открытом меню
      if (mobileMenuOpen.value) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }
    
    const closeMobileMenu = () => {
      mobileMenuOpen.value = false
      document.body.style.overflow = ''
    }
    
    const handleResize = () => {
      isMobile.value = window.innerWidth <= 768
      if (!isMobile.value) {
        closeMobileMenu()
      }
    }
    
    const logout = async () => {
      try {
        await apiService.logout()
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
      }
    }
    
    onMounted(() => {
      window.addEventListener('resize', handleResize)
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      document.body.style.overflow = ''
    })
    
    return {
      mobileMenuOpen,
      isMobile,
      toggleMobileMenu,
      closeMobileMenu,
      logout
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary-color: #4f46e5;
  --secondary-color: #10b981;
  --danger-color: #ef4444;
  --warning-color: #f59e0b;
  --dark-color: #1f2937;
  --gray-color: #6b7280;
  --light-color: #f3f4f6;
  --white: #ffffff;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  --radius: 8px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f5f5;
  color: var(--dark-color);
}

.app {
  display: flex;
  min-height: 100vh;
  position: relative;
}

/* Мобильная кнопка меню */
.mobile-menu-btn {
  position: fixed;
  top: 1rem;
  left: 1rem;
  z-index: 1000;
  background: var(--primary-color);
  color: white;
  border: none;
  width: 45px;
  height: 45px;
  border-radius: 8px;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: var(--shadow);
}

/* Sidebar */
.sidebar {
  width: 260px;
  background: #2c3e50;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
  transition: transform 0.3s ease;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #34495e;
}

.sidebar-header h2 {
  font-size: 1.5rem;
  color: #ecf0f1;
}

.nav-menu {
  flex: 1;
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  color: #ecf0f1;
  text-decoration: none;
  transition: all 0.3s;
  cursor: pointer;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  font-size: 1rem;
}

.nav-item:hover {
  background: #34495e;
}

.nav-item.router-link-active {
  background: #34495e;
  color: #3498db;
  border-right: 3px solid #3498db;
}

.logout-btn {
  color: #e74c3c;
  margin-top: auto;
  border-top: 1px solid #34495e;
}

.logout-btn:hover {
  background: #34495e;
  color: #e74c3c;
}

.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 2rem;
  width: calc(100% - 260px);
}

/* Mobile styles */
@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
  }
  
  .sidebar {
    transform: translateX(-100%);
    width: 280px;
  }
  
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
    padding: 1rem;
    padding-top: 4rem;
    width: 100%;
  }
  
  .mobile-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 99;
  }
}

/* Адаптивные стили для всех компонентов */
@media (max-width: 768px) {
  /* Статистика */
  .stats-grid {
    grid-template-columns: 1fr !important;
    gap: 1rem;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  /* Быстрые действия */
  .quick-actions {
    flex-direction: column;
  }
  
  .quick-actions .btn {
    width: 100%;
    justify-content: center;
  }
  
  /* Таблицы */
  .table-responsive {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .table {
    min-width: 600px;
  }
  
  /* Карточки */
  .card {
    padding: 1rem;
  }
  
  .card-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .card-header .btn {
    width: 100%;
  }
  
  /* Модальные окна */
  .modal-content {
    width: 95%;
    margin: 1rem;
    max-height: 85vh;
  }
  
  /* Формы */
  .form-group select,
  .form-group input,
  .form-group textarea {
    font-size: 16px; /* Предотвращает зумирование на iOS */
  }
  
  /* Фильтры */
  .filters {
    grid-template-columns: 1fr !important;
    gap: 1rem;
  }
  
  /* Категории */
  .category-stat {
    padding: 0.75rem;
  }
  
  .subcategories {
    padding-left: 0.5rem;
  }
  
  .subcategory {
    padding: 0.5rem;
  }
  
  /* Заголовки */
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .page-header .btn {
    width: 100%;
  }
  
  /* Вкладки */
  .type-tabs {
    flex-direction: column;
  }
  
  .tab-btn {
    width: 100%;
  }
  
  /* Таблица долгов */
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .btn-sm {
    width: 100%;
  }
  
  /* Детали долга */
  .debt-details {
    padding: 0.5rem;
  }
  
  .detail-row {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  /* Пагинация */
  .pagination {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .pagination button {
    width: 100%;
  }
  
  /* Категории дерево */
  .category-item {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .category-info {
    width: 100%;
  }
  
  .category-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .category-children {
    margin-left: 0.5rem;
    padding-left: 0.5rem;
  }
}

/* Для очень маленьких экранов */
@media (max-width: 480px) {
  .main-content {
    padding: 0.75rem;
    padding-top: 4rem;
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
  
  .btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }
  
  .modal-header h3 {
    font-size: 1.1rem;
  }
}

/* Стили для кнопок */
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

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: #4338ca;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-success {
  background: var(--secondary-color);
  color: white;
}

.btn-success:hover {
  background: #059669;
}

.btn-danger {
  background: var(--danger-color);
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-info {
  background: #3b82f6;
  color: white;
}

.btn-info:hover {
  background: #2563eb;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
}

/* Стили для карточек */
.card {
  background: white;
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
}

/* Стили для форм */
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
}

.form-label.required:after {
  content: " *";
  color: var(--danger-color);
}

.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: var(--radius);
  font-size: 0.875rem;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
}

textarea.form-control {
  resize: vertical;
  min-height: 60px;
}

/* Стили для таблиц */
.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.table th {
  font-weight: 600;
  background: #f9fafb;
}

/* Стили для модальных окон */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: var(--radius);
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.3s;
}

.modal-close:hover {
  color: #374151;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
}

/* Адаптивные стили для модальных окон */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 1rem;
  }
}

/* Утилиты */
.text-success {
  color: var(--secondary-color);
}

.text-danger {
  color: var(--danger-color);
}

.text-center {
  text-align: center;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  margin-bottom: 1rem;
}

.alert-info {
  background: #dbeafe;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.alert-danger {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.alert-warning {
  background: #fed7aa;
  color: #92400e;
  border: 1px solid #fed7aa;
}
</style>