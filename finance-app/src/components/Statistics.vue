<template>
  <div>
    <h1 style="margin-bottom: 2rem;">Аналитика</h1>

    <div class="card">
      <div class="filters-header" @click="showFilters = !showFilters">
        <h3>Фильтры</h3>
        <i :class="showFilters ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
      </div>
      
      <div class="filters" :class="{ 'filters-hidden': !showFilters }">
        <div class="filter-group">
          <label>Тип:</label>
          <select v-model="currentType" class="form-control">
            <option value="income">Доходы</option>
            <option value="expense">Расходы</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Период:</label>
          <select v-model="selectedPeriod" class="form-control">
            <option value="month">За месяц</option>
            <option value="year">За год</option>
          </select>
        </div>

        <div class="filter-group" v-if="selectedPeriod === 'month'">
          <label>Год:</label>
          <select v-model="selectedYear" class="form-control">
            <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>

        <div class="filter-group" v-if="selectedPeriod === 'month'">
          <label>Месяц:</label>
          <select v-model="selectedMonth" class="form-control">
            <option v-for="(name, index) in months" :key="index" :value="index + 1">{{ name }}</option>
          </select>
        </div>

        <div class="filter-group" v-if="selectedPeriod === 'year'">
          <label>Год:</label>
          <select v-model="selectedYear" class="form-control">
            <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>

        <div class="filter-actions">
          <button @click="loadStatistics" class="btn btn-primary">Применить</button>
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-title">Общая сумма</div>
        <div class="stat-value" :class="currentType === 'income' ? 'text-success' : 'text-danger'">
          {{ formatCurrency(totalAmount) }}
        </div>
      </div>

      <div class="stat-card" v-if="selectedPeriod === 'year'">
        <div class="stat-title">Количество транзакций</div>
        <div class="stat-value">{{ transactionCount }}</div>
      </div>

      <div class="stat-card" v-if="selectedPeriod === 'year'">
        <div class="stat-title">Средняя сумма</div>
        <div class="stat-value">{{ formatCurrency(averageAmount) }}</div>
      </div>
    </div>

    <!-- Category Breakdown (only for month view) -->
    <div class="card" v-if="selectedPeriod === 'month'">
      <div class="card-header">
        <h3 class="card-title">Разбивка по категориям</h3>
      </div>

      <!-- Для мобильных и планшетов: карточки категорий -->
      <div class="mobile-categories">
        <div v-for="category in statistics" :key="category.id" class="category-card">
          <div class="category-header">
            <span class="category-name">
              <i class="fas fa-folder"></i>
              {{ category.name }}
            </span>
            <span class="category-total">{{ formatCurrency(category.total) }}</span>
          </div>
          
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: getPercentage(category.total) + '%' }"
              :class="currentType === 'income' ? 'progress-income' : 'progress-expense'"
            ></div>
          </div>
          
          <div class="category-percentage">{{ getPercentage(category.total) }}%</div>

          <!-- Subcategories -->
          <div v-if="category.children && category.children.length" class="subcategories">
            <div v-for="child in category.children" :key="child.id" class="subcategory">
              <span class="subcategory-name">↳ {{ child.name }}</span>
              <span class="subcategory-total">{{ formatCurrency(child.total) }}</span>
            </div>
          </div>
        </div>

        <div v-if="statistics.length === 0" class="empty-state">
          <i class="fas fa-chart-bar"></i>
          <p>Нет данных за выбранный период</p>
        </div>
      </div>

      <!-- Для десктопа: обычное отображение -->
      <div class="desktop-categories">
        <div v-for="category in statistics" :key="category.id" class="category-stat">
          <div class="category-header">
            <span class="category-name">
              <i class="fas fa-folder"></i>
              {{ category.name }}
            </span>
            <span class="category-total">{{ formatCurrency(category.total) }}</span>
          </div>
          
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: getPercentage(category.total) + '%' }"
              :class="currentType === 'income' ? 'progress-income' : 'progress-expense'"
            ></div>
          </div>
          
          <div class="category-percentage">{{ getPercentage(category.total) }}%</div>

          <!-- Subcategories -->
          <div v-if="category.children && category.children.length" class="subcategories">
            <div v-for="child in category.children" :key="child.id" class="subcategory">
              <span class="subcategory-name">↳ {{ child.name }}</span>
              <span class="subcategory-total">{{ formatCurrency(child.total) }}</span>
            </div>
          </div>
        </div>

        <div v-if="statistics.length === 0" class="empty-state">
          Нет данных за выбранный период
        </div>
      </div>
    </div>

    <!-- Monthly Analytics (only for year view) -->
    <div class="card" v-if="selectedPeriod === 'year'">
      <div class="card-header">
        <h3 class="card-title">Аналитика по месяцам</h3>
      </div>

      <!-- Для мобильных и планшетов: карточки месяцев -->
      <div class="mobile-months">
        <div v-for="item in monthlyAnalytics" :key="item.period" class="month-card">
          <div class="month-header">
            <div class="month-name">{{ item.month_name }} {{ item.year }}</div>
            <div class="month-total" :class="currentType === 'income' ? 'text-success' : 'text-danger'">
              {{ formatCurrency(item.total_amount) }}
            </div>
          </div>
          
          <div class="month-details">
            <div class="detail-item">
              <span class="detail-label">
                <i class="fas fa-receipt"></i> Транзакций:
              </span>
              <span class="detail-value">{{ item.transaction_count }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">
                <i class="fas fa-chart-line"></i> Средняя сумма:
              </span>
              <span class="detail-value">{{ formatCurrency(item.avg_amount) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">
                <i class="fas fa-trend"></i> Изменение:
              </span>
              <span class="detail-value" v-if="item.change_vs_prev_percent !== 0" :class="getTrendClass(item)">
                {{ item.trend_vs_prev }} {{ Math.abs(item.change_vs_prev_percent).toFixed(1) }}%
              </span>
              <span class="detail-value" v-else>—</span>
            </div>
          </div>
        </div>
        <div v-if="monthlyAnalytics.length === 0" class="empty-state">
          <i class="fas fa-chart-line"></i>
          <p>Нет данных за выбранный год</p>
        </div>
      </div>

      <!-- Для десктопа: таблица -->
      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>Месяц</th>
              <th>Сумма</th>
              <th>Кол-во транзакций</th>
              <th>Средняя сумма</th>
              <th>Изменение</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in monthlyAnalytics" :key="item.period">
              <td>{{ item.month_name }} {{ item.year }}</td>
              <td :class="currentType === 'income' ? 'text-success' : 'text-danger'">
                {{ formatCurrency(item.total_amount) }}
               </td>
              <td>{{ item.transaction_count }}</td>
              <td>{{ formatCurrency(item.avg_amount) }}</td>
              <td>
                <span v-if="item.change_vs_prev_percent !== 0" :class="getTrendClass(item)">
                  {{ item.trend_vs_prev }} {{ Math.abs(item.change_vs_prev_percent).toFixed(1) }}%
                </span>
                <span v-else>—</span>
                </td>
              </tr>
            <tr v-if="monthlyAnalytics.length === 0">
              <td colspan="5" style="text-align: center;">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Charts (only for year view) -->
    <div class="card" v-if="selectedPeriod === 'year' && monthlyAnalytics.length > 0">
      <div class="card-header">
        <h3 class="card-title">Визуализация</h3>
      </div>
      <div class="chart-container">
        <canvas id="chartCanvas" width="800" height="400" style="max-width: 100%; height: auto;"></canvas>
      </div>
      <div class="chart-note" v-if="isMobile">
        <i class="fas fa-chart-simple"></i>
        Для детального просмотра графика поверните устройство горизонтально
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'Statistics',
  setup() {
    const statistics = ref([])
    const monthlyAnalytics = ref([])
    const totalAmount = ref(0)
    const transactionCount = ref(0)
    const currentType = ref('expense')
    const selectedPeriod = ref('month')
    const selectedYear = ref(new Date().getFullYear())
    const selectedMonth = ref(new Date().getMonth() + 1)
    const showFilters = ref(true)
    const isMobile = ref(false)
    
    const years = computed(() => {
      const currentYear = new Date().getFullYear()
      return Array.from({ length: 5 }, (_, i) => currentYear - i)
    })
    
    const months = [
      'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
      'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]

    const averageAmount = computed(() => {
      if (transactionCount.value === 0) return 0
      return totalAmount.value / transactionCount.value
    })

    const checkMobile = () => {
      isMobile.value = window.innerWidth <= 768
    }

    const loadStatistics = async () => {
      try {
        if (selectedPeriod.value === 'month') {
          const data = await apiService.getMonthStatistics(
            selectedMonth.value, 
            selectedYear.value, 
            currentType.value
          )
          
          totalAmount.value = parseFloat(data.total_amount) || 0
          statistics.value = data.statistics || []
          
          const countTransactions = (categories) => {
            let count = 0
            for (const cat of categories) {
              if (cat.transaction_count) {
                count += cat.transaction_count
              }
              if (cat.children && cat.children.length) {
                count += countTransactions(cat.children)
              }
            }
            return count
          }
          
          transactionCount.value = countTransactions(statistics.value)
          monthlyAnalytics.value = []
          
        } else {
          const yearlyData = await apiService.getMonthlyAnalytics(selectedYear.value, currentType.value)
          monthlyAnalytics.value = yearlyData.results || []
          
          totalAmount.value = monthlyAnalytics.value.reduce((sum, item) => sum + parseFloat(item.total_amount), 0)
          transactionCount.value = monthlyAnalytics.value.reduce((sum, item) => sum + item.transaction_count, 0)
          
          statistics.value = []
          
          await nextTick()
          if (monthlyAnalytics.value.length > 0) {
            setTimeout(() => drawChart(), 100)
          }
        }
      } catch (error) {
        console.error('Error loading statistics:', error)
      }
    }

    const getPercentage = (total) => {
      if (totalAmount.value === 0) return 0
      const percentage = (parseFloat(total) / totalAmount.value) * 100
      return percentage.toFixed(1)
    }

    const getTrendClass = (item) => {
      if (item.change_vs_prev_percent > 0) {
        return currentType.value === 'income' ? 'text-success' : 'text-danger'
      } else if (item.change_vs_prev_percent < 0) {
        return currentType.value === 'income' ? 'text-danger' : 'text-success'
      }
      return ''
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
        
        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
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
      if (!value) return '0 ₽'
      const numValue = parseFloat(value)
      if (isNaN(numValue)) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(numValue)
    }

    const handleResize = () => {
      checkMobile()
      if (selectedPeriod.value === 'year' && monthlyAnalytics.value.length > 0) {
        setTimeout(() => drawChart(), 100)
      }
    }

    onMounted(() => {
      checkMobile()
      loadStatistics()
      window.addEventListener('resize', handleResize)
    })

    watch([currentType, selectedPeriod, selectedYear, selectedMonth], () => {
      loadStatistics()
    })

    return {
      statistics,
      monthlyAnalytics,
      totalAmount,
      transactionCount,
      currentType,
      selectedPeriod,
      selectedYear,
      selectedMonth,
      years,
      months,
      averageAmount,
      showFilters,
      isMobile,
      loadStatistics,
      getPercentage,
      getTrendClass,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.filters-header {
  display: none;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 1rem;
  background: var(--white);
  border-radius: var(--radius);
  margin-bottom: 1rem;
}

.filters-header h3 {
  font-size: 1rem;
  margin: 0;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
  padding: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  font-size: 0.875rem;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* Стили для категорий (десктоп) */
.desktop-categories {
  display: block;
}

.category-stat {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--light-color);
  border-radius: var(--radius);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.category-name {
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-total {
  font-weight: 600;
}

.progress-bar {
  height: 24px;
  background: #e5e7eb;
  border-radius: var(--radius);
  overflow: hidden;
  margin: 0.5rem 0;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  color: white;
  font-size: 12px;
  font-weight: 600;
}

.progress-income {
  background: linear-gradient(90deg, #10b981, #34d399);
}

.progress-expense {
  background: linear-gradient(90deg, #ef4444, #f87171);
}

.category-percentage {
  text-align: right;
  font-size: 0.875rem;
  color: var(--gray-color);
}

.subcategories {
  margin-top: 1rem;
  padding-left: 2rem;
}

.subcategory {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  border-left: 2px solid var(--primary-color);
  margin-bottom: 0.5rem;
  background: white;
  border-radius: var(--radius);
}

.subcategory-name {
  color: var(--gray-color);
}

.subcategory-total {
  font-weight: 500;
}

/* Стили для карточек категорий (мобильная версия) */
.mobile-categories {
  display: none;
}

.category-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  padding: 1rem;
  margin-bottom: 1rem;
}

/* Стили для карточек месяцев (мобильная версия) */
.mobile-months {
  display: none;
}

.month-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  padding: 1rem;
  margin-bottom: 1rem;
}

.month-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--light-color);
}

.month-name {
  font-weight: 600;
  font-size: 1rem;
}

.month-total {
  font-weight: 700;
  font-size: 1.125rem;
}

.month-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.detail-label {
  color: var(--gray-color);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.detail-value {
  color: var(--dark-color);
  font-weight: 500;
}

/* Десктопная таблица */
.desktop-table {
  display: block;
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--light-color);
}

.table th {
  font-weight: 600;
  background: var(--light-color);
}

.chart-container {
  overflow-x: auto;
  padding: 1rem;
}

.chart-note {
  text-align: center;
  padding: 1rem;
  color: var(--gray-color);
  font-size: 0.875rem;
  border-top: 1px solid var(--light-color);
  margin-top: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  text-align: center;
}

.stat-title {
  font-size: 0.875rem;
  color: var(--gray-color);
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
}

.text-success {
  color: var(--secondary-color);
}

.text-danger {
  color: var(--danger-color);
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--gray-color);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
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
}

/* Адаптивные стили - для планшетов и мобильных */
@media (max-width: 1024px) {
  .desktop-categories {
    display: none;
  }
  
  .mobile-categories {
    display: block;
  }
  
  .filters-header {
    display: flex;
  }
  
  .filters {
    display: grid;
  }
  
  .filters-hidden {
    display: none;
  }
  
  .card {
    padding: 1rem;
  }
  
  .stats-grid {
    gap: 1rem;
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
}

/* Для мобильных устройств (до 768px) */
@media (max-width: 768px) {
  h1 {
    text-align: center;
    font-size: 1.5rem;
  }

  .filters {
    grid-template-columns: 1fr;
    gap: 0.75rem;
    padding: 1rem;
  }
  
  .filter-actions {
    flex-direction: column;
  }
  
  .filter-actions .btn {
    width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .stat-title {
    font-size: 0.75rem;
  }
  
  .category-card {
    padding: 0.75rem;
  }
  
  .category-name {
    font-size: 0.875rem;
  }
  
  .category-total {
    font-size: 0.875rem;
  }
  
  .subcategories {
    padding-left: 1rem;
  }
  
  .subcategory {
    font-size: 0.75rem;
  }
  
  .desktop-table {
    display: none;
  }
  
  .mobile-months {
    display: block;
  }
  
  .month-name {
    font-size: 0.875rem;
  }
  
  .month-total {
    font-size: 1rem;
  }
  
  .detail-item {
    font-size: 0.75rem;
  }
  
  .empty-state {
    padding: 2rem;
  }
  
  .empty-state i {
    font-size: 2rem;
  }
  
  .chart-container {
    padding: 0.5rem;
  }
}

/* Для очень маленьких экранов (до 480px) */
@media (max-width: 480px) {
  h1 {
    font-size: 1.25rem;
  }
  
  .stat-value {
    font-size: 1rem;
  }
  
  .category-card {
    padding: 0.5rem;
  }
  
  .progress-bar {
    height: 20px;
  }
  
  .progress-fill {
    font-size: 10px;
  }
  
  .subcategory {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .month-card {
    padding: 0.75rem;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}

/* Для планшетов в горизонтальной ориентации */
@media (min-width: 769px) and (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .desktop-table {
    display: block;
  }
  
  .mobile-months {
    display: none;
  }
  
  .table th,
  .table td {
    padding: 0.5rem;
    font-size: 0.875rem;
  }
}
</style>