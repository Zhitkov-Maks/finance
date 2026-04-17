<template>
  <div class="app">
    <div v-if="isAuthenticated" class="sidebar">
      <div class="sidebar-header">
        <h2>💰 Finance Manager</h2>
        <p>Управление финансами</p>
      </div>
      
      <div class="nav-menu">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <i class="fas fa-chart-line"></i>
          <span>Дашборд</span>
        </router-link>
        
        <router-link to="/accounts" class="nav-item" :class="{ active: $route.path === '/accounts' }">
          <i class="fas fa-credit-card"></i>
          <span>Счета</span>
        </router-link>
        
        <router-link to="/categories" class="nav-item" :class="{ active: $route.path === '/categories' }">
          <i class="fas fa-tags"></i>
          <span>Категории</span>
        </router-link>
        
        <router-link to="/transactions" class="nav-item" :class="{ active: $route.path === '/transactions' }">
          <i class="fas fa-exchange-alt"></i>
          <span>Транзакции</span>
        </router-link>
        
        <router-link to="/transfers" class="nav-item" :class="{ active: $route.path === '/transfers' }">
          <i class="fas fa-money-bill-transfer"></i>
          <span>Переводы</span>
        </router-link>
        
        <router-link to="/debts" class="nav-item" :class="{ active: $route.path === '/debts' }">
          <i class="fas fa-hand-holding-usd"></i>
          <span>Долги</span>
        </router-link>
        
        <router-link to="/statistics" class="nav-item" :class="{ active: $route.path === '/statistics' }">
          <i class="fas fa-chart-bar"></i>
          <span>Статистика</span>
        </router-link>
        
        <div class="nav-item logout-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Выйти</span>
        </div>
      </div>
    </div>
    
    <div class="main-content" :class="{ 'no-sidebar': !isAuthenticated }">
      <router-view />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from './services/api.js'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const isAuthenticated = computed(() => !!localStorage.getItem('auth_token'))
    
    const handleLogout = async () => {
      try {
        await apiService.logout()
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
        localStorage.removeItem('auth_token')
        router.push('/login')
      }
    }
    
    return {
      isAuthenticated,
      handleLogout
    }
  }
}
</script>

<style scoped>
.no-sidebar {
  margin-left: 0 !important;
}
</style>