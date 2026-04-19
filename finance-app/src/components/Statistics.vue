<template>
  <div>
    <h1 style="margin-bottom: 2rem;">Аналитика</h1>

    <div class="card">
      <div class="filters">
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

      <!-- Показываем только при просмотре за год -->
      <div class="stat-card" v-if="selectedPeriod === 'year'">
        <div class="stat-title">Количество транзакций</div>
        <div class="stat-value">{{ transactionCount }}</div>
      </div>

      <!-- Показываем только при просмотре за год -->
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

      <div class="categories-stats">
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

      <div class="table-responsive">
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
      <canvas id="chartCanvas" width="800" height="400" style="max-width: 100%; height: auto;"></canvas>
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

    const loadStatistics = async () => {
      try {
        if (selectedPeriod.value === 'month') {
          // Загружаем статистику за месяц
          const data = await apiService.getMonthStatistics(
            selectedMonth.value, 
            selectedYear.value, 
            currentType.value
          )
          
          totalAmount.value = parseFloat(data.total_amount) || 0
          statistics.value = data.statistics || []
          
          // Подсчитываем общее количество транзакций
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
          // Загружаем годовую статистику
          const yearlyData = await apiService.getMonthlyAnalytics(selectedYear.value, currentType.value)
          monthlyAnalytics.value = yearlyData.results || []
          
          // Подсчитываем общую сумму за год
          totalAmount.value = monthlyAnalytics.value.reduce((sum, item) => sum + parseFloat(item.total_amount), 0)
          transactionCount.value = monthlyAnalytics.value.reduce((sum, item) => sum + item.transaction_count, 0)
          
          // Очищаем статистику по категориям
          statistics.value = []
          
          // Отрисовываем график
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
      // Округляем до одного знака после запятой
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
      
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      if (monthlyAnalytics.value.length === 0) return
      
      const width = canvas.width
      const height = canvas.height
      const padding = 60
      const chartWidth = width - 2 * padding
      const chartHeight = height - 2 * padding
      
      // Find max value
      const maxValue = Math.max(...monthlyAnalytics.value.map(item => parseFloat(item.total_amount)), 0)
      
      // Draw axes
      ctx.beginPath()
      ctx.strokeStyle = '#ccc'
      ctx.lineWidth = 1
      
      // Y-axis
      ctx.moveTo(padding, padding)
      ctx.lineTo(padding, height - padding)
      // X-axis
      ctx.moveTo(padding, height - padding)
      ctx.lineTo(width - padding, height - padding)
      ctx.stroke()
      
      // Draw Y-axis labels
      ctx.fillStyle = '#666'
      ctx.font = '12px Arial'
      for (let i = 0; i <= 5; i++) {
        const value = (maxValue / 5) * i
        const y = height - padding - (i / 5) * chartHeight
        ctx.fillText(formatCurrency(value), 10, y + 4)
      }
        
      // Draw line chart
      const step = chartWidth / (monthlyAnalytics.value.length - 1)
      
      ctx.beginPath()
      ctx.strokeStyle = currentType.value === 'income' ? '#10b981' : '#ef4444'
      ctx.lineWidth = 3
      
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
      
      // Draw points
      monthlyAnalytics.value.forEach((item, index) => {
        const x = padding + index * step
        const y = height - padding - (parseFloat(item.total_amount) / maxValue) * chartHeight
        
        ctx.beginPath()
        ctx.fillStyle = currentType.value === 'income' ? '#10b981' : '#ef4444'
        ctx.arc(x, y, 6, 0, 2 * Math.PI)
        ctx.fill()
        
        ctx.beginPath()
        ctx.fillStyle = 'white'
        ctx.arc(x, y, 3, 0, 2 * Math.PI)
        ctx.fill()
        
        // Add labels
        ctx.fillStyle = '#666'
        ctx.font = '12px Arial'
        ctx.fillText(item.month_name.substring(0, 3), x - 15, height - padding + 20)
      })
    }

    const formatCurrency = (value) => {
      if (!value) return '0 ₽'
      const numValue = parseFloat(value)
      if (isNaN(numValue)) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(numValue)
    }

    onMounted(() => {
      loadStatistics()
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
      loadStatistics,
      getPercentage,
      getTrendClass,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
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

.categories-stats {
  padding: 1rem;
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

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--gray-color);
}

.table-responsive {
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

@media (max-width: 768px) {
  h1 {
    text-align: center;
  }

  .subcategories {
    padding-left: 1rem;
  }
  
  .filters {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>