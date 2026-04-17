<template>
  <div>
    <div class="card-header">
      <h1>Транзакции</h1>
      <button @click="openAddModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Добавить транзакцию
      </button>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="filters">
        <div class="filter-group">
          <label>Тип:</label>
          <select v-model="filters.type" class="form-control" @change="applyFilters">
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

    <!-- Transactions Table -->
    <div class="card">
      <div class="table-responsive">
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
            <tr v-for="transaction in paginatedTransactions" :key="transaction.id">
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
            <tr v-if="filteredTransactions.length === 0">
              <td colspan="8" class="text-center">Нет транзакций</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-secondary">
          <i class="fas fa-chevron-left"></i> Назад
        </button>
        <span>Страница {{ currentPage }} из {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-secondary">
          Вперед <i class="fas fa-chevron-right"></i>
        </button>
      </div>
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
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'TransactionsList',
  setup() {
    const incomeTransactions = ref([])
    const expenseTransactions = ref([])
    const accounts = ref([])
    const incomeCategories = ref([])
    const expenseCategories = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const showAddModal = ref(false)
    const showDeleteModal = ref(false)
    const editingTransaction = ref(null)
    const transactionToDelete = ref(null)
    const filters = ref({
      type: '',
      account_name: '',
      category_name: '',
      amount_gte: '',
      amount_lte: '',
      create_at_after: '',
      create_at_before: ''
    })
    const formData = ref({
      type: 'expense',
      amount: '',
      category: '',
      account: '',
      create_at: new Date().toISOString().slice(0, 16),
      comment: ''
    })

    // Объединенные транзакции с типом
    const allTransactions = computed(() => {
      const income = incomeTransactions.value.map(t => ({ ...t, transaction_type: 'income' }))
      const expense = expenseTransactions.value.map(t => ({ ...t, transaction_type: 'expense' }))
      return [...income, ...expense]
    })

    // Фильтрованные транзакции
    const filteredTransactions = computed(() => {
      let filtered = [...allTransactions.value]
      
      if (filters.value.type) {
        filtered = filtered.filter(t => t.transaction_type === filters.value.type)
      }
      if (filters.value.account_name) {
        filtered = filtered.filter(t => 
          t.account?.name?.toLowerCase().includes(filters.value.account_name.toLowerCase())
        )
      }
      if (filters.value.category_name) {
        filtered = filtered.filter(t => 
          t.category?.name?.toLowerCase().includes(filters.value.category_name.toLowerCase())
        )
      }
      if (filters.value.amount_gte) {
        filtered = filtered.filter(t => parseFloat(t.amount) >= parseFloat(filters.value.amount_gte))
      }
      if (filters.value.amount_lte) {
        filtered = filtered.filter(t => parseFloat(t.amount) <= parseFloat(filters.value.amount_lte))
      }
      if (filters.value.create_at_after) {
        filtered = filtered.filter(t => new Date(t.create_at) >= new Date(filters.value.create_at_after))
      }
      if (filters.value.create_at_before) {
        filtered = filtered.filter(t => new Date(t.create_at) <= new Date(filters.value.create_at_before))
      }
      
      // Сортировка по дате (новые сверху)
      filtered.sort((a, b) => new Date(b.create_at) - new Date(a.create_at))
      
      return filtered
    })

    // Пагинированные транзакции
    const paginatedTransactions = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredTransactions.value.slice(start, end)
    })

    const totalPages = computed(() => Math.ceil(filteredTransactions.value.length / pageSize.value))

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

    const loadTransactions = async () => {
      try {
        const [incomeData, expenseData] = await Promise.all([
          apiService.getTransactions({ page: 1, page_size: 100, type: 'income' }),
          apiService.getTransactions({ page: 1, page_size: 100, type: 'expense' })
        ])
        
        incomeTransactions.value = incomeData.results || []
        expenseTransactions.value = expenseData.results || []
      } catch (error) {
        console.error('Error loading transactions:', error)
      }
    }

    const loadAccounts = async () => {
      try {
        const data = await apiService.getAccounts(1, 100)
        accounts.value = data.results[0]?.accounts || []
      } catch (error) {
        console.error('Error loading accounts:', error)
      }
    }

    const loadCategories = async () => {
      try {
        // Загружаем категории доходов
        const incomeData = await apiService.getCategories('income', 1, 100, true)
        incomeCategories.value = await Promise.all(
          incomeData.results.map(async (cat) => {
            if (cat.has_children) {
              return await apiService.getCategory(cat.id)
            }
            return cat
          })
        )
        
        // Загружаем категории расходов (используем 'expence' в API)
        const expenseData = await apiService.getCategories('expense', 1, 100, true)
        expenseCategories.value = await Promise.all(
          expenseData.results.map(async (cat) => {
            if (cat.has_children) {
              return await apiService.getCategory(cat.id)
            }
            return cat
          })
        )
      } catch (error) {
        console.error('Error loading categories:', error)
      }
    }

    const onTypeChange = () => {
      // Сбрасываем выбранную категорию при смене типа
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
      if (!formData.value.category || !formData.value.account) {
        alert('Заполните все поля')
        return
      }
      
      try {
        const data = {
          amount: formData.value.amount,
          create_at: new Date(formData.value.create_at).toISOString(),
          category: parseInt(formData.value.category),
          account: parseInt(formData.value.account),
          comment: formData.value.comment
        }
        
        if (editingTransaction.value) {
          await apiService.updateTransaction(editingTransaction.value.id, data)
        } else {
          await apiService.createTransaction(formData.value.type, data)
        }
        closeModal()
        await Promise.all([loadTransactions(), loadAccounts()])
      } catch (error) {
        console.error('Error saving transaction:', error)
        alert('Ошибка при сохранении транзакции')
      }
    }

    const editTransaction = (transaction) => {
      editingTransaction.value = transaction
      formData.value = {
        type: transaction.transaction_type,
        amount: transaction.amount,
        category: transaction.category?.id,
        account: transaction.account?.id,
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
        await Promise.all([loadTransactions(), loadAccounts()])
      } catch (error) {
        console.error('Error deleting transaction:', error)
        alert('Ошибка при удалении транзакции')
      }
    }

    const applyFilters = () => {
      currentPage.value = 1
    }

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
      applyFilters()
    }

    const closeModal = () => {
      showAddModal.value = false
      editingTransaction.value = null
    }

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }

    const formatCurrency = (value) => {
      if (!value) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(value)
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ru-RU')
    }

    onMounted(() => {
      Promise.all([loadTransactions(), loadAccounts(), loadCategories()])
    })

    return {
      paginatedTransactions,
      filteredTransactions,
      accounts,
      activeAccounts,
      currentPage,
      totalPages,
      filters,
      showAddModal,
      showDeleteModal,
      editingTransaction,
      transactionToDelete,
      formData,
      availableCategories,
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
</style>