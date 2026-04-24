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

      <!-- Универсальное отображение категорий -->
      <div class="categories-container">
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
            >
              <span class="progress-text">{{ getPercentage(category.total) }}%</span>
            </div>
          </div>

          <!-- Subcategories with their own progress bars (blue color) -->
          <div v-if="category.children && category.children.length" class="subcategories">
            <div v-for="child in category.children" :key="child.id" class="subcategory-item">
              <div class="subcategory-header">
                <span class="subcategory-name">
                  <i class="fas fa-level-down-alt"></i>
                  {{ child.name }}
                </span>
                <span class="subcategory-total">{{ formatCurrency(child.total) }}</span>
              </div>
              <div class="progress-bar subcategory-progress">
                <div 
                  class="progress-fill progress-subcategory" 
                  :style="{ width: getSubPercentage(category.total, child.total) + '%' }"
                >
                  <span class="progress-text-small">{{ getSubPercentage(category.total, child.total) }}%</span>
                </div>
              </div>
              <div class="subcategory-percent-info">
                {{ getSubPercentage(category.total, child.total) }}% от категории "{{ category.name }}"
              </div>
            </div>
          </div>
        </div>

        <div v-if="statistics.length === 0" class="empty-state">
          <i class="fas fa-chart-bar"></i>
          <p>Нет данных за выбранный период</p>
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
        <div v-for="item in monthlyAnalytics" :key="item.period" class="month-card" @click="toggleMonthDetails(item)">
          <div class="month-header">
            <div class="month-name">
              {{ item.month_name }} {{ item.year }}
              <i :class="expandedMonths[item.period] ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" class="expand-icon"></i>
            </div>
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

          <!-- Разбивка по категориям для месяца -->
          <div v-if="expandedMonths[item.period] && monthCategories[item.period]" class="month-categories">
            <div class="month-categories-title">
              <i class="fas fa-chart-pie"></i> Разбивка по категориям
            </div>
            <div v-for="cat in monthCategories[item.period]" :key="cat.id" class="month-category-item">
              <div class="month-category-header">
                <span class="month-category-name">{{ cat.name }}</span>
                <span class="month-category-total">{{ formatCurrency(cat.total) }}</span>
              </div>
              <div class="progress-bar small">
                <div 
                  class="progress-fill" 
                  :style="{ width: getMonthCategoryPercentage(item.total_amount, cat.total) + '%' }"
                  :class="currentType === 'income' ? 'progress-income' : 'progress-expense'"
                >
                  <span class="progress-text-small">{{ getMonthCategoryPercentage(item.total_amount, cat.total) }}%</span>
                </div>
              </div>
              
              <!-- Дочерние категории (blue color) -->
              <div v-if="cat.children && cat.children.length" class="month-subcategories">
                <div v-for="child in cat.children" :key="child.id" class="month-subcategory">
                  <div class="month-subcategory-header">
                    <span class="month-subcategory-name">
                      <i class="fas fa-level-down-alt"></i>
                      {{ child.name }}
                    </span>
                    <span class="month-subcategory-total">{{ formatCurrency(child.total) }}</span>
                  </div>
                  <div class="progress-bar very-small">
                    <div 
                      class="progress-fill progress-subcategory" 
                      :style="{ width: getMonthSubCategoryPercentage(cat.total, child.total) + '%' }"
                    >
                      <span class="progress-text-very-small">{{ getMonthSubCategoryPercentage(cat.total, child.total) }}%</span>
                    </div>
                  </div>
                  <div class="month-subcategory-percentage">
                    {{ getMonthSubCategoryPercentage(cat.total, child.total) }}% от категории "{{ cat.name }}"
                  </div>
                </div>
              </div>
            </div>
            <div v-if="!monthCategories[item.period] || monthCategories[item.period].length === 0" class="empty-state-small">
              Нет данных по категориям
            </div>
          </div>
        </div>
        <div v-if="monthlyAnalytics.length === 0" class="empty-state">
          <i class="fas fa-chart-line"></i>
          <p>Нет данных за выбранный год</p>
        </div>
      </div>

      <!-- Для десктопа: таблица с возможностью раскрытия -->
      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>Месяц</th>
              <th>Сумма</th>
              <th>Кол-во транзакций</th>
              <th>Средняя сумма</th>
              <th>Изменение</th>
              <th style="width: 50px"></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="item in monthlyAnalytics" :key="item.period">
              <tr @click="toggleMonthDetails(item)" style="cursor: pointer;">
                <td>
                  <strong>{{ item.month_name }} {{ item.year }}</strong>
                </td>
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
                <td style="text-align: center;">
                  <i :class="expandedMonths[item.period] ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                </td>
              </tr>
              <tr v-if="expandedMonths[item.period]">
                <td colspan="6" class="expanded-row">
                  <div class="month-categories-table">
                    <div class="expanded-title">
                      <i class="fas fa-chart-pie"></i> Разбивка по категориям за {{ item.month_name }} {{ item.year }}
                    </div>
                    <div v-if="monthCategories[item.period] && monthCategories[item.period].length > 0">
                      <div v-for="cat in monthCategories[item.period]" :key="cat.id" class="month-category-expanded">
                        <div class="category-row">
                          <span class="category-name-expanded">{{ cat.name }}</span>
                          <span class="category-total-expanded">{{ formatCurrency(cat.total) }}</span>
                          <span class="category-percentage-expanded">{{ getMonthCategoryPercentage(item.total_amount, cat.total) }}%</span>
                        </div>
                        <div class="progress-bar small">
                          <div 
                            class="progress-fill" 
                            :style="{ width: getMonthCategoryPercentage(item.total_amount, cat.total) + '%' }"
                            :class="currentType === 'income' ? 'progress-income' : 'progress-expense'"
                          >
                            <span class="progress-text-small">{{ getMonthCategoryPercentage(item.total_amount, cat.total) }}%</span>
                          </div>
                        </div>
                        
                        <!-- Дочерние категории (blue color) -->
                        <div v-if="cat.children && cat.children.length" class="subcategories-expanded">
                          <div v-for="child in cat.children" :key="child.id" class="subcategory-row">
                            <div class="subcategory-info">
                              <span class="subcategory-name-expanded">
                                <i class="fas fa-level-down-alt"></i>
                                {{ child.name }}
                              </span>
                              <span class="subcategory-total-expanded">{{ formatCurrency(child.total) }}</span>
                            </div>
                            <div class="progress-bar very-small">
                              <div 
                                class="progress-fill progress-subcategory" 
                                :style="{ width: getMonthSubCategoryPercentage(cat.total, child.total) + '%' }"
                              >
                                <span class="progress-text-very-small">{{ getMonthSubCategoryPercentage(cat.total, child.total) }}%</span>
                              </div>
                            </div>
                            <div class="subcategory-percentage-expanded">
                              {{ getMonthSubCategoryPercentage(cat.total, child.total) }}% от категории "{{ cat.name }}"
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-else class="empty-state-small">
                      Нет данных по категориям
                    </div>
                  </div>
                </td>
              </tr>
            </template>
            <tr v-if="monthlyAnalytics.length === 0">
              <td colspan="6" class="text-center">Нет данных</td>
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
    const expandedMonths = ref({})
    const monthCategories = ref({})
    
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

    const loadMonthCategories = async (year, month) => {
      try {
        const data = await apiService.getMonthStatistics(month, year, currentType.value)
        return data.statistics || []
      } catch (error) {
        console.error(`Error loading categories for ${month}.${year}:`, error)
        return []
      }
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
          
          // Очищаем кэш категорий при смене года или типа
          monthCategories.value = {}
          expandedMonths.value = {}
          
          await nextTick()
          if (monthlyAnalytics.value.length > 0) {
            setTimeout(() => drawChart(), 100)
          }
        }
      } catch (error) {
        console.error('Error loading statistics:', error)
      }
    }

    const toggleMonthDetails = async (item) => {
      const period = item.period
      
      if (expandedMonths.value[period]) {
        expandedMonths.value[period] = false
      } else {
        if (!monthCategories.value[period]) {
          const [year, month] = period.split('-')
          monthCategories.value[period] = await loadMonthCategories(parseInt(year), parseInt(month))
        }
        expandedMonths.value[period] = true
      }
      
      expandedMonths.value = { ...expandedMonths.value }
    }

    const getPercentage = (total) => {
      if (totalAmount.value === 0) return 0
      const percentage = (parseFloat(total) / totalAmount.value) * 100
      return percentage.toFixed(1)
    }

    const getSubPercentage = (parentTotal, childTotal) => {
      if (parseFloat(parentTotal) === 0) return 0
      const percentage = (parseFloat(childTotal) / parseFloat(parentTotal)) * 100
      return percentage.toFixed(1)
    }

    const getMonthCategoryPercentage = (monthTotal, categoryTotal) => {
      if (parseFloat(monthTotal) === 0) return 0
      const percentage = (parseFloat(categoryTotal) / parseFloat(monthTotal)) * 100
      return percentage.toFixed(1)
    }

    const getMonthSubCategoryPercentage = (categoryTotal, subCategoryTotal) => {
      if (parseFloat(categoryTotal) === 0) return 0
      const percentage = (parseFloat(subCategoryTotal) / parseFloat(categoryTotal)) * 100
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
      if (!value && value !== 0) return '0 ₽'
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
      expandedMonths,
      monthCategories,
      loadStatistics,
      toggleMonthDetails,
      getPercentage,
      getSubPercentage,
      getMonthCategoryPercentage,
      getMonthSubCategoryPercentage,
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

/* Стили для категорий */
.categories-container {
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
  flex-wrap: wrap;
  gap: 0.5rem;
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
  height: 32px;
  background: #e5e7eb;
  border-radius: var(--radius);
  overflow: hidden;
  margin: 0.5rem 0;
  position: relative;
}

.progress-bar.small {
  height: 28px;
}

.progress-bar.very-small {
  height: 24px;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  color: white;
  font-weight: 600;
  position: relative;
  overflow: hidden;
}

/* Стиль для дочерних категорий - СИНИЙ цвет */
.progress-subcategory {
  background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd);
}

.progress-text {
  font-size: 12px;
  text-shadow: 0 0 2px rgba(0,0,0,0.3);
}

.progress-text-small {
  font-size: 11px;
  text-shadow: 0 0 2px rgba(0,0,0,0.3);
}

.progress-text-very-small {
  font-size: 10px;
  text-shadow: 0 0 2px rgba(0,0,0,0.3);
}

/* Градиенты для доходов (основные категории) */
.progress-income {
  background: linear-gradient(90deg, #10b981, #34d399, #6ee7b7);
}

/* Градиенты для расходов (основные категории) */
.progress-expense {
  background: linear-gradient(90deg, #ef4444, #f87171, #fca5a5);
}

.subcategories {
  margin-top: 1rem;
  padding-left: 1.5rem;
}

.subcategory-item {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: white;
  border-radius: var(--radius);
  border-left: 3px solid #3b82f6;
}

.subcategory-item:last-child {
  margin-bottom: 0;
}

.subcategory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.subcategory-name {
  color: var(--gray-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.subcategory-name i {
  font-size: 0.75rem;
}

.subcategory-total {
  font-weight: 600;
}

.subcategory-progress {
  margin: 0.5rem 0;
}

.subcategory-percent-info {
  font-size: 0.7rem;
  color: var(--gray-color);
  text-align: right;
  margin-top: 0.25rem;
}

/* Стили для раскрывающихся категорий в годовой аналитике */
.expanded-row {
  background: #f9fafb;
  padding: 1rem;
}

.month-categories-table {
  padding: 1rem;
}

.expanded-title {
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--light-color);
}

.month-category-expanded {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: white;
  border-radius: var(--radius);
}

.category-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.category-name-expanded {
  font-weight: 600;
  flex: 1;
}

.category-total-expanded {
  font-weight: 500;
  min-width: 100px;
  text-align: right;
}

.category-percentage-expanded {
  color: var(--gray-color);
  font-size: 0.875rem;
  min-width: 70px;
  text-align: right;
}

.subcategories-expanded {
  margin-top: 0.75rem;
  padding-left: 1.5rem;
}

.subcategory-row {
  padding: 0.75rem;
  border-left: 3px solid #3b82f6;
  margin-top: 0.5rem;
  background: #f9fafb;
  border-radius: var(--radius);
}

.subcategory-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.subcategory-name-expanded {
  color: var(--gray-color);
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.subcategory-name-expanded i {
  font-size: 0.75rem;
}

.subcategory-total-expanded {
  font-weight: 500;
  min-width: 100px;
  text-align: right;
}

.subcategory-percentage-expanded {
  font-size: 0.7rem;
  color: var(--gray-color);
  text-align: right;
  margin-top: 0.25rem;
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
  cursor: pointer;
  transition: all 0.2s;
}

.month-card:hover {
  box-shadow: var(--shadow);
}

.month-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--light-color);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.month-name {
  font-weight: 600;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.expand-icon {
  color: var(--gray-color);
  font-size: 0.875rem;
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

.month-categories {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.month-categories-title {
  font-weight: 600;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: var(--primary-color);
}

.month-category-item {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--light-color);
  border-radius: var(--radius);
}

.month-category-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.month-category-name {
  font-weight: 500;
}

.month-category-total {
  font-weight: 500;
}

.month-category-percentage {
  font-size: 0.75rem;
  color: var(--gray-color);
  text-align: right;
  margin-top: 0.25rem;
}

.month-subcategories {
  margin-top: 0.75rem;
  padding-left: 1rem;
}

.month-subcategory {
  padding: 0.5rem;
  background: white;
  border-radius: var(--radius);
  margin-top: 0.5rem;
  border-left: 3px solid #3b82f6;
}

.month-subcategory-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.month-subcategory-name {
  font-size: 0.875rem;
  color: var(--gray-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.month-subcategory-total {
  font-size: 0.875rem;
  font-weight: 500;
}

.month-subcategory-percentage {
  font-size: 0.7rem;
  color: var(--gray-color);
  text-align: right;
  margin-top: 0.25rem;
}

.empty-state-small {
  text-align: center;
  padding: 1rem;
  color: var(--gray-color);
  font-size: 0.875rem;
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

/* Адаптивные стили */
@media (max-width: 1024px) {
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
  
  .progress-bar {
    height: 28px;
  }
  
  .progress-bar.small {
    height: 24px;
  }
  
  .progress-bar.very-small {
    height: 20px;
  }
  
  .progress-text,
  .progress-text-small,
  .progress-text-very-small {
    font-size: 9px;
  }
}

@media (max-width: 480px) {
  h1 {
    font-size: 1.25rem;
  }
  
  .stat-value {
    font-size: 1rem;
  }
  
  .category-stat {
    padding: 0.75rem;
  }
  
  .subcategories {
    padding-left: 0.75rem;
  }
  
  .subcategory-item {
    padding: 0.5rem;
  }
  
  .month-card {
    padding: 0.75rem;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .category-row,
  .subcategory-info {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .category-total-expanded,
  .category-percentage-expanded,
  .subcategory-total-expanded,
  .subcategory-percentage-expanded {
    text-align: left;
  }
}

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
    font-size: 1rem;
  }
}
</style>