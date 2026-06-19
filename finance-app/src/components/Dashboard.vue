<template>
  <div class="dashboard-container">
    <h1 class="dashboard-title">Дашборд</h1>

    <!-- Статистика -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-title">Общий баланс</div>
        <div class="stat-value">{{ formatCurrency(totalBalance) }}</div>
      </div>

      <div class="stat-card">
        <div class="stat-title">Доходы (месяц)</div>
        <div class="stat-value text-success">{{ formatCurrency(monthlyIncome) }}</div>
      </div>

      <div class="stat-card">
        <div class="stat-title">Расходы (месяц)</div>
        <div class="stat-value text-danger">{{ formatCurrency(monthlyExpense) }}</div>
      </div>
    </div>

    <!-- Панель действий и курсы валют -->
    <div class="actions-panel">
      <button @click="showAddTransaction = true" class="btn btn-success">
        <i class="fas fa-exchange-alt"></i> Добавить транзакцию
      </button>

      <div class="exchange-rates" v-if="exchangeRates.length > 0">
        <div v-for="rate in exchangeRates" :key="rate.code" class="rate-item" :title="`Курс ЦБ РФ на ${rate.date}`">
          <span class="rate-currency">{{ rate.code }}</span>
          <span class="rate-value">{{ rate.value }} ₽</span>
        </div>
        <div v-if="exchangeRatesError" class="rate-error" title="Не удалось загрузить курс валют">
          ⚠️
        </div>
      </div>
      <div v-else-if="!exchangeRatesLoading" class="exchange-rates-placeholder"></div>
    </div>

    <!-- НОВЫЙ БЛОК: Финансовые метрики и прогноз -->
    <div class="insights-grid">
      <!-- Карточка прогноза -->
      <div class="card forecast-card">
        <div class="card-header">
          <h3 class="card-title">📈 Прогноз на конец месяца</h3>
          <span class="forecast-date">{{ formatDate(now) }}</span>
        </div>

        <div class="forecast-content">
          <div class="forecast-main">
            <div class="forecast-value" :class="forecastStatus.class">
              {{ formatCurrency(forecastBalance) }}
            </div>
            <div class="forecast-label">Прогнозируемый остаток</div>
          </div>

          <div class="forecast-details">
            <div class="forecast-item">
              <span class="forecast-item-label">Средний доход в день</span>
              <span class="forecast-item-value text-success">
                {{ formatCurrency(averageDailyIncome) }}
              </span>
            </div>
            <div class="forecast-item">
              <span class="forecast-item-label">Средний расход в день</span>
              <span class="forecast-item-value text-danger">
                {{ formatCurrency(averageDailyExpense) }}
              </span>
            </div>
            <div class="forecast-item">
              <span class="forecast-item-label">Осталось дней</span>
              <span class="forecast-item-value">{{ daysLeftInMonth }}</span>
            </div>
            <div class="forecast-item">
              <span class="forecast-item-label">Дневной бюджет</span>
              <span class="forecast-item-value" :class="dailyBudgetClass">
                {{ formatCurrency(dailyBudget) }}
              </span>
            </div>
          </div>

          <!-- Прогресс-бар дня -->
          <div class="daily-progress">
            <div class="progress-label">
              <span>Прогресс месяца</span>
              <span>{{ dailyProgress }}%</span>
            </div>
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: dailyProgress + '%' }"
                :class="progressClass"
              ></div>
            </div>
          </div>

          <!-- Статус прогноза -->
          <div class="forecast-status" :class="forecastStatus.class">
            <i :class="forecastStatus.icon"></i>
            {{ forecastStatus.message }}
          </div>
        </div>
      </div>

      <!-- Карточка сравнения с прошлым месяцем -->
      <div class="card comparison-card">
        <div class="card-header">
          <h3 class="card-title">📊 Сравнение с прошлым месяцем</h3>
        </div>

        <div class="comparison-content">
          <div class="comparison-item">
            <div class="comparison-label">
              <i class="fas fa-arrow-up text-success"></i> Доходы
            </div>
            <div class="comparison-values">
              <span class="comparison-current">{{ formatCurrency(monthlyIncome) }}</span>
              <span class="comparison-change" :class="incomeChangeClass">
                {{ incomeChange }}
              </span>
            </div>
          </div>

          <div class="comparison-item">
            <div class="comparison-label">
              <i class="fas fa-arrow-down text-danger"></i> Расходы
            </div>
            <div class="comparison-values">
              <span class="comparison-current">{{ formatCurrency(monthlyExpense) }}</span>
              <span class="comparison-change" :class="expenseChangeClass">
                {{ expenseChange }}
              </span>
            </div>
          </div>

          <div class="comparison-item highlight">
            <div class="comparison-label">
              <i class="fas fa-wallet"></i> Остаток
            </div>
            <div class="comparison-values">
              <span class="comparison-current">{{ formatCurrency(monthlyIncome - monthlyExpense) }}</span>
              <span class="comparison-change" :class="savingsChangeClass">
                {{ savingsChange }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Добавить транзакцию -->
    <div v-if="showAddTransaction" class="modal" @click.self="showAddTransaction = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Добавить транзакцию</h3>
          <button class="modal-close" @click="showAddTransaction = false">&times;</button>
        </div>

        <form @submit.prevent="addTransaction">
          <div class="form-group">
            <label class="form-label">Тип</label>
            <select v-model="newTransaction.type" class="form-control" required>
              <option value="income">Доход</option>
              <option value="expense">Расход</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Сумма</label>
            <input type="number" v-model="newTransaction.amount" class="form-control" step="0.01" required>
          </div>

          <div class="form-group">
            <label class="form-label">Категория</label>
            <select v-model="newTransaction.category" class="form-control" required>
              <option value="">Выберите категорию</option>
              <option v-for="cat in availableCategories" :key="cat.id" :value="cat.id">
                {{ '—'.repeat(cat.level) }} {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Счет</label>
            <select v-model="newTransaction.account" class="form-control" required>
              <option value="">Выберите счет</option>
              <option v-for="acc in activeAccounts" :key="acc.id" :value="acc.id">
                {{ acc.name }} ({{ formatCurrency(acc.balance) }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Комментарий</label>
            <textarea v-model="newTransaction.comment" class="form-control" rows="2"></textarea>
          </div>

          <div class="modal-footer">
            <button type="button" @click="showAddTransaction = false" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Добавить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'Dashboard',
  setup() {
    const accounts = ref([])
    const incomeTransactionsList = ref([])
    const expenseTransactionsList = ref([])
    const incomeCategories = ref([])
    const expenseCategories = ref([])
    const loading = ref(false)
    const showAddTransaction = ref(false)
    const monthlyIncome = ref(0)
    const monthlyExpense = ref(0)
    const exchangeRates = ref([])
    const exchangeRatesLoading = ref(true)
    const exchangeRatesError = ref(false)
    const now = ref(new Date())
    let ratesUpdateInterval = null

    const newTransaction = ref({
      type: 'expense',
      amount: '',
      category: '',
      account: '',
      comment: ''
    })

    // Данные за прошлый месяц
    const previousMonthData = ref({
      income: 0,
      expense: 0
    })

    // --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
    const formatCurrency = (value) => {
      if (!value && value !== 0) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(value)
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = typeof dateString === 'string' ? new Date(dateString) : dateString
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    }

    const formatShortDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // --- ОСНОВНЫЕ COMPUTED ---
    const totalBalance = computed(() => {
      return accounts.value
        .filter(acc => acc.is_active)
        .reduce((sum, acc) => sum + parseFloat(acc.balance), 0)
    })

    const activeAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active)
    })

    // --- Загрузка данных за прошлый месяц через API (как в Statistics) ---
    const loadPreviousMonthStatistics = async () => {
      const nowDate = new Date()
      const currentMonth = nowDate.getMonth() + 1
      const currentYear = nowDate.getFullYear()
      
      // Вычисляем предыдущий месяц
      let prevMonth = currentMonth - 1
      let prevYear = currentYear
      if (prevMonth === 0) {
        prevMonth = 12
        prevYear = currentYear - 1
      }

      try {
        // Используем getStatistics для получения данных за предыдущий месяц
        const expenseStats = await apiService.getStatistics(prevMonth, prevYear, 'expense')
        previousMonthData.value.expense = parseFloat(expenseStats.total_amount) || 0

        const incomeStats = await apiService.getStatistics(prevMonth, prevYear, 'income')
        previousMonthData.value.income = parseFloat(incomeStats.total_amount) || 0

        console.log(`Данные за прошлый месяц (${prevMonth}.${prevYear}): доходы=${previousMonthData.value.income}, расходы=${previousMonthData.value.expense}`)
      } catch (error) {
        console.error('Error loading previous month statistics:', error)
        previousMonthData.value.income = 0
        previousMonthData.value.expense = 0
      }
    }

    // --- Расчет прогноза ---
    const daysInMonth = computed(() => {
      const date = new Date()
      return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
    })

    const daysPassed = computed(() => {
      const date = new Date()
      return date.getDate()
    })

    const daysLeftInMonth = computed(() => {
      return daysInMonth.value - daysPassed.value
    })

    const averageDailyIncome = computed(() => {
      if (daysPassed.value === 0) return 0
      return monthlyIncome.value / daysPassed.value
    })

    const averageDailyExpense = computed(() => {
      if (daysPassed.value === 0) return 0
      return monthlyExpense.value / daysPassed.value
    })

    const dailyBudget = computed(() => {
      if (daysLeftInMonth.value === 0) return 0
      const currentBalance = totalBalance.value
      return currentBalance / daysLeftInMonth.value
    })

    const forecastBalance = computed(() => {
      const currentBalance = totalBalance.value
      const dailyNet = averageDailyIncome.value - averageDailyExpense.value
      const forecast = currentBalance + (dailyNet * daysLeftInMonth.value)
      return Math.max(0, forecast)
    })

    // Статус прогноза
    const forecastStatus = computed(() => {
      const diff = forecastBalance.value - totalBalance.value
      if (diff > 0) {
        return {
          class: 'status-positive',
          icon: 'fas fa-arrow-up',
          message: `Ожидается рост на ${formatCurrency(diff)}`
        }
      } else if (diff < 0) {
        return {
          class: 'status-negative',
          icon: 'fas fa-arrow-down',
          message: `Ожидается снижение на ${formatCurrency(Math.abs(diff))}`
        }
      } else {
        return {
          class: 'status-neutral',
          icon: 'fas fa-minus',
          message: 'Остаток останется без изменений'
        }
      }
    })

    const dailyProgress = computed(() => {
      return Math.min(100, Math.round((daysPassed.value / daysInMonth.value) * 100))
    })

    const progressClass = computed(() => {
      if (dailyProgress.value < 30) return 'progress-low'
      if (dailyProgress.value < 70) return 'progress-medium'
      return 'progress-high'
    })

    const dailyBudgetClass = computed(() => {
      if (dailyBudget.value > 0) return 'text-success'
      if (dailyBudget.value < 0) return 'text-danger'
      return ''
    })

    // Сравнение с прошлым месяцем
    const incomeChange = computed(() => {
      if (previousMonthData.value.income === 0) return 'Нет данных'
      const diff = monthlyIncome.value - previousMonthData.value.income
      const percent = (diff / previousMonthData.value.income) * 100
      return `${diff > 0 ? '+' : ''}${percent.toFixed(1)}%`
    })

    const incomeChangeClass = computed(() => {
      if (previousMonthData.value.income === 0) return ''
      return monthlyIncome.value > previousMonthData.value.income ? 'text-success' : 'text-danger'
    })

    const expenseChange = computed(() => {
      if (previousMonthData.value.expense === 0) return 'Нет данных'
      const diff = monthlyExpense.value - previousMonthData.value.expense
      const percent = (diff / previousMonthData.value.expense) * 100
      return `${diff > 0 ? '+' : ''}${percent.toFixed(1)}%`
    })

    const expenseChangeClass = computed(() => {
      if (previousMonthData.value.expense === 0) return ''
      return monthlyExpense.value < previousMonthData.value.expense ? 'text-success' : 'text-danger'
    })

    const savingsChange = computed(() => {
      const current = monthlyIncome.value - monthlyExpense.value
      const previous = previousMonthData.value.income - previousMonthData.value.expense
      if (previous === 0) return 'Нет данных'
      const diff = current - previous
      const percent = (diff / Math.abs(previous)) * 100
      return `${diff > 0 ? '+' : ''}${percent.toFixed(1)}%`
    })

    const savingsChangeClass = computed(() => {
      const current = monthlyIncome.value - monthlyExpense.value
      const previous = previousMonthData.value.income - previousMonthData.value.expense
      if (previous === 0) return ''
      return current > previous ? 'text-success' : 'text-danger'
    })

    const availableCategories = computed(() => {
      const categories = newTransaction.value.type === 'income' ? incomeCategories.value : expenseCategories.value
      return flattenCategories(categories)
    })

    const flattenCategories = (categories, level = 0) => {
      let result = []
      for (const cat of categories) {
        result.push({ ...cat, level, name: cat.name })
        if (cat.children && cat.children.length) {
          result = result.concat(flattenCategories(cat.children, level + 1))
        }
      }
      return result
    }

    // --- МЕТОДЫ ---
    const fetchExchangeRates = async () => {
      exchangeRatesLoading.value = true
      exchangeRatesError.value = false
      try {
        const response = await fetch('https://www.cbr-xml-daily.ru/daily_json.js')
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        const data = await response.json()

        const CURRENCIES_TO_SHOW = ['USD', 'EUR', 'CNY']
        const rates = []
        for (const code of CURRENCIES_TO_SHOW) {
          if (data.Valute[code]) {
            const valute = data.Valute[code]
            const valuePerUnit = valute.Value / valute.Nominal
            rates.push({
              code: code,
              name: valute.Name,
              value: valuePerUnit.toFixed(2),
              date: data.Date.split('T')[0]
            })
          }
        }
        exchangeRates.value = rates
        exchangeRatesError.value = false
      } catch (error) {
        console.error('Failed to fetch exchange rates:', error)
        exchangeRatesError.value = true
      } finally {
        exchangeRatesLoading.value = false
      }
    }

    const loadMonthlyStatistics = async () => {
      const now = new Date()
      const month = now.getMonth() + 1
      const year = now.getFullYear()

      try {
        const expenseStats = await apiService.getStatistics(month, year, 'expense')
        monthlyExpense.value = parseFloat(expenseStats.total_amount) || 0

        const incomeStats = await apiService.getStatistics(month, year, 'income')
        monthlyIncome.value = parseFloat(incomeStats.total_amount) || 0

        console.log(`Статистика за ${month}.${year}: доходы=${monthlyIncome.value}, расходы=${monthlyExpense.value}`)
      } catch (error) {
        console.error('Error loading monthly statistics:', error)
        monthlyIncome.value = 0
        monthlyExpense.value = 0
      }
    }

    const loadData = async () => {
      loading.value = true
      try {
        const accountsData = await apiService.getAccounts(1, 100)
        accounts.value = accountsData.results[0]?.accounts || []

        const incomeData = await apiService.getTransactions({ page: 1, page_size: 5, type: 'income' })
        incomeTransactionsList.value = (incomeData.results || []).map(t => ({ ...t, transaction_type: 'income' }))

        const expenseData = await apiService.getTransactions({ page: 1, page_size: 5, type: 'expense' })
        expenseTransactionsList.value = (expenseData.results || []).map(t => ({ ...t, transaction_type: 'expense' }))

        const incomeCatData = await apiService.getCategories('income', 1, 100, true)
        incomeCategories.value = incomeCatData.results || []

        const expenseCatData = await apiService.getCategories('expense', 1, 100, true)
        expenseCategories.value = expenseCatData.results || []

        await loadMonthlyStatistics()
        await loadPreviousMonthStatistics()
      } catch (error) {
        console.error('Error loading data:', error)
      } finally {
        loading.value = false
      }
    }

    const addTransaction = async () => {
      if (!newTransaction.value.category || !newTransaction.value.account) {
        alert('Заполните все поля')
        return
      }

      try {
        await apiService.createTransaction(newTransaction.value.type, {
          amount: newTransaction.value.amount,
          create_at: new Date().toISOString(),
          category: parseInt(newTransaction.value.category),
          account: parseInt(newTransaction.value.account),
          comment: newTransaction.value.comment
        })
        showAddTransaction.value = false
        newTransaction.value = {
          type: 'expense',
          amount: '',
          category: '',
          account: '',
          comment: ''
        }
        await loadData()
      } catch (error) {
        console.error('Error creating transaction:', error)
        alert('Ошибка при создании транзакции')
      }
    }

    // --- LIFECYCLE ---
    onMounted(() => {
      loadData()
      fetchExchangeRates()
      ratesUpdateInterval = setInterval(fetchExchangeRates, 3600000)
    })

    onBeforeUnmount(() => {
      if (ratesUpdateInterval) {
        clearInterval(ratesUpdateInterval)
      }
    })

    return {
      accounts,
      loading,
      showAddTransaction,
      newTransaction,
      totalBalance,
      activeAccounts,
      monthlyIncome,
      monthlyExpense,
      availableCategories,
      exchangeRates,
      exchangeRatesLoading,
      exchangeRatesError,
      now,
      daysLeftInMonth,
      averageDailyIncome,
      averageDailyExpense,
      dailyBudget,
      forecastBalance,
      forecastStatus,
      dailyProgress,
      progressClass,
      dailyBudgetClass,
      incomeChange,
      incomeChangeClass,
      expenseChange,
      expenseChangeClass,
      savingsChange,
      savingsChangeClass,
      addTransaction,
      formatCurrency,
      formatDate,
      formatShortDate
    }
  }
}
</script>

<style scoped>
/* Увеличенный отступ сверху для дашборда */
.dashboard-container {
  padding-top: 0.5rem;
}

.dashboard-title {
  margin-bottom: 2rem;
  margin-top: 0;
}

/* Панель действий и курсы */
.actions-panel {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
}

.exchange-rates {
  display: flex;
  gap: 1rem;
  background: var(--light-color, #f3f4f6);
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  flex-wrap: wrap;
}

.rate-item {
  display: inline-flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.rate-currency {
  color: var(--gray-color, #6b7280);
}

.rate-value {
  color: var(--dark-color, #1f2937);
  font-weight: 600;
}

.rate-error {
  cursor: help;
  font-size: 1rem;
}

.exchange-rates-placeholder {
  min-width: 180px;
}

/* Стили карточек */
.card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.25rem;
  box-shadow: var(--shadow);
  margin-bottom: 1.5rem;
}

.card:last-child {
  margin-bottom: 0;
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
  margin: 0;
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
  font-size: 2rem;
  font-weight: 700;
  color: var(--dark-color);
}

.text-success {
  color: var(--secondary-color);
}

.text-danger {
  color: var(--danger-color);
}

/* Стили для нового блока */
.insights-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* Карточка прогноза */
.forecast-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.forecast-card .card-header {
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.forecast-card .card-title {
  color: white;
}

.forecast-date {
  font-size: 0.875rem;
  opacity: 0.8;
}

.forecast-content {
  padding: 0.5rem 0;
}

.forecast-main {
  text-align: center;
  margin-bottom: 1.5rem;
}

.forecast-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.forecast-label {
  font-size: 0.875rem;
  opacity: 0.8;
}

.forecast-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.forecast-item {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.75rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
}

.forecast-item-label {
  font-size: 0.75rem;
  opacity: 0.8;
  margin-bottom: 0.25rem;
}

.forecast-item-value {
  font-size: 1.1rem;
  font-weight: 600;
}

.forecast-item-value.text-success {
  color: #34d399;
}

.forecast-item-value.text-danger {
  color: #f87171;
}

.daily-progress {
  margin-bottom: 1rem;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.6s ease;
}

.progress-fill.progress-low {
  background: #34d399;
}

.progress-fill.progress-medium {
  background: #fbbf24;
}

.progress-fill.progress-high {
  background: #f87171;
}

.forecast-status {
  padding: 0.75rem;
  border-radius: 0.5rem;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
}

.forecast-status.status-positive {
  background: rgba(52, 211, 153, 0.2);
  color: #34d399;
}

.forecast-status.status-negative {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.forecast-status.status-neutral {
  background: rgba(255, 255, 255, 0.1);
  color: #fbbf24;
}

/* Карточка сравнения */
.comparison-card {
  background: var(--white);
}

.comparison-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comparison-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: var(--light-color);
}

.comparison-item.highlight {
  background: #f3f4f6;
  border: 2px solid var(--primary-color);
}

.comparison-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.comparison-values {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.comparison-current {
  font-weight: 600;
}

.comparison-change {
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.05);
}

/* Модалка */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: var(--radius);
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  font-size: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-secondary {
  background: var(--light-color);
  color: var(--dark-color);
}

.btn-success {
  background: var(--secondary-color);
  color: white;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .insights-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .forecast-details {
    grid-template-columns: 1fr 1fr;
  }

  .dashboard-title {
    text-align: center;
  }

  .forecast-value {
    font-size: 2rem;
  }
  
  .comparison-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .comparison-values {
    justify-content: space-between;
  }

  .stats-grid {
    gap: 1rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .forecast-details {
    grid-template-columns: 1fr;
  }
  
  .forecast-value {
    font-size: 1.5rem;
  }

  .actions-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .exchange-rates {
    justify-content: center;
  }
}
</style>