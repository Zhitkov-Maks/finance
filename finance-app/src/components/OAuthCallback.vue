<template>
  <div class="oauth-callback-container">
    <div class="oauth-callback-card">
      <div v-if="loading" class="loading-spinner">
        <p>Авторизация через Яндекс...</p>
        <div class="spinner"></div>
      </div>
      <div v-if="error" class="alert alert-error">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '../services/api'

export default {
  name: 'OAuthCallback',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const loading = ref(true)
    const error = ref('')

    onMounted(async () => {
      const token = route.query.token
      console.log('OAuth callback received token:', token ? 'Yes' : 'No')

      if (token) {
        try {
          // Сохраняем токен
          localStorage.setItem('auth_token', token)
          console.log('Token saved to localStorage')

          // Проверяем, что токен работает
          try {
            await apiService.getCurrentUser()
            console.log('Token is valid, redirecting to home')
            loading.value = false
            // Перенаправляем на главную
            router.push('/')
          } catch (err) {
            console.error('Token validation failed:', err)
            error.value = 'Ошибка авторизации. Попробуйте войти снова.'
            loading.value = false
            // Перенаправляем на страницу логина через 2 секунды
            setTimeout(() => {
              router.push('/login?error=oauth_failed')
            }, 2000)
          }
        } catch (err) {
          console.error('Error saving token:', err)
          error.value = 'Ошибка сохранения токена'
          loading.value = false
        }
      } else {
        error.value = 'Токен авторизации не получен'
        loading.value = false
        setTimeout(() => {
          router.push('/login?error=no_token')
        }, 2000)
      }
    })

    return {
      loading,
      error
    }
  }
}
</script>

<style scoped>
.oauth-callback-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.oauth-callback-card {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  min-width: 300px;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.alert-error {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
}
</style>