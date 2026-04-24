<template>
  <div>
    <div class="page-header">
      <h1>Профиль пользователя</h1>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-title">ID пользователя</div>
        <div class="stat-value">{{ userInfo.id || '—' }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Email</div>
        <div class="stat-value">{{ userInfo.email || '—' }}</div>
      </div>
    </div>

    <!-- Смена Email -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-envelope"></i> Смена email
        </h3>
      </div>

      <form @submit.prevent="handleChangeEmail">
        <div class="form-group">
          <label class="form-label required">Текущий пароль</label>
          <div class="password-input-wrapper">
            <input 
              :type="showEmailCurrentPassword ? 'text' : 'password'" 
              v-model="emailForm.current_password" 
              class="form-control" 
              required
              placeholder="Введите текущий пароль"
            >
            <button 
              type="button" 
              class="password-toggle" 
              @click="showEmailCurrentPassword = !showEmailCurrentPassword"
            >
              <i :class="showEmailCurrentPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label required">Новый email</label>
          <div class="email-input-wrapper">
            <input 
              type="email" 
              v-model="emailForm.new_email" 
              class="form-control" 
              required
              placeholder="Введите новый email"
              @input="validateEmail"
            >
          </div>
          <div v-if="emailError" class="error-message">
            <i class="fas fa-exclamation-circle"></i> {{ emailError }}
          </div>
          <div v-if="emailValid" class="success-message">
            <i class="fas fa-check-circle"></i> Email валиден
          </div>
        </div>

        <div class="form-group">
          <label class="form-label required">Подтверждение email</label>
          <div class="email-input-wrapper">
            <input 
              type="email" 
              v-model="emailForm.confirm_email" 
              class="form-control" 
              required
              placeholder="Подтвердите новый email"
              @input="checkEmailMatch"
            >
          </div>
          <div v-if="emailMismatch" class="error-message">
            <i class="fas fa-exclamation-circle"></i> Email не совпадают
          </div>
        </div>

        <div class="modal-footer">
          <button type="submit" class="btn btn-primary" :disabled="!isEmailFormValid || emailLoading">
            <i v-if="emailLoading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-save"></i>
            {{ emailLoading ? 'Сохранение...' : 'Сменить email' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Смена пароля -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-key"></i> Смена пароля
        </h3>
      </div>

      <form @submit.prevent="handleChangePassword">
        <div class="form-group">
          <label class="form-label required">Текущий пароль</label>
          <div class="password-input-wrapper">
            <input 
              :type="showCurrentPassword ? 'text' : 'password'" 
              v-model="passwordForm.current_password" 
              class="form-control" 
              required
              placeholder="Введите текущий пароль"
            >
            <button 
              type="button" 
              class="password-toggle" 
              @click="showCurrentPassword = !showCurrentPassword"
            >
              <i :class="showCurrentPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label required">Новый пароль</label>
          <div class="password-input-wrapper">
            <input 
              :type="showNewPassword ? 'text' : 'password'" 
              v-model="passwordForm.new_password" 
              class="form-control" 
              required
              placeholder="Введите новый пароль"
              @input="validatePassword"
            >
            <button 
              type="button" 
              class="password-toggle" 
              @click="showNewPassword = !showNewPassword"
            >
              <i :class="showNewPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <div v-if="passwordStrength" class="password-strength">
            <div class="strength-bar">
              <div 
                class="strength-fill" 
                :class="strengthClass"
                :style="{ width: passwordStrength.percentage + '%' }"
              ></div>
            </div>
            <span class="strength-text" :class="strengthClass">
              {{ passwordStrength.text }}
            </span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label required">Подтверждение пароля</label>
          <div class="password-input-wrapper">
            <input 
              :type="showConfirmPassword ? 'text' : 'password'" 
              v-model="passwordForm.confirm_password" 
              class="form-control" 
              required
              placeholder="Подтвердите новый пароль"
              @input="checkPasswordMatch"
            >
            <button 
              type="button" 
              class="password-toggle" 
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <div v-if="passwordMismatch" class="error-message">
            <i class="fas fa-exclamation-circle"></i> Пароли не совпадают
          </div>
        </div>

        <div class="password-requirements">
          <h4>Требования к паролю:</h4>
          <ul>
            <li :class="{ valid: passwordLengthValid }">
              <i :class="passwordLengthValid ? 'fas fa-check-circle' : 'fas fa-circle'"></i>
              Минимум 8 символов
            </li>
            <li :class="{ valid: hasUpperCase }">
              <i :class="hasUpperCase ? 'fas fa-check-circle' : 'fas fa-circle'"></i>
              Хотя бы одна заглавная буква (A-Z)
            </li>
            <li :class="{ valid: hasLowerCase }">
              <i :class="hasLowerCase ? 'fas fa-check-circle' : 'fas fa-circle'"></i>
              Хотя бы одна строчная буква (a-z)
            </li>
            <li :class="{ valid: hasNumber }">
              <i :class="hasNumber ? 'fas fa-check-circle' : 'fas fa-circle'"></i>
              Хотя бы одна цифра (0-9)
            </li>
          </ul>
        </div>

        <div class="modal-footer">
          <button type="submit" class="btn btn-primary" :disabled="!isPasswordFormValid || passwordLoading">
            <i v-if="passwordLoading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-save"></i>
            {{ passwordLoading ? 'Сохранение...' : 'Сменить пароль' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Уведомления -->
    <div v-if="showSuccess" class="alert alert-success success-toast">
      <i class="fas fa-check-circle"></i>
      {{ successMessage }}
    </div>

    <div v-if="showError" class="alert alert-danger error-toast">
      <i class="fas fa-exclamation-triangle"></i>
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'Profile',
  setup() {
    const userInfo = ref({
      id: null,
      email: ''
    })
    
    // State for password change
    const passwordLoading = ref(false)
    const showCurrentPassword = ref(false)
    const showNewPassword = ref(false)
    const showConfirmPassword = ref(false)
    
    const passwordForm = ref({
      current_password: '',
      new_password: '',
      confirm_password: ''
    })

    // State for email change
    const emailLoading = ref(false)
    const showEmailCurrentPassword = ref(false)
    
    const emailForm = ref({
      current_password: '',
      new_email: '',
      confirm_email: ''
    })

    // Notification state
    const showSuccess = ref(false)
    const showError = ref(false)
    const successMessage = ref('')
    const errorMessage = ref('')

    // Email validation
    const emailError = computed(() => {
      const email = emailForm.value.new_email
      if (!email) return ''
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(email)) return 'Неверный формат email'
      return ''
    })

    const emailValid = computed(() => {
      return emailForm.value.new_email && !emailError.value
    })

    const emailMismatch = computed(() => {
      return emailForm.value.new_email !== emailForm.value.confirm_email && 
             emailForm.value.confirm_email !== ''
    })

    const isEmailFormValid = computed(() => {
      return emailForm.value.current_password &&
             emailForm.value.new_email &&
             emailForm.value.confirm_email &&
             !emailError.value &&
             !emailMismatch.value
    })

    // Password validation
    const passwordStrength = computed(() => {
      const password = passwordForm.value.new_password
      if (!password) return null
      
      let strength = 0
      if (password.length >= 8) strength += 25
      if (/[A-Z]/.test(password)) strength += 25
      if (/[a-z]/.test(password)) strength += 25
      if (/[0-9]/.test(password)) strength += 25
      
      let text = ''
      if (strength <= 25) {
        text = 'Слабый'
      } else if (strength <= 50) {
        text = 'Средний'
      } else if (strength <= 75) {
        text = 'Хороший'
      } else {
        text = 'Отличный'
      }
      
      return {
        percentage: strength,
        text: text
      }
    })

    const strengthClass = computed(() => {
      const strength = passwordStrength.value?.percentage || 0
      if (strength <= 25) return 'strength-weak'
      if (strength <= 50) return 'strength-medium'
      if (strength <= 75) return 'strength-good'
      return 'strength-excellent'
    })

    const passwordLengthValid = computed(() => {
      return passwordForm.value.new_password.length >= 8
    })

    const hasUpperCase = computed(() => {
      return /[A-Z]/.test(passwordForm.value.new_password)
    })

    const hasLowerCase = computed(() => {
      return /[a-z]/.test(passwordForm.value.new_password)
    })

    const hasNumber = computed(() => {
      return /[0-9]/.test(passwordForm.value.new_password)
    })

    const passwordMismatch = computed(() => {
      return passwordForm.value.new_password !== passwordForm.value.confirm_password && 
             passwordForm.value.confirm_password !== ''
    })

    const isPasswordFormValid = computed(() => {
      return passwordForm.value.current_password &&
             passwordForm.value.new_password &&
             passwordForm.value.confirm_password &&
             passwordLengthValid.value &&
             hasUpperCase.value &&
             hasLowerCase.value &&
             hasNumber.value &&
             !passwordMismatch.value
    })

    // Validation functions
    const validatePassword = () => {}
    const checkPasswordMatch = () => {}
    const validateEmail = () => {}
    const checkEmailMatch = () => {}

    const loadUserInfo = async () => {
      try {
        const data = await apiService.getCurrentUser()
        userInfo.value = data
      } catch (error) {
        console.error('Error loading user info:', error)
        showErrorToast('Ошибка при загрузке информации пользователя')
      }
    }

    const handleChangeEmail = async () => {
      if (!isEmailFormValid.value) return
      
      emailLoading.value = true
      try {
        await apiService.changeEmail(
          emailForm.value.current_password,
          emailForm.value.new_email
        )
        
        // Обновляем информацию о пользователе
        await loadUserInfo()
        
        // Очищаем форму
        emailForm.value = {
          current_password: '',
          new_email: '',
          confirm_email: ''
        }
        
        showSuccessToast('Email успешно изменен!')
      } catch (error) {
        console.error('Error changing email:', error)
        if (error.response?.data?.current_password) {
          showErrorToast('Неверный текущий пароль')
        } else if (error.response?.data?.new_email) {
          showErrorToast('Email уже используется или неверный формат')
        } else {
          showErrorToast('Ошибка при смене email. Попробуйте позже.')
        }
      } finally {
        emailLoading.value = false
      }
    }

    const handleChangePassword = async () => {
      if (!isPasswordFormValid.value) return
      
      passwordLoading.value = true
      try {
        await apiService.changePassword(
          passwordForm.value.current_password,
          passwordForm.value.new_password
        )
        
        // Очищаем форму
        passwordForm.value = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        }
        
        showSuccessToast('Пароль успешно изменен!')
      } catch (error) {
        console.error('Error changing password:', error)
        if (error.response?.data?.current_password) {
          showErrorToast('Неверный текущий пароль')
        } else if (error.response?.data?.new_password) {
          showErrorToast('Новый пароль не соответствует требованиям')
        } else {
          showErrorToast('Ошибка при смене пароля. Попробуйте позже.')
        }
      } finally {
        passwordLoading.value = false
      }
    }

    const showSuccessToast = (message) => {
      successMessage.value = message
      showSuccess.value = true
      setTimeout(() => {
        showSuccess.value = false
      }, 3000)
    }

    const showErrorToast = (message) => {
      errorMessage.value = message
      showError.value = true
      setTimeout(() => {
        showError.value = false
      }, 3000)
    }

    onMounted(() => {
      loadUserInfo()
    })

    return {
      userInfo,
      // Email change
      emailLoading,
      showEmailCurrentPassword,
      emailForm,
      emailError,
      emailValid,
      emailMismatch,
      isEmailFormValid,
      handleChangeEmail,
      validateEmail,
      checkEmailMatch,
      // Password change
      passwordLoading,
      showCurrentPassword,
      showNewPassword,
      showConfirmPassword,
      passwordForm,
      passwordStrength,
      strengthClass,
      passwordLengthValid,
      hasUpperCase,
      hasLowerCase,
      hasNumber,
      passwordMismatch,
      isPasswordFormValid,
      handleChangePassword,
      validatePassword,
      checkPasswordMatch,
      // Notifications
      showSuccess,
      showError,
      successMessage,
      errorMessage
    }
  }
}
</script>

<style scoped>
/* Добавьте стили для email валидации */
.email-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.success-message {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--secondary-color);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Остальные стили остаются без изменений */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h1 {
  font-size: 1.875rem;
  color: var(--dark-color);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.5rem;
  box-shadow: var(--shadow);
}

.stat-title {
  font-size: 0.875rem;
  color: var(--gray-color);
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--dark-color);
  word-break: break-all;
}

.card {
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--light-color);
  flex-wrap: wrap;
  gap: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Стили для поля пароля */
.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper .form-control {
  padding-right: 2.5rem;
}

.password-toggle {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--gray-color);
  padding: 0.25rem;
  font-size: 1rem;
  transition: color 0.3s;
}

.password-toggle:hover {
  color: var(--dark-color);
}

/* Стили для индикатора силы пароля */
.password-strength {
  margin-top: 0.5rem;
}

.strength-bar {
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s, background-color 0.3s;
}

.strength-text {
  font-size: 0.75rem;
}

.strength-weak {
  background: #ef4444;
  color: #ef4444;
}

.strength-medium {
  background: #f59e0b;
  color: #f59e0b;
}

.strength-good {
  background: #10b981;
  color: #10b981;
}

.strength-excellent {
  background: #059669;
  color: #059669;
}

/* Стили для требований к паролю */
.password-requirements {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--light-color);
  border-radius: var(--radius);
}

.password-requirements h4 {
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  color: var(--gray-color);
}

.password-requirements ul {
  list-style: none;
  padding-left: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.password-requirements li {
  font-size: 0.75rem;
  color: var(--gray-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.password-requirements li i {
  font-size: 0.7rem;
}

.password-requirements li.valid {
  color: var(--secondary-color);
}

.error-message {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--danger-color);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

/* Уведомления */
.success-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.error-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.alert-success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.alert-danger {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

/* Адаптивные стили */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    text-align: center;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
  
  .card {
    padding: 1rem;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .modal-footer .btn {
    width: 100%;
  }
  
  .success-toast,
  .error-toast {
    bottom: 1rem;
    right: 1rem;
    left: 1rem;
  }
}

@media (max-width: 480px) {
  h1 {
    font-size: 1.25rem;
  }
  
  .stat-value {
    font-size: 1rem;
  }
  
  .password-requirements ul {
    display: block;
  }
  
  .password-requirements li {
    margin-bottom: 0.25rem;
  }
}
</style>