<template>
  <div v-if="loading" class="login-container">
    <div class="login-card">
      <p>Проверка сессии...</p>
    </div>
  </div>

  <div v-else-if="isLoggedIn">
    <!-- Если пользователь уже авторизован — уводим сразу, не показываем форму -->
    <p>Вы уже авторизованы. Перенаправляем...</p>
  </div>

  <div v-else class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>💰 Finance Manager</h1>
        <p>Войдите в свой аккаунт</p>
      </div>

      <div v-if="error" class="alert alert-error">
        <i class="fas fa-exclamation-circle"></i>
        {{ error }}
      </div>

      <div v-if="successMessage" class="alert alert-success">
        <i class="fas fa-check-circle"></i>
        {{ successMessage }}
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
            :disabled="loading"
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
            :disabled="loading"
          >
        </div>

        <button
          type="submit"
          class="btn btn-primary"
          :disabled="loading"
          style="width: 100%"
        >
          <i class="fas fa-sign-in-alt"></i>
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>

        <div style="margin-top: 1rem; text-align: center">
          <!-- Обычная ссылка: Django сам обработает OAuth и сделает редирект -->
          <a href="/auth/yandex/login/" class="btn btn-secondary" style="width: 100%">
            <i class="fab fa-yandex"></i>
            Войти через Яндекс ID
          </a>
        </div>
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
          <i class="fas fa-exclamation-circle"></i>
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '../services/api.js'

export default {
  name: 'LoginForm',
  setup() {
    const route = useRoute()
    const router = useRouter()

    const email = ref('')
    const password = ref('')
    const error = ref('')
    const successMessage = ref('')
    const loading = ref(true)
    const isLoggedIn = ref(false)

    const showRegister = ref(false)
    const registerEmail = ref('')
    const registerPassword = ref('')
    const registerRePassword = ref('')
    const registerError = ref('')

    // Проверяем параметры URL при загрузке
    const checkUrlParams = () => {
      const errorParam = route.query.error
      const messageParam = route.query.message

      // Обработка ошибок
      if (errorParam === 'oauth_failed') {
        error.value = 'Не удалось войти через Яндекс. Попробуйте снова.'
      } else if (errorParam === 'no_token') {
        error.value = 'Ошибка авторизации через Яндекс. Токен не получен.'
      } else if (errorParam === 'token_invalid') {
        error.value = 'Токен авторизации недействителен. Попробуйте снова.'
      } else if (errorParam === 'auth_failed') {
        error.value = 'Ошибка авторизации. Попробуйте снова.'
      } else if (errorParam) {
        error.value = `Ошибка: ${errorParam}`
      }

      // Обработка успешных сообщений
      if (messageParam === 'logout') {
        successMessage.value = 'Вы успешно вышли из системы.'
        // Очищаем параметры URL
        router.replace({ query: {} })
      } else if (messageParam === 'registered') {
        successMessage.value = 'Регистрация успешна! Войдите в систему.'
        // Очищаем параметры URL
        router.replace({ query: {} })
      }
    }

    // Проверка авторизации через токен из localStorage
    const checkTokenAuth = async () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        try {
          console.log('Checking token validity...')
          await apiService.getCurrentUser()
          isLoggedIn.value = true
          router.push('/')
          return true
        } catch (err) {
          console.warn('Token invalid, removing...')
          localStorage.removeItem('auth_token')
          return false
        }
      }
      return false
    }

    // Проверка сессии через куки
    const checkSessionAuth = async () => {
      try {
        await apiService.get('/auth/me/')
        isLoggedIn.value = true
        router.push('/')
        return true
      } catch (err) {
        console.warn('Not authenticated (expected for login page)', err)
        isLoggedIn.value = false
        return false
      }
    }

    onMounted(async () => {
      // Обрабатываем параметры URL
      checkUrlParams()

      // Сначала проверяем токен, затем сессию
      const isTokenValid = await checkTokenAuth()
      if (!isTokenValid) {
        await checkSessionAuth()
      }

      loading.value = false
    })

    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      successMessage.value = ''

      try {
        await apiService.login(email.value, password.value)
        // Успешный вход
        router.push('/')
      } catch (err) {
        console.error('Login error:', err)
        if (err.response?.status === 401) {
          error.value = 'Неверный email или пароль'
        } else if (err.response?.data?.detail) {
          error.value = err.response.data.detail
        } else if (err.response?.data?.non_field_errors) {
          error.value = err.response.data.non_field_errors.join(', ')
        } else {
          error.value = 'Ошибка при входе. Попробуйте позже.'
        }
      } finally {
        loading.value = false
      }
    }

    const handleRegister = async () => {
      registerError.value = ''
      loading.value = true

      if (registerPassword.value !== registerRePassword.value) {
        registerError.value = 'Пароли не совпадают'
        loading.value = false
        return
      }

      if (registerPassword.value.length < 8) {
        registerError.value = 'Пароль должен содержать минимум 8 символов'
        loading.value = false
        return
      }

      try {
        await apiService.register(
          registerEmail.value,
          registerPassword.value,
          registerRePassword.value
        )
        showRegister.value = false
        registerError.value = ''

        email.value = registerEmail.value
        password.value = registerPassword.value

        // Автоматический вход после регистрации
        await handleLogin()
      } catch (err) {
        console.error('Registration error:', err)
        if (err.response?.data?.email) {
          registerError.value = err.response.data.email.join(', ')
        } else if (err.response?.data?.password) {
          registerError.value = err.response.data.password.join(', ')
        } else if (err.response?.data?.detail) {
          registerError.value = err.response.data.detail
        } else {
          registerError.value = 'Ошибка регистрации. Попробуйте позже.'
        }
      } finally {
        loading.value = false
      }
    }

    // Очищаем сообщения при уходе со страницы
    onBeforeUnmount(() => {
      error.value = ''
      successMessage.value = ''
    })

    return {
      email,
      password,
      error,
      successMessage,
      loading,
      isLoggedIn,
      showRegister,
      registerEmail,
      registerPassword,
      registerRePassword,
      registerError,
      handleLogin,
      handleRegister,
    }
  },
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 420px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #333;
  font-size: 28px;
  margin-bottom: 8px;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.alert-success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
}

.alert i {
  font-size: 18px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.form-control {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a67d8;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f3f4f6;
  color: #333;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

/* Modal styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  padding: 32px;
  border-radius: 12px;
  width: 100%;
  max-width: 420px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0 8px;
}

.modal-close:hover {
  color: #333;
}
</style>