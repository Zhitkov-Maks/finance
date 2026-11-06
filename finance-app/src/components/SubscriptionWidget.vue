<template>
  <div class="card subscription-card" v-if="activeSubscriptions.length > 0">
    <div class="card-header">
      <h3 class="card-title">💳 Мои подписки</h3>
      <div class="warning-badge" :class="warningClass">
        {{ warningText }}
      </div>
    </div>

    <div class="subscription-content">
      <div class="subscription-main">
        <div class="subscription-amount">
          {{ formatCurrency(monthlyTotal) }}<span class="period">/мес</span>
        </div>
        <div class="subscription-yearly">
          В год выходит: <strong>{{ formatCurrency(yearlyTotal) }}</strong>
        </div>
      </div>

      <!-- Кнопка раскрытия списка -->
      <button class="toggle-list-btn" @click="isExpanded = !isExpanded">
        <span>{{ isExpanded ? 'Скрыть список' : 'Показать список' }} ({{ activeSubscriptions.length }})</span>
        <i :class="isExpanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
      </button>

      <!-- Выпадающий список -->
      <div v-if="isExpanded" class="subscription-list">
        <div v-for="sub in activeSubscriptions" :key="sub.id" class="subscription-item">
          <div class="sub-info">
            <span class="sub-title">{{ sub.title }}</span>
            <span class="sub-date">Списание: {{ formatDate(sub.next_run_date) }}</span>
          </div>
          <div class="sub-amount">{{ formatCurrency(sub.amount) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'SubscriptionWidget',
  setup() {
    const subscriptions = ref([])
    const isExpanded = ref(false)
    const loading = ref(false)

    const loadSubscriptions = async () => {
      loading.value = true
      try {
        // Используем существующий метод получения регулярных операций
        const data = await apiService.getRecurring({ is_active: true })
        // Фильтруем только подписки
        subscriptions.value = (data.results || data).filter(
          item => item.is_subscription && item.type_transaction === 'expense'
        )
      } catch (error) {
        console.error('Failed to load subscriptions', error)
      } finally {
        loading.value = false
      }
    }

    const activeSubscriptions = computed(() => subscriptions.value)

    const monthlyTotal = computed(() => {
      return activeSubscriptions.value.reduce((sum, sub) => sum + parseFloat(sub.amount), 0)
    })

    const yearlyTotal = computed(() => monthlyTotal.value * 12)

    // Логика предупреждений
    const warningClass = computed(() => {
      if (monthlyTotal.value === 0) return 'warning-none'
      if (monthlyTotal.value < 1000) return 'warning-success'
      if (monthlyTotal.value <= 3000) return 'warning-medium'
      return 'warning-danger'
    })

    const warningText = computed(() => {
      if (monthlyTotal.value === 0) return 'Нет подписок'
      if (monthlyTotal.value < 1000) return 'Всё ок'
      if (monthlyTotal.value <= 3000) return 'Задумайтесь'
      return 'Пересмотрите подписки'
    })

    const formatCurrency = (value) => {
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency', currency: 'RUB', maximumFractionDigits: 0
      }).format(value)
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' })
    }

    onMounted(() => {
      loadSubscriptions()
      window.addEventListener('transaction-created', loadSubscriptions)
    })

    return {
      activeSubscriptions,
      isExpanded,
      monthlyTotal,
      yearlyTotal,
      warningClass,
      warningText,
      formatCurrency,
      formatDate
    }
  }
}
</script>

<style scoped>
.subscription-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-left: 4px solid #8b5cf6; /* Фиолетовый акцент для подписок */
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--light-color);
  padding-bottom: 0.75rem;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.1rem;
  color: var(--dark-color);
  margin: 0;
}

/* Бейджи предупреждений */
.warning-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 9999px;
  text-transform: uppercase;
}

.warning-success { background: rgba(16, 185, 129, 0.1); color: #059669; }
.warning-medium { background: rgba(245, 158, 11, 0.1); color: #d97706; }
.warning-danger { background: rgba(239, 68, 68, 0.1); color: #dc2626; }

.subscription-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.subscription-main {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.subscription-amount {
  font-size: 2rem;
  font-weight: 800;
  color: var(--dark-color);
}

.subscription-amount .period {
  font-size: 1rem;
  font-weight: 500;
  color: var(--gray-color);
  margin-left: 0.25rem;
}

.subscription-yearly {
  font-size: 0.85rem;
  color: var(--gray-color);
}

.subscription-yearly strong {
  color: var(--danger-color);
}

.toggle-list-btn {
  background: var(--light-color);
  border: none;
  padding: 0.5rem;
  border-radius: var(--radius);
  color: var(--dark-color);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.toggle-list-btn:hover {
  background: var(--gray-color);
  color: var(--white);
}

.subscription-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
  animation: slideDown 0.2s ease;
}

.subscription-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.75rem;
  background: var(--light-color);
  border-radius: var(--radius);
}

.sub-info {
  display: flex;
  flex-direction: column;
}

.sub-title {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--dark-color);
}

.sub-date {
  font-size: 0.7rem;
  color: var(--gray-color);
}

.sub-amount {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--dark-color);
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>