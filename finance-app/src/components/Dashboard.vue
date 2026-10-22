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

    <!-- ============================================================ -->
    <!-- ИНСАЙТЫ                                                       -->
    <!-- ============================================================ -->
    <InsightsWidget ref="insightsWidgetRef" />

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

    <!-- ============================================================ -->
    <!-- ВИДЖЕТ БЮДЖЕТА МЕСЯЦА                                         -->
    <!-- ============================================================ -->
    <div
      v-if="budgetSummary && budgetSummary.total_budget"
      class="card budget-widget"
      @click="$router.push('/budgets')"
    >
      <div class="budget-widget-header">
        <h3 class="card-title">
          <i class="fas fa-wallet"></i> Бюджет месяца
        </h3>
        <i class="fas fa-chevron-right budget-widget-arrow"></i>
      </div>

      <div class="budget-widget-amounts">
        <span
          class="budget-widget-spent"
          :class="budgetSummary.total_budget.is_exceeded ? 'text-danger' : ''"
        >
          {{ formatCurrency(budgetSummary.total_budget.spent) }}
        </span>
        <span class="budget-widget-sep">из</span>
        <span class="budget-widget-limit">
          {{ formatCurrency(budgetSummary.total_budget.amount) }}
        </span>
      </div>

      <div class="budget-widget-progress">
        <div class="progress-bar">
          <div
            class="progress-fill"
            :class="budgetPercentClass"
            :style="{ width: Math.min(budgetSummary.total_budget.percent, 100) + '%' }"
          ></div>
        </div>
        <div class="budget-widget-info">
          <span>{{ budgetSummary.total_budget.percent }}%</span>
          <span
            :class="budgetSummary.total_budget.remaining >= 0 ? 'text-success' : 'text-danger'"
          >
            {{ budgetSummary.total_budget.remaining >= 0 ? 'Осталось' : 'Перерасход' }}:
            {{ formatCurrency(Math.abs(budgetSummary.total_budget.remaining)) }}
          </span>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- ДИНАМИКА БАЛАНСА                                              -->
    <!-- ============================================================ -->
    <div v-if="activeAccounts.length > 0" class="card balance-history-card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-chart-line"></i> Динамика баланса
        </h3>
        <div class="history-controls">
          <div class="history-range">
            <button
              v-for="range in historyRanges"
              :key="range.value"
              class="range-btn"
              :class="{ active: historyRange === range.value }"
              @click="historyRange = range.value"
            >
              {{ range.label }}
            </button>
          </div>
          <div class="history-mode">
            <button
              class="range-btn"
              :class="{ active: historyMode === 'all' }"
              @click="historyMode = 'all'"
            >
              Все счета
            </button>
            <button
              class="range-btn"
              :class="{ active: historyMode === 'total' }"
              @click="historyMode = 'total'"
            >
              Только итог
            </button>
          </div>
        </div>
      </div>

      <div class="history-body">
        <div v-if="historyLoading" class="history-loading">
          <i class="fas fa-spinner fa-spin"></i>
          <span>Загрузка истории...</span>
        </div>

        <div v-else-if="historyError" class="history-error">
          <i class="fas fa-exclamation-triangle"></i>
          <span>{{ historyError }}</span>
          <button class="btn btn-sm btn-primary" @click="loadBalanceHistory">
            <i class="fas fa-redo"></i> Повторить
          </button>
        </div>

        <template v-else>
          <div class="history-chart-wrapper">
            <canvas
              ref="historyCanvas"
              class="history-canvas"
              @mousemove="onHistoryMouseMove"
              @mouseleave="onHistoryMouseLeave"
            ></canvas>

            <div
              v-if="historyTooltip.visible"
              class="history-tooltip"
              :style="{
                left: historyTooltip.x + 'px',
                top: historyTooltip.y + 'px'
              }"
            >
              <div class="history-tooltip-date">{{ historyTooltip.date }}</div>
              <div
                v-for="row in historyTooltip.rows"
                :key="row.id"
                class="history-tooltip-row"
              >
                <span class="history-tooltip-color" :style="{ background: row.color }"></span>
                <span class="history-tooltip-name">{{ row.name }}</span>
                <span class="history-tooltip-value">{{ formatCurrency(row.value) }}</span>
              </div>
              <div class="history-tooltip-total">
                <span>Итого:</span>
                <strong>{{ formatCurrency(historyTooltip.total) }}</strong>
              </div>
            </div>
          </div>

          <div v-if="historyMode === 'all' && historyAccounts.length > 0" class="history-legend">
            <button
              v-for="acc in historyAccounts"
              :key="acc.id"
              class="history-legend-item"
              :class="{ 'is-off': !visibleHistoryAccounts.has(acc.id) }"
              @click="toggleHistoryAccount(acc.id)"
            >
              <span class="history-legend-color" :style="{ background: acc.color }"></span>
              <span class="history-legend-name">{{ acc.name }}</span>
              <span class="history-legend-value">
                {{ formatCompactCurrency(acc.lastBalance) }}
              </span>
            </button>
          </div>

          <div class="history-footer">
            <div class="history-stats">
              <div class="history-stat">
                <span class="history-stat-label">Изменение за период</span>
                <span class="history-stat-value" :class="historyChangeClass">
                  {{ historyChange >= 0 ? '+' : '' }}{{ formatCurrency(historyChange) }}
                  <small>({{ historyChangePercent > 0 ? '+' : '' }}{{ historyChangePercent }}%)</small>
                </span>
              </div>
              <div class="history-stat">
                <span class="history-stat-label">Начало периода</span>
                <span class="history-stat-value">{{ formatCurrency(historyStartBalance) }}</span>
              </div>
              <div class="history-stat">
                <span class="history-stat-label">Конец периода</span>
                <span class="history-stat-value">{{ formatCurrency(historyEndBalance) }}</span>
              </div>
              <div class="history-stat">
                <span class="history-stat-label">Минимум / Максимум</span>
                <span class="history-stat-value">
                  {{ formatCompactCurrency(historyMinTotal) }} /
                  {{ formatCompactCurrency(historyMaxTotal) }}
                </span>
              </div>
            </div>
            <div class="history-period-label">
              {{ historyPeriodLabel }}
            </div>
          </div>
        </template>
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
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import apiService from '../services/api.js'
import InsightsWidget from './InsightsWidget.vue'

// =============================================================================
// Константы
// =============================================================================
const DISTRIBUTION_COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1',
  '#14b8a6', '#a855f7'
]

// =============================================================================
// Утилиты
// =============================================================================
const formatDateKey = (d) => {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const toNumber = (value) => {
  const n = parseFloat(value)
  return Number.isFinite(n) ? n : 0
}

const parentWidth = (canvas, fallback = 800) => {
  const wrapper = canvas.parentElement
  return wrapper ? wrapper.clientWidth : fallback
}

const setupCanvas = (canvas, cssWidth, cssHeight) => {
  const dpr = window.devicePixelRatio || 1
  canvas.width = cssWidth * dpr
  canvas.height = cssHeight * dpr
  canvas.style.width = `${cssWidth}px`
  canvas.style.height = `${cssHeight}px`
  const ctx = canvas.getContext('2d')
  ctx.setTransform(1, 0, 0, 1, 0, 0)
  ctx.scale(dpr, dpr)
  ctx.clearRect(0, 0, cssWidth, cssHeight)
  return { ctx, cssWidth, cssHeight }
}

export default {
  name: 'Dashboard',
  components: { InsightsWidget },
  setup() {
    // =========================================================================
    // Состояние — счета
    // =========================================================================
    const accounts = ref([])
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
    let insightsRefreshInterval = null

    // Ссылка на дочерний виджет инсайтов
    const insightsWidgetRef = ref(null)

    // --- ТЕМНАЯ ТЕМА ДЛЯ CANVAS ---
    const isDarkTheme = ref(document.documentElement.getAttribute('data-theme') === 'dark')

    // Бюджет
    const budgetSummary = ref(null)
    const budgetLoading = ref(false)

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

    // =========================================================================
    // Карусель статистики
    // =========================================================================
    const currentStatIndex = ref(0)
    const touchStartX = ref(0)
    const touchDeltaX = ref(0)
    const isDragging = ref(false)
    const SWIPE_THRESHOLD = 50

    const isMobileView = ref(false)

    const updateViewport = () => {
      isMobileView.value = window.innerWidth <= 1024
    }

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

    const cardPosition = (index) => {
      if (!isMobileView.value) return {}

      const offset = index - currentStatIndex.value

      if (Math.abs(offset) > 1) {
        return { display: 'none' }
      }

      if (offset === 0) {
        return {
          transform: 'translateX(-50%) scale(1)',
          zIndex: 3,
          opacity: 1
        }
      }

      const direction = offset > 0 ? 1 : -1
      return {
        transform: `translateX(calc(-50% + ${direction * 20}px)) scale(0.94)`,
        zIndex: 2,
        opacity: 1
      }
    }

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

    // =========================================================================
    // Форматирование
    // =========================================================================
    const formatCurrency = (value) => {
      if (value === null || value === undefined || isNaN(value)) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB'
      }).format(value)
    }

    const formatCompactCurrency = (value) => {
      if (value === null || value === undefined || value === '') return '0'
      const abs = Math.abs(value)
      if (abs >= 1_000_000) return (value / 1_000_000).toFixed(1) + 'M'
      if (abs >= 1_000) return (value / 1_000).toFixed(0) + 'k'
      return String(Math.round(value))
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

    // =========================================================================
    // Computed — счета
    // =========================================================================
    const totalBalance = computed(() => {
      return accounts.value
        .filter(acc => acc.is_active)
        .reduce((sum, acc) => sum + parseFloat(acc.balance || 0), 0)
    })

    const activeAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active)
    })

    // =========================================================================
    // Виджет бюджета
    // =========================================================================
    const budgetPercentClass = computed(() => {
      const p = budgetSummary.value?.total_budget?.percent || 0
      if (p >= 100) return 'progress-danger'
      if (p >= 80) return 'progress-warning'
      return 'progress-success'
    })

    const loadBudgetSummary = async () => {
      budgetLoading.value = true
      try {
        const nowDate = new Date()
        const dateParam = `${nowDate.getFullYear()}-${String(nowDate.getMonth() + 1).padStart(2, '0')}-01`
        const data = await apiService.getBudgetSummary('monthly', dateParam)
        budgetSummary.value = data
      } catch (error) {
        console.error('Error loading budget summary:', error)
        budgetSummary.value = null
      } finally {
        budgetLoading.value = false
      }
    }

    // =========================================================================
    // Динамика баланса — состояние
    // =========================================================================
    const historyCanvas = ref(null)
    const historyRange = ref(30)
    const historyRanges = [
      { value: 7, label: '7 дней' },
      { value: 30, label: '30 дней' },
      { value: 90, label: '90 дней' },
      { value: 180, label: '180 дней' }
    ]
    const historyMode = ref('all')
    const historyLoading = ref(false)
    const historyError = ref('')
    const historyRawData = ref(null)
    const visibleHistoryAccounts = ref(new Set())
    const historyChartMetrics = ref({
      paddingLeft: 60, paddingRight: 20, paddingTop: 20, paddingBottom: 40
    })

    const historyTooltip = ref({
      visible: false, x: 0, y: 0, date: '', rows: [], total: 0
    })

    const historyAccounts = computed(() => {
      if (!historyRawData.value?.accounts) return []
      return historyRawData.value.accounts.map((acc, index) => {
        const series = historyRawData.value.results.map((r) => ({
          date: r.date,
          value: toNumber(r.accounts[String(acc.id)])
        }))
        return {
          id: acc.id,
          name: acc.name,
          color: DISTRIBUTION_COLORS[index % DISTRIBUTION_COLORS.length],
          series,
          lastBalance: series.length > 0 ? series[series.length - 1].value : 0
        }
      })
    })

    const historyTotalSeries = computed(() => {
      if (!historyRawData.value?.results) return []
      return historyRawData.value.results.map((r) => ({
        date: r.date,
        value: toNumber(r.total)
      }))
    })

    const historyStartBalance = computed(() => {
      const s = historyTotalSeries.value
      return s.length > 0 ? s[0].value : 0
    })

    const historyEndBalance = computed(() => {
      const s = historyTotalSeries.value
      return s.length > 0 ? s[s.length - 1].value : 0
    })

    const historyChange = computed(() => historyEndBalance.value - historyStartBalance.value)

    const historyChangePercent = computed(() => {
      if (historyStartBalance.value === 0) return 0
      return ((historyChange.value / Math.abs(historyStartBalance.value)) * 100).toFixed(1)
    })

    const historyChangeClass = computed(() => {
      if (historyChange.value > 0) return 'text-success'
      if (historyChange.value < 0) return 'text-danger'
      return ''
    })

    const historyMinTotal = computed(() => {
      const s = historyTotalSeries.value
      return s.length === 0 ? 0 : Math.min(...s.map((p) => p.value))
    })

    const historyMaxTotal = computed(() => {
      const s = historyTotalSeries.value
      return s.length === 0 ? 0 : Math.max(...s.map((p) => p.value))
    })

    const historyPeriodLabel = computed(() => {
      const results = historyRawData.value?.results
      if (!results?.length) return ''
      const first = results[0].date
      const last = results[results.length - 1].date
      return `${formatDateShortLabel(first)} — ${formatDateShortLabel(last)}`
    })

    const formatDateShortLabel = (iso) => {
      if (!iso) return ''
      return new Date(iso).toLocaleDateString('ru-RU', {
        day: '2-digit', month: '2-digit', year: 'numeric'
      })
    }

    // =========================================================================
    // Динамика баланса — отрисовка
    // =========================================================================
    const getCanvasColors = () => ({
      grid: isDarkTheme.value ? '#374151' : '#e5e7eb',
      text: isDarkTheme.value ? '#9ca3af' : '#9ca3af',
      textBold: isDarkTheme.value ? '#f3f4f6' : '#6b7280',
      totalLine: isDarkTheme.value ? '#f3f4f6' : '#111827'
    })

    const drawHistoryChart = () => {
      const canvas = historyCanvas.value
      if (!canvas) return
      const totalSeries = historyTotalSeries.value

      if (totalSeries.length === 0) {
        setupCanvas(canvas, parentWidth(canvas, 900), 100)
        return
      }

      const cssWidth = parentWidth(canvas, 900)
      const cssHeight = 320
      const { ctx } = setupCanvas(canvas, cssWidth, cssHeight)
      const colors = getCanvasColors()

      const paddingLeft = 60
      const paddingRight = 20
      const paddingTop = 20
      const paddingBottom = 40
      historyChartMetrics.value = { paddingLeft, paddingRight, paddingTop, paddingBottom }

      const chartWidth = cssWidth - paddingLeft - paddingRight
      const chartHeight = cssHeight - paddingTop - paddingBottom

      const visibleSeries = []
      if (historyMode.value === 'total') {
        visibleSeries.push({
          id: 'total', name: 'Итого', color: '#3b82f6',
          series: totalSeries, isTotal: true
        })
      } else {
        historyAccounts.value.forEach((acc) => {
          if (visibleHistoryAccounts.value.has(acc.id)) {
            visibleSeries.push({
              id: acc.id, name: acc.name, color: acc.color,
              series: acc.series, isTotal: false
            })
          }
        })
        visibleSeries.push({
          id: 'total', name: 'Итого', color: colors.totalLine,
          series: totalSeries, isTotal: true
        })
      }

      const allValues = visibleSeries.flatMap((s) => s.series.map((p) => p.value))
      let minValue = Math.min(...allValues, 0)
      let maxValue = Math.max(...allValues, 0)
      const range = maxValue - minValue || 1
      minValue -= range * 0.05
      maxValue += range * 0.05

      const xStep = totalSeries.length > 1 ? chartWidth / (totalSeries.length - 1) : 0
      const yScale = (v) =>
        paddingTop + chartHeight - ((v - minValue) / (maxValue - minValue)) * chartHeight

      ctx.strokeStyle = colors.grid
      ctx.lineWidth = 1
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.fillStyle = colors.text
      ctx.textAlign = 'right'
      ctx.textBaseline = 'middle'

      for (let i = 0; i <= 5; i++) {
        const y = paddingTop + chartHeight - (i / 5) * chartHeight
        ctx.beginPath()
        ctx.moveTo(paddingLeft, y)
        ctx.lineTo(cssWidth - paddingRight, y)
        ctx.stroke()
        ctx.fillText(formatCompactCurrency(minValue + ((maxValue - minValue) / 5) * i), paddingLeft - 6, y)
      }

      if (minValue < 0 && maxValue > 0) {
        const y0 = yScale(0)
        ctx.strokeStyle = colors.text
        ctx.setLineDash([4, 4])
        ctx.beginPath()
        ctx.moveTo(paddingLeft, y0)
        ctx.lineTo(cssWidth - paddingRight, y0)
        ctx.stroke()
        ctx.setLineDash([])
      }

      visibleSeries.forEach((s) => {
        if (s.series.length === 0) return
        ctx.beginPath()
        ctx.strokeStyle = s.color
        ctx.lineWidth = s.isTotal ? 3 : 1.75
        ctx.lineJoin = 'round'
        ctx.lineCap = 'round'

        s.series.forEach((p, i) => {
          const x = paddingLeft + i * xStep
          const y = yScale(p.value)
          if (i === 0) ctx.moveTo(x, y)
          else ctx.lineTo(x, y)
        })
        ctx.stroke()

        if (s.series.length <= 40) {
          s.series.forEach((p, i) => {
            const x = paddingLeft + i * xStep
            const y = yScale(p.value)
            ctx.beginPath()
            ctx.fillStyle = s.color
            ctx.arc(x, y, s.isTotal ? 3 : 2, 0, 2 * Math.PI)
            ctx.fill()
          })
        }
      })

      // Подписи по оси X
      ctx.fillStyle = colors.textBold
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'top'

      const MIN_LABEL_SPACING = 36
      const maxLabels = Math.max(2, Math.floor(chartWidth / MIN_LABEL_SPACING))
      const step = Math.max(1, Math.ceil(totalSeries.length / maxLabels))

      let lastLabelX = -Infinity
      totalSeries.forEach((p, i) => {
        const isFirst = i === 0
        const isLast = i === totalSeries.length - 1
        const showByStep = i % step === 0
        if (!isFirst && !isLast && !showByStep) return

        const x = paddingLeft + i * xStep
        if (x - lastLabelX < MIN_LABEL_SPACING * 0.9) {
          if (!isFirst) return
        }

        const label = new Date(p.date).toLocaleDateString('ru-RU', {
          day: '2-digit', month: '2-digit'
        })
        ctx.fillText(label, x, paddingTop + chartHeight + 8)
        lastLabelX = x
      })
    }

    const onHistoryMouseMove = (event) => {
      const canvas = historyCanvas.value
      if (!canvas) return
      const totalSeries = historyTotalSeries.value
      if (totalSeries.length === 0) return

      const rect = canvas.getBoundingClientRect()
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top

      const { paddingLeft, paddingRight } = historyChartMetrics.value
      const chartWidth = rect.width - paddingLeft - paddingRight

      if (x < paddingLeft || x > rect.width - paddingRight) {
        historyTooltip.value.visible = false
        return
      }

      const xStep = totalSeries.length > 1 ? chartWidth / (totalSeries.length - 1) : 0
      const idx = Math.round((x - paddingLeft) / xStep)
      const clampedIdx = Math.max(0, Math.min(totalSeries.length - 1, idx))
      const point = totalSeries[clampedIdx]

      const rows = []
      if (historyMode.value === 'total') {
        rows.push({ id: 'total', name: 'Итого', color: '#3b82f6', value: point.value })
      } else {
        historyAccounts.value.forEach((acc) => {
          if (!visibleHistoryAccounts.value.has(acc.id)) return
          const p = acc.series[clampedIdx]
          if (p) {
            rows.push({ id: acc.id, name: acc.name, color: acc.color, value: p.value })
          }
        })
      }

      historyTooltip.value = {
        visible: true,
        x,
        y,
        date: new Date(point.date).toLocaleDateString('ru-RU', {
          day: '2-digit', month: '2-digit', year: 'numeric'
        }),
        rows,
        total: point.value
      }
    }

    const onHistoryMouseLeave = () => {
      historyTooltip.value.visible = false
    }

    const scheduleHistoryDraw = () => {
      nextTick(() => setTimeout(drawHistoryChart, 50))
    }

    const loadBalanceHistory = async () => {
      historyLoading.value = true
      historyError.value = ''
      try {
        const dateTo = new Date()
        const dateFrom = new Date()
        dateFrom.setDate(dateFrom.getDate() - historyRange.value + 1)

        const data = await apiService.getBalanceHistory(
          formatDateKey(dateFrom),
          formatDateKey(dateTo)
        )
        historyRawData.value = data
        scheduleHistoryDraw()
      } catch (error) {
        console.error('Error loading balance history:', error)
        historyError.value = 'Не удалось загрузить историю баланса. Проверьте соединение.'
        historyRawData.value = null
      } finally {
        historyLoading.value = false
      }
    }

    const toggleHistoryAccount = (accountId) => {
      const s = new Set(visibleHistoryAccounts.value)
      if (s.has(accountId)) s.delete(accountId)
      else s.add(accountId)
      visibleHistoryAccounts.value = s
      scheduleHistoryDraw()
    }

    // =========================================================================
    // Загрузка статистики
    // =========================================================================
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

    // =========================================================================
    // Прогноз
    // =========================================================================
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

    // =========================================================================
    // Сравнение
    // =========================================================================
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

    // =========================================================================
    // Категории
    // =========================================================================
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

    // =========================================================================
    // Методы
    // =========================================================================
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
        // Счета и категории не зависят друг от друга — грузим параллельно
        const [accountsData, incomeCatData, expenseCatData] = await Promise.all([
          apiService.getAccounts(1, 100),
          apiService.getCategories('income', 1, 100, true),
          apiService.getCategories('expense', 1, 100, true),
        ])

        accounts.value = accountsData.results[0]?.accounts || []
        incomeCategories.value = incomeCatData.results || []
        expenseCategories.value = expenseCatData.results || []

        // Статистика и бюджет — параллельно
        await Promise.all([
          loadMonthlyStatistics(),
          loadPreviousMonthStatistics(),
          loadBalanceHistory(),
          loadBudgetSummary()
        ])
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

        // Обновляем инсайты (могут появиться дубликаты/скачки)
        if (insightsWidgetRef.value?.loadInsights) {
          await insightsWidgetRef.value.loadInsights()
        }
      } catch (error) {
        console.error('Error creating transaction:', error)
        alert('Ошибка при создании транзакции')
      }
    }

    // =========================================================================
    // Watchers
    // =========================================================================
    watch(
      historyAccounts,
      (list) => {
        if (list.length === 0) return
        const ids = list.map((a) => a.id)
        const currentIds = Array.from(visibleHistoryAccounts.value)
        const sameSet =
          currentIds.length === ids.length && ids.every((id) => currentIds.includes(id))
        if (!sameSet) visibleHistoryAccounts.value = new Set(ids)
      },
      { immediate: true }
    )

    watch(historyRange, () => loadBalanceHistory())
    watch(historyMode, () => scheduleHistoryDraw())
    watch(visibleHistoryAccounts, () => scheduleHistoryDraw(), { deep: true })

    const handleResize = () => scheduleHistoryDraw()

    // Слушатель изменения темы
    const themeObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'data-theme') {
          isDarkTheme.value = document.documentElement.getAttribute('data-theme') === 'dark'
          scheduleHistoryDraw()
        }
      })
    })

    // =========================================================================
    // Lifecycle
    // =========================================================================
    onMounted(() => {
      updateViewport()
      window.addEventListener('resize', updateViewport)
      window.addEventListener('resize', handleResize)
      themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })

      loadData()
      fetchExchangeRates()
      ratesUpdateInterval = setInterval(fetchExchangeRates, 3600000)

      // Автообновление инсайтов раз в 5 минут
      insightsRefreshInterval = setInterval(() => {
        insightsWidgetRef.value?.loadInsights?.()
      }, 5 * 60 * 1000)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', updateViewport)
      window.removeEventListener('resize', handleResize)
      themeObserver.disconnect()
      if (ratesUpdateInterval) {
        clearInterval(ratesUpdateInterval)
      }
      if (insightsRefreshInterval) {
        clearInterval(insightsRefreshInterval)
        insightsRefreshInterval = null
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
      formatCompactCurrency,
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
      onMouseDown,
      // Бюджет
      budgetSummary,
      budgetLoading,
      budgetPercentClass,
      // Динамика баланса
      historyCanvas,
      historyRange,
      historyRanges,
      historyMode,
      historyLoading,
      historyError,
      historyAccounts,
      visibleHistoryAccounts,
      historyTotalSeries,
      historyStartBalance,
      historyEndBalance,
      historyChange,
      historyChangePercent,
      historyChangeClass,
      historyMinTotal,
      historyMaxTotal,
      historyPeriodLabel,
      historyTooltip,
      loadBalanceHistory,
      toggleHistoryAccount,
      onHistoryMouseMove,
      onHistoryMouseLeave,
      // Инсайты
      insightsWidgetRef
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
  color: var(--dark-color);
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
  background: var(--light-color);
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
  color: var(--gray-color);
}

.rate-value {
  color: var(--dark-color);
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
  background: var(--white);
  border-radius: var(--radius, 12px);
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--dark-color);
}

.comparison-period {
  font-size: 0.875rem;
  color: var(--gray-color);
  font-weight: 500;
}

/* ============================================================
   СТАТИСТИКА
   ============================================================ */
.stats-carousel {
  margin-bottom: 2rem;
}

.stats-carousel-track {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.stat-card {
  border-radius: var(--radius, 12px);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow);
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
}

.stat-value {
  font-size: 1.6rem;
  font-weight: 700;
  line-height: 1.2;
  word-break: break-word;
}

/* Карточка баланса — использует переменные темы */
.stat-card-balance {
  background: linear-gradient(135deg, var(--white) 0%, var(--light-color) 100%);
  border: 1px solid var(--light-color);
}

.stat-card-balance .stat-title {
  color: var(--gray-color);
}

.stat-card-balance .stat-value {
  color: var(--dark-color);
}

.stat-card-expense {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-card-expense .stat-title {
  color: #ffffff;
}
.stat-card-expense .stat-value {
  color: #ffffff;
}

.stat-card-income {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-card-income .stat-title {
  color: #ffffff;
}
.stat-card-income .stat-value {
  color: #ffffff;
}

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
  background: var(--gray-color);
  transition: all 0.25s ease;
  cursor: pointer;
}

.stats-dot.active {
  width: 24px;
  border-radius: 4px;
  background: var(--primary-color);
}

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

.text-success {
  color: var(--secondary-color);
}

.text-danger {
  color: var(--danger-color);
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

/* Карточка прогноза — фиолетовый градиент отлично смотрится в обеих темах */
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

.progress-fill.progress-low { background: #34d399; }
.progress-fill.progress-medium { background: #fbbf24; }
.progress-fill.progress-high { background: #f87171; }

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
  color: var(--dark-color);
}

.comparison-item.highlight {
  background: var(--light-color);
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

:global(:root[data-theme="dark"]) .comparison-change {
  background: rgba(255, 255, 255, 0.1);
}

/* ============================================================
   ВИДЖЕТ БЮДЖЕТА
   ============================================================ */
.budget-widget {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-bottom: 1.5rem;
  background: var(--white);
}

.budget-widget:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.budget-widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.budget-widget-header .card-title {
  font-size: 1.1rem;
}

.budget-widget-arrow {
  color: var(--gray-color);
  font-size: 0.875rem;
}

.budget-widget-amounts {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.budget-widget-spent {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--dark-color);
}

.budget-widget-sep {
  color: var(--gray-color);
  font-size: 0.875rem;
}

.budget-widget-limit {
  color: var(--gray-color);
  font-size: 1rem;
}

.budget-widget-progress .progress-bar {
  height: 8px;
  background: var(--light-color);
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.budget-widget-progress .progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.progress-success { background: #10b981; }
.progress-warning { background: #f59e0b; }
.progress-danger  { background: #ef4444; }

.budget-widget-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--gray-color);
  font-weight: 500;
}

/* ============================================================
   ДИНАМИКА БАЛАНСА
   ============================================================ */
.balance-history-card {
  margin-bottom: 1.5rem;
  background: var(--white);
}

.history-controls {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.history-range,
.history-mode {
  display: flex;
  gap: 0.25rem;
  background: var(--light-color);
  padding: 0.25rem;
  border-radius: var(--radius);
}

.range-btn {
  padding: 0.375rem 0.75rem;
  border: none;
  background: transparent;
  border-radius: calc(var(--radius) - 2px);
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--gray-color);
  cursor: pointer;
  transition: all 0.2s;
}

.range-btn:hover {
  color: var(--dark-color);
}

.range-btn.active {
  background: var(--white);
  color: var(--primary-color);
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.history-body {
  padding: 0.5rem 0;
}

.history-loading,
.history-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  color: var(--gray-color);
  font-size: 0.9rem;
}

.history-error {
  flex-direction: column;
  color: var(--danger-color);
}

.history-error i {
  font-size: 2rem;
}

.history-chart-wrapper {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.history-canvas {
  display: block;
  width: 100%;
  cursor: crosshair;
}

.history-tooltip {
  position: absolute;
  z-index: 10;
  background: rgba(17, 24, 39, 0.95);
  color: white;
  border-radius: var(--radius);
  padding: 0.625rem 0.75rem;
  font-size: 0.75rem;
  pointer-events: none;
  transform: translate(-50%, -100%);
  margin-top: -10px;
  min-width: 180px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.history-tooltip::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: rgba(17, 24, 39, 0.95);
  border-bottom: none;
}

.history-tooltip-date {
  font-weight: 700;
  font-size: 0.8rem;
  margin-bottom: 0.4rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.history-tooltip-row {
  display: grid;
  grid-template-columns: 10px 1fr auto;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.25rem;
}

.history-tooltip-color {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.history-tooltip-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-tooltip-value {
  font-weight: 600;
  white-space: nowrap;
}

.history-tooltip-total {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.4rem;
  padding-top: 0.4rem;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  font-weight: 700;
}

.history-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.history-legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  background: var(--white);
  border: 1px solid var(--light-color);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--dark-color);
}

.history-legend-item:hover {
  background: var(--light-color);
}

.history-legend-item.is-off {
  opacity: 0.4;
  text-decoration: line-through;
}

.history-legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}

.history-legend-name {
  font-weight: 500;
}

.history-legend-value {
  color: var(--gray-color);
  font-size: 0.75rem;
}

.history-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
  flex-wrap: wrap;
  gap: 1rem;
}

.history-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.history-stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.history-stat-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: var(--gray-color);
  font-weight: 500;
}

.history-stat-value {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--dark-color);
}

.history-stat-value small {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--gray-color);
}

.history-period-label {
  font-size: 0.8rem;
  color: var(--gray-color);
  font-style: italic;
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
  background: var(--white);
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

.modal-header h3 {
  color: var(--dark-color);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--gray-color);
}

.modal-footer {
  display: flex;
  justify-content: center;
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
  color: var(--dark-color);
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--gray-color);
  border-radius: var(--radius);
  font-size: 1rem;
  background: var(--white);
  color: var(--dark-color);
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

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

/* ============================================================
   АДАПТИВНОСТЬ
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

  .budget-widget-spent {
    font-size: 1.5rem;
  }

  .history-controls {
    flex-direction: column;
    width: 100%;
  }

  .history-range,
  .history-mode {
    width: 100%;
  }

  .range-btn {
    flex: 1;
    font-size: 0.7rem;
    padding: 0.375rem 0.25rem;
  }

  .history-stats {
    gap: 1rem;
  }

  .history-stat-value {
    font-size: 0.85rem;
  }

  .history-footer {
    flex-direction: column;
    align-items: flex-start;
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

  .history-legend {
    gap: 0.375rem;
  }

  .history-legend-item {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
  }

  .history-stats {
    flex-direction: column;
    gap: 0.5rem;
  }

  .history-tooltip {
    min-width: 150px;
    font-size: 0.7rem;
  }
}
</style>