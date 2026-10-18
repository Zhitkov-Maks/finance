<template>
  <div class="budgets-page">
    <div class="page-header">
      <h1>Бюджеты</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Добавить бюджет
      </button>
    </div>

    <!-- Фильтры периода -->
    <div class="filters-bar">
      <div class="period-switcher">
        <button
          class="range-btn"
          :class="{ active: periodType === 'monthly' }"
          @click="periodType = 'monthly'"
        >
          На месяц
        </button>
        <button
          class="range-btn"
          :class="{ active: periodType === 'weekly' }"
          @click="periodType = 'weekly'"
        >
          На неделю
        </button>
      </div>

      <div class="date-picker" v-if="periodType === 'monthly'">
        <input
          type="month"
          v-model="selectedMonth"
          class="form-control"
          @change="loadData"
        />
      </div>
    </div>

    <!-- Загрузка -->
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Загрузка бюджетов...</p>
    </div>

    <template v-else>
      <!-- ====================================================== -->
      <!-- ОБЩИЙ БЮДЖЕТ                                            -->
      <!-- ====================================================== -->
      <div v-if="summary && summary.total_budget" class="total-budget-card">
        <div class="total-budget-header">
          <div class="total-budget-title">
            <i class="fas fa-globe"></i> Общий бюджет
          </div>
          <div class="budget-actions">
            <button
              @click="editTotalBudget"
              class="btn-icon"
              title="Редактировать"
            >
              <i class="fas fa-edit"></i>
            </button>
            <button
              @click="confirmDeleteTotalBudget"
              class="btn-icon"
              title="Удалить"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>

        <div class="total-budget-amounts">
          <span
            class="budget-spent"
            :class="summary.total_budget.is_exceeded ? 'is-exceeded' : ''"
          >
            {{ formatCurrency(summary.total_budget.spent) }}
          </span>
          <span class="budget-separator">из</span>
          <span class="budget-limit">
            {{ formatCurrency(summary.total_budget.amount) }}
          </span>
        </div>

        <div class="progress-container">
          <div class="progress-bar big">
            <div
              class="progress-fill"
              :class="getProgressClass(summary.total_budget.percent)"
              :style="{ width: Math.min(summary.total_budget.percent, 100) + '%' }"
            ></div>
          </div>
          <div class="progress-info">
            <span>{{ summary.total_budget.percent }}%</span>
            <span
              :class="
                summary.total_budget.remaining >= 0 ? 'text-success' : 'text-danger'
              "
            >
              {{ summary.total_budget.remaining >= 0 ? 'Осталось' : 'Перерасход' }}:
              {{ formatCurrency(Math.abs(summary.total_budget.remaining)) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Заглушка: общий бюджет не задан -->
      <div v-else-if="summary" class="total-budget-empty">
        <div class="total-budget-empty-text">
          <i class="fas fa-globe"></i>
          <div>
            <div class="total-budget-empty-title">Общий бюджет не задан</div>
            <div class="total-budget-empty-hint">
              Установите лимит на все расходы за период
            </div>
          </div>
        </div>
        <button @click="openCreateTotalBudget" class="btn btn-primary btn-sm">
          <i class="fas fa-plus"></i> Добавить общий бюджет
        </button>
      </div>

      <!-- ====================================================== -->
      <!-- СВОДКА ПО КАТЕГОРИЙНЫМ                                  -->
      <!-- ====================================================== -->
      <div
        class="summary-cards"
        v-if="summary && summary.totals && summary.totals.limit > 0"
      >
        <div class="summary-card">
          <div class="summary-label">Лимитов по категориям</div>
          <div class="summary-value">{{ formatCurrency(summary.totals.limit) }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">Потрачено</div>
          <div class="summary-value text-danger">
            {{ formatCurrency(summary.totals.spent) }}
          </div>
        </div>
        <div class="summary-card">
          <div class="summary-label">Осталось</div>
          <div
            class="summary-value"
            :class="summary.totals.remaining >= 0 ? 'text-success' : 'text-danger'"
          >
            {{ formatCurrency(summary.totals.remaining) }}
          </div>
        </div>
        <div class="summary-card">
          <div class="summary-label">Использовано</div>
          <div class="summary-value">{{ summary.totals.percent }}%</div>
        </div>
      </div>

      <!-- ====================================================== -->
      <!-- БЮДЖЕТЫ ПО КАТЕГОРИЯМ                                  -->
      <!-- ====================================================== -->
      <h2 class="section-title" v-if="summary && summary.budgets.length > 0">
        Бюджеты по категориям
      </h2>

      <div
        class="budgets-grid"
        v-if="summary && summary.budgets.length > 0"
      >
        <div
          v-for="budget in summary.budgets"
          :key="budget.id"
          class="budget-card"
        >
          <div class="budget-header">
            <div class="budget-category">
              <i class="fas fa-folder"></i>
              {{ budget.category.name }}
            </div>
            <div class="budget-actions">
              <button
                @click="editBudget(budget)"
                class="btn-icon"
                title="Редактировать"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button
                @click="confirmDelete(budget)"
                class="btn-icon text-danger"
                title="Удалить"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>

          <div class="budget-amounts">
            <span
              class="budget-spent"
              :class="budget.is_exceeded ? 'text-danger' : ''"
            >
              {{ formatCurrency(budget.spent) }}
            </span>
            <span class="budget-separator">из</span>
            <span class="budget-limit">{{ formatCurrency(budget.amount) }}</span>
          </div>

          <div class="progress-container">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :class="getProgressClass(budget.percent)"
                :style="{ width: Math.min(budget.percent, 100) + '%' }"
              ></div>
            </div>
            <div class="progress-info">
              <span>{{ budget.percent }}%</span>
              <span
                :class="budget.remaining >= 0 ? 'text-success' : 'text-danger'"
              >
                {{ budget.remaining >= 0 ? 'Осталось' : 'Перерасход' }}:
                {{ formatCurrency(Math.abs(budget.remaining)) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div
        v-else-if="summary && summary.budgets.length === 0 && !summary.total_budget"
        class="empty-state"
      >
        <i class="fas fa-wallet"></i>
        <p>
          У вас пока нет бюджетов. Добавьте первый, чтобы контролировать
          расходы!
        </p>
      </div>
    </template>

    <!-- ====================================================== -->
    <!-- МОДАЛКА СОЗДАНИЯ / РЕДАКТИРОВАНИЯ                       -->
    <!-- ====================================================== -->
    <div v-if="showModal" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            {{ editingBudget ? 'Редактировать бюджет' : 'Новый бюджет' }}
          </h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>

        <form @submit.prevent="saveBudget">
          <div class="form-group">
            <label class="form-label required">Бюджет на</label>
            <select
              v-model="formData.category"
              class="form-control"
              :disabled="!!editingBudget"
            >
              <option :value="null">🌐 Общий бюджет (все расходы)</option>
              <option
                v-for="cat in availableCategories"
                :key="cat.id"
                :value="cat.id"
              >
                {{ '—'.repeat(cat.level) }} {{ cat.name }}
              </option>
            </select>
            <small class="form-hint" v-if="!editingBudget">
              {{
                formData.category === null
                  ? 'Общий бюджет — лимит на все расходы за период'
                  : 'Бюджеты можно ставить только на категории расходов'
              }}
            </small>
          </div>

          <div class="form-group">
            <label class="form-label required">Лимит (₽)</label>
            <input
              type="number"
              v-model="formData.amount"
              class="form-control"
              step="0.01"
              min="1"
              required
              placeholder="Например: 30000"
            />
          </div>

          <div class="form-group">
            <label class="form-label required">Период</label>
            <select
              v-model="formData.period_type"
              class="form-control"
              required
              :disabled="!!editingBudget"
            >
              <option value="monthly">Ежемесячно</option>
              <option value="weekly">Еженедельно</option>
            </select>
          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="closeModal"
            >
              Отмена
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="saving"
            >
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ====================================================== -->
    <!-- МОДАЛКА УДАЛЕНИЯ                                        -->
    <!-- ====================================================== -->
    <div
      v-if="showDeleteModal"
      class="modal"
      @click.self="showDeleteModal = false"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h3>Удалить бюджет</h3>
          <button
            class="modal-close"
            @click="showDeleteModal = false"
          >
            &times;
          </button>
        </div>
        <p>
          Вы уверены, что хотите удалить
          <strong>{{ budgetToDelete?.category?.name || 'бюджет' }}</strong>?
        </p>
        <div class="modal-footer">
          <button
            class="btn btn-secondary"
            @click="showDeleteModal = false"
          >
            Отмена
          </button>
          <button class="btn btn-danger" @click="deleteBudget">
            Удалить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'BudgetsView',
  setup() {
    const loading = ref(true)
    const saving = ref(false)
    const summary = ref(null)
    const categories = ref([])

    // --- Период ---
    const periodType = ref('monthly')
    const now = new Date()
    const selectedMonth = ref(
      `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    )

    // --- Модалки ---
    const showModal = ref(false)
    const showDeleteModal = ref(false)
    const editingBudget = ref(null)
    const budgetToDelete = ref(null)

    const formData = ref({
      category: null,
      amount: '',
      period_type: 'monthly',
    })

    // ========================================================
    // Загрузка
    // ========================================================
    const loadCategories = async () => {
      try {
        const data = await apiService.getCategories('expense', 1, 200, true)
        categories.value = data.results || []
      } catch (error) {
        console.error('Ошибка загрузки категорий:', error)
      }
    }

    const loadData = async () => {
      loading.value = true
      try {
        let dateParam = null
        if (periodType.value === 'monthly' && selectedMonth.value) {
          dateParam = `${selectedMonth.value}-01`
        }
        const data = await apiService.getBudgetSummary(
          periodType.value,
          dateParam
        )
        summary.value = data
      } catch (error) {
        console.error('Ошибка загрузки бюджетов:', error)
        summary.value = null
      } finally {
        loading.value = false
      }
    }

    // ========================================================
    // Вспомогательные
    // ========================================================
    const flattenCategories = (cats, level = 0) => {
      let result = []
      for (const cat of cats) {
        result.push({ ...cat, level })
        if (cat.children && cat.children.length) {
          result = result.concat(flattenCategories(cat.children, level + 1))
        }
      }
      return result
    }

    const availableCategories = computed(() =>
      flattenCategories(categories.value)
    )

    const formatCurrency = (val) => {
      if (!val && val !== 0) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(val)
    }

    const getProgressClass = (percent) => {
      if (percent >= 100) return 'progress-danger'
      if (percent >= 80) return 'progress-warning'
      return 'progress-success'
    }

    // ========================================================
    // Действия — общий бюджет
    // ========================================================
    const openCreateTotalBudget = () => {
      editingBudget.value = null
      formData.value = {
        category: null,
        amount: '',
        period_type: periodType.value,
      }
      showModal.value = true
    }

    const editTotalBudget = () => {
      const tb = summary.value?.total_budget
      if (!tb) return
      editingBudget.value = {
        id: tb.id,
        category: null,
        amount: tb.amount,
      }
      formData.value = {
        category: null,
        amount: tb.amount,
        period_type: summary.value.period.type,
      }
      showModal.value = true
    }

    const confirmDeleteTotalBudget = () => {
      const tb = summary.value?.total_budget
      if (!tb) return
      budgetToDelete.value = {
        id: tb.id,
        category: { name: 'Общий бюджет' },
      }
      showDeleteModal.value = true
    }

    // ========================================================
    // Действия — категорийные бюджеты
    // ========================================================
    const openCreateModal = () => {
      editingBudget.value = null
      formData.value = {
        category: null,
        amount: '',
        period_type: periodType.value,
      }
      showModal.value = true
    }

    const editBudget = (budget) => {
      editingBudget.value = budget
      formData.value = {
        category: budget.category.id,
        amount: budget.amount,
        period_type: budget.period_type,
      }
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
      editingBudget.value = null
    }

    // ========================================================
    // Сохранение
    // ========================================================
    const saveBudget = async () => {
      saving.value = true
      try {
        const payload = {
          category: formData.value.category, // null = общий
          amount: parseFloat(formData.value.amount),
          period_type: formData.value.period_type,
        }

        if (editingBudget.value) {
          await apiService.updateBudget(editingBudget.value.id, payload)
        } else {
          await apiService.createBudget(payload)
        }

        closeModal()
        await loadData()
      } catch (error) {
        console.error('Ошибка сохранения бюджета:', error)
        const apiError =
          error.response?.data?.non_field_errors?.[0] ||
          error.response?.data?.category?.[0] ||
          error.response?.data?.amount?.[0] ||
          'Ошибка при сохранении бюджета'
        alert(apiError)
      } finally {
        saving.value = false
      }
    }

    // ========================================================
    // Удаление
    // ========================================================
    const confirmDelete = (budget) => {
      budgetToDelete.value = budget
      showDeleteModal.value = true
    }

    const deleteBudget = async () => {
      try {
        await apiService.deleteBudget(budgetToDelete.value.id)
        showDeleteModal.value = false
        budgetToDelete.value = null
        await loadData()
      } catch (error) {
        console.error('Ошибка удаления:', error)
        alert('Не удалось удалить бюджет')
      }
    }

    // ========================================================
    // Watchers / Lifecycle
    // ========================================================
    watch(periodType, () => loadData())

    onMounted(() => {
      loadCategories()
      loadData()
    })

    return {
      loading,
      saving,
      summary,
      periodType,
      selectedMonth,
      showModal,
      showDeleteModal,
      editingBudget,
      budgetToDelete,
      formData,
      availableCategories,
      formatCurrency,
      getProgressClass,
      // общий бюджет
      openCreateTotalBudget,
      editTotalBudget,
      confirmDeleteTotalBudget,
      // категорийные
      openCreateModal,
      editBudget,
      closeModal,
      saveBudget,
      confirmDelete,
      deleteBudget,
      loadData,
    }
  },
}
</script>

<style scoped>
.budgets-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

/* ============================================================
   Фильтры периода
   ============================================================ */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.period-switcher {
  display: flex;
  background: var(--light-color);
  padding: 0.25rem;
  border-radius: var(--radius);
}

.range-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  border-radius: calc(var(--radius) - 2px);
  font-weight: 500;
  color: var(--gray-color);
  cursor: pointer;
  transition: all 0.2s;
}

.range-btn.active {
  background: var(--white);
  color: var(--primary-color);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.date-picker {
  width: 200px;
}

/* ============================================================
   Загрузка
   ============================================================ */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem;
  color: var(--gray-color);
}

/* ============================================================
   ОБЩИЙ БЮДЖЕТ
   ============================================================ */
.total-budget-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
}

.total-budget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.total-budget-title {
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.total-budget-amounts {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.total-budget-card .budget-spent {
  font-size: 2rem;
  font-weight: 700;
  color: white;
}

.total-budget-card .budget-spent.is-exceeded {
  color: #fecaca;
}

.total-budget-card .budget-separator {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
}

.total-budget-card .budget-limit {
  color: rgba(255, 255, 255, 0.85);
  font-size: 1.1rem;
}

.total-budget-card .progress-bar {
  background: rgba(255, 255, 255, 0.2);
}

.total-budget-card .progress-info {
  color: rgba(255, 255, 255, 0.95);
}

.total-budget-card .progress-info .text-success {
  color: #86efac;
}

.total-budget-card .progress-info .text-danger {
  color: #fca5a5;
}

.total-budget-card .btn-icon {
  color: white;
}

.total-budget-card .btn-icon:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

/* Заглушка «общий не задан» */
.total-budget-empty {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--white);
  border: 1px dashed #d1d5db;
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.total-budget-empty-text {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--gray-color);
}

.total-budget-empty-text > i {
  font-size: 1.5rem;
}

.total-budget-empty-title {
  font-weight: 600;
  color: var(--dark-color);
  margin-bottom: 0.125rem;
}

.total-budget-empty-hint {
  font-size: 0.813rem;
  color: var(--gray-color);
}

/* ============================================================
   Сводка по категорийным
   ============================================================ */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: var(--white);
  padding: 1.25rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  text-align: center;
}

.summary-label {
  font-size: 0.875rem;
  color: var(--gray-color);
  margin-bottom: 0.5rem;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
}

/* ============================================================
   Заголовок секции категорийных
   ============================================================ */
.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--dark-color);
}

/* ============================================================
   Сетка бюджетов
   ============================================================ */
.budgets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.budget-card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.25rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
}

.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.budget-category {
  font-weight: 600;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--dark-color);
}

.budget-category i {
  color: var(--gray-color);
}

.budget-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-icon {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: var(--gray-color);
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
  font-size: 0.875rem;
}

.btn-icon:hover {
  background: var(--light-color);
  color: var(--primary-color);
}

.btn-icon.text-danger:hover {
  background: #fee2e2;
  color: #ef4444;
}

.budget-amounts {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.budget-spent {
  font-size: 1.5rem;
  font-weight: 700;
}

.budget-separator {
  color: var(--gray-color);
  font-size: 0.875rem;
}

.budget-limit {
  font-size: 1rem;
  color: var(--gray-color);
}

/* ============================================================
   Прогресс
   ============================================================ */
.progress-container {
  margin-top: auto;
}

.progress-bar {
  height: 8px;
  background: var(--light-color);
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-bar.big {
  height: 12px;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.progress-success {
  background: #10b981;
}
.progress-warning {
  background: #f59e0b;
}
.progress-danger {
  background: #ef4444;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--gray-color);
  font-weight: 500;
}

.text-success {
  color: #10b981;
}
.text-danger {
  color: #ef4444;
}

/* ============================================================
   Пустое состояние
   ============================================================ */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  background: var(--white);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  color: var(--gray-color);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* ============================================================
   Формы / модалки
   ============================================================ */
.form-hint {
  display: block;
  margin-top: 0.375rem;
  font-size: 0.75rem;
  color: var(--gray-color);
}

/* ============================================================
   Адаптив
   ============================================================ */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    text-align: center;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .period-switcher {
    justify-content: space-between;
  }

  .date-picker {
    width: 100%;
  }

  .summary-cards {
    grid-template-columns: 1fr 1fr;
  }

  .summary-value {
    font-size: 1.25rem;
  }

  .total-budget-amounts .budget-spent {
    font-size: 1.5rem;
  }

  .total-budget-empty {
    flex-direction: column;
    align-items: flex-start;
  }

  .budget-card {
    padding: 1rem;
  }

  .budget-category {
    font-size: 1rem;
  }

  .budget-spent {
    font-size: 1.25rem;
  }
}

@media (max-width: 480px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>