<template>
  <div class="statistics-page">
    <div class="page-header">
      <h1 class="page-title">Аналитика</h1>
    </div>

    <!-- Фильтры -->
    <div class="card filters-card">
      <div class="filters-header" @click="showFilters = !showFilters">
        <h3 class="filters-title">Фильтры</h3>
        <i :class="showFilters ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
      </div>

      <div class="filters-body" :class="{ 'filters-hidden': !showFilters }">
        <div class="filters-grid">
          <div class="filter-field">
            <label class="filter-label">Тип:</label>
            <select v-model="currentType" class="form-control">
              <option value="income">Доходы</option>
              <option value="expense">Расходы</option>
            </select>
          </div>

          <div class="filter-field">
            <label class="filter-label">Период:</label>
            <select v-model="selectedPeriod" class="form-control">
              <option value="month">За месяц</option>
              <option value="year">За год</option>
            </select>
          </div>

          <div class="filter-field" v-if="selectedPeriod === 'month'">
            <label class="filter-label">Год:</label>
            <select v-model="selectedYear" class="form-control">
              <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>

          <div class="filter-field" v-if="selectedPeriod === 'month'">
            <label class="filter-label">Месяц:</label>
            <select v-model="selectedMonth" class="form-control">
              <option v-for="(name, index) in months" :key="index" :value="index + 1">{{ name }}</option>
            </select>
          </div>

          <div class="filter-field" v-if="selectedPeriod === 'year'">
            <label class="filter-label">Год:</label>
            <select v-model="selectedYear" class="form-control">
              <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>

          <div class="filter-actions">
            <button @click="loadStatistics" class="btn btn-primary">Применить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Карточки статистики -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-card-title">Общая сумма</div>
        <div class="stat-card-value" :class="currentType === 'income' ? 'text-success' : 'text-danger'">
          {{ formatCurrency(totalAmount) }}
        </div>
      </div>

      <div class="stat-card" v-if="selectedPeriod === 'year'">
        <div class="stat-card-title">Транзакций</div>
        <div class="stat-card-value">{{ transactionCount }}</div>
      </div>

      <div class="stat-card" v-if="selectedPeriod === 'year'">
        <div class="stat-card-title">Средняя сумма</div>
        <div class="stat-card-value">{{ formatCurrency(averageAmount) }}</div>
      </div>

      <div class="stat-card" v-if="selectedPeriod === 'year' && monthlyAnalytics.length > 0">
        <div class="stat-card-title">Максимум</div>
        <div class="stat-card-value text-success">{{ formatCurrency(maxMonthAmount) }}</div>
        <div class="stat-card-subtitle">{{ maxMonthName }}</div>
      </div>

      <div class="stat-card" v-if="selectedPeriod === 'year' && monthlyAnalytics.length > 0">
        <div class="stat-card-title">Минимум</div>
        <div class="stat-card-value text-danger">{{ formatCurrency(minMonthAmount) }}</div>
        <div class="stat-card-subtitle">{{ minMonthName }}</div>
      </div>
    </div>

    <!-- Месячная статистика -->
    <div class="card full-width-card" v-if="selectedPeriod === 'month'">
      <div class="card-header">
        <h3 class="card-title">Разбивка по категориям</h3>
        <div class="sort-buttons">
          <button @click="sortCategories('desc')" class="btn-sort" :class="{ active: sortOrder === 'desc' }">
            <i class="fas fa-sort-amount-down"></i> По убыванию
          </button>
          <button @click="sortCategories('asc')" class="btn-sort" :class="{ active: sortOrder === 'asc' }">
            <i class="fas fa-sort-amount-up-alt"></i> По возрастанию
          </button>
        </div>
      </div>

      <!-- Круговая диаграмма на всю ширину -->
      <div class="pie-chart-section" v-if="statistics.length > 0">
        <div class="pie-chart-wrapper">
          <canvas id="pieChartCanvas" class="pie-chart-canvas"></canvas>
        </div>
        <div class="pie-chart-legend">
          <div v-for="category in statistics" :key="category.id" class="legend-item">
            <span class="legend-color" :style="{ backgroundColor: getCategoryColor(category.id) }"></span>
            <span class="legend-name">{{ category.name }}</span>
            <span class="legend-percent">{{ getPercentage(category.total) }}%</span>
          </div>
        </div>
      </div>

      <!-- Список категорий на всю ширину -->
      <div class="categories-list full-width">
        <div v-for="category in sortedStatistics" :key="category.id" class="category-item full-width-item">
          <div class="category-header" @click="category.children?.length && toggleCategory(category.id)">
            <div class="category-name">
              <i v-if="category.children?.length" :class="expandedCategories[category.id] ? 'fas fa-chevron-down' : 'fas fa-chevron-right'" class="expand-icon"></i>
              <i v-else class="fas fa-folder placeholder-icon"></i>
              <i class="fas fa-folder"></i>
              <span>{{ category.name }}</span>
            </div>
            <div class="category-total">{{ formatCurrency(category.total) }}</div>
          </div>

          <div class="progress-wrapper">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: getPercentage(category.total) + '%' }" :class="currentType === 'income' ? 'progress-income' : 'progress-expense'">
                <span class="progress-text">{{ getPercentage(category.total) }}%</span>
              </div>
            </div>
            <div class="progress-percent-info">{{ getPercentage(category.total) }}% от общей суммы</div>
          </div>

          <!-- Подкатегории -->
          <div v-if="category.children?.length" class="subcategories" v-show="expandedCategories[category.id]">
            <div v-for="child in sortedChildren(category.children)" :key="child.id" class="subcategory-item">
              <div class="subcategory-header">
                <div class="subcategory-name">
                  <i class="fas fa-level-down-alt"></i>
                  <span>{{ child.name }}</span>
                </div>
                <div class="subcategory-total">{{ formatCurrency(child.total) }}</div>
              </div>
              <div class="progress-bar subcategory-progress">
                <div class="progress-fill progress-subcategory" :style="{ width: getSubPercentage(category.total, child.total) + '%' }">
                  <span class="progress-text-small">{{ getSubPercentage(category.total, child.total) }}%</span>
                </div>
              </div>
              <div class="subcategory-percent">{{ getSubPercentage(category.total, child.total) }}% от категории</div>
            </div>
          </div>

          <div v-if="category.children?.length && !expandedCategories[category.id]" class="expand-hint" @click="toggleCategory(category.id)">
            <i class="fas fa-eye"></i> Показать подкатегории ({{ category.children.length }})
          </div>
        </div>

        <div v-if="statistics.length === 0" class="empty-state">
          <i class="fas fa-chart-bar"></i>
          <p>Нет данных за выбранный период</p>
        </div>
      </div>
    </div>

    <!-- Годовая статистика -->
    <div class="card full-width-card" v-if="selectedPeriod === 'year'">
      <div class="card-header">
        <h3 class="card-title">Аналитика по месяцам</h3>
      </div>

      <!-- Мобильные карточки -->
      <div class="mobile-months-grid">
        <div v-for="item in monthlyAnalytics" :key="item.period" class="mobile-month-card">
          <div class="mobile-month-header">
            <div class="mobile-month-name">
              <span class="month-name-text">{{ item.month_name }} {{ item.year }}</span>
              <span class="trend-badge" :class="getTrendBadgeClass(item)">{{ item.trend_vs_prev }}</span>
            </div>
            <div class="mobile-month-amount" :class="currentType === 'income' ? 'text-success' : 'text-danger'">
              {{ formatCurrency(item.total_amount) }}
            </div>
          </div>

          <div class="mobile-stats-grid">
            <div class="mobile-stat">
              <div class="mobile-stat-label">Транзакции</div>
              <div class="mobile-stat-value">{{ item.transaction_count }}</div>
            </div>
            <div class="mobile-stat">
              <div class="mobile-stat-label">Средняя</div>
              <div class="mobile-stat-value">{{ formatCurrency(item.avg_amount) }}</div>
            </div>
            <div class="mobile-stat">
              <div class="mobile-stat-label">Изменение</div>
              <div class="mobile-stat-value" :class="getTrendClass(item)">
                {{ item.change_vs_prev_percent !== 0 ? (item.change_vs_prev_percent > 0 ? '+' : '') + item.change_vs_prev_percent.toFixed(1) + '%' : '—' }}
              </div>
            </div>
            <div class="mobile-stat">
              <div class="mobile-stat-label">Абс. изм.</div>
              <div class="mobile-stat-value" :class="getTrendClass(item)">
                {{ item.absolute_change_vs_prev !== 0 ? (item.absolute_change_vs_prev > 0 ? '+' : '') + formatCurrency(Math.abs(item.absolute_change_vs_prev)) : '—' }}
              </div>
            </div>
          </div>

          <div class="mobile-progress">
            <div class="progress-label">Доля от максимума</div>
            <div class="progress-bar small">
              <div class="progress-fill" :style="{ width: getMonthPercentOfMax(item.total_amount) + '%' }" :class="currentType === 'income' ? 'progress-income' : 'progress-expense'">
                <span class="progress-text-small">{{ getMonthPercentOfMax(item.total_amount) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Десктоп таблица -->
      <div class="desktop-table-wrapper">
        <table class="analytics-table">
          <thead>
            <tr>
              <th>Месяц</th>
              <th>Сумма</th>
              <th>Транзакции</th>
              <th>Средняя</th>
              <th>Изменение</th>
              <th>Абс. изменение</th>
              <th>Доля от макс.</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in monthlyAnalytics" :key="item.period">
              <td class="table-month-cell">
                <strong>{{ item.month_name }} {{ item.year }}</strong>
                <span class="trend-badge small" :class="getTrendBadgeClass(item)">{{ item.trend_vs_prev }}</span>
              </td>
              <td :class="currentType === 'income' ? 'text-success' : 'text-danger'">
                <strong>{{ formatCurrency(item.total_amount) }}</strong>
              </td>
              <td>{{ item.transaction_count }}</td>
              <td>{{ formatCurrency(item.avg_amount) }}</td>
              <td :class="getTrendClass(item)">
                {{ item.change_vs_prev_percent !== 0 ? (item.change_vs_prev_percent > 0 ? '+' : '') + item.change_vs_prev_percent.toFixed(1) + '%' : '—' }}
              </td>
              <td :class="getTrendClass(item)">
                {{ item.absolute_change_vs_prev !== 0 ? (item.absolute_change_vs_prev > 0 ? '+' : '') + formatCurrency(Math.abs(item.absolute_change_vs_prev)) : '—' }}
              </td>
              <td>
                <div class="table-progress">
                  <div class="progress-bar small">
                    <div class="progress-fill" :style="{ width: getMonthPercentOfMax(item.total_amount) + '%' }" :class="currentType === 'income' ? 'progress-income' : 'progress-expense'"></div>
                  </div>
                  <span class="table-progress-value">{{ getMonthPercentOfMax(item.total_amount) }}%</span>
                </div>
              </td>
            </tr>
            <tr v-if="monthlyAnalytics.length === 0">
              <td colspan="7" class="text-center">Нет данных за выбранный год</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Годовая сводка -->
      <div class="year-summary" v-if="monthlyAnalytics.length > 0">
        <div class="summary-card">
          <div class="summary-label">Среднее за месяц</div>
          <div class="summary-value">{{ formatCurrency(averageMonthlyAmount) }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">Медиана</div>
          <div class="summary-value">{{ formatCurrency(medianMonthlyAmount) }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">Стандартное отклонение</div>
          <div class="summary-value">{{ formatCurrency(standardDeviation) }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">Коэф. вариации</div>
          <div class="summary-value">{{ coefficientOfVariation.toFixed(1) }}%</div>
        </div>
      </div>
    </div>

    <!-- График -->
    <div class="card full-width-card" v-if="selectedPeriod === 'year' && monthlyAnalytics.length > 0">
      <div class="card-header">
        <h3 class="card-title">Визуализация</h3>
      </div>
      <div class="chart-section">
        <canvas id="chartCanvas" width="800" height="400" class="chart-canvas"></canvas>
      </div>
      <div class="chart-note" v-if="isMobile">
        <i class="fas fa-chart-simple"></i> Поверните устройство для детального просмотра
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'Statistics',
  setup() {
    const statistics = ref([])
    const sortedStatistics = ref([])
    const monthlyAnalytics = ref([])
    const totalAmount = ref(0)
    const transactionCount = ref(0)
    const currentType = ref('expense')
    const selectedPeriod = ref('month')
    const selectedYear = ref(new Date().getFullYear())
    const selectedMonth = ref(new Date().getMonth() + 1)
    const showFilters = ref(true)
    const isMobile = ref(false)
    const expandedCategories = ref({})
    const sortOrder = ref('desc')
    const categoryColors = ref({})
    let resizeObserver = null

    const years = computed(() => {
      const currentYear = new Date().getFullYear()
      return Array.from({ length: 5 }, (_, i) => currentYear - i)
    })

    const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    const colorPalette = ['#10b981', '#ef4444', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1', '#14b8a6', '#d946ef', '#0ea5e9', '#a855f7', '#22c55e']

    const averageAmount = computed(() => transactionCount.value === 0 ? 0 : totalAmount.value / transactionCount.value)

    const maxMonthAmount = computed(() => {
      if (monthlyAnalytics.value.length === 0) return 0
      return Math.max(...monthlyAnalytics.value.map(item => parseFloat(item.total_amount)))
    })

    const maxMonthName = computed(() => {
      const maxItem = monthlyAnalytics.value.reduce((max, item) => parseFloat(item.total_amount) > parseFloat(max.total_amount) ? item : max, monthlyAnalytics.value[0])
      return maxItem ? `${maxItem.month_name} ${maxItem.year}` : ''
    })

    const minMonthAmount = computed(() => {
      if (monthlyAnalytics.value.length === 0) return 0
      return Math.min(...monthlyAnalytics.value.map(item => parseFloat(item.total_amount)))
    })

    const minMonthName = computed(() => {
      const minItem = monthlyAnalytics.value.reduce((min, item) => parseFloat(item.total_amount) < parseFloat(min.total_amount) ? item : min, monthlyAnalytics.value[0])
      return minItem ? `${minItem.month_name} ${minItem.year}` : ''
    })

    const averageMonthlyAmount = computed(() => {
      if (monthlyAnalytics.value.length === 0) return 0
      const sum = monthlyAnalytics.value.reduce((s, item) => s + parseFloat(item.total_amount), 0)
      return sum / monthlyAnalytics.value.length
    })

    const medianMonthlyAmount = computed(() => {
      if (monthlyAnalytics.value.length === 0) return 0
      const amounts = [...monthlyAnalytics.value].map(item => parseFloat(item.total_amount)).sort((a, b) => a - b)
      const mid = Math.floor(amounts.length / 2)
      return amounts.length % 2 === 0 ? (amounts[mid - 1] + amounts[mid]) / 2 : amounts[mid]
    })

    const standardDeviation = computed(() => {
      if (monthlyAnalytics.value.length < 2) return 0
      const mean = averageMonthlyAmount.value
      const squaredDiffs = monthlyAnalytics.value.map(item => Math.pow(parseFloat(item.total_amount) - mean, 2))
      const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / monthlyAnalytics.value.length
      return Math.sqrt(variance)
    })

    const coefficientOfVariation = computed(() => {
      if (averageMonthlyAmount.value === 0) return 0
      return (standardDeviation.value / averageMonthlyAmount.value) * 100
    })

    const getCategoryColor = (categoryId) => categoryColors.value[categoryId] || '#ccc'

    const assignColorsToCategories = () => {
      statistics.value.forEach((category, index) => {
        categoryColors.value[category.id] = colorPalette[index % colorPalette.length]
      })
    }

    const getMonthPercentOfMax = (amount) => {
      if (maxMonthAmount.value === 0) return 0
      return ((parseFloat(amount) / maxMonthAmount.value) * 100).toFixed(1)
    }

    const drawPieChart = () => {
      const canvas = document.getElementById('pieChartCanvas')
      if (!canvas) return

      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const container = canvas.parentElement
      if (!container) return

      const containerWidth = container.clientWidth
      let size = Math.min(containerWidth - 40, 350)

      canvas.width = size
      canvas.height = size
      canvas.style.width = `${size}px`
      canvas.style.height = `${size}px`

      const centerX = size / 2
      const centerY = size / 2
      const radius = size / 2 - 20

      ctx.clearRect(0, 0, size, size)

      if (statistics.value.length === 0) return

      let startAngle = -Math.PI / 2

      statistics.value.forEach((category) => {
        const percentage = parseFloat(getPercentage(category.total)) / 100
        const angle = percentage * 2 * Math.PI
        const endAngle = startAngle + angle

        ctx.beginPath()
        ctx.fillStyle = categoryColors.value[category.id]
        ctx.moveTo(centerX, centerY)
        ctx.arc(centerX, centerY, radius, startAngle, endAngle)
        ctx.fill()
        ctx.strokeStyle = '#ffffff'
        ctx.lineWidth = 1.5
        ctx.stroke()

        if (percentage > 0.08) {
          const midAngle = startAngle + angle / 2
          const textRadius = radius * 0.7
          const x = centerX + Math.cos(midAngle) * textRadius
          const y = centerY + Math.sin(midAngle) * textRadius
          ctx.fillStyle = '#ffffff'
          const fontSize = size < 250 ? 11 : 13
          ctx.font = `bold ${fontSize}px Arial`
          ctx.shadowBlur = 0
          const percentText = `${getPercentage(category.total)}%`
          ctx.fillText(percentText, x - (fontSize * percentText.length) / 3, y + fontSize / 3)
        }

        startAngle = endAngle
      })
    }

    const sortCategories = (order) => {
      sortOrder.value = order
      const sorted = [...statistics.value]
      sorted.sort((a, b) => sortOrder.value === 'desc' ? parseFloat(b.total) - parseFloat(a.total) : parseFloat(a.total) - parseFloat(b.total))
      sortedStatistics.value = sorted
    }

    const sortedChildren = (children) => {
      return [...children].sort((a, b) => parseFloat(b.total) - parseFloat(a.total))
    }

    const toggleCategory = (categoryId) => {
      expandedCategories.value[categoryId] = !expandedCategories.value[categoryId]
      expandedCategories.value = { ...expandedCategories.value }
    }

    const checkMobile = () => {
      isMobile.value = window.innerWidth <= 768
    }

    const loadStatistics = async () => {
      try {
        if (selectedPeriod.value === 'month') {
          const data = await apiService.getMonthStatistics(selectedMonth.value, selectedYear.value, currentType.value)
          totalAmount.value = parseFloat(data.total_amount) || 0
          statistics.value = data.statistics || []
          assignColorsToCategories()
          sortCategories(sortOrder.value)

          const newExpanded = {}
          statistics.value.forEach(cat => { newExpanded[cat.id] = false })
          expandedCategories.value = newExpanded

          await nextTick()
          setTimeout(() => drawPieChart(), 100)
        } else {
          const yearlyData = await apiService.getMonthlyAnalytics(selectedYear.value, currentType.value)
          monthlyAnalytics.value = yearlyData.results || []
          totalAmount.value = monthlyAnalytics.value.reduce((sum, item) => sum + parseFloat(item.total_amount), 0)
          transactionCount.value = monthlyAnalytics.value.reduce((sum, item) => sum + item.transaction_count, 0)
          statistics.value = []
          sortedStatistics.value = []

          await nextTick()
          if (monthlyAnalytics.value.length > 0) setTimeout(() => drawChart(), 100)
        }
      } catch (error) {
        console.error('Error loading statistics:', error)
      }
    }

    const getPercentage = (total) => {
      if (totalAmount.value === 0) return 0
      return ((parseFloat(total) / totalAmount.value) * 100).toFixed(1)
    }

    const getSubPercentage = (parentTotal, childTotal) => {
      if (parseFloat(parentTotal) === 0) return 0
      return ((parseFloat(childTotal) / parseFloat(parentTotal)) * 100).toFixed(1)
    }

    const getTrendClass = (item) => {
      if (item.change_vs_prev_percent > 0) return currentType.value === 'income' ? 'text-success' : 'text-danger'
      if (item.change_vs_prev_percent < 0) return currentType.value === 'income' ? 'text-danger' : 'text-success'
      return ''
    }

    const getTrendBadgeClass = (item) => {
      if (item.change_vs_prev_percent > 0) return 'trend-up'
      if (item.change_vs_prev_percent < 0) return 'trend-down'
      return 'trend-neutral'
    }

    const drawChart = () => {
      const canvas = document.getElementById('chartCanvas')
      if (!canvas) return

      const ctx = canvas.getContext('2d')
      if (!ctx) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)
      if (monthlyAnalytics.value.length === 0) return

      const width = canvas.width
      const height = canvas.height
      const padding = isMobile.value ? 50 : 60
      const chartWidth = width - 2 * padding
      const chartHeight = height - 2 * padding
      const maxValue = Math.max(...monthlyAnalytics.value.map(item => parseFloat(item.total_amount)), 0)

      ctx.beginPath()
      ctx.strokeStyle = '#ccc'
      ctx.lineWidth = 1
      ctx.moveTo(padding, padding)
      ctx.lineTo(padding, height - padding)
      ctx.moveTo(padding, height - padding)
      ctx.lineTo(width - padding, height - padding)
      ctx.stroke()

      ctx.fillStyle = '#666'
      ctx.font = isMobile.value ? '10px Arial' : '12px Arial'
      for (let i = 0; i <= 5; i++) {
        const value = (maxValue / 5) * i
        const y = height - padding - (i / 5) * chartHeight
        ctx.fillText(formatCurrency(value), 10, y + 4)
      }

      const step = chartWidth / (monthlyAnalytics.value.length - 1)
      ctx.beginPath()
      ctx.strokeStyle = currentType.value === 'income' ? '#10b981' : '#ef4444'
      ctx.lineWidth = isMobile.value ? 2 : 3

      monthlyAnalytics.value.forEach((item, index) => {
        const x = padding + index * step
        const y = height - padding - (parseFloat(item.total_amount) / maxValue) * chartHeight
        if (index === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      })
      ctx.stroke()

      monthlyAnalytics.value.forEach((item, index) => {
        const x = padding + index * step
        const y = height - padding - (parseFloat(item.total_amount) / maxValue) * chartHeight
        ctx.beginPath()
        ctx.fillStyle = currentType.value === 'income' ? '#10b981' : '#ef4444'
        ctx.arc(x, y, isMobile.value ? 4 : 6, 0, 2 * Math.PI)
        ctx.fill()
        ctx.beginPath()
        ctx.fillStyle = 'white'
        ctx.arc(x, y, isMobile.value ? 2 : 3, 0, 2 * Math.PI)
        ctx.fill()
        ctx.fillStyle = '#666'
        ctx.font = isMobile.value ? '10px Arial' : '12px Arial'
        const monthLabel = isMobile.value ? item.month_name.substring(0, 3) : item.month_name.substring(0, 3)
        ctx.fillText(monthLabel, x - (isMobile.value ? 10 : 15), height - padding + (isMobile.value ? 15 : 20))
      })
    }

    const formatCurrency = (value) => {
      if (!value && value !== 0) return '0 ₽'
      const numValue = parseFloat(value)
      if (isNaN(numValue)) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(numValue)
    }

    const handleResize = () => {
      checkMobile()
      if (selectedPeriod.value === 'year' && monthlyAnalytics.value.length > 0) {
        setTimeout(() => drawChart(), 100)
      }
      if (selectedPeriod.value === 'month' && statistics.value.length > 0) {
        setTimeout(() => drawPieChart(), 100)
      }
    }

    onMounted(() => {
      checkMobile()
      loadStatistics()
      window.addEventListener('resize', handleResize)

      if (window.ResizeObserver) {
        resizeObserver = new ResizeObserver(() => {
          if (selectedPeriod.value === 'month' && statistics.value.length > 0) {
            setTimeout(() => drawPieChart(), 100)
          }
        })
        const pieWrapper = document.querySelector('.pie-chart-wrapper')
        if (pieWrapper) {
          resizeObserver.observe(pieWrapper)
        }
      }
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      if (resizeObserver) {
        resizeObserver.disconnect()
      }
    })

    watch([currentType, selectedPeriod, selectedYear, selectedMonth], () => loadStatistics())

    return {
      statistics, sortedStatistics, monthlyAnalytics, totalAmount, transactionCount, currentType,
      selectedPeriod, selectedYear, selectedMonth, years, months, averageAmount, showFilters, isMobile,
      expandedCategories, sortOrder, maxMonthAmount, maxMonthName, minMonthAmount, minMonthName,
      averageMonthlyAmount, medianMonthlyAmount, standardDeviation, coefficientOfVariation,
      loadStatistics, toggleCategory, sortCategories, sortedChildren, getPercentage, getSubPercentage,
      getMonthPercentOfMax, getTrendClass, getTrendBadgeClass, formatCurrency, getCategoryColor
    }
  }
}
</script>

<style scoped>
/* ========== Общие стили ========== */
.statistics-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
  background: #f3f4f6;
  min-height: 100vh;
}

.page-header {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem;
  margin-bottom: 0.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: #1f2937;
  text-align: center;
}

/* ========== Карточки ========== */
.card {
  background: #ffffff;
  border-radius: 0;
  box-shadow: none;
  margin-bottom: 0.5rem;
  overflow: hidden;
  border: none;
  border-bottom: 1px solid #e5e7eb;
}

.full-width-card {
  margin-left: 0;
  margin-right: 0;
  border-radius: 0;
}

.card:last-child {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: #1f2937;
}

/* ========== Фильтры ========== */
.filters-card {
  margin-bottom: 0.5rem;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.875rem 1rem;
  cursor: pointer;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.filters-header:hover {
  background: #f3f4f6;
}

.filters-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0;
  color: #374151;
}

.filters-body {
  padding: 1rem;
  background: #ffffff;
  transition: all 0.3s ease;
}

.filters-hidden {
  display: none;
}

.filters-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #4b5563;
}

.filter-actions {
  margin-top: 0.5rem;
}

/* ========== Формы и кнопки ========== */
.form-control {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.813rem;
  transition: all 0.2s;
  background: #ffffff;
  color: #1f2937;
  width: 100%;
}

.form-control:hover {
  border-color: #9ca3af;
}

.form-control:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.813rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: #f9fafb;
  color: #374151;
  width: 100%;
}

.btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-primary {
  background: #6366f1;
  color: white;
  border: 1px solid #6366f1;
}

.btn-primary:hover {
  background: #4f46e5;
  border-color: #4f46e5;
}

.btn-sort {
  padding: 0.375rem 0.75rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #374151;
  width: auto;
}

.btn-sort:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.btn-sort.active {
  background: #6366f1;
  color: white;
  border-color: #6366f1;
}

.sort-buttons {
  display: flex;
  gap: 0.5rem;
}

/* ========== Карточки статистики ========== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0 0.5rem;
}

.stat-card {
  background: #ffffff;
  border-radius: 10px;
  padding: 0.875rem;
  text-align: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
}

.stat-card:first-child {
  grid-column: span 2;
}

.stat-card-title {
  font-size: 0.688rem;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: #6b7280;
  margin-bottom: 0.375rem;
}

.stat-card-value {
  font-size: 1.25rem;
  font-weight: 700;
}

.stat-card-subtitle {
  font-size: 0.625rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

/* ========== Цвета текста ========== */
.text-success { color: #10b981; }
.text-danger { color: #ef4444; }

/* ========== Круговая диаграмма ========== */
.pie-chart-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
}

.pie-chart-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  background: transparent;
}

.pie-chart-canvas {
  display: block;
  margin: 0 auto;
  background: transparent;
}

.pie-chart-legend {
  width: 100%;
  max-height: 250px;
  overflow-y: auto;
  background: #ffffff;
  border-radius: 8px;
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.legend-item:last-child {
  border-bottom: none;
}

.legend-color {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-name {
  flex: 1;
  font-size: 0.75rem;
  color: #374151;
}

.legend-percent {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
}

/* ========== Список категорий на всю ширину ========== */
.categories-list {
  padding: 0;
}

.categories-list.full-width {
  padding: 0;
}

.category-item {
  margin-bottom: 0;
  padding: 1rem;
  background: #ffffff;
  border-radius: 0;
  border: none;
  border-bottom: 1px solid #e5e7eb;
}

.category-item:last-child {
  border-bottom: none;
}

.category-item.full-width-item {
  border-radius: 0;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
}

.category-header:hover {
  opacity: 0.8;
}

.category-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  color: #1f2937;
}

.expand-icon {
  font-size: 0.688rem;
  color: #6b7280;
}

.placeholder-icon {
  width: 12px;
  visibility: hidden;
}

.category-total {
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
}

/* ========== Прогресс-бары ========== */
.progress-wrapper {
  margin-top: 0.5rem;
}

.progress-bar {
  height: 28px;
  background: #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.progress-bar.small {
  height: 24px;
}

.progress-fill {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  color: white;
  font-weight: 600;
  font-size: 0.688rem;
  transition: width 0.3s ease;
}

.progress-income {
  background: linear-gradient(90deg, #10b981, #34d399);
}

.progress-expense {
  background: linear-gradient(90deg, #ef4444, #f87171);
}

.progress-subcategory {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.progress-text {
  font-size: 0.688rem;
  text-shadow: 0 0 2px rgba(0,0,0,0.3);
}

.progress-text-small {
  font-size: 0.625rem;
  text-shadow: 0 0 2px rgba(0,0,0,0.3);
}

.progress-percent-info {
  font-size: 0.625rem;
  color: #6b7280;
  text-align: right;
  margin-top: 0.25rem;
}

/* ========== Подкатегории ========== */
.subcategories {
  margin-top: 0.75rem;
  padding-left: 1rem;
}

.subcategory-item {
  margin-bottom: 0.75rem;
  padding: 0.625rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  border-left-width: 3px;
}

.subcategory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.375rem;
}

.subcategory-name {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: #4b5563;
}

.subcategory-total {
  font-weight: 600;
  font-size: 0.75rem;
}

.subcategory-progress {
  margin: 0.375rem 0;
}

.subcategory-percent {
  font-size: 0.625rem;
  color: #6b7280;
  text-align: right;
}

.expand-hint {
  font-size: 0.688rem;
  color: #6366f1;
  cursor: pointer;
  text-align: right;
  margin-top: 0.375rem;
  padding: 0.25rem;
}

.expand-hint:hover {
  text-decoration: underline;
}

/* ========== Мобильные карточки месяцев ========== */
.mobile-months-grid {
  display: block;
  padding: 0;
}

.mobile-month-card {
  background: #ffffff;
  border-radius: 0;
  padding: 1rem;
  margin-bottom: 0;
  border: none;
  border-bottom: 1px solid #e5e7eb;
}

.mobile-month-card:last-child {
  border-bottom: none;
}

.mobile-month-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.mobile-month-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.month-name-text {
  font-weight: 600;
  font-size: 0.875rem;
}

.mobile-month-amount {
  font-size: 1rem;
  font-weight: 700;
}

.mobile-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.mobile-stat {
  text-align: center;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.mobile-stat-label {
  font-size: 0.625rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.mobile-stat-value {
  font-size: 0.813rem;
  font-weight: 600;
}

.mobile-progress {
  margin-top: 0.5rem;
}

.progress-label {
  font-size: 0.625rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

/* ========== Десктоп таблица (скрыта на мобильных) ========== */
.desktop-table-wrapper {
  display: none;
}

/* ========== Тренд бейджи ========== */
.trend-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.688rem;
  font-weight: 500;
}

.trend-badge.small {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  margin-left: 0.375rem;
}

.trend-badge.trend-up {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.trend-badge.trend-down {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.trend-badge.trend-neutral {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

/* ========== Годовая сводка ========== */
.year-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.summary-card {
  text-align: center;
  padding: 0.625rem;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.summary-label {
  font-size: 0.625rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.summary-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
}

/* ========== График ========== */
.chart-section {
  padding: 1rem;
  overflow-x: auto;
  background: #ffffff;
}

.chart-canvas {
  max-width: 100%;
  height: auto;
  background: #ffffff;
}

.chart-note {
  text-align: center;
  padding: 0.5rem;
  font-size: 0.688rem;
  color: #6b7280;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

/* ========== Пустое состояние ========== */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.empty-state i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.text-center {
  text-align: center;
}

/* ========== Планшеты и десктоп ========== */
@media (min-width: 768px) {
  .statistics-page {
    padding: 0 1rem;
  }

  .page-header {
    background: transparent;
    border-bottom: none;
    padding: 0;
    margin-bottom: 1.5rem;
  }

  .page-title {
    font-size: 1.75rem;
    text-align: left;
    padding: 0;
  }

  .card {
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border: 1px solid #e5e7eb;
  }

  .full-width-card {
    border-radius: 12px;
  }

  .card:last-child {
    margin-bottom: 1.5rem;
  }

  .card-header {
    padding: 1.25rem 1.5rem;
  }

  .filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .filter-actions .btn {
    width: auto;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    padding: 0;
    margin-bottom: 1.5rem;
  }

  .stat-card:first-child {
    grid-column: auto;
  }

  .stat-card {
    padding: 1.25rem;
  }

  .pie-chart-section {
    flex-direction: row;
    padding: 1.5rem;
  }

  .pie-chart-legend {
    max-width: 280px;
    max-height: 320px;
  }

  .categories-list {
    padding: 1.5rem;
  }

  .categories-list.full-width {
    padding: 1.5rem;
  }

  .category-item {
    margin-bottom: 1rem;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
  }

  .category-item.full-width-item {
    border-radius: 10px;
  }

  .mobile-months-grid {
    display: none;
  }

  .desktop-table-wrapper {
    display: block;
    padding: 0 1.5rem 1.5rem 1.5rem;
  }

  .year-summary {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    padding: 1.5rem;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .analytics-table {
    font-size: 0.75rem;
  }

  .analytics-table th,
  .analytics-table td {
    padding: 0.5rem;
  }
}
</style>