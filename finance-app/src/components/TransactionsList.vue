<template>
  <div>
    <div class="page-header">
      <h1>Транзакции</h1>
      <button @click="openAddModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Добавить транзакцию
      </button>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="filters-header" @click="showFilters = !showFilters">
        <h3>Фильтры</h3>
        <i :class="showFilters ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
      </div>
      
      <div class="filters" :class="{ 'filters-hidden': !showFilters }">
        <div class="filter-group">
          <label>Тип:</label>
          <select v-model="filters.type" class="form-control">
            <option value="">Все</option>
            <option value="income">Доходы</option>
            <option value="expense">Расходы</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Счет:</label>
          <input type="text" v-model="filters.account_name" placeholder="Название счета" class="form-control">
        </div>

        <div class="filter-group">
          <label>Категория:</label>
          <input type="text" v-model="filters.category_name" placeholder="Категория" class="form-control">
        </div>

        <div class="filter-group">
          <label>Сумма от:</label>
          <input type="number" v-model="filters.amount_gte" placeholder="Мин" class="form-control">
        </div>

        <div class="filter-group">
          <label>Сумма до:</label>
          <input type="number" v-model="filters.amount_lte" placeholder="Макс" class="form-control">
        </div>

        <div class="filter-group">
          <label>Дата с:</label>
          <input type="date" v-model="filters.create_at_after" class="form-control">
        </div>

        <div class="filter-group">
          <label>Дата по:</label>
          <input type="date" v-model="filters.create_at_before" class="form-control">
        </div>

        <div class="filter-actions">
          <button @click="applyFilters" class="btn btn-primary">Применить</button>
          <button @click="resetFilters" class="btn btn-secondary">Сбросить</button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Загрузка...</p>
    </div>

    <!-- Transactions Table / Mobile Cards -->
    <div v-else class="card">
      <!-- Мобильные карточки -->
      <div class="mobile-transactions">
        <div v-for="transaction in transactions" :key="transaction.id" class="transaction-card">
          <div class="transaction-header">
            <div class="transaction-date">{{ formatDate(transaction.create_at) }}</div>
            <div class="transaction-actions-mobile">
              <button @click="editTransaction(transaction)" class="btn-icon" title="Редактировать">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="confirmDelete(transaction)" class="btn-icon btn-icon-danger" title="Удалить">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          
          <div class="transaction-amount" :class="transaction.transaction_type === 'income' ? 'text-success' : 'text-danger'">
            {{ formatCurrency(transaction.amount) }}
          </div>
          
          <div class="transaction-details">
            <div class="detail-item">
              <span class="detail-label">
                <i class="fas fa-tag"></i> Тип:
              </span>
              <span class="badge" :class="transaction.transaction_type === 'income' ? 'badge-success' : 'badge-danger'">
                {{ transaction.transaction_type === 'income' ? 'Доход' : 'Расход' }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">
                <i class="fas fa-folder"></i> Категория:
              </span>
              <span class="detail-value">{{ transaction.category?.name || '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">
                <i class="fas fa-credit-card"></i> Счет:
              </span>
              <span class="detail-value">{{ transaction.account?.name || '—' }}</span>
            </div>
            <div v-if="transaction.comment" class="detail-item">
              <span class="detail-label">
                <i class="fas fa-comment"></i> Комментарий:
              </span>
              <span class="detail-value">{{ transaction.comment }}</span>
            </div>
          </div>
        </div>
        <div v-if="transactions.length === 0" class="empty-state">
          <i class="fas fa-receipt"></i>
          <p>Нет транзакций</p>
        </div>
      </div>

      <!-- Десктопная таблица -->
      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Дата</th>
              <th>Сумма</th>
              <th>Тип</th>
              <th>Категория</th>
              <th>Счет</th>
              <th>Комментарий</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in transactions" :key="transaction.id">
              <td>{{ transaction.id }}</td>
              <td>{{ formatDate(transaction.create_at) }}</td>
              <td :class="transaction.transaction_type === 'income' ? 'text-success' : 'text-danger'">
                <strong>{{ formatCurrency(transaction.amount) }}</strong>
              </td>
              <td>
                <span class="badge" :class="transaction.transaction_type === 'income' ? 'badge-success' : 'badge-danger'">
                  {{ transaction.transaction_type === 'income' ? 'Доход' : 'Расход' }}
                </span>
               </td>
              <td>{{ transaction.category?.name || '—' }}</td>
              <td>{{ transaction.account?.name || '—' }}</td>
              <td>{{ transaction.comment || '—' }}</td>
              <td>
                <button @click="editTransaction(transaction)" class="btn btn-sm btn-info" title="Редактировать">
                  <i class="fas fa-edit"></i>
                </button>
                <button @click="confirmDelete(transaction)" class="btn btn-sm btn-danger" title="Удалить">
                  <i class="fas fa-trash"></i>
                </button>
               </td>
            </tr>
            <tr v-if="transactions.length === 0">
              <td colspan="8" class="text-center">Нет транзакций</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="totalPages > 1 && !loading">
      <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-secondary">
        <i class="fas fa-chevron-left"></i> <span class="pagination-text">Назад</span>
      </button>
      <span class="pagination-info">
        Страница {{ currentPage }} из {{ totalPages }}
        (всего записей: {{ totalItems }})
      </span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-secondary">
        <span class="pagination-text">Вперед</span> <i class="fas fa-chevron-right"></i>
      </button>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showAddModal" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingTransaction ? 'Редактировать транзакцию' : 'Добавить транзакцию' }}</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>

        <form @submit.prevent="saveTransaction">
          <div class="form-group">
            <label class="form-label required">Тип</label>
            <select v-model="formData.type" class="form-control" required @change="onTypeChange">
              <option value="income">💰 Доход</option>
              <option value="expense">💸 Расход</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Сумма</label>
            <input type="number" v-model="formData.amount" class="form-control" step="0.01" required placeholder="0.00">
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
            <label class="form-label required">Счет</label>
            <select v-model="formData.account" class="form-control" required>
              <option value="">Выберите счет</option>
              <option v-for="acc in activeAccounts" :key="acc.id" :value="acc.id">
                {{ acc.name }} ({{ formatCurrency(acc.balance) }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Дата и время</label>
            <input type="datetime-local" v-model="formData.create_at" class="form-control" required>
          </div>

          <div class="form-group">
            <label class="form-label">Комментарий</label>
            <textarea v-model="formData.comment" class="form-control" rows="3" placeholder="Необязательно"></textarea>
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">
              {{ editingTransaction ? 'Обновить' : 'Создать' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal" @click.self="showDeleteModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Подтверждение удаления</h3>
          <button class="modal-close" @click="showDeleteModal = false">&times;</button>
        </div>
        <p>Вы уверены, что хотите удалить транзакцию?</p>
        <p class="text-muted">Сумма: {{ formatCurrency(transactionToDelete?.amount) }}</p>
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-secondary">Отмена</button>
          <button @click="deleteTransaction" class="btn btn-danger">Да, удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'TransactionsList',
  setup() {
    const transactions = ref([])
    const accounts = ref([])
    const incomeCategories = ref([])
    const expenseCategories = ref([])
    const loading = ref(false)

    // Пагинация
    const currentPage = ref(1)
    const pageSize = ref(50)
    const totalPages = ref(1)
    const totalItems = ref(0)

    // Фильтры
    const filters = ref({
      type: '',
      account_name: '',
      category_name: '',
      amount_gte: '',
      amount_lte: '',
      create_at_after: '',
      create_at_before: ''
    })

    const showAddModal = ref(false)
    const showDeleteModal = ref(false)
    const showFilters = ref(true)
    const editingTransaction = ref(null)
    const transactionToDelete = ref(null)

    const formData = ref({
      type: 'expense',
      amount: '',
      category: '',
      account: '',
      create_at: new Date().toISOString().slice(0, 16),
      comment: ''
    })

    // Активные счета
    const activeAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active)
    })

    // Доступные категории в зависимости от выбранного типа
    const availableCategories = computed(() => {
      const categories = formData.value.type === 'income' ? incomeCategories.value : expenseCategories.value
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

    // Загрузка транзакций с сервера с фильтрацией и пагинацией
    const loadTransactions = async () => {
      loading.value = true
      try {
        // Строим параметры запроса
        const params = {
          page: currentPage.value,
          page_size: pageSize.value
        }

        // Добавляем только непустые фильтры
        Object.keys(filters.value).forEach(key => {
          if (filters.value[key] !== '' && filters.value[key] !== null && filters.value[key] !== undefined) {
            params[key] = filters.value[key]
          }
        })

        console.log('Загрузка транзакций с параметрами:', params)
        
        const response = await apiService.getTransactions(params)
        
        transactions.value = response.results || []
        totalItems.value = response.count || 0
        totalPages.value = Math.ceil(totalItems.value / pageSize.value)
        
        console.log(`Загружено ${transactions.value.length} транзакций из ${totalItems.value}`)
      } catch (error) {
        console.error('Error loading transactions:', error)
        transactions.value = []
        totalItems.value = 0
        totalPages.value = 1
      } finally {
        loading.value = false
      }
    }

    const loadAccounts = async () => {
      try {
        const response = await apiService.getAccounts(1, 100)
        // Исправляем обработку ответа
        accounts.value = response.results || response.accounts || []
        console.log('Загружено счетов:', accounts.value.length)
      } catch (error) {
        console.error('Error loading accounts:', error)
        accounts.value = []
      }
    }

    const loadCategories = async () => {
      try {
        const [incomeData, expenseData] = await Promise.all([
          apiService.getCategories('income', 1, 100, true),
          apiService.getCategories('expense', 1, 100, true)
        ])
        incomeCategories.value = incomeData.results || []
        expenseCategories.value = expenseData.results || []
        console.log('Загружено категорий доходов:', incomeCategories.value.length)
        console.log('Загружено категорий расходов:', expenseCategories.value.length)
      } catch (error) {
        console.error('Error loading categories:', error)
        incomeCategories.value = []
        expenseCategories.value = []
      }
    }

    // Применение фильтров - сбрасываем на первую страницу и перезагружаем
    const applyFilters = () => {
      currentPage.value = 1
      loadTransactions()
    }

    // Debounced фильтрация для текстовых полей
    let debounceTimer = null
    const applyFiltersDebounced = () => {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        currentPage.value = 1
        loadTransactions()
      }, 500)
    }

    // Сброс фильтров
    const resetFilters = () => {
      filters.value = {
        type: '',
        account_name: '',
        category_name: '',
        amount_gte: '',
        amount_lte: '',
        create_at_after: '',
        create_at_before: ''
      }
      currentPage.value = 1
      loadTransactions()
    }

    // Навигация по страницам
    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadTransactions()
      }
    }

    const prevPage = () => goToPage(currentPage.value - 1)
    const nextPage = () => goToPage(currentPage.value + 1)

    // Следим за изменениями фильтров для автоматической загрузки
    watch(() => filters.value.type, () => {
      currentPage.value = 1
      loadTransactions()
    })

    watch(() => filters.value.create_at_after, () => {
      currentPage.value = 1
      loadTransactions()
    })

    watch(() => filters.value.create_at_before, () => {
      currentPage.value = 1
      loadTransactions()
    })

    // Для текстовых полей используем debounced загрузку
    watch(() => filters.value.account_name, () => {
      applyFiltersDebounced()
    })

    watch(() => filters.value.category_name, () => {
      applyFiltersDebounced()
    })

    watch(() => filters.value.amount_gte, () => {
      applyFiltersDebounced()
    })

    watch(() => filters.value.amount_lte, () => {
      applyFiltersDebounced()
    })

    const onTypeChange = () => {
      formData.value.category = ''
    }

    const openAddModal = () => {
      editingTransaction.value = null
      formData.value = {
        type: 'expense',
        amount: '',
        category: '',
        account: '',
        create_at: new Date().toISOString().slice(0, 16),
        comment: ''
      }
      showAddModal.value = true
    }

    const saveTransaction = async () => {
      if (!formData.value.category || !formData.value.account || !formData.value.amount) {
        alert('Заполните все обязательные поля')
        return
      }

      try {
        const data = {
          amount: parseFloat(formData.value.amount),
          create_at: new Date(formData.value.create_at).toISOString(),
          category: parseInt(formData.value.category),
          account: parseInt(formData.value.account),
          comment: formData.value.comment || ''
        }

        if (editingTransaction.value) {
          await apiService.updateTransaction(editingTransaction.value.id, data)
        } else {
          await apiService.createTransaction(formData.value.type, data)
        }
        
        closeModal()
        await loadTransactions() // Перезагружаем текущую страницу
        await loadAccounts() // Обновляем балансы счетов
      } catch (error) {
        console.error('Error saving transaction:', error)
        alert('Ошибка при сохранении транзакции')
      }
    }

    const editTransaction = (transaction) => {
      editingTransaction.value = transaction
      formData.value = {
        type: transaction.transaction_type || transaction.type,
        amount: transaction.amount,
        category: transaction.category?.id || '',
        account: transaction.account?.id || '',
        create_at: transaction.create_at.slice(0, 16),
        comment: transaction.comment || ''
      }
      showAddModal.value = true
    }

    const confirmDelete = (transaction) => {
      transactionToDelete.value = transaction
      showDeleteModal.value = true
    }

    const deleteTransaction = async () => {
      try {
        await apiService.deleteTransaction(transactionToDelete.value.id)
        showDeleteModal.value = false
        
        // Если удалили последнюю транзакцию на странице, переходим на предыдущую
        if (transactions.value.length === 1 && currentPage.value > 1) {
          currentPage.value--
        }
        await loadTransactions()
        await loadAccounts()
      } catch (error) {
        console.error('Error deleting transaction:', error)
        alert('Ошибка при удалении транзакции')
      }
    }

    const closeModal = () => {
      showAddModal.value = false
      editingTransaction.value = null
    }

    const formatCurrency = (value) => {
      if (!value) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { 
        style: 'currency', 
        currency: 'RUB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2 
      }).format(value)
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(async () => {
      await Promise.all([loadTransactions(), loadAccounts(), loadCategories()])
    })

    return {
      // Данные для шаблона
      transactions,
      activeAccounts,
      availableCategories,
      loading,
      
      // Пагинация
      currentPage,
      totalPages,
      totalItems,
      
      // Фильтры
      filters,
      
      // UI состояние
      showFilters,
      showAddModal,
      showDeleteModal,
      editingTransaction,
      transactionToDelete,
      formData,
      
      // Методы
      openAddModal,
      saveTransaction,
      editTransaction,
      confirmDelete,
      deleteTransaction,
      applyFilters,
      resetFilters,
      closeModal,
      prevPage,
      nextPage,
      onTypeChange,
      formatCurrency,
      formatDate
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

.page-header h1 {
  font-size: 1.875rem;
  color: var(--dark-color);
}

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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
}

.badge-danger {
  background: #fee2e2;
  color: #991b1b;
}

.text-success {
  color: var(--secondary-color);
  font-weight: 600;
}

.text-danger {
  color: var(--danger-color);
  font-weight: 600;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  margin: 0 0.25rem;
}

.btn-info {
  background: #3b82f6;
  color: white;
}

.btn-info:hover {
  background: #2563eb;
}

.table-responsive {
  overflow-x: auto;
}

.text-center {
  text-align: center;
}

.text-muted {
  color: var(--gray-color);
  font-size: 0.875rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.required:after {
  content: " *";
  color: var(--danger-color);
}

/* Стили для карточек транзакций (мобильная и планшетная версия) */
.mobile-transactions {
  display: none;
}

.transaction-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  padding: 1rem;
  margin-bottom: 1rem;
}

.transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--light-color);
}

.transaction-date {
  font-size: 0.75rem;
  color: var(--gray-color);
}

.transaction-actions-mobile {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: var(--gray-color);
  transition: color 0.3s;
}

.btn-icon:hover {
  color: var(--primary-color);
}

.btn-icon-danger:hover {
  color: var(--danger-color);
}

.transaction-amount {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-align: center;
  padding: 0.5rem;
  background: var(--light-color);
  border-radius: var(--radius);
}

.transaction-details {
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
  text-align: right;
  word-break: break-word;
  max-width: 60%;
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
  color: var(--gray-color);
}

/* Адаптивные стили - для планшетов и мобильных */
@media (max-width: 1024px) {
  .desktop-table {
    display: none;
  }
  
  .mobile-transactions {
    display: block;
  }
  
  .filters-header {
    display: flex;
  }
  
  .filters {
    display: grid;
    padding: 1rem;
  }
  
  .filters-hidden {
    display: none;
  }
  
  .card {
    padding: 0;
  }
}

/* Для мобильных устройств (до 768px) */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    text-align: center;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .page-header .btn {
    width: 100%;
  }
  
  .filters {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .filter-actions {
    flex-direction: column;
  }
  
  .filter-actions .btn {
    width: 100%;
  }
  
  .pagination {
    flex-wrap: wrap;
  }
  
  .pagination-text {
    display: inline;
  }
  
  /* Модальные окна */
  .modal-content {
    width: 95%;
    margin: 1rem;
    max-height: 85vh;
  }
  
  .modal-header h3 {
    font-size: 1.1rem;
  }
  
  .form-group {
    margin-bottom: 0.75rem;
  }
  
  .form-label {
    font-size: 0.8rem;
  }
  
  .form-control {
    font-size: 16px;
    padding: 0.5rem;
  }
  
  .modal-footer {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .modal-footer .btn {
    width: 100%;
  }
}

/* Для очень маленьких экранов (до 480px) */
@media (max-width: 480px) {
  .transaction-amount {
    font-size: 1rem;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .detail-value {
    max-width: 100%;
    text-align: left;
  }
  
  .pagination-info {
    font-size: 0.875rem;
  }
  
  .pagination .btn {
    padding: 0.5rem;
  }
}

/* Для планшетов в горизонтальной ориентации (1025px-1280px) */
@media (min-width: 1025px) and (max-width: 1280px) {
  .desktop-table {
    display: block;
  }
  
  .mobile-transactions {
    display: none;
  }
  
  .table th,
  .table td {
    padding: 0.5rem;
    font-size: 0.875rem;
  }
  
  .btn-sm {
    padding: 0.2rem 0.4rem;
  }
}
</style>