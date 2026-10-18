<template>
  <div class="card upcoming-widget" v-if="payments.length > 0 || loading">
    <div class="card-header">
      <h3 class="card-title">
        <i class="fas fa-calendar-clock"></i> Ближайшие платежи
      </h3>
      <router-link to="/recurring" class="widget-link">Все →</router-link>
    </div>

    <div v-if="loading" class="widget-loading">
      <i class="fas fa-spinner fa-spin"></i>
    </div>

    <div v-else class="upcoming-list">
      <div v-for="(item, idx) in payments" :key="`${item.id}-${idx}`" class="upcoming-item">
        <div class="upcoming-left">
          <div class="upcoming-title">{{ item.title }}</div>
          <div class="upcoming-date">
            <i class="fas fa-calendar"></i>
            {{ formatDate(item.date) }}
            <span class="upcoming-days" :class="getDaysClass(item)">
              {{ daysLabel(item) }}
            </span>
          </div>
          <div class="upcoming-meta" v-if="item.category_name || item.account_name">
            <span v-if="item.account_name">{{ item.account_name }}</span>
            <span v-if="item.category_name">· {{ item.category_name }}</span>
          </div>
        </div>
        <div class="upcoming-amount" :class="item.type_transaction === 'income' ? 'text-success' : 'text-danger'">
          {{ item.type_transaction === 'income' ? '+' : '−' }}{{ formatCurrency(item.amount) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'UpcomingPaymentsWidget',
  setup() {
    const payments = ref([])
    const loading = ref(true)

    const loadPayments = async () => {
      loading.value = true
      try {
        const data = await apiService.getUpcomingPayments(30)
        // Endpoint возвращает плоский массив
        const list = Array.isArray(data) ? data : (data.results || [])
        payments.value = list.slice(0, 5)
      } catch (e) {
        console.error('Error loading upcoming payments:', e)
        payments.value = []
      } finally {
        loading.value = false
      }
    }

    const formatCurrency = (value) => {
      if (!value && value !== 0) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency', currency: 'RUB',
        minimumFractionDigits: 0, maximumFractionDigits: 2
      }).format(value)
    }

    const formatDate = (dateString) => {
      if (!dateString) return '—'
      return new Date(dateString).toLocaleDateString('ru-RU', {
        day: '2-digit', month: 'short'
      })
    }

    const daysUntil = (dateString) => {
      if (!dateString) return null
      const today = new Date(); today.setHours(0, 0, 0, 0)
      const target = new Date(dateString); target.setHours(0, 0, 0, 0)
      return Math.round((target - today) / (1000 * 60 * 60 * 24))
    }

    const daysLabel = (item) => {
      const d = daysUntil(item.date)
      if (d === null) return ''
      if (d === 0) return 'сегодня'
      if (d === 1) return 'завтра'
      if (d > 0) return `через ${d} дн.`
      if (d === -1) return 'вчера'
      return `${Math.abs(d)} дн. назад`
    }

    const getDaysClass = (item) => {
      const d = daysUntil(item.date)
      if (d === null) return ''
      if (d <= 1) return 'days-critical'
      if (d <= 3) return 'days-soon'
      return 'days-normal'
    }

    onMounted(loadPayments)

    return { payments, loading, formatCurrency, formatDate, daysLabel, getDaysClass }
  }
}
</script>

<style scoped>
.upcoming-widget { margin-bottom: 1.5rem; }

.widget-link {
  font-size: 0.8rem;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}
.widget-link:hover { text-decoration: underline; }

.widget-loading {
  text-align: center;
  padding: 2rem;
  color: var(--gray-color);
}

.upcoming-list { display: flex; flex-direction: column; gap: 0.5rem; }

.upcoming-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: var(--radius);
  background: #f9fafb;
  transition: background 0.2s;
}
.upcoming-item:hover { background: var(--light-color); }

.upcoming-left { flex: 1; min-width: 0; }
.upcoming-title {
  font-weight: 600;
  color: var(--dark-color);
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.upcoming-date {
  font-size: 0.75rem;
  color: var(--gray-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.upcoming-meta {
  font-size: 0.7rem;
  color: var(--gray-color);
  margin-top: 0.15rem;
}
.upcoming-days {
  padding: 0.1rem 0.4rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.65rem;
}
.days-critical { background: #fee2e2; color: #991b1b; }
.days-soon { background: #fef3c7; color: #92400e; }
.days-normal { background: #e0e7ff; color: #3730a3; }

.upcoming-amount {
  font-weight: 700;
  font-size: 0.95rem;
  margin-left: 1rem;
  white-space: nowrap;
}
.text-success { color: var(--secondary-color); }
.text-danger { color: var(--danger-color); }

@media (max-width: 480px) {
  .upcoming-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .upcoming-amount {
    margin-left: 0;
    align-self: flex-end;
  }
}
</style>