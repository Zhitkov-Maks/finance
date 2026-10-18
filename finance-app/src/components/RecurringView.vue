<template>
  <div>
    <div class="page-header">
      <h1>Регулярные операции</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Добавить
      </button>
    </div>

    <!-- Статистика -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-title">Всего</div>
        <div class="stat-value">{{ recurring.length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Активных</div>
        <div class="stat-value text-success">{{ activeCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Ближайший платёж</div>
        <div class="stat-value" :class="nearestPaymentClass">
          {{ nearestPayment ? formatDate(nearestPayment.next_run_date) : '—' }}
        </div>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="card">
      <div class="filters">
        <div class="filter-group">
          <label>Тип:</label>
          <select v-model="filters.type_transaction" class="form-control" @change="loadRecurring">
            <option value="">Все</option>
            <option value="income">Доходы</option>
            <option value="expense">Расходы</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Статус:</label>
          <select v-model="filters.is_active" class="form-control" @change="loadRecurring">
            <option value="">Все</option>
            <option :value="true">Активные</option>
            <option :value="false">Неактивные</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Загрузка...</p>
    </div>

    <div v-else class="card">
      <!-- Desktop -->
      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Тип</th>
              <th>Сумма</th>
              <th>Счёт</th>
              <th>Категория</th>
              <th>Расписание</th>
              <th>Следующий</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredRecurring" :key="item.id">
              <td><strong>{{ item.title }}</strong></td>
              <td>
                <span class="badge" :class="item.type_transaction === 'income' ? 'badge-success' : 'badge-danger'">
                  {{ item.type_display || (item.type_transaction === 'income' ? 'Доход' : 'Расход') }}
                </span>
              </td>
              <td :class="item.type_transaction === 'income' ? 'text-success' : 'text-danger'">
                <strong>{{ formatCurrency(item.amount) }}</strong>
              </td>
              <td>{{ item.account_name || '—' }}</td>
              <td>{{ item.category_name || '—' }}</td>
              <td>
                <span class="schedule-badge">
                  <i :class="getScheduleIcon(item.schedule_type)"></i>
                  {{ item.schedule_display || getScheduleLabel(item.schedule_type) }}
                </span>
              </td>
              <td>{{ formatDate(item.next_run_date) }}</td>
              <td>
                <span class="badge" :class="item.is_active ? 'badge-success' : 'badge-secondary'">
                  {{ item.is_active ? 'Активна' : 'Неактивна' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editRecurring(item)" class="btn btn-sm btn-info" title="Редактировать">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    @click="toggleActive(item)"
                    class="btn btn-sm"
                    :class="item.is_active ? 'btn-warning' : 'btn-success'"
                    :title="item.is_active ? 'Приостановить' : 'Возобновить'"
                  >
                    <i :class="item.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
                  </button>
                  <button @click="confirmDelete(item)" class="btn btn-sm btn-danger" title="Удалить">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredRecurring.length === 0">
              <td colspan="9" class="text-center">Нет регулярных операций</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile -->
      <div class="mobile-cards">
        <div v-for="item in filteredRecurring" :key="item.id" class="recurring-card">
          <div class="recurring-compact" @click="toggleExpand(item.id)">
            <div class="compact-left">
              <div class="recurring-title">{{ item.title }}</div>
              <div class="recurring-meta">
                <span class="badge badge-sm" :class="item.type_transaction === 'income' ? 'badge-success' : 'badge-danger'">
                  {{ item.type_display || (item.type_transaction === 'income' ? 'Доход' : 'Расход') }}
                </span>
                <span class="schedule-small">
                  <i :class="getScheduleIcon(item.schedule_type)"></i>
                  {{ item.schedule_display || getScheduleLabel(item.schedule_type) }}
                </span>
              </div>
            </div>
            <div class="compact-right">
              <div class="recurring-amount" :class="item.type_transaction === 'income' ? 'text-success' : 'text-danger'">
                {{ formatCurrency(item.amount) }}
              </div>
              <button class="expand-icon" @click.stop="toggleExpand(item.id)">
                <i :class="expanded.has(item.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>
          </div>

          <div v-if="expanded.has(item.id)" class="recurring-expanded">
            <div class="detail-item">
              <span class="detail-label"><i class="fas fa-credit-card"></i> Счёт:</span>
              <span class="detail-value">{{ item.account_name || '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label"><i class="fas fa-folder"></i> Категория:</span>
              <span class="detail-value">{{ item.category_name || '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label"><i class="fas fa-calendar-check"></i> Следующий:</span>
              <span class="detail-value">{{ formatDate(item.next_run_date) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label"><i class="fas fa-history"></i> Последний:</span>
              <span class="detail-value">{{ item.last_run_date ? formatDate(item.last_run_date) : '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label"><i class="fas fa-flag-checkered"></i> Статус:</span>
              <span class="detail-value">
                <span class="badge" :class="item.is_active ? 'badge-success' : 'badge-secondary'">
                  {{ item.is_active ? 'Активна' : 'Неактивна' }}
                </span>
              </span>
            </div>
            <div class="detail-item" v-if="item.comment">
              <span class="detail-label"><i class="fas fa-comment"></i> Комментарий:</span>
              <span class="detail-value">{{ item.comment }}</span>
            </div>
            <div class="recurring-actions">
              <button @click="editRecurring(item)" class="btn btn-sm btn-info">
                <i class="fas fa-edit"></i> Изменить
              </button>
              <button
                @click="toggleActive(item)"
                class="btn btn-sm"
                :class="item.is_active ? 'btn-warning' : 'btn-success'"
              >
                <i :class="item.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
                {{ item.is_active ? 'Пауза' : 'Запустить' }}
              </button>
              <button @click="confirmDelete(item)" class="btn btn-sm btn-danger">
                <i class="fas fa-trash"></i> Удалить
              </button>
            </div>
          </div>
        </div>
        <div v-if="filteredRecurring.length === 0" class="empty-state">
          <i class="fas fa-redo"></i>
          <p>Нет регулярных операций</p>
          <button @click="openCreateModal" class="btn btn-primary">Создать первую</button>
        </div>
      </div>
    </div>

    <!-- Модалка создания/редактирования -->
    <div v-if="showModal" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editing ? 'Редактировать' : 'Новая регулярная операция' }}</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>

        <form @submit.prevent="saveRecurring">
          <div class="form-group">
            <label class="form-label required">Название</label>
            <input type="text" v-model="formData.title" class="form-control" required placeholder="Например: Netflix, Аренда">
          </div>

          <div class="form-group">
            <label class="form-label required">Тип</label>
            <select v-model="formData.type_transaction" class="form-control" required @change="onTypeChange">
              <option value="expense">Расход</option>
              <option value="income">Доход</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Сумма</label>
            <input type="number" v-model="formData.amount" class="form-control" step="0.01" required placeholder="0.00">
          </div>

          <div class="form-group">
            <label class="form-label required">Счёт</label>
            <select v-model="formData.account" class="form-control" required>
              <option value="">Выберите счёт</option>
              <option v-for="acc in activeAccounts" :key="acc.id" :value="acc.id">
                {{ acc.name }} ({{ formatCurrency(acc.balance) }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Категория</label>
            <select v-model="formData.category" class="form-control" required>
              <option value="">Выберите категорию</option>
              <option v-for="cat in availableCategories" :key="cat.id" :value="cat.id">
                {{ '—'.repeat(cat.level) }} {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Периодичность</label>
            <select v-model="formData.schedule_type" class="form-control" required @change="onScheduleChange">
              <option value="daily">Ежедневно</option>
              <option value="weekly">Еженедельно</option>
              <option value="monthly">Ежемесячно</option>
            </select>
          </div>

          <!-- Для ежемесячных — день месяца -->
          <div class="form-group" v-if="formData.schedule_type === 'monthly'">
            <label class="form-label">День месяца</label>
            <input type="number" v-model="formData.day_of_month" class="form-control" min="1" max="31" placeholder="1-31 (опционально)">
            <small class="form-hint">Если оставить пустым, будет использована дата из «Следующий запуск»</small>
          </div>

          <!-- Для еженедельных — день недели -->
          <div class="form-group" v-if="formData.schedule_type === 'weekly'">
            <label class="form-label">День недели</label>
            <select v-model="formData.weekday" class="form-control">
              <option :value="null">— Не указан —</option>
              <option :value="0">Понедельник</option>
              <option :value="1">Вторник</option>
              <option :value="2">Среда</option>
              <option :value="3">Четверг</option>
              <option :value="4">Пятница</option>
              <option :value="5">Суббота</option>
              <option :value="6">Воскресенье</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Дата начала</label>
            <input type="date" v-model="formData.start_date" class="form-control" required>
          </div>

          <div class="form-group">
            <label class="form-label required">Следующий запуск</label>
            <input type="date" v-model="formData.next_run_date" class="form-control" required>
            <small class="form-hint">Celery запустит операцию, когда эта дата наступит</small>
          </div>

          <div class="form-group">
            <label class="form-label">Дата окончания</label>
            <input type="date" v-model="formData.end_date" class="form-control">
            <small class="form-hint">Оставьте пустым для бессрочной операции</small>
          </div>

          <div class="form-group">
            <label class="form-label">Комментарий</label>
            <textarea v-model="formData.comment" class="form-control" rows="2" placeholder="Необязательно"></textarea>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="formData.is_active">
              <span>Активна</span>
            </label>
          </div>

          <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            Задача создаст транзакцию, обновит баланс счёта и перенесёт «Следующий запуск» на следующий период.
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? 'Сохранение...' : (editing ? 'Обновить' : 'Создать') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модалка удаления -->
    <div v-if="showDeleteModal" class="modal" @click.self="showDeleteModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Удалить регулярную операцию?</h3>
          <button class="modal-close" @click="showDeleteModal = false">&times;</button>
        </div>
        <p>Вы уверены, что хотите удалить <strong>"{{ itemToDelete?.title }}"</strong>?</p>
        <p class="text-muted">Уже созданные транзакции останутся в истории.</p>
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-secondary">Отмена</button>
          <button @click="deleteRecurring" class="btn btn-danger">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'RecurringView',
  setup() {
    const recurring = ref([])
    const accounts = ref([])
    const incomeCategories = ref([])
    const expenseCategories = ref([])
    const loading = ref(false)
    const saving = ref(false)

    const filters = ref({ type_transaction: '', is_active: '' })

    const showModal = ref(false)
    const showDeleteModal = ref(false)
    const editing = ref(null)
    const itemToDelete = ref(null)
    const expanded = ref(new Set())

    const formData = ref(emptyForm())

    function emptyForm() {
      return {
        title: '',
        type_transaction: 'expense',
        amount: '',
        account: '',
        category: '',
        schedule_type: 'monthly',
        day_of_month: null,
        weekday: null,
        start_date: new Date().toISOString().slice(0, 10),
        end_date: '',
        next_run_date: new Date().toISOString().slice(0, 10),
        comment: '',
        is_active: true
      }
    }

    const activeAccounts = computed(() => accounts.value.filter(a => a.is_active))

    const availableCategories = computed(() => {
      const cats = formData.value.type_transaction === 'income' ? incomeCategories.value : expenseCategories.value
      return flattenCategories(cats)
    })

    const flattenCategories = (cats, level = 0) => {
      let result = []
      if (!Array.isArray(cats)) return result
      for (const cat of cats) {
        if (!cat) continue
        result.push({ ...cat, level })
        if (cat.children?.length) {
          result = result.concat(flattenCategories(cat.children, level + 1))
        }
      }
      return result
    }

    const activeCount = computed(() => recurring.value.filter(r => r.is_active).length)

    // Фильтр на клиенте — если бэк не поддерживает query-параметры
    const filteredRecurring = computed(() => {
      return recurring.value.filter(r => {
        if (filters.value.type_transaction && r.type_transaction !== filters.value.type_transaction) return false
        if (filters.value.is_active !== '' && r.is_active !== filters.value.is_active) return false
        return true
      })
    })

    const nearestPayment = computed(() => {
      const active = recurring.value.filter(r => r.is_active && r.next_run_date)
      if (!active.length) return null
      return active.reduce((min, cur) =>
        new Date(cur.next_run_date) < new Date(min.next_run_date) ? cur : min
      )
    })

    const nearestPaymentClass = computed(() => {
      if (!nearestPayment.value) return ''
      const days = Math.ceil((new Date(nearestPayment.value.next_run_date) - new Date()) / (1000 * 60 * 60 * 24))
      if (days <= 3) return 'text-danger'
      if (days <= 7) return 'text-warning'
      return 'text-success'
    })

    // --- helpers ---
    const getScheduleLabel = (type) => ({
      daily: 'Ежедневно',
      weekly: 'Еженедельно',
      monthly: 'Ежемесячно'
    }[type] || type || '—')

    const getScheduleIcon = (type) => ({
      daily: 'fas fa-sun',
      weekly: 'fas fa-calendar-week',
      monthly: 'fas fa-calendar-alt'
    }[type] || 'fas fa-repeat')

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
        day: '2-digit', month: '2-digit', year: 'numeric'
      })
    }

    // --- data ---
    const loadRecurring = async () => {
      loading.value = true
      try {
        const params = {}
        if (filters.value.type_transaction) params.type_transaction = filters.value.type_transaction
        if (filters.value.is_active !== '') params.is_active = filters.value.is_active
        const data = await apiService.getRecurring(params)
        // Обрабатываем и пагинированный, и плоский ответ
        recurring.value = Array.isArray(data) ? data : (data.results || [])
      } catch (e) {
        console.error('Error loading recurring:', e)
        recurring.value = []
      } finally {
        loading.value = false
      }
    }

    const loadAccounts = async () => {
      try {
        const data = await apiService.getAccounts(1, 100)
        accounts.value = data.results?.[0]?.accounts || data.results || data.accounts || []
      } catch (e) {
        console.error('Error loading accounts:', e)
      }
    }

    const loadCategories = async () => {
      try {
        const inc = await apiService.getCategories('income', 1, 100, true)
        incomeCategories.value = inc.results || []
        const exp = await apiService.getCategories('expense', 1, 100, true)
        expenseCategories.value = exp.results || []
      } catch (e) {
        console.error('Error loading categories:', e)
      }
    }

    // --- form logic ---
    const onTypeChange = () => {
      formData.value.category = ''
    }

    const onScheduleChange = () => {
      // Сбрасываем специфичные для типа поля
      if (formData.value.schedule_type !== 'monthly') formData.value.day_of_month = null
      if (formData.value.schedule_type !== 'weekly') formData.value.weekday = null
    }

    // Синхронизация next_run_date при изменении start_date,
    // если пользователь ещё не трогал next_run_date вручную
    watch(() => formData.value.start_date, (newVal, oldVal) => {
      if (!newVal) return
      // Если next_run_date пустой или совпадает со старым start_date — обновляем
      if (!formData.value.next_run_date || formData.value.next_run_date === oldVal) {
        formData.value.next_run_date = newVal
      }
    })

    // --- modals ---
    const openCreateModal = () => {
      editing.value = null
      formData.value = emptyForm()
      formData.value.account = activeAccounts.value[0]?.id || ''
      showModal.value = true
    }

    const editRecurring = (item) => {
      editing.value = item
      formData.value = {
        title: item.title,
        type_transaction: item.type_transaction,
        amount: item.amount,
        account: item.account,
        category: item.category,
        schedule_type: item.schedule_type,
        day_of_month: item.day_of_month ?? null,
        weekday: item.weekday ?? null,
        start_date: item.start_date,
        end_date: item.end_date || '',
        next_run_date: item.next_run_date,
        comment: item.comment || '',
        is_active: item.is_active
      }
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
      editing.value = null
    }

    const saveRecurring = async () => {
      saving.value = true
      try {
        // Payload строго под RecurringTransactionSerializer
        const payload = {
          title: formData.value.title,
          account: parseInt(formData.value.account),
          category: parseInt(formData.value.category),
          type_transaction: formData.value.type_transaction,
          amount: parseFloat(formData.value.amount),
          comment: formData.value.comment || '',
          schedule_type: formData.value.schedule_type,
          start_date: formData.value.start_date,
          next_run_date: formData.value.next_run_date,
          is_active: formData.value.is_active
        }

        // day_of_month — только для monthly
        if (formData.value.schedule_type === 'monthly' && formData.value.day_of_month) {
          payload.day_of_month = parseInt(formData.value.day_of_month)
        }

        // weekday — только для weekly
        if (formData.value.schedule_type === 'weekly' && formData.value.weekday !== null && formData.value.weekday !== '') {
          payload.weekday = parseInt(formData.value.weekday)
        }

        // end_date — опционально
        if (formData.value.end_date) {
          payload.end_date = formData.value.end_date
        }

        if (editing.value) {
          await apiService.updateRecurring(editing.value.id, payload)
        } else {
          await apiService.createRecurring(payload)
        }
        closeModal()
        await loadRecurring()
      } catch (e) {
        console.error('Error saving recurring:', e)
        const detail = e.response?.data
        let msg = 'Ошибка сохранения'
        if (typeof detail === 'string') msg = detail
        else if (detail?.detail) msg = detail.detail
        else if (detail && typeof detail === 'object') {
          msg = Object.entries(detail)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
            .join('\n')
        }
        alert(msg)
      } finally {
        saving.value = false
      }
    }

    const toggleActive = async (item) => {
      try {
        await apiService.patchRecurring(item.id, { is_active: !item.is_active })
        await loadRecurring()
      } catch (e) {
        console.error('Error toggling:', e)
        alert('Ошибка: ' + (e.message || 'Неизвестно'))
      }
    }

    const confirmDelete = (item) => {
      itemToDelete.value = item
      showDeleteModal.value = true
    }

    const deleteRecurring = async () => {
      try {
        await apiService.deleteRecurring(itemToDelete.value.id)
        showDeleteModal.value = false
        await loadRecurring()
      } catch (e) {
        console.error('Error deleting:', e)
        alert('Ошибка: ' + (e.message || 'Неизвестно'))
      }
    }

    const toggleExpand = (id) => {
      const s = new Set(expanded.value)
      s.has(id) ? s.delete(id) : s.add(id)
      expanded.value = s
    }

    onMounted(async () => {
      await Promise.all([loadAccounts(), loadCategories()])
      await loadRecurring()
    })

    return {
      recurring, accounts, loading, saving,
      filters, showModal, showDeleteModal, editing, itemToDelete, expanded,
      formData, activeAccounts, availableCategories,
      activeCount, filteredRecurring, nearestPayment, nearestPaymentClass,
      getScheduleLabel, getScheduleIcon,
      formatCurrency, formatDate,
      loadRecurring, openCreateModal, editRecurring, closeModal,
      saveRecurring, toggleActive, confirmDelete, deleteRecurring,
      toggleExpand, onTypeChange, onScheduleChange
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.page-header h1 { font-size: 1.875rem; color: var(--dark-color); }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.stat-card {
  background: var(--white);
  padding: 1.5rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}
.stat-title { font-size: 0.875rem; color: var(--gray-color); margin-bottom: 0.5rem; }
.stat-value { font-size: 1.75rem; font-weight: 700; color: var(--dark-color); }

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem;
}
.filter-group { display: flex; flex-direction: column; gap: 0.5rem; }
.filter-group label { font-weight: 500; font-size: 0.875rem; }

.loading-state {
  text-align: center;
  padding: 3rem;
  color: var(--gray-color);
}
.loading-state i { font-size: 2rem; margin-bottom: 0.5rem; }

.desktop-table { display: block; overflow-x: auto; }
.mobile-cards { display: none; }

.table { width: 100%; border-collapse: collapse; }
.table th, .table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--light-color);
}
.table th { font-weight: 600; color: var(--gray-color); }

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}
.badge-success { background: #d1fae5; color: #065f46; }
.badge-danger { background: #fee2e2; color: #991b1b; }
.badge-secondary { background: #e5e7eb; color: #4b5563; }
.badge-sm { font-size: 0.65rem; padding: 0.15rem 0.5rem; }

.schedule-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8rem;
  color: var(--gray-color);
}
.schedule-small {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.7rem;
  color: var(--gray-color);
}

.text-success { color: var(--secondary-color); }
.text-danger { color: var(--danger-color); }
.text-warning { color: var(--warning-color); font-weight: 600; }
.text-muted { color: var(--gray-color); }
.text-center { text-align: center; }

.action-buttons { display: flex; gap: 0.375rem; flex-wrap: wrap; }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.875rem; }
.btn-info { background: #3b82f6; color: white; }
.btn-warning { background: #f59e0b; color: white; }
.btn-success { background: var(--secondary-color); color: white; }

.recurring-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  margin-bottom: 0.5rem;
  overflow: hidden;
}
.recurring-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.recurring-compact:hover { background: #f9fafb; }
.compact-left { flex: 1; min-width: 0; }
.recurring-title { font-weight: 600; color: var(--dark-color); margin-bottom: 0.25rem; }
.recurring-meta { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.compact-right { display: flex; align-items: center; gap: 0.5rem; }
.recurring-amount { font-weight: 700; }
.recurring-expanded {
  padding: 1rem;
  border-top: 1px solid var(--light-color);
  background: #fafafa;
}
.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  padding: 0.375rem 0;
}
.detail-label { color: var(--gray-color); }
.detail-value { color: var(--dark-color); text-align: right; max-width: 60%; word-break: break-word; }
.recurring-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.75rem; }
.recurring-actions .btn-sm { flex: 1; }

.expand-icon {
  background: none;
  border: none;
  cursor: pointer;
  width: 32px; height: 32px;
  border-radius: 50%;
  color: var(--gray-color);
  display: flex;
  align-items: center;
  justify-content: center;
}
.expand-icon:hover { background: var(--light-color); color: var(--primary-color); }

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.form-hint {
  display: block;
  font-size: 0.7rem;
  color: var(--gray-color);
  margin-top: 0.25rem;
  font-style: italic;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--gray-color);
}
.empty-state i { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }

.modal-footer {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.alert {
  padding: 0.75rem;
  border-radius: var(--radius);
  margin: 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
}
.alert-info { background: #dbeafe; color: #1e40af; }

@media (max-width: 1024px) {
  .desktop-table { display: none; }
  .mobile-cards { display: block; }
  .filters { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .page-header { flex-direction: column; text-align: center; }
  .page-header h1 { font-size: 1.5rem; }
  .page-header .btn { width: 100%; }
  .stats-grid { grid-template-columns: 1fr; }
  .detail-item { flex-direction: column; align-items: flex-start; gap: 0.25rem; }
  .detail-value { max-width: 100%; text-align: left; }
  .recurring-actions { flex-direction: column; }
  .recurring-actions .btn-sm { width: 100%; }
  .modal-footer { flex-direction: column; }
  .modal-footer .btn { width: 100%; }
}
</style>