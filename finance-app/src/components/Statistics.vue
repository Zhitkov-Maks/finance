<template>
  <div class="statistics-page" :class="{ 'is-loading': loading }">
    <!-- Шапка -->
    <div class="page-header">
      <h1 class="page-title">Аналитика</h1>
    </div>

    <!-- Навигация по месяцам -->
    <div class="card period-nav-card" v-if="selectedPeriod === 'month'">
      <div class="period-nav">
        <button class="nav-arrow" @click="shiftMonth(-1)" aria-label="Предыдущий месяц">
          <i class="fas fa-chevron-left"></i>
        </button>
        <div class="period-label">
          <strong>{{ months[selectedMonth - 1] }} {{ selectedYear }}</strong>
          <span class="period-hint">{{ periodHint }}</span>
        </div>
        <button
          class="nav-arrow"
          :disabled="isCurrentMonth"
          @click="shiftMonth(1)"
          aria-label="Следующий месяц"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Фильтры (скрыты по умолчанию) -->
    <div class="card filters-card">
      <div class="filters-header" @click="showFilters = !showFilters">
        <h3 class="filters-title">
          <i class="fas fa-sliders-h"></i>
          Фильтры
        </h3>
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
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- Карточки статистики — МЕСЯЦ                                   -->
    <!-- ============================================================ -->
    <div class="stats-grid" v-if="selectedPeriod === 'month'">
      <div class="stat-card stat-main hover-lift">
        <div class="stat-card-title">Общая сумма</div>
        <div class="stat-card-value" :class="currentType === 'income' ? 'text-success' : 'text-danger'">
          {{ formatCurrency(totalAmount) }}
        </div>
      </div>

      <div class="stat-card hover-lift">
        <div class="stat-card-title">Транзакций</div>
        <div class="stat-card-value">{{ transactionCount }}</div>
      </div>

      <div class="stat-card hover-lift">
        <div class="stat-card-title">Средний чек</div>
        <div class="stat-card-value">{{ formatCurrency(averageAmount) }}</div>
      </div>

      <div class="stat-card hover-lift" v-if="maxOrTop">
        <div class="stat-card-title">Крупнейшая</div>
        <div class="stat-card-value">{{ formatCurrency(maxOrTop.amount) }}</div>
        <div class="stat-card-subtitle" :title="maxOrTop.label">{{ maxOrTop.label }}</div>
      </div>

      <div class="stat-card stat-compare hover-lift" v-if="previousMonthStats">
        <div class="stat-card-title">vs прошлый месяц</div>
        <div class="stat-card-value" :class="getDeltaClass(monthComparison.percent)">
          {{ formatDelta(monthComparison.percent) }}
        </div>
        <div class="stat-card-subtitle">
          {{ formatDeltaAbs(monthComparison.absolute) }} к {{ formatCurrency(monthComparison.previous) }}
        </div>
      </div>
    </div>

    <!-- Карточки статистики — ГОД -->
    <div class="stats-grid" v-else>
      <div class="stat-card hover-lift">
        <div class="stat-card-title">Общая сумма</div>
        <div class="stat-card-value" :class="currentType === 'income' ? 'text-success' : 'text-danger'">
          {{ formatCurrency(totalAmount) }}
        </div>
      </div>

      <div class="stat-card hover-lift">
        <div class="stat-card-title">Транзакций</div>
        <div class="stat-card-value">{{ transactionCount }}</div>
      </div>

      <div class="stat-card hover-lift">
        <div class="stat-card-title">Средняя сумма</div>
        <div class="stat-card-value">{{ formatCurrency(averageAmount) }}</div>
      </div>

      <div class="stat-card hover-lift" v-if="monthlyAnalytics.length > 0">
        <div class="stat-card-title">Максимум</div>
        <div class="stat-card-value text-success">{{ formatCurrency(maxMonthAmount) }}</div>
        <div class="stat-card-subtitle">{{ maxMonthName }}</div>
      </div>

      <div class="stat-card hover-lift" v-if="monthlyAnalytics.length > 0">
        <div class="stat-card-title">Минимум</div>
        <div class="stat-card-value text-danger">{{ formatCurrency(minMonthAmount) }}</div>
        <div class="stat-card-subtitle">{{ minMonthName }}</div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- Топ-3 категории плитками (только месяц)                       -->
    <!-- ============================================================ -->
    <div class="top-categories" v-if="selectedPeriod === 'month' && topCategories.length > 0">
      <div
        v-for="(cat, i) in topCategories"
        :key="cat.id"
        class="top-card hover-lift"
        :class="`top-rank-${i + 1}`"
        @click="openCategoryTransactions(cat)"
        title="Показать транзакции категории"
      >
        <div class="top-rank">#{{ i + 1 }}</div>
        <div class="top-color" :style="{ backgroundColor: getCategoryColor(cat.id) }"></div>
        <div class="top-info">
          <div class="top-name">{{ cat.name }}</div>
          <div class="top-amount">{{ formatCurrency(cat.total) }}</div>
        </div>
        <div class="top-share">{{ getPercentage(cat.total) }}%</div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- Разбивка по категориям (только месяц)                         -->
    <!-- ============================================================ -->
    <div class="card full-width-card" v-if="selectedPeriod === 'month'">
      <div class="card-header">
        <h3 class="card-title">Разбивка по категориям</h3>
        <div class="sort-buttons">
          <button @click="sortCategories('desc')" class="btn-sort" :class="{ active: sortOrder === 'desc' }">
            <i class="fas fa-sort-amount-down"></i> Убыв.
          </button>
          <button @click="sortCategories('asc')" class="btn-sort" :class="{ active: sortOrder === 'asc' }">
            <i class="fas fa-sort-amount-up-alt"></i> Возр.
          </button>
        </div>
      </div>

      <!-- Donut-диаграмма -->
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

      <!-- Компактный список категорий -->
      <div class="categories-list full-width">
        <div
          v-for="category in sortedStatistics"
          :key="category.id"
          class="category-item full-width-item hover-lift"
          :class="{ 'is-expanded': expandedCategories[category.id] }"
        >
          <div class="category-header" @click="category.children?.length ? toggleCategory(category.id) : openCategoryTransactions(category)">
            <div class="category-left">
              <button
                v-if="category.children?.length"
                class="expand-icon-btn"
                :aria-expanded="!!expandedCategories[category.id]"
                @click.stop="toggleCategory(category.id)"
              >
                <i :class="expandedCategories[category.id] ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"></i>
              </button>
              <div v-else class="expand-icon-placeholder"></div>

              <span class="category-dot" :style="{ backgroundColor: getCategoryColor(category.id) }"></span>

              <span class="category-name-text" :title="category.name">{{ category.name }}</span>

              <span
                v-if="category.trend !== undefined && category.trend !== 0"
                class="trend-badge small"
                :class="getTrendBadgeClass({ change_vs_prev_percent: category.trend })"
              >
                <i :class="category.trend > 0 ? 'fas fa-arrow-trend-up' : 'fas fa-arrow-trend-down'"></i>
                {{ Math.abs(category.trend).toFixed(0) }}%
              </span>
            </div>

            <div class="category-right">
              <span
                class="category-total category-total-clickable"
                @click.stop="openCategoryTransactions(category)"
              >
                {{ formatCurrency(category.total) }}
              </span>
              <span class="category-percent">{{ getPercentage(category.total) }}%</span>
            </div>
          </div>

          <!-- Тонкий прогресс-бар -->
          <div class="progress-wrapper">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: getPercentage(category.total) + '%' }"
                :class="currentType === 'income' ? 'progress-income' : 'progress-expense'"
              ></div>
            </div>
          </div>

          <!-- Подкатегории (с анимацией) -->
          <transition name="slide-fade">
            <div v-if="category.children?.length && expandedCategories[category.id]" class="subcategories">
              <div v-for="child in sortedChildren(category.children)" :key="child.id" class="subcategory-item">
                <div class="subcategory-header" @click="openCategoryTransactions(child, category.name)">
                  <div class="subcategory-left">
                    <i class="fas fa-level-up-alt fa-rotate-90 subcategory-icon"></i>
                    <span class="subcategory-name">{{ child.name }}</span>
                  </div>
                  <div class="subcategory-right">
                    <span class="subcategory-total">{{ formatCurrency(child.total) }}</span>
                    <span class="subcategory-percent">{{ getSubPercentage(category.total, child.total) }}%</span>
                  </div>
                </div>
                <div class="progress-bar subcategory-progress">
                  <div
                    class="progress-fill progress-subcategory"
                    :style="{ width: getSubPercentage(category.total, child.total) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </transition>
        </div>

        <div v-if="statistics.length === 0" class="empty-state">
          <i class="fas fa-chart-pie"></i>
          <p>Нет данных за выбранный период</p>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- График по дням месяца                                         -->
    <!-- ============================================================ -->
    <div class="card full-width-card" v-if="selectedPeriod === 'month'">
      <div class="card-header">
        <h3 class="card-title">По дням месяца</h3>
        <span class="chart-mini-note">сумма транзакций в день</span>
      </div>
      <div class="daily-chart-section">
        <canvas v-show="hasDailyData" id="dailyChartCanvas" class="daily-chart-canvas"></canvas>
        <div v-if="!hasDailyData" class="empty-state" style="padding: 1.5rem 0;">
          <i class="fas fa-chart-bar"></i>
          <p>Нет данных за этот месяц</p>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- Сравнение с тем же месяцем прошлого года                      -->
    <!-- ============================================================ -->
    <div class="card full-width-card" v-if="selectedPeriod === 'month' && sameMonthLastYearStats">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-history"></i>
          Сравнение с {{ months[selectedMonth - 1] }} {{ selectedYear - 1 }}
        </h3>
      </div>
      <div class="comparison-section">
        <div class="comparison-item hover-lift">
          <div class="comparison-label">{{ months[selectedMonth - 1] }} {{ selectedYear - 1 }}</div>
          <div class="comparison-value">{{ formatCurrency(sameMonthLastYearStats.total_amount) }}</div>
        </div>
        <div class="comparison-arrow">
          <i
            :class="yearComparison.percent >= 0 ? 'fas fa-arrow-trend-up' : 'fas fa-arrow-trend-down'"
            :style="{ color: getDeltaColor(yearComparison.percent) }"
          ></i>
        </div>
        <div class="comparison-item hover-lift">
          <div class="comparison-label">{{ months[selectedMonth - 1] }} {{ selectedYear }}</div>
          <div class="comparison-value">{{ formatCurrency(totalAmount) }}</div>
        </div>
        <div class="comparison-change hover-lift" :class="getDeltaClass(yearComparison.percent)">
          <div class="comparison-change-percent">{{ formatDelta(yearComparison.percent) }}</div>
          <div class="comparison-change-abs">{{ formatDeltaAbs(yearComparison.absolute) }}</div>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- Годовая статистика                                            -->
    <!-- ============================================================ -->
    <div class="card full-width-card" v-if="selectedPeriod === 'year'">
      <div class="card-header">
        <h3 class="card-title">Аналитика по месяцам</h3>
      </div>

      <div class="mobile-months-grid">
        <div v-for="item in monthlyAnalytics" :key="item.period" class="mobile-month-card hover-lift">
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
              <div
                class="progress-fill"
                :style="{ width: getMonthPercentOfMax(item.total_amount) + '%' }"
                :class="currentType === 'income' ? 'progress-income' : 'progress-expense'"
              >
                <span class="progress-text-small">{{ getMonthPercentOfMax(item.total_amount) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

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
                    <div
                      class="progress-fill"
                      :style="{ width: getMonthPercentOfMax(item.total_amount) + '%' }"
                      :class="currentType === 'income' ? 'progress-income' : 'progress-expense'"
                    ></div>
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

      <div class="year-summary" v-if="monthlyAnalytics.length > 0">
        <div class="summary-card hover-lift">
          <div class="summary-label">Среднее за месяц</div>
          <div class="summary-value">{{ formatCurrency(averageMonthlyAmount) }}</div>
        </div>
        <div class="summary-card hover-lift">
          <div class="summary-label">Медиана</div>
          <div class="summary-value">{{ formatCurrency(medianMonthlyAmount) }}</div>
        </div>
        <div class="summary-card hover-lift">
          <div class="summary-label">Стандартное отклонение</div>
          <div class="summary-value">{{ formatCurrency(standardDeviation) }}</div>
        </div>
        <div class="summary-card hover-lift">
          <div class="summary-label">Коэф. вариации</div>
          <div class="summary-value">{{ coefficientOfVariation.toFixed(1) }}%</div>
        </div>
      </div>
    </div>

    <!-- График (год) -->
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

    <!-- ============================================================ -->
    <!-- Модальное окно с транзакциями категории                       -->
    <!-- ============================================================ -->
    <div v-if="showCategoryModal" class="modal" @click.self="closeCategoryModal">
      <div class="modal-content modal-wide">
        <div class="modal-header">
          <div>
            <h3>Транзакции: {{ modalCategory?.name }}</h3>
            <p class="modal-subtitle">
              {{ months[selectedMonth - 1] }} {{ selectedYear }}
              <template v-if="modalParentCategoryName">
                • {{ modalParentCategoryName }}
              </template>
              • {{ currentType === 'income' ? 'Доходы' : 'Расходы' }}
            </p>
          </div>
          <button class="modal-close" @click="closeCategoryModal">&times;</button>
        </div>

        <div v-if="modalLoading" class="modal-loading">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Загрузка...</p>
        </div>

        <div v-else-if="modalError" class="modal-error">
          <i class="fas fa-exclamation-triangle"></i>
          <p>{{ modalError }}</p>
        </div>

        <template v-else>
          <div class="modal-summary">
            <span>Найдено: <strong>{{ modalTotalItems }}</strong></span>
            <span>
              Итого:
              <strong :class="currentType === 'income' ? 'text-success' : 'text-danger'">
                {{ formatCurrency(modalTotalSum) }}
              </strong>
            </span>
          </div>

          <div class="modal-transactions-list">
            <div v-for="t in modalTransactions" :key="t.id" class="modal-transaction-item">
              <div class="modal-transaction-left">
                <div class="modal-transaction-date">
                  <i class="fas fa-calendar-day"></i>
                  {{ formatModalDate(t.create_at) }}
                </div>
                <div class="modal-transaction-meta">
                  <span v-if="t.account?.name" class="modal-transaction-account">
                    <i class="fas fa-credit-card"></i> {{ t.account.name }}
                  </span>
                  <span v-if="t.comment" class="modal-transaction-comment">
                    — {{ t.comment }}
                  </span>
                </div>
              </div>
              <div
                class="modal-transaction-amount"
                :class="currentType === 'income' ? 'text-success' : 'text-danger'"
              >
                {{ formatCurrency(t.amount) }}
              </div>
            </div>

            <div v-if="modalTransactions.length === 0" class="empty-state">
              <i class="fas fa-receipt"></i>
              <p>Нет транзакций за этот период</p>
            </div>
          </div>

          <div v-if="modalTotalPages > 1" class="modal-pagination">
            <button
              class="btn btn-secondary modal-page-btn hover-lift"
              :disabled="modalCurrentPage === 1"
              @click="modalPrevPage"
              aria-label="Предыдущая страница"
            >
              <i class="fas fa-chevron-left"></i>
              <span class="modal-page-label">Назад</span>
            </button>
            <span class="modal-pagination-info">
              <span class="modal-page-info-full">Страница </span>
              <strong>{{ modalCurrentPage }}</strong>
              <span class="modal-page-info-full"> из </span>
              <span class="modal-page-info-short"> / </span>
              <span>{{ modalTotalPages }}</span>
            </span>
            <button
              class="btn btn-secondary modal-page-btn hover-lift"
              :disabled="modalCurrentPage === modalTotalPages"
              @click="modalNextPage"
              aria-label="Следующая страница"
            >
              <span class="modal-page-label">Вперед</span>
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </template>
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
    // --------- базовое состояние ---------
    const statistics = ref([])
    const sortedStatistics = ref([])
    const monthlyAnalytics = ref([])
    const totalAmount = ref(0)
    const transactionCount = ref(0)
    const currentType = ref('expense')
    const selectedPeriod = ref('month')
    const selectedYear = ref(new Date().getFullYear())
    const selectedMonth = ref(new Date().getMonth() + 1)
    const showFilters = ref(false)
    const isMobile = ref(false)
    const isTablet = ref(false)
    const expandedCategories = ref({})
    const sortOrder = ref('desc')
    const categoryColors = ref({})
    const loading = ref(false)

    let resizeObserver = null
    let loadRequestId = 0

    // --------- состояние для месяца ---------
    const previousMonthStats = ref(null)
    const sameMonthLastYearStats = ref(null)
    const dailyStatistics = ref([])
    const maxTransaction = ref(null)

    // --------- тема ---------
    const isDarkTheme = ref(document.documentElement.getAttribute('data-theme') === 'dark')

    // --------- модалка ---------
    const showCategoryModal = ref(false)
    const modalCategory = ref(null)
    const modalParentCategoryName = ref('')
    const modalTransactions = ref([])
    const modalLoading = ref(false)
    const modalError = ref('')
    const modalCurrentPage = ref(1)
    const modalPageSize = ref(20)
    const modalTotalPages = ref(1)
    const modalTotalItems = ref(0)

    const modalTotalSum = computed(() => {
      return modalTransactions.value.reduce((sum, t) => sum + (parseFloat(t.amount) || 0), 0)
    })

    // --------- списки ---------
    const years = computed(() => {
      const currentYear = new Date().getFullYear()
      return Array.from({ length: 5 }, (_, i) => currentYear - i)
    })
    const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    const colorPalette = ['#10b981', '#ef4444', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1', '#14b8a6', '#d946ef', '#0ea5e9', '#a855f7', '#22c55e']

    // --------- навигация ---------
    const isCurrentMonth = computed(() => {
      const now = new Date()
      return selectedYear.value === now.getFullYear() && selectedMonth.value === now.getMonth() + 1
    })

    const periodHint = computed(() => {
      const now = new Date()
      const diff = (now.getFullYear() - selectedYear.value) * 12 + (now.getMonth() + 1 - selectedMonth.value)
      if (diff === 0) return 'текущий месяц'
      if (diff === 1) return 'прошлый месяц'
      if (diff < 12) return `${diff} мес. назад`
      const y = Math.floor(diff / 12)
      const m = diff % 12
      return m > 0 ? `${y} г. ${m} мес. назад` : `${y} г. назад`
    })

    const shiftMonth = (delta) => {
      let m = selectedMonth.value + delta
      let y = selectedYear.value
      if (m < 1)  { m = 12; y-- }
      if (m > 12) { m = 1;  y++ }
      selectedMonth.value = m
      selectedYear.value = y
    }

    // --------- вычисляемые значения ---------
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

    const monthComparison = computed(() => {
      const cur = totalAmount.value
      if (!previousMonthStats.value) return { absolute: 0, percent: 0, previous: 0 }
      const prev = parseFloat(previousMonthStats.value.total_amount) || 0
      return {
        absolute: cur - prev,
        percent: prev === 0 ? (cur > 0 ? 100 : 0) : ((cur - prev) / prev) * 100,
        previous: prev
      }
    })

    const yearComparison = computed(() => {
      const cur = totalAmount.value
      if (!sameMonthLastYearStats.value) return { absolute: 0, percent: 0, previous: 0 }
      const prev = parseFloat(sameMonthLastYearStats.value.total_amount) || 0
      return {
        absolute: cur - prev,
        percent: prev === 0 ? (cur > 0 ? 100 : 0) : ((cur - prev) / prev) * 100,
        previous: prev
      }
    })

    const topCategories = computed(() => {
      return [...statistics.value].sort((a, b) => parseFloat(b.total) - parseFloat(a.total)).slice(0, 3)
    })

    const maxOrTop = computed(() => {
      if (maxTransaction.value && maxTransaction.value.amount) {
        return { amount: maxTransaction.value.amount, label: maxTransaction.value.category_name || '—' }
      }
      if (topCategories.value.length > 0) {
        return { amount: topCategories.value[0].total, label: `${topCategories.value[0].name} (категория)` }
      }
      return null
    })

    const hasDailyData = computed(() => {
      if (!Array.isArray(dailyStatistics.value) || dailyStatistics.value.length === 0) return false
      return dailyStatistics.value.some(d => {
        const val = parseFloat(d.total_amount)
        return !isNaN(val) && val > 0
      })
    })

    // --------- утилиты ---------
    const getCategoryColor = (categoryId) => categoryColors.value[categoryId] || '#ccc'

    const assignColorsToCategories = () => {
      statistics.value.forEach((category, index) => {
        categoryColors.value[category.id] = colorPalette[index % colorPalette.length]
      })
    }

    const enrichWithTrends = () => {
      const prevMap = {}
      if (previousMonthStats.value?.statistics) {
        previousMonthStats.value.statistics.forEach(c => {
          const total = parseFloat(c.total) || 0
          if (total > 0) prevMap[c.id] = total
        })
      }
      statistics.value.forEach(cat => {
        const prev = prevMap[cat.id]
        const cur = parseFloat(cat.total) || 0
        cat.trend = (prev !== undefined && prev > 0) ? ((cur - prev) / prev) * 100 : undefined
      })
    }

    const getMonthPercentOfMax = (amount) => {
      if (maxMonthAmount.value === 0) return 0
      return ((parseFloat(amount) / maxMonthAmount.value) * 100).toFixed(1)
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

    const getDeltaClass = (percent) => {
      if (percent > 0) return currentType.value === 'income' ? 'text-success' : 'text-danger'
      if (percent < 0) return currentType.value === 'income' ? 'text-danger' : 'text-success'
      return ''
    }

    const getDeltaColor = (percent) => {
      if (percent > 0) return currentType.value === 'income' ? 'var(--secondary-color)' : 'var(--danger-color)'
      if (percent < 0) return currentType.value === 'income' ? 'var(--danger-color)' : 'var(--secondary-color)'
      return 'var(--gray-color)'
    }

    const formatDelta = (percent) => {
      if (!percent || percent === 0) return '—'
      return (percent > 0 ? '+' : '') + percent.toFixed(1) + '%'
    }

    const formatDeltaAbs = (value) => {
      if (!value || value === 0) return '—'
      const sign = value > 0 ? '+' : '−'
      return sign + formatCurrency(Math.abs(value))
    }

    const formatCurrency = (value) => {
      if (!value && value !== 0) return '0 ₽'
      const numValue = parseFloat(value)
      if (isNaN(numValue)) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(numValue)
    }

    const formatShortCurrency = (value) => {
      const v = parseFloat(value) || 0
      if (Math.abs(v) >= 1000000) return (v / 1000000).toFixed(1) + 'M'
      if (Math.abs(v) >= 1000) return Math.round(v / 1000) + 'k'
      return Math.round(v).toString()
    }

    const formatDateOnly = (date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    const formatModalDate = (dateString) => {
      if (!dateString) return ''
      const d = new Date(dateString)
      if (isNaN(d.getTime())) return ''
      return d.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
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

    // --------- графика ---------
    const getCanvasColors = () => ({
      stroke: isDarkTheme.value ? '#252936' : '#ffffff',
      text: isDarkTheme.value ? '#9ca3af' : '#666666',
      grid: isDarkTheme.value ? '#374151' : '#ccc'
    })

    const drawPieChart = () => {
      const canvas = document.getElementById('pieChartCanvas')
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const container = canvas.parentElement
      if (!container) return

      const containerWidth = container.clientWidth
      const size = Math.min(containerWidth - 40, isTablet.value ? 280 : 350)
      canvas.width = size
      canvas.height = size
      canvas.style.width = `${size}px`
      canvas.style.height = `${size}px`

      const centerX = size / 2
      const centerY = size / 2
      const radius = size / 2 - 20
      const innerRadius = radius * 0.62
      const colors = getCanvasColors()

      ctx.clearRect(0, 0, size, size)

      if (statistics.value.length === 0) {
        ctx.beginPath()
        ctx.arc(centerX, centerY, (radius + innerRadius) / 2, 0, 2 * Math.PI)
        ctx.lineWidth = radius - innerRadius
        ctx.strokeStyle = isDarkTheme.value ? '#374151' : '#e5e7eb'
        ctx.stroke()
        return
      }

      let startAngle = -Math.PI / 2

      statistics.value.forEach((category) => {
        const percentage = parseFloat(getPercentage(category.total)) / 100
        const angle = percentage * 2 * Math.PI
        const endAngle = startAngle + angle

        ctx.beginPath()
        ctx.fillStyle = categoryColors.value[category.id]
        ctx.moveTo(centerX + Math.cos(startAngle) * innerRadius, centerY + Math.sin(startAngle) * innerRadius)
        ctx.arc(centerX, centerY, radius, startAngle, endAngle)
        ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true)
        ctx.closePath()
        ctx.fill()
        ctx.strokeStyle = colors.stroke
        ctx.lineWidth = 3
        ctx.stroke()

        startAngle = endAngle
      })

      startAngle = -Math.PI / 2
      statistics.value.forEach((category) => {
        const percentage = parseFloat(getPercentage(category.total)) / 100
        const angle = percentage * 2 * Math.PI
        const endAngle = startAngle + angle
        if (percentage > 0.08) {
          const midAngle = startAngle + angle / 2
          const textRadius = (radius + innerRadius) / 2
          const x = centerX + Math.cos(midAngle) * textRadius
          const y = centerY + Math.sin(midAngle) * textRadius
          ctx.fillStyle = '#ffffff'
          const fontSize = size < 250 ? 10 : 12
          ctx.font = `bold ${fontSize}px Arial`
          ctx.textAlign = 'center'
          ctx.fillText(`${getPercentage(category.total)}%`, x, y + fontSize / 3)
        }
        startAngle = endAngle
      })

      ctx.fillStyle = isDarkTheme.value ? '#9ca3af' : '#6b7280'
      ctx.font = '11px Arial'
      ctx.textAlign = 'center'
      ctx.fillText('Всего', centerX, centerY - 6)

      ctx.fillStyle = isDarkTheme.value ? '#f3f4f6' : '#111827'
      ctx.font = `bold ${size < 250 ? 14 : 16}px Arial`
      ctx.fillText(formatShortCurrency(totalAmount.value), centerX, centerY + 14)
    }

    const drawDailyChart = () => {
      const canvas = document.getElementById('dailyChartCanvas')
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const container = canvas.parentElement
      const width = container ? container.clientWidth : 600
      if (width < 50) return

      const height = 200
      const dpr = window.devicePixelRatio || 1
      canvas.width = width * dpr
      canvas.height = height * dpr
      canvas.style.width = `${width}px`
      canvas.style.height = `${height}px`
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, width, height)

      const daysInMonth = new Date(selectedYear.value, selectedMonth.value, 0).getDate()
      const dailyMap = {}
      dailyStatistics.value.forEach(d => {
        if (d.day) dailyMap[d.day] = parseFloat(d.total_amount) || 0
      })

      const data = []
      for (let day = 1; day <= daysInMonth; day++) {
        data.push(dailyMap[day] || 0)
      }

      const maxValue = Math.max(...data, 1)
      const padding = { top: 16, right: 12, bottom: 28, left: 44 }
      const chartWidth = width - padding.left - padding.right
      const chartHeight = height - padding.top - padding.bottom
      const colors = getCanvasColors()

      ctx.strokeStyle = isDarkTheme.value ? '#374151' : '#e5e7eb'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(padding.left, padding.top)
      ctx.lineTo(padding.left, height - padding.bottom)
      ctx.lineTo(width - padding.right, height - padding.bottom)
      ctx.stroke()

      ctx.fillStyle = colors.text
      ctx.font = '10px Arial'
      ctx.textAlign = 'right'
      for (let i = 0; i <= 3; i++) {
        const value = (maxValue / 3) * i
        const y = height - padding.bottom - (i / 3) * chartHeight
        ctx.fillText(formatShortCurrency(value), padding.left - 6, y + 3)
      }

      const barWidth = chartWidth / daysInMonth
      const gap = Math.max(1, barWidth * 0.3)
      data.forEach((value, i) => {
        const barHeight = (value / maxValue) * chartHeight
        const x = padding.left + i * barWidth + gap / 2
        const y = height - padding.bottom - barHeight
        const w = Math.max(1, barWidth - gap)

        if (value > 0) {
          ctx.fillStyle = currentType.value === 'income' ? '#10b981' : '#ef4444'
          const radius = Math.min(3, w / 2)
          ctx.beginPath()
          ctx.moveTo(x, y + barHeight)
          ctx.lineTo(x, y + radius)
          ctx.quadraticCurveTo(x, y, x + radius, y)
          ctx.lineTo(x + w - radius, y)
          ctx.quadraticCurveTo(x + w, y, x + w, y + radius)
          ctx.lineTo(x + w, y + barHeight)
          ctx.fill()
        } else {
          ctx.fillStyle = isDarkTheme.value ? '#374151' : '#e5e7eb'
          ctx.fillRect(x, height - padding.bottom - 2, w, 2)
        }
      })

      ctx.fillStyle = colors.text
      ctx.font = '10px Arial'
      ctx.textAlign = 'center'
      const step = daysInMonth <= 10 ? 1 : 5
      for (let day = 1; day <= daysInMonth; day += step) {
        const x = padding.left + (day - 0.5) * barWidth
        ctx.fillText(day, x, height - padding.bottom + 14)
      }
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
      const padding = isMobile.value || isTablet.value ? 50 : 60
      const chartWidth = width - 2 * padding
      const chartHeight = height - 2 * padding
      const maxValue = Math.max(...monthlyAnalytics.value.map(item => parseFloat(item.total_amount)), 0)
      const colors = getCanvasColors()

      ctx.beginPath()
      ctx.strokeStyle = colors.grid
      ctx.lineWidth = 1
      ctx.moveTo(padding, padding)
      ctx.lineTo(padding, height - padding)
      ctx.moveTo(padding, height - padding)
      ctx.lineTo(width - padding, height - padding)
      ctx.stroke()

      ctx.fillStyle = colors.text
      ctx.font = isMobile.value || isTablet.value ? '10px Arial' : '12px Arial'
      for (let i = 0; i <= 5; i++) {
        const value = (maxValue / 5) * i
        const y = height - padding - (i / 5) * chartHeight
        ctx.fillText(formatCurrency(value), 10, y + 4)
      }

      const step = chartWidth / (monthlyAnalytics.value.length - 1)
      ctx.beginPath()
      ctx.strokeStyle = currentType.value === 'income' ? '#10b981' : '#ef4444'
      ctx.lineWidth = isMobile.value || isTablet.value ? 2 : 3

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
        ctx.arc(x, y, isMobile.value || isTablet.value ? 4 : 6, 0, 2 * Math.PI)
        ctx.fill()

        ctx.beginPath()
        ctx.fillStyle = isDarkTheme.value ? '#252936' : '#ffffff'
        ctx.arc(x, y, isMobile.value || isTablet.value ? 2 : 3, 0, 2 * Math.PI)
        ctx.fill()

        ctx.fillStyle = colors.text
        ctx.font = isMobile.value || isTablet.value ? '10px Arial' : '12px Arial'
        const monthLabel = item.month_name.substring(0, 3)
        ctx.fillText(monthLabel, x - (isMobile.value || isTablet.value ? 10 : 15), height - padding + (isMobile.value || isTablet.value ? 15 : 20))
      })
    }

    const redrawAllCharts = () => {
      setTimeout(() => {
        if (selectedPeriod.value === 'month') {
          if (statistics.value.length > 0) drawPieChart()
          if (hasDailyData.value) drawDailyChart()
        } else {
          if (monthlyAnalytics.value.length > 0) drawChart()
        }
      }, 100)
    }

    // --------- загрузка данных ---------
    const resetMonthState = () => {
      totalAmount.value = 0
      statistics.value = []
      sortedStatistics.value = []
      transactionCount.value = 0
      previousMonthStats.value = null
      sameMonthLastYearStats.value = null
      dailyStatistics.value = []
      maxTransaction.value = null
    }

    const loadMonthData = async (myId) => {
      const curMonth = selectedMonth.value
      const curYear = selectedYear.value
      const curType = currentType.value
      const prevMonth = curMonth === 1 ? 12 : curMonth - 1
      const prevYear = curMonth === 1 ? curYear - 1 : curYear

      let current
      try {
        current = await apiService.getMonthStatistics(curMonth, curYear, curType)
      } catch (err) {
        console.error('[stats] current API failed', err)
        if (myId === loadRequestId) {
          resetMonthState()
          await nextTick()
          redrawAllCharts()
        }
        return
      }

      if (myId !== loadRequestId) return

      const [previous, lastYear, dailyRaw] = await Promise.all([
        apiService.getMonthStatistics(prevMonth, prevYear, curType).catch(() => null),
        apiService.getMonthStatistics(curMonth, curYear - 1, curType).catch(() => null),
        apiService.getDailyStatistics(curMonth, curYear, curType).catch((e) => {
          console.warn('Ошибка загрузки дневной статистики:', e)
          return null
        })
      ])

      if (myId !== loadRequestId) return

      totalAmount.value = parseFloat(current.total_amount) || 0
      statistics.value = current.statistics || []
      previousMonthStats.value = previous
      sameMonthLastYearStats.value = lastYear

      const dailyArray = dailyRaw?.results || (Array.isArray(dailyRaw) ? dailyRaw : [])
      dailyStatistics.value = dailyArray

      maxTransaction.value = current.max_transaction || null

      let count = 0
      if (typeof current.transaction_count === 'number') count = current.transaction_count
      else if (typeof current.count === 'number') count = current.count
      if (!count) count = statistics.value.reduce((s, c) => s + (c.transaction_count || 0), 0)
      if (!count && dailyStatistics.value.length) count = dailyStatistics.value.reduce((s, d) => s + (d.transaction_count || 0), 0)

      if (!count && totalAmount.value > 0) {
        try {
          const firstDay = new Date(curYear, curMonth - 1, 1)
          const lastDay = new Date(curYear, curMonth, 0)
          const resp = await apiService.getTransactions({
            page: 1, page_size: 1, type: curType,
            create_at_after: formatDateOnly(firstDay),
            create_at_before: formatDateOnly(lastDay)
          })
          count = resp.count || 0
        } catch (e) { /* ignore */ }
      }

      if (myId === loadRequestId) transactionCount.value = count

      assignColorsToCategories()
      enrichWithTrends()
      sortCategories(sortOrder.value)

      const newExpanded = {}
      statistics.value.forEach(cat => { newExpanded[cat.id] = false })
      expandedCategories.value = newExpanded

      if (myId !== loadRequestId) return
      await nextTick()
      redrawAllCharts()
    }

    const loadYearData = async (myId) => {
      let yearlyData
      try {
        yearlyData = await apiService.getMonthlyAnalytics(selectedYear.value, currentType.value)
      } catch (err) {
        console.error('[stats] year API failed', err)
        if (myId === loadRequestId) {
          monthlyAnalytics.value = []
          totalAmount.value = 0
          transactionCount.value = 0
        }
        return
      }
      if (myId !== loadRequestId) return

      monthlyAnalytics.value = yearlyData.results || []
      totalAmount.value = monthlyAnalytics.value.reduce((sum, item) => sum + parseFloat(item.total_amount), 0)
      transactionCount.value = monthlyAnalytics.value.reduce((sum, item) => sum + item.transaction_count, 0)
      statistics.value = []
      sortedStatistics.value = []
      previousMonthStats.value = null
      sameMonthLastYearStats.value = null
      dailyStatistics.value = []
      maxTransaction.value = null

      await nextTick()
      redrawAllCharts()
    }

    const loadStatistics = async () => {
      const myId = ++loadRequestId
      loading.value = true
      try {
        if (selectedPeriod.value === 'month') {
          await loadMonthData(myId)
        } else {
          await loadYearData(myId)
        }
      } catch (error) {
        console.error('[stats] load error', error)
      } finally {
        if (myId === loadRequestId) loading.value = false
      }
    }

    // --------- модалка ---------
    const openCategoryTransactions = async (category, parentName = '') => {
      if (!category) return
      modalCategory.value = category
      modalParentCategoryName.value = parentName
      modalCurrentPage.value = 1
      showCategoryModal.value = true
      await loadCategoryTransactions()
    }

    const loadCategoryTransactions = async () => {
      if (!modalCategory.value) return
      modalLoading.value = true
      modalError.value = ''

      try {
        const year = selectedYear.value
        const month = selectedMonth.value
        const firstDay = new Date(year, month - 1, 1)
        const lastDay = new Date(year, month, 0)

        const params = {
          page: modalCurrentPage.value,
          page_size: modalPageSize.value,
          type: currentType.value,
          create_at_after: formatDateOnly(firstDay),
          create_at_before: formatDateOnly(lastDay)
        }

        if (modalCategory.value.id === 0) {
          params.category_isnull = 'true'
        } else {
          params.category_id = modalCategory.value.id
        }

        const response = await apiService.getTransactions(params)
        modalTransactions.value = response.results || []
        modalTotalItems.value = response.count || 0
        modalTotalPages.value = Math.max(1, Math.ceil(modalTotalItems.value / modalPageSize.value))
      } catch (error) {
        console.error('Error loading category transactions:', error)
        modalError.value = 'Не удалось загрузить транзакции. Проверьте соединение.'
        modalTransactions.value = []
        modalTotalItems.value = 0
        modalTotalPages.value = 1
      } finally {
        modalLoading.value = false
      }
    }

    const closeCategoryModal = () => {
      showCategoryModal.value = false
      modalCategory.value = null
      modalParentCategoryName.value = ''
      modalTransactions.value = []
      modalCurrentPage.value = 1
      modalTotalPages.value = 1
      modalTotalItems.value = 0
      modalError.value = ''
    }

    const modalPrevPage = () => {
      if (modalCurrentPage.value > 1) {
        modalCurrentPage.value--
        loadCategoryTransactions()
      }
    }

    const modalNextPage = () => {
      if (modalCurrentPage.value < modalTotalPages.value) {
        modalCurrentPage.value++
        loadCategoryTransactions()
      }
    }

    // --------- ресайз и тема ---------
    const checkScreenSize = () => {
      const width = window.innerWidth
      isMobile.value = width <= 768
      isTablet.value = width >= 768 && width <= 1024
    }

    const handleResize = () => {
      checkScreenSize()
      redrawAllCharts()
    }

    const themeObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'data-theme') {
          isDarkTheme.value = document.documentElement.getAttribute('data-theme') === 'dark'
          redrawAllCharts()
        }
      })
    })

    onMounted(() => {
      checkScreenSize()
      loadStatistics()
      window.addEventListener('resize', handleResize)
      themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })

      if (window.ResizeObserver) {
        resizeObserver = new ResizeObserver(() => {
          redrawAllCharts()
        })
        const pieWrapper = document.querySelector('.pie-chart-wrapper')
        if (pieWrapper) resizeObserver.observe(pieWrapper)
      }
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      themeObserver.disconnect()
      if (resizeObserver) resizeObserver.disconnect()
    })

    watch([currentType, selectedPeriod, selectedYear, selectedMonth], () => loadStatistics())

    return {
      statistics, sortedStatistics, monthlyAnalytics, totalAmount, transactionCount, currentType,
      selectedPeriod, selectedYear, selectedMonth, years, months, averageAmount, showFilters, isMobile, isTablet,
      expandedCategories, sortOrder, maxMonthAmount, maxMonthName, minMonthAmount, minMonthName,
      averageMonthlyAmount, medianMonthlyAmount, standardDeviation, coefficientOfVariation,
      loading,

      previousMonthStats, sameMonthLastYearStats, dailyStatistics, maxTransaction,
      monthComparison, yearComparison, topCategories, maxOrTop, hasDailyData,
      isCurrentMonth, periodHint, shiftMonth,

      loadStatistics, toggleCategory, sortCategories, sortedChildren,
      getPercentage, getSubPercentage, getMonthPercentOfMax,
      getTrendClass, getTrendBadgeClass, getDeltaClass, getDeltaColor,
      formatCurrency, formatDelta, formatDeltaAbs, getCategoryColor,

      showCategoryModal, modalCategory, modalParentCategoryName,
      modalTransactions, modalLoading, modalError, modalTotalSum,
      modalCurrentPage, modalTotalPages, modalTotalItems,
      openCategoryTransactions, closeCategoryModal, modalPrevPage, modalNextPage,
      formatModalDate
    }
  }
}
</script>

<style scoped>
/* ========== Общие стили и переменные ========== */
.statistics-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
  /* Отступ снизу, чтобы кнопка "+" (FAB) не перекрывала контент */
  padding-bottom: 90px;
  min-height: 100vh;
  transition: opacity 0.3s ease;
  /* Защита от горизонтального скролла */
  overflow-x: hidden;
  box-sizing: border-box;
  width: 100%;
}

.statistics-page.is-loading .stats-grid,
.statistics-page.is-loading .top-categories {
  opacity: 0.6;
}

.page-header {
  padding: 0.5rem 0 1.5rem;
  text-align: center;
}
.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0;
  color: var(--dark-color);
  letter-spacing: -0.5px;
}

/* ========== Эффекты наведения ========== */
.hover-lift {
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.25s ease,
              border-color 0.25s ease;
}
.hover-lift:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  border-color: rgba(99, 102, 241, 0.4);
}
.hover-lift:active {
  transform: translateY(-1px) scale(0.99);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

/* ========== Универсальные карточки ========== */
.card {
  background: var(--white);
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
  margin-bottom: 1rem;
  overflow: hidden;
  border: 1px solid var(--light-color);
  box-sizing: border-box;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--light-color);
  background: var(--white);
}
.card-title {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0;
  color: var(--dark-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.card-title i { color: var(--primary-color); }

/* ========== Навигация по месяцам ========== */
.period-nav-card {
  padding: 0.75rem 1rem;
}
.period-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.nav-arrow {
  background: var(--light-color);
  border: none;
  border-radius: 12px;
  color: var(--dark-color);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.nav-arrow:hover:not(:disabled) {
  background: var(--primary-color);
  color: #fff;
  transform: scale(1.05);
}
.nav-arrow:active:not(:disabled) {
  transform: scale(0.95);
}
.nav-arrow:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.period-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1.3;
  text-align: center;
}
.period-label strong {
  font-size: 1.1rem;
  color: var(--dark-color);
}
.period-hint {
  font-size: 0.75rem;
  color: var(--gray-color);
  font-weight: 500;
}

/* ========== Фильтры ========== */
.filters-card { margin-bottom: 1rem; }
.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  cursor: pointer;
  background: var(--light-color);
  border-radius: 16px;
  transition: background 0.2s;
}
.filters-header:hover {
  background: rgba(99, 102, 241, 0.08);
}
.filters-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
  color: var(--dark-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.filters-body {
  padding: 1.5rem;
  background: var(--white);
  border-top: 1px solid var(--light-color);
}
.filters-hidden { display: none; }
.filters-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.filter-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--gray-color);
  margin-bottom: 0.25rem;
  display: block;
}
.form-control {
  padding: 0.65rem 1rem;
  border: 2px solid var(--light-color);
  border-radius: 12px;
  font-size: 0.9rem;
  transition: all 0.2s;
  background: var(--white);
  color: var(--dark-color);
  width: 100%;
  outline: none;
  box-sizing: border-box;
}
.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

/* ========== Карточки статистики ========== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}
.stat-card {
  background: var(--white);
  border-radius: 16px;
  padding: 1.25rem;
  text-align: center;
  border: 1px solid var(--light-color);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
  box-sizing: border-box;
  /* Убираем возможное вылезание контента */
  overflow: hidden;
  min-width: 0;
}
.stat-card.stat-main { grid-column: span 2; }
.stat-card-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--gray-color);
  margin-bottom: 0.5rem;
  font-weight: 600;
}
.stat-card-value {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--dark-color);
}
.stat-card-subtitle {
  font-size: 0.75rem;
  color: var(--gray-color);
  margin-top: 0.35rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.stat-compare .stat-card-value { font-size: 1.4rem; }

.text-success { color: var(--secondary-color) !important; }
.text-danger { color: var(--danger-color) !important; }

/* ========== Топ-3 категории ========== */
.top-categories {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}
.top-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: 16px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
  box-sizing: border-box;
}
.top-card.top-rank-1 { border-left: 4px solid #f59e0b; }
.top-card.top-rank-2 { border-left: 4px solid #94a3b8; }
.top-card.top-rank-3 { border-left: 4px solid #b45309; }
.top-rank {
  font-weight: 800;
  font-size: 1rem;
  color: var(--gray-color);
  min-width: 30px;
}
.top-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}
.top-info { flex: 1; min-width: 0; }
.top-name {
  font-size: 0.9rem;
  color: var(--dark-color);
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.top-amount {
  font-size: 0.8rem;
  color: var(--gray-color);
  margin-top: 2px;
}
.top-share {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--dark-color);
  flex-shrink: 0;
}

/* ========== Donut-диаграмма ========== */
.pie-chart-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
  padding: 1.5rem;
  background: var(--light-color);
}
.pie-chart-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 260px;
}
.pie-chart-canvas {
  display: block;
  margin: 0 auto;
}
.pie-chart-legend {
  width: 100%;
  max-height: 250px;
  overflow-y: auto;
  background: var(--white);
  border-radius: 12px;
  padding: 0.75rem;
  border: 1px solid var(--light-color);
  box-sizing: border-box;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-bottom: 1px solid var(--light-color);
}
.legend-item:last-child { border-bottom: none; }
.legend-color { width: 12px; height: 12px; border-radius: 4px; flex-shrink: 0; }
.legend-name {
  flex: 1;
  font-size: 0.85rem;
  color: var(--dark-color);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.legend-percent { font-size: 0.85rem; font-weight: 700; color: var(--gray-color); }

/* ========== Компактный список категорий ========== */
.categories-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
}
.category-item {
  background: var(--white);
  border-radius: 16px;
  padding: 1.25rem;
  border: 1px solid var(--light-color);
  position: relative;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
  box-sizing: border-box;
}
.category-item.is-expanded {
  border-color: var(--primary-color);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.1);
}
.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
  gap: 0.75rem;
  flex-wrap: wrap; /* Позволяет переносить сумму на новую строку, если не влезает */
}
.category-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
  flex: 1;
}
.category-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}
.expand-icon-btn {
  background: var(--light-color);
  border: none;
  cursor: pointer;
  width: 24px;
  height: 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gray-color);
  font-size: 0.7rem;
  transition: all 0.2s;
}
.category-item:hover .expand-icon-btn {
  background: var(--primary-color);
  color: #fff;
}
.expand-icon-placeholder { width: 24px; height: 24px; }
.category-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 0 0 3px var(--white), 0 0 0 5px rgba(0,0,0,0.03);
}
.category-name-text {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--dark-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.2s;
}
.category-header:hover .category-name-text { color: var(--primary-color); }
.category-total {
  font-weight: 800;
  font-size: 1rem;
  color: var(--dark-color);
  transition: color 0.2s;
}
.category-total:hover { color: var(--primary-color); }
.category-percent {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--gray-color);
  background: var(--light-color);
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
  min-width: 50px;
  text-align: center;
}

/* ========== Тонкие прогресс-бары ========== */
.progress-wrapper { margin-top: 1rem; }
.progress-bar {
  height: 8px;
  background: var(--light-color);
  border-radius: 99px;
  overflow: hidden;
  position: relative;
}
.progress-bar.small { height: 24px; }
.progress-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.progress-income {
  background: linear-gradient(90deg, #10b981, #34d399);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
}
.progress-expense {
  background: linear-gradient(90deg, #ef4444, #f87171);
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
}
.progress-subcategory {
  background: linear-gradient(90deg, #60a5fa, #93c5fd);
  opacity: 0.9;
}

.mobile-progress .progress-fill,
.table-progress .progress-fill {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10px;
  color: #fff;
  font-weight: 700;
  font-size: 0.75rem;
}
.progress-text-small { font-size: 0.7rem; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }

/* ========== Подкатегории ========== */
.subcategories {
  margin-top: 1rem;
  padding-top: 1rem;
  padding-left: 1.5rem;
  border-top: 1px dashed var(--light-color);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
}
.subcategories::before {
  content: '';
  position: absolute;
  left: 0.5rem;
  top: 0;
  bottom: 1rem;
  width: 2px;
  background: var(--light-color);
  border-radius: 2px;
}
.subcategory-item { position: relative; cursor: pointer; }
.subcategory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}
.subcategory-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--gray-color);
  transition: color 0.2s;
}
.subcategory-item:hover .subcategory-left { color: var(--dark-color); }
.subcategory-icon { font-size: 0.75rem; opacity: 0.6; }
.subcategory-name { font-weight: 600; }
.subcategory-right { display: flex; align-items: center; gap: 0.75rem; }
.subcategory-total { font-weight: 700; font-size: 0.85rem; color: var(--dark-color); }
.subcategory-percent { font-size: 0.75rem; color: var(--gray-color); font-weight: 600; min-width: 40px; text-align: right; }
.subcategory-progress {
  height: 6px;
  background: var(--white);
  border: 1px solid var(--light-color);
}

/* ========== Тренд-бейджи ========== */
.trend-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.2rem 0.5rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
}
.trend-badge.small { font-size: 0.7rem; padding: 0.15rem 0.4rem; }
.trend-badge.trend-up { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.trend-badge.trend-down { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.trend-badge.trend-neutral { background: rgba(107, 114, 128, 0.15); color: var(--gray-color); }

/* ========== Дневной график ========== */
.daily-chart-section { padding: 1.5rem; background: var(--white); overflow-x: hidden; }
.daily-chart-canvas { display: block; width: 100%; max-width: 100%; }

/* ========== Сравнение с прошлым годом ========== */
.comparison-section {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--light-color);
}
.comparison-item {
  flex: 1;
  min-width: 130px;
  padding: 1rem;
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  box-sizing: border-box;
}
.comparison-label { font-size: 0.75rem; font-weight: 600; color: var(--gray-color); margin-bottom: 0.35rem; }
.comparison-value { font-weight: 800; font-size: 1rem; color: var(--dark-color); }
.comparison-arrow { font-size: 1.25rem; text-align: center; padding: 0 0.5rem; }
.comparison-change {
  flex: 1;
  min-width: 130px;
  padding: 1rem;
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: 12px;
  text-align: center;
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  box-sizing: border-box;
}
.comparison-change-percent { font-size: 1.1rem; }
.comparison-change-abs { font-size: 0.75rem; color: var(--gray-color); margin-top: 0.35rem; font-weight: 600; }

/* ========== Мобильные карточки месяцев (год) ========== */
.mobile-months-grid { display: block; padding: 1rem; }
.mobile-month-card {
  background: var(--white);
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  border: 1px solid var(--light-color);
  box-shadow: 0 4px 15px rgba(0,0,0,0.02);
  box-sizing: border-box;
}
.mobile-month-card:last-child { margin-bottom: 0; }
.mobile-month-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--light-color);
}
.mobile-month-name { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; color: var(--dark-color); }
.month-name-text { font-weight: 700; font-size: 0.95rem; }
.mobile-month-amount { font-size: 1.1rem; font-weight: 800; }
.mobile-stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-bottom: 1rem; }
.mobile-stat { text-align: center; padding: 0.75rem; background: var(--light-color); border-radius: 12px; }
.mobile-stat-label { font-size: 0.7rem; font-weight: 600; color: var(--gray-color); margin-bottom: 0.35rem; }
.mobile-stat-value { font-size: 0.9rem; font-weight: 700; color: var(--dark-color); }
.mobile-progress { margin-top: 0.75rem; }
.progress-label { font-size: 0.75rem; font-weight: 600; color: var(--gray-color); margin-bottom: 0.35rem; }

/* ========== Десктоп таблица ========== */
.desktop-table-wrapper { display: none; padding: 0 1.5rem 1.5rem; }
.analytics-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.analytics-table th {
  text-align: left;
  padding: 1rem;
  background: var(--light-color);
  color: var(--gray-color);
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.analytics-table th:first-child { border-top-left-radius: 12px; border-bottom-left-radius: 12px; }
.analytics-table th:last-child { border-top-right-radius: 12px; border-bottom-right-radius: 12px; }
.analytics-table td { padding: 1rem; border-bottom: 1px solid var(--light-color); color: var(--dark-color); }
.analytics-table tr:last-child td { border-bottom: none; }
.table-month-cell { display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; }
.table-progress { display: flex; align-items: center; gap: 0.75rem; min-width: 120px; }
.table-progress .progress-bar { flex: 1; height: 24px; }
.table-progress-value { font-size: 0.75rem; font-weight: 700; color: var(--gray-color); min-width: 40px; text-align: right; }

/* ========== Годовая сводка ========== */
.year-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--light-color);
  background: var(--light-color);
}
.summary-card {
  text-align: center;
  padding: 1rem;
  background: var(--white);
  border-radius: 12px;
  border: 1px solid var(--light-color);
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}
.summary-label { font-size: 0.7rem; font-weight: 600; color: var(--gray-color); margin-bottom: 0.35rem; }
.summary-value { font-size: 0.95rem; font-weight: 800; color: var(--dark-color); }

/* ========== Годовой график ========== */
.chart-section { padding: 1.5rem; overflow-x: auto; background: var(--white); }
.chart-canvas { max-width: 100%; height: auto; }
.chart-note {
  text-align: center;
  padding: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--gray-color);
  border-top: 1px solid var(--light-color);
  background: var(--light-color);
}

/* ========== Пустое состояние ========== */
.empty-state { text-align: center; padding: 2rem; color: var(--gray-color); }
.empty-state i { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.4; }
.empty-state p { font-weight: 500; }
.text-center { text-align: center; }

/* ========== Анимации ========== */
.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from,
.slide-fade-leave-to { transform: translateY(-10px); opacity: 0; max-height: 0; }

@keyframes pulse-soft {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(0.98); }
  100% { opacity: 1; transform: scale(1); }
}
.is-loading .stat-card-value { animation: pulse-soft 1.5s infinite ease-in-out; }

/* ============================================================
   Модальное окно
   ============================================================ */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  box-sizing: border-box;
}
.modal-content {
  background: var(--white);
  border-radius: 20px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  border: 1px solid var(--light-color);
  box-sizing: border-box;
}
.modal-content.modal-wide { max-width: 720px; }
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  border-bottom: 1px solid var(--light-color);
  gap: 1rem;
  position: sticky;
  top: 0;
  background: var(--white);
  z-index: 1;
  border-radius: 20px 20px 0 0;
}
.modal-header h3 { margin: 0; font-size: 1.2rem; font-weight: 800; color: var(--dark-color); }
.modal-subtitle { margin: 0.35rem 0 0; font-size: 0.85rem; font-weight: 500; color: var(--gray-color); }
.modal-close {
  background: var(--light-color);
  border: none;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  color: var(--gray-color);
  padding: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
  flex-shrink: 0;
}
.modal-close:hover { background: var(--danger-color); color: #fff; transform: rotate(90deg); }
.modal-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--light-color);
  border-bottom: 1px solid var(--light-color);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--gray-color);
  flex-wrap: wrap;
  gap: 0.5rem;
}
.modal-summary strong { color: var(--dark-color); font-weight: 800; }

.modal-transactions-list { padding: 0.5rem 0; flex: 1; }
.modal-transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--light-color);
  gap: 1rem;
  transition: background 0.2s;
}
.modal-transaction-item:hover { background: var(--light-color); }
.modal-transaction-item:last-child { border-bottom: none; }
.modal-transaction-left { flex: 1; min-width: 0; }
.modal-transaction-date {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--gray-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
}
.modal-transaction-meta { font-size: 0.85rem; font-weight: 500; color: var(--gray-color); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.modal-transaction-account { color: var(--gray-color); margin-right: 0.5rem; display: inline-flex; align-items: center; gap: 0.35rem; }
.modal-transaction-comment { color: var(--gray-color); font-style: italic; }
.modal-transaction-amount { font-size: 1.1rem; font-weight: 800; white-space: nowrap; flex-shrink: 0; }

.modal-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--light-color);
  flex-wrap: nowrap;
  position: sticky;
  bottom: 0;
  background: var(--white);
  border-radius: 0 0 20px 20px;
}
.modal-pagination .btn {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  width: auto;
  border-radius: 10px;
}
.modal-page-btn { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; white-space: nowrap; }
.modal-pagination-info { font-size: 0.85rem; font-weight: 600; color: var(--gray-color); text-align: center; }
.modal-page-info-short { display: none; }

.modal-loading, .modal-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  color: var(--gray-color);
  gap: 1rem;
}
.modal-loading i, .modal-error i { font-size: 2.5rem; }
.modal-error { color: var(--danger-color); }
.modal-loading p, .modal-error p { margin: 0; font-size: 0.9rem; font-weight: 600; }

.btn {
  padding: 0.65rem 1.25rem;
  border: 1px solid var(--gray-color);
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--light-color);
  color: var(--dark-color);
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { background: var(--white); color: var(--dark-color); border: 1px solid var(--light-color); }
.btn-secondary:hover:not(:disabled) { border-color: var(--primary-color); color: var(--primary-color); }

/* ============================================================
   АДАПТИВ
   ============================================================ */
@media (min-width: 768px) {
  .page-title { text-align: left; padding-left: 0.5rem; }
  .filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; align-items: end; }
  .stats-grid { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
  .stat-card.stat-main { grid-column: auto; }
  .top-categories { grid-template-columns: repeat(3, 1fr); }
  .pie-chart-section { flex-direction: row; }
  .pie-chart-legend { max-width: 300px; max-height: 320px; }
  .comparison-section { gap: 1.5rem; }
  .comparison-item, .comparison-change { min-width: 180px; }
  .year-summary { grid-template-columns: repeat(4, 1fr); }
  .mobile-months-grid { display: none; }
  .desktop-table-wrapper { display: block; }
}

@media (min-width: 1025px) {
  .statistics-page { padding: 2rem 2rem 90px; }
  .period-nav-card { padding: 1rem 2rem; }
  .stats-grid { gap: 1.5rem; }
  .stat-card { padding: 1.5rem; }
  .stat-card-value { font-size: 1.8rem; }
  .top-categories { gap: 1.5rem; }
  .top-card { padding: 1.25rem 1.5rem; }
  .category-item { padding: 1.5rem; }
  .daily-chart-section, .chart-section { padding: 2rem; }
}

@media (min-width: 900px) and (max-width: 1024px) and (orientation: landscape) {
  .desktop-table-wrapper { display: block; }
  .mobile-months-grid { display: none; }
}

/* ============================================================
   МОБИЛЬНЫЕ (≤ 768px)
   ============================================================ */
@media (max-width: 768px) {
  .statistics-page { padding: 0.75rem 0.75rem 90px; }

  /* Уменьшаем отступы карточек, чтобы влезало 2 колонки */
  .stats-grid { gap: 0.5rem; }
  .stat-card { border-radius: 12px; padding: 0.75rem 0.5rem; }
  .stat-card-title { font-size: 0.65rem; letter-spacing: 0.2px; margin-bottom: 0.25rem; }
  .stat-card-value { font-size: 1.15rem; }

  /* Разрешаем перенос текста в подзаголовках (убираем обрезку) */
  .stat-card-subtitle {
    white-space: normal;
    font-size: 0.65rem;
    line-height: 1.2;
    margin-top: 0.25rem;
  }
  .stat-compare .stat-card-value { font-size: 1.1rem; }

  .card { border-radius: 12px; margin-bottom: 0.75rem; }
  .card-header { padding: 1rem; flex-direction: column; align-items: flex-start; gap: 0.5rem; }
  .filters-header { padding: 1rem; border-radius: 12px; }
  .filters-body { padding: 1rem; }

  .top-card { border-radius: 12px; padding: 0.75rem 1rem; }
  .top-rank { min-width: 24px; font-size: 0.9rem; }
  .top-name { font-size: 0.85rem; }
  .top-share { font-size: 0.85rem; }

  .categories-list { padding: 1rem; }
  .category-item { border-radius: 12px; padding: 1rem; }

  /* Карточка категории: перенос суммы под название, если не влезает */
  .category-header { flex-wrap: wrap; gap: 0.5rem; }
  .category-right { width: 100%; justify-content: space-between; margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px dashed var(--light-color); }

  .category-name-text { font-size: 0.85rem; max-width: 140px; }
  .category-total { font-size: 0.9rem; }
  .category-percent { min-width: auto; padding: 0.15rem 0.5rem; font-size: 0.75rem; }

  .subcategories { padding-left: 1rem; }
  .subcategories::before { left: 0.25rem; }

  .comparison-section { padding: 1rem; gap: 0.75rem; }
  .comparison-item, .comparison-change { border-radius: 10px; padding: 0.75rem; min-width: 100px; }
  .comparison-change-abs { font-size: 0.7rem; }

  .daily-chart-section { padding: 1rem; }
  .year-summary { padding: 1rem; gap: 0.75rem; }
  .summary-card { border-radius: 10px; padding: 0.75rem; }

  .modal-content { border-radius: 16px; }
  .modal-header { padding: 1rem 1.25rem; border-radius: 16px 16px 0 0; }
  .modal-transaction-item { padding: 0.75rem 1.25rem; flex-direction: column; align-items: stretch; gap: 0.5rem; }
  .modal-transaction-amount { align-self: flex-end; }
  .modal-pagination { border-radius: 0 0 16px 16px; padding: 0.75rem 1rem; }
  .modal-page-label { display: none; }
}
</style>