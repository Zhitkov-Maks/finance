<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>💰 Finance Manager</h1>
        <p>Войдите в свой аккаунт</p>
      </div>
      
      <div v-if="error" class="alert alert-error">
        {{ error }}
      </div>
    
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">Email</label>
          <input 
            type="email" 
            v-model="email" 
            class="form-control"
            required
            placeholder="example@mail.com"
          >
        </div>
    
        <div class="form-group">
          <label class="form-label">Пароль</label>
          <input 
            type="password" 
            v-model="password" 
            class="form-control"
            required
            placeholder="Введите пароль"
          >
        </div>
    
        <button type="submit" class="btn btn-primary" :disabled="loading" style="width: 100%">
          <i class="fas fa-sign-in-alt"></i>
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
      
      <div style="margin-top: 1rem; text-align: center">
        <button @click="showRegister = true" class="btn btn-secondary">
          <i class="fas fa-user-plus"></i>
          Зарегистрироваться
        </button>
      </div>
    </div>
    
    <!-- Register Modal -->
    <div v-if="showRegister" class="modal" @click.self="showRegister = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Регистрация</h3>
          <button class="modal-close" @click="showRegister = false">&times;</button>
        </div>
        
        <div v-if="registerError" class="alert alert-error">
          {{ registerError }}
        </div>
        
        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input type="email" v-model="registerEmail" class="form-control" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">Пароль</label>
            <input type="password" v-model="registerPassword" class="form-control" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">Подтверждение пароля</label>
            <input type="password" v-model="registerRePassword" class="form-control" required>
          </div>
          
          <button type="submit" class="btn btn-primary" style="width: 100%">
            Зарегистрироваться
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api.js'

export default {
  name: 'LoginForm',
  setup() {
    const router = useRouter()
    const email = ref('')
    const password = ref('')
    const error = ref('')
    const loading = ref(false)
    const showRegister = ref(false)
    
    const registerEmail = ref('')
    const registerPassword = ref('')
    const registerRePassword = ref('')
    const registerError = ref('')
    
    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      
      try {
        await apiService.login(email.value, password.value)
        router.push('/')
      } catch (err) {
        error.value = 'Неверный email или пароль'
        console.error(err)
      } finally {
        loading.value = false
      }
    }
    
    const handleRegister = async () => {
      if (registerPassword.value !== registerRePassword.value) {
        registerError.value = 'Пароли не совпадают'
        return
      }
      
      try {
        await apiService.register(registerEmail.value, registerPassword.value, registerRePassword.value)
        showRegister.value = false
        await handleLogin()
      } catch (err) {
        registerError.value = 'Ошибка регистрации'
        console.error(err)
      }
    }
    
    return {
      email,
      password,
      error,
      loading,
      showRegister,
      registerEmail,
      registerPassword,
      registerRePassword,
      registerError,
      handleLogin,
      handleRegister
    }
  }
}
</script>
