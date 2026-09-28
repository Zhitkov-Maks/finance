<template>
  <div class="dashboard-container">
    <h1 class="dashboard-title">Дашборд</h1>

    <!-- Статистика: стек карточек на мобилке, сетка на десктопе -->
    <div class="stats-carousel" :class="{ 'is-mobile': isMobileView }">
      <div
        class="stats-carousel-track"
        :class="{ 'is-mobile': isMobileView }"
        @touchstart.passive="onTouchStart"
        @touchmove.passive="onTouchMove"
        @touchend="onTouchEnd"
        @touchcancel="onTouchEnd"
        @mousedown="onMouseDown"
      >
        <div
          v-for="(card, i) in statCards"
          :key="card.key"
          class="stat-card"
          :class="[card.class, { 'is-active': i === currentStatIndex }]"
          :style="cardPosition(i)"
        >
          <div class="stat-title">{{ card.title }}</div>
          <div class="stat-value">{{ formatCurrency(card.value) }}</div>
        </div>
      </div>

      <!-- Точки-индикаторы -->
      <div class="stats-dots" :class="{ 'is-mobile': isMobileView }">
        <span
          v-for="i in 3"
          :key="i - 1"
          class="stats-dot"
          :class="{ active: currentStatIndex === i - 1 }"
          @click="currentStatIndex = i - 1"
        ></span>
      </div>
    </div>

    <!-- Панель действий и курсы валют -->
    <div class="actions-panel">
      <button @click="showAddTransaction = true" class="btn btn-success">
        <i class="fas fa-exchange-alt"></i> Добавить транзакцию
      </button>

      <div class="exchange-rates" v-if="exchangeRates.length > 0">
        <div
          v-for="rate in exchangeRates"
          :key="rate.code"
          class="rate-item"
          :title="`Курс ЦБ РФ на ${rate.date}`"
        >
          <span class="rate-currency">{{ rate.code }}</span>
          <span class="rate-value">{{ rate.value }} ₽</span>
        </div>
        <div
          v-if="exchangeRatesError"
          class="rate-error"
          title="Не удалось загрузить курс валют"
        >
          ⚠️
        </div>
      </div>
      <div
        v-else-if="!exchangeRatesLoading"
        class="exchange-rates-placeholder"
      ></div>
    </div>

    <!-- Финансовые метрики и прогноз -->
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
          <span class="comparison-period">
            {{ formatMonthYear(previousMonth) }}
          </span>
        </div>

        <div class="comparison-content">
          <div class="comparison-item">
            <div class="comparison-label">
              <i class="fas fa-arrow-up text-success"></i> Доходы
            </div>
            <div class="comparison-values">
              <span class="comparison-current">
                {{ formatCurrency(previousMonthData.income) }}
              </span>
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
              <span class="comparison-current">
                {{ formatCurrency(previousMonthData.expense) }}
              </span>
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
              <span class="comparison-current">
                {{ formatCurrency(previousMonthData.income - previousMonthData.expense) }}
              </span>
              <span class="comparison-change" :class="savingsChangeClass">
                {{ savingsChange }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Добавить транзакцию -->
    <div
      v-if="showAddTransaction"
      class="modal"
      @click.self="showAddTransaction = false"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h3>Добавить транзакцию</h3>
          <button class="modal-close" @click="showAddTransaction = false">
            &times;
          </button>
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
            <input
              type="number"
              v-model="newTransaction.amount"
              class="form-control"
              step="0.01"
              required
            >
          </div>

          <div class="form-group">
            <label class="form-label">Категория</label>
            <select v-model="newTransaction.category" class="form-control" required>
              <option value="">Выберите категорию</option>
              <option
                v-for="cat in availableCategories"
                :key="cat.id"
                :value="cat.id"
              >
                {{ '—'.repeat(cat.level) }} {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Счет</label>
            <select v-model="newTransaction.account" class="form-control" required>
              <option value="">Выберите счет</option>
              <option
                v-for="acc in activeAccounts"
                :key="acc.id"
                :value="acc.id"
              >
                {{ acc.name }} ({{ formatCurrency(acc.balance) }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Комментарий</label>
            <textarea
              v-model="newTransaction.comment"
              class="form-control"
              rows="2"
            ></textarea>
          </div>

          <div class="modal-footer">
            <button
              type="button"
              @click="showAddTransaction = false"
              class="btn btn-secondary"
            >
              Отмена
            </button>
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

    const previousMonthData = ref({
      income: 0,
      expense: 0
    })

    // ===== КАРУСЕЛЬ =====
    const currentStatIndex = ref(0)
    const touchStartX = ref(0)
    const touchDeltaX = ref(0)
    const isDragging = ref(false)
    const SWIPE_THRESHOLD = 50

    const isMobileView = ref(false)

    const updateViewport = () => {
      isMobileView.value = window.innerWidth <= 1024
    }

    // Карточки статистики
    const statCards = computed(() => [
      {
        key: 'balance',
        title: 'Общий баланс',
        value: totalBalance.value,
        class: 'stat-card-balance'
      },
      {
        key: 'expense',
        title: 'Расходы (месяц)',
        value: monthlyExpense.value,
        class: 'stat-card-expense'
      },
      {
        key: 'income',
        title: 'Доходы (месяц)',
        value: monthlyIncome.value,
        class: 'stat-card-income'
      }
    ])

    // Позиционирование карточек в стеке (только на мобилке)
    // Позиционирование карточек в стеке (только на мобилке)
    const cardPosition = (index) => {
      if (!isMobileView.value) return {}

      const offset = index - currentStatIndex.value

      // Дальние карточки полностью скрываем
      if (Math.abs(offset) > 1) {
        return { display: 'none' }
      }

      // Активная карточка — ровно по центру
      if (offset === 0) {
        return {
          transform: 'translateX(-50%) scale(1)',
          zIndex: 3,
          opacity: 1
        }
      }

      // Соседняя карточка: чуть смещена и чуть меньше
      const direction = offset > 0 ? 1 : -1
      return {
        transform: `translateX(calc(-50% + ${direction * 20}px)) scale(0.94)`,
        zIndex: 2,
        opacity: 1
      }
    }

    // Свайп
    const onTouchStart = (e) => {
      if (!isMobileView.value) return
      touchStartX.value = e.touches[0].clientX
      touchDeltaX.value = 0
      isDragging.value = true
    }

    const onTouchMove = (e) => {
      if (!isDragging.value || !isMobileView.value) return
      touchDeltaX.value = e.touches[0].clientX - touchStartX.value
    }

    const onTouchEnd = () => {
      if (!isDragging.value) return
      isDragging.value = false

      if (touchDeltaX.value < -SWIPE_THRESHOLD && currentStatIndex.value < 2) {
        currentStatIndex.value++
      } else if (touchDeltaX.value > SWIPE_THRESHOLD && currentStatIndex.value > 0) {
        currentStatIndex.value--
      }
      touchDeltaX.value = 0
    }

    const onMouseDown = (e) => {
      if (!isMobileView.value) return
      touchStartX.value = e.clientX
      touchDeltaX.value = 0
      isDragging.value = true

      const onMouseMove = (ev) => {
        if (!isDragging.value) return
        touchDeltaX.value = ev.clientX - touchStartX.value
      }
      const onMouseUp = () => {
        onTouchEnd()
        window.removeEventListener('mousemove', onMouseMove)
        window.removeEventListener('mouseup', onMouseUp)
      }
      window.addEventListener('mousemove', onMouseMove)
      window.addEventListener('mouseup', onMouseUp)
    }

    // ===== ВСПОМОГАТЕЛЬНЫЕ =====
    const formatCurrency = (value) => {
      if (value === null || value === undefined || isNaN(value)) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB'
      }).format(value)
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date =
        typeof dateString === 'string' ? new Date(dateString) : dateString
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

    const previousMonth = computed(() => {
      const nowDate = new Date()
      const currentMonth = nowDate.getMonth() + 1
      const currentYear = nowDate.getFullYear()

      let prevMonth = currentMonth - 1
      let prevYear = currentYear
      if (prevMonth === 0) {
        prevMonth = 12
        prevYear = currentYear - 1
      }
      return { month: prevMonth, year: prevYear }
    })

    const formatMonthYear = (date) => {
      const monthNames = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
      ]
      return `${monthNames[date.month - 1]} ${date.year}`
    }

    // ===== COMPUTED =====
    const totalBalance = computed(() => {
      return accounts.value
        .filter(acc => acc.is_active)
        .reduce((sum, acc) => sum + parseFloat(acc.balance || 0), 0)
    })

    const activeAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active)
    })

    // ===== ЗАГРУЗКА СТАТИСТИКИ =====
    const loadPreviousMonthStatistics = async () => {
      const nowDate = new Date()
      const currentMonth = nowDate.getMonth() + 1
      const currentYear = nowDate.getFullYear()

      let prevMonth = currentMonth - 1
      let prevYear = currentYear
      if (prevMonth === 0) {
        prevMonth = 12
        prevYear = currentYear - 1
      }

      try {
        const expenseStats = await apiService.getStatistics(prevMonth, prevYear, 'expense')
        previousMonthData.value.expense = parseFloat(expenseStats.total_amount) || 0

        const incomeStats = await apiService.getStatistics(prevMonth, prevYear, 'income')
        previousMonthData.value.income = parseFloat(incomeStats.total_amount) || 0
      } catch (error) {
        console.error('Error loading previous month statistics:', error)
        previousMonthData.value.income = 0
        previousMonthData.value.expense = 0
      }
    }

    // ===== ПРОГНОЗ =====
    const daysInMonth = computed(() => {
      const date = new Date()
      return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
    })

    const daysPassed = computed(() => new Date().getDate())

    const daysLeftInMonth = computed(() => daysInMonth.value - daysPassed.value)

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
      return totalBalance.value / daysLeftInMonth.value
    })

    const forecastBalance = computed(() => {
      const projectedExpenses =
        averageDailyExpense.value * daysLeftInMonth.value
      return Math.round((totalBalance.value - projectedExpenses) * 100) / 100
    })

    const forecastWithExpectedIncome = computed(() => {
      const projectedIncome = averageDailyIncome.value * daysLeftInMonth.value
      const projectedExpenses = averageDailyExpense.value * daysLeftInMonth.value
      const forecast = totalBalance.value + projectedIncome - projectedExpenses
      return Math.max(0, Math.round(forecast * 100) / 100)
    })

    const forecastStatus = computed(() => {
      const diff = forecastBalance.value - totalBalance.value

      if (daysLeftInMonth.value === 0) {
        return {
          class: 'status-neutral',
          icon: 'fas fa-minus',
          message: 'Месяц завершен'
        }
      }

      if (averageDailyExpense.value === 0) {
        return {
          class: 'status-neutral',
          icon: 'fas fa-minus',
          message: 'Расходы не зафиксированы'
        }
      }

      const percentChange =
        totalBalance.value !== 0
          ? (diff / totalBalance.value) * 100
          : 0

      if (percentChange > 5) {
        return {
          class: 'status-positive',
          icon: 'fas fa-arrow-up',
          message: `Ожидается рост на ${formatCurrency(diff)} (${percentChange.toFixed(1)}%)`
        }
      } else if (percentChange < -5) {
        return {
          class: 'status-negative',
          icon: 'fas fa-arrow-down',
          message: `Ожидается снижение на ${formatCurrency(Math.abs(diff))} (${Math.abs(percentChange).toFixed(1)}%)`
        }
      } else {
        const dailyCost = averageDailyExpense.value
        const totalProjectedCost = dailyCost * daysLeftInMonth.value

        if (totalProjectedCost > totalBalance.value) {
          return {
            class: 'status-negative',
            icon: 'fas fa-exclamation-triangle',
            message: `Бюджет превышен на ${formatCurrency(totalProjectedCost - totalBalance.value)}`
          }
        } else {
          return {
            class: 'status-positive',
            icon: 'fas fa-check-circle',
            message: `Денег хватит на ${Math.floor(totalBalance.value / dailyCost)} дней`
          }
        }
      }
    })

    const dailyProgress = computed(() => {
      return Math.min(
        100,
        Math.round((daysPassed.value / daysInMonth.value) * 100)
      )
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

    // ===== СРАВНЕНИЕ =====
    const incomeChange = computed(() => {
      if (previousMonthData.value.income === 0) return 'Нет данных'
      const diff = monthlyIncome.value - previousMonthData.value.income
      const percent = (diff / previousMonthData.value.income) * 100
      return `${diff > 0 ? '+' : ''}${percent.toFixed(1)}%`
    })

    const incomeChangeClass = computed(() => {
      if (previousMonthData.value.income === 0) return ''
      return monthlyIncome.value > previousMonthData.value.income
        ? 'text-success'
        : 'text-danger'
    })

    const expenseChange = computed(() => {
      if (previousMonthData.value.expense === 0) return 'Нет данных'
      const diff = monthlyExpense.value - previousMonthData.value.expense
      const percent = (diff / previousMonthData.value.expense) * 100
      return `${diff > 0 ? '+' : ''}${percent.toFixed(1)}%`
    })

    const expenseChangeClass = computed(() => {
      if (previousMonthData.value.expense === 0) return ''
      return monthlyExpense.value < previousMonthData.value.expense
        ? 'text-success'
        : 'text-danger'
    })

    const savingsChange = computed(() => {
      const current = monthlyIncome.value - monthlyExpense.value
      const previous =
        previousMonthData.value.income - previousMonthData.value.expense
      if (previous === 0) return 'Нет данных'
      const diff = current - previous
      const percent = (diff / Math.abs(previous)) * 100
      return `${diff > 0 ? '+' : ''}${percent.toFixed(1)}%`
    })

    const savingsChangeClass = computed(() => {
      const current = monthlyIncome.value - monthlyExpense.value
      const previous =
        previousMonthData.value.income - previousMonthData.value.expense
      if (previous === 0) return ''
      return current > previous ? 'text-success' : 'text-danger'
    })

    // ===== КАТЕГОРИИ =====
    const availableCategories = computed(() => {
      const categories =
        newTransaction.value.type === 'income'
          ? incomeCategories.value
          : expenseCategories.value
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

    // ===== МЕТОДЫ =====
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
              code,
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
      const nowDate = new Date()
      const month = nowDate.getMonth() + 1
      const year = nowDate.getFullYear()

      try {
        const expenseStats = await apiService.getStatistics(month, year, 'expense')
        monthlyExpense.value = parseFloat(expenseStats.total_amount) || 0

        const incomeStats = await apiService.getStatistics(month, year, 'income')
        monthlyIncome.value = parseFloat(incomeStats.total_amount) || 0
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

        const incomeData = await apiService.getTransactions({
          page: 1,
          page_size: 5,
          type: 'income'
        })
        incomeTransactionsList.value = (incomeData.results || []).map(t => ({
          ...t,
          transaction_type: 'income'
        }))

        const expenseData = await apiService.getTransactions({
          page: 1,
          page_size: 5,
          type: 'expense'
        })
        expenseTransactionsList.value = (expenseData.results || []).map(t => ({
          ...t,
          transaction_type: 'expense'
        }))

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

    // ===== LIFECYCLE =====
    onMounted(() => {
      updateViewport()
      window.addEventListener('resize', updateViewport)
      loadData()
      fetchExchangeRates()
      ratesUpdateInterval = setInterval(fetchExchangeRates, 3600000)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', updateViewport)
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
      previousMonth,
      previousMonthData,
      daysLeftInMonth,
      averageDailyIncome,
      averageDailyExpense,
      dailyBudget,
      forecastBalance,
      forecastWithExpectedIncome,
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
      formatShortDate,
      formatMonthYear,
      // Карусель
      currentStatIndex,
      isMobileView,
      statCards,
      cardPosition,
      onTouchStart,
      onTouchMove,
      onTouchEnd,
      onMouseDown
    }
  }
}
</script>

<style scoped>
/* ============================================================
   БАЗОВЫЕ СТИЛИ
   ============================================================ */
.dashboard-container {
  padding-top: 0.5rem;
}

.dashboard-title {
  margin-bottom: 2rem;
  margin-top: 0;
}

/* ---------- Панель действий и курсы ---------- */
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

/* ---------- Карточки ---------- */
.card {
  background: var(--white, #fff);
  border-radius: var(--radius, 12px);
  padding: 1.25rem;
  box-shadow: var(--shadow, 0 2px 8px rgba(0, 0, 0, 0.08));
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
  border-bottom: 2px solid var(--light-color, #f3f4f6);
  flex-wrap: wrap;
  gap: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.comparison-period {
  font-size: 0.875rem;
  color: var(--gray-color, #6b7280);
  font-weight: 500;
}

/* ============================================================
   СТАТИСТИКА: ДЕСКТОП — СЕТКА 3 КОЛОНКИ
   ============================================================ */
.stats-carousel {
  margin-bottom: 2rem;
}

.stats-carousel-track {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

/* ===== Базовые стили карточки ===== */
.stat-card {
  border-radius: var(--radius, 12px);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow, 0 4px 12px rgba(0, 0, 0, 0.08));
  box-sizing: border-box;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 110px;
  color: white;
}

.stat-title {
  font-size: 0.85rem;
  margin-bottom: 0.4rem;
  color: #1f2937;
}

.stat-value {
  font-size: 1.6rem;
  font-weight: 700;
  line-height: 1.2;
  word-break: break-word;
}

/* ===== Цвета карточек ===== */

/* Баланс — белый */
.stat-card-balance {
  background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%);
  border: 1px solid #e5e7eb;
}

.stat-card-balance .stat-title {
  color: #6b7280;
}

.stat-card-balance .stat-value {
  color: #1f2937;
}

/* Расходы — красный */
.stat-card-expense {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-card-expense .stat-title {
  color: #ffffff;
}
.stat-card-expense .stat-value {
  color: #ffffff;
}

/* Доходы — синий */
.stat-card-income {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-card-income .stat-title {
  color: #ffffff;
}
.stat-card-income .stat-value {
  color: #ffffff;
}

/* ===== Точки-индикаторы ===== */
.stats-dots {
  display: none;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.stats-dots.is-mobile {
  display: flex;
}

.stats-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #d1d5db;
  transition: all 0.25s ease;
  cursor: pointer;
}

.stats-dot.active {
  width: 24px;
  border-radius: 4px;
  background: var(--primary-color, #667eea);
}

/* ===== МОБИЛКА: СТЕК КАРТОЧЕК ===== */
.stats-carousel.is-mobile {
  position: relative;
  height: 150px;
  overflow: visible;
}

.stats-carousel-track.is-mobile {
  position: relative;
  display: block;
  width: 100%;
  height: 100%;
}

.stats-carousel-track.is-mobile .stat-card {
  position: absolute;
  top: 0;
  left: 50%;
  width: calc(100% - 24px);
  height: 100%;
  transform: translateX(-50%);
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.35s ease;
  will-change: transform;
}

/* Общие цвета текста */
.text-success {
  color: var(--secondary-color, #10b981);
}

.text-danger {
  color: var(--danger-color, #ef4444);
}

/* ============================================================
   ИНСАЙТЫ
   ============================================================ */
.insights-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

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

/* ---------- Карточка сравнения ---------- */
.comparison-card {
  background: var(--white, #fff);
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
  background: var(--light-color, #f3f4f6);
}

.comparison-item.highlight {
  background: #f3f4f6;
  border: 2px solid var(--primary-color, #667eea);
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

/* ============================================================
   МОДАЛКА
   ============================================================ */
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
  border-radius: var(--radius, 12px);
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
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color, #f3f4f6);
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
  border: 1px solid var(--light-color, #f3f4f6);
  border-radius: var(--radius, 12px);
  font-size: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--radius, 12px);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
}

.btn-primary {
  background: var(--primary-color, #667eea);
  color: white;
}

.btn-secondary {
  background: var(--light-color, #f3f4f6);
  color: var(--dark-color, #1f2937);
}

.btn-success {
  background: var(--secondary-color, #10b981);
  color: white;
}

/* ============================================================
   АДАПТИВНОСТЬ (общие блоки)
   ============================================================ */
@media (max-width: 1024px) {
  .insights-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-title {
    text-align: center;
  }

  .forecast-details {
    grid-template-columns: 1fr 1fr;
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