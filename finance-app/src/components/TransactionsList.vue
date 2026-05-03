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
          <select v-model="localFilters.type" class="form-control">
            <option value="">Все</option>
            <option value="income">Доходы</option>
            <option value="expense">Расходы</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Счет:</label>
          <input type="text" v-model="localFilters.account_name" placeholder="Название счета" class="form-control">
        </div>

        <div class="filter-group">
          <label>Категория:</label>
          <input type="text" v-model="localFilters.category_name" placeholder="Категория" class="form-control">
        </div>

        <div class="filter-group">
          <label>Сумма от:</label>
          <input type="number" v-model="localFilters.amount_gte" placeholder="Мин" class="form-control">
        </div>

        <div class="filter-group">
          <label>Сумма до:</label>
          <input type="number" v-model="localFilters.amount_lte" placeholder="Макс" class="form-control">
        </div>

        <div class="filter-group">
          <label>Дата с:</label>
          <input type="date" v-model="localFilters.create_at_after" class="form-control">
        </div>

        <div class="filter-group">
          <label>Дата по:</label>
          <input type="date" v-model="localFilters.create_at_before" class="form-control">
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
      <div class="mobile-transactions">
        <div v-for="transaction in transactions" :key="transaction.id" class="transaction-card">
          <!-- Компактный заголовок -->
          <div class="transaction-compact" @click="toggleExpand(transaction.id)">
            <div class="compact-left">
              <div class="transaction-date-compact">{{ formatShortDate(transaction.create_at) }}</div>
              <span class="badge" :class="getTransactionType(transaction) === 'income' ? 'badge-success' : 'badge-danger'">
                {{ getTransactionType(transaction) === 'income' ? 'Доход' : 'Расход' }}
              </span>
            </div>
            <div class="compact-right">
              <div class="transaction-amount-compact" :class="getTransactionType(transaction) === 'income' ? 'text-success' : 'text-danger'">
                {{ formatCurrency(transaction.amount) }}
              </div>
              <button class="expand-icon" @click.stop="toggleExpand(transaction.id)">
                <i :class="expandedTransactions.has(transaction.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>
          </div>

          <!-- Раскрывающаяся детальная информация -->
          <div v-if="expandedTransactions.has(transaction.id)" class="transaction-expanded">
            <div class="transaction-details">
              <div class="detail-item">
                <span class="detail-label">
                  <i class="fas fa-tag"></i> Тип:
                </span>
                <span class="badge" :class="getTransactionType(transaction) === 'income' ? 'badge-success' : 'badge-danger'">
                  {{ getTransactionType(transaction) === 'income' ? 'Доход' : 'Расход' }}
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
              <div class="detail-item">
                <span class="detail-label">
                  <i class="fas fa-clock"></i> Полная дата:
                </span>
                <span class="detail-value">{{ formatDate(transaction.create_at) }}</span>
              </div>
            </div>
            <div class="transaction-actions-expanded">
              <button @click="editTransaction(transaction)" class="btn btn-sm btn-info">
                <i class="fas fa-edit"></i> Редактировать
              </button>
              <button @click="confirmDelete(transaction)" class="btn btn-sm btn-danger">
                <i class="fas fa-trash"></i> Удалить
              </button>
            </div>
          </div>
        </div>
        <div v-if="transactions.length === 0" class="empty-state">
          <i class="fas fa-receipt"></i>
          <p>Нет транзакций</p>
        </div>
      </div>

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
              <td :class="getTransactionType(transaction) === 'income' ? 'text-success' : 'text-danger'">
                <strong>{{ formatCurrency(transaction.amount) }}</strong>
              </td>
              <td>
                <span class="badge" :class="getTransactionType(transaction) === 'income' ? 'badge-success' : 'badge-danger'">
                  {{ getTransactionType(transaction) === 'income' ? 'Доход' : 'Расход' }}
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

    <!-- Add/Edit Modal -->
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
            <button type="submit" class="btn btn-primary">{{ editingTransaction ? 'Обновить' : 'Создать' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Modal -->
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
    const transactions = ref([])
    const accounts = ref([])
    const incomeCategories = ref([])
    const expenseCategories = ref([])
    const loading = ref(false)
    const expandedTransactions = ref(new Set())

    // Пагинация
    const currentPage = ref(1)
    const pageSize = ref(50)
    const totalPages = ref(1)
    const totalItems = ref(0)

    // Локальные фильтры
    const localFilters = ref({
      type: '',
      account_name: '',
      category_name: '',
      amount_gte: '',
      amount_lte: '',
      create_at_after: '',
      create_at_before: ''
    })

    // Активные фильтры
    const activeFilters = ref({
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

    // Функция для получения типа транзакции
    const getTransactionType = (transaction) => {
      if (!transaction) return 'expense'

      // 1. Прямое поле transaction_type
      if (transaction.transaction_type) {
        return transaction.transaction_type
      }

      // 2. Поле type
      if (transaction.type) {
        return transaction.type
      }

      // 3. Определяем по типу категории (самый надежный способ для вашего API)
      if (transaction.category && transaction.category.type_transaction) {
        return transaction.category.type_transaction
      }

      // 4. Если есть ID категории, но нет объекта, пробуем найти категорию в загруженных списках
      if (transaction.category_id) {
        const allCategories = [...incomeCategories.value, ...expenseCategories.value]
        const foundCategory = findCategoryById(allCategories, transaction.category_id)
        if (foundCategory && foundCategory.type_transaction) {
          return foundCategory.type_transaction
        }
      }

      // 5. По умолчанию расход
      console.warn('Не удалось определить тип транзакции:', transaction)
      return 'expense'
    }

    // Вспомогательная функция для поиска категории по ID
    const findCategoryById = (categories, id) => {
      for (const cat of categories) {
        if (cat.id === id) return cat
        if (cat.children && cat.children.length) {
          const found = findCategoryById(cat.children, id)
          if (found) return found
        }
      }
      return null
    }

    const activeAccounts = computed(() => {
      if (!accounts.value || !Array.isArray(accounts.value)) {
        return []
      }
      return accounts.value.filter(acc => acc && acc.is_active === true)
    })

    const availableCategories = computed(() => {
      // Используем тип из формы для фильтрации категорий
      const categories = formData.value.type === 'income' ? incomeCategories.value : expenseCategories.value
      return flattenCategories(categories)
    })

    const flattenCategories = (categories, level = 0) => {
      let result = []
      if (!categories || !Array.isArray(categories)) return result

      for (const cat of categories) {
        if (cat) {
          result.push({
            ...cat,
            level,
            name: cat.name,
            type_transaction: cat.type_transaction // Сохраняем тип категории
          })
          if (cat.children && cat.children.length) {
            result = result.concat(flattenCategories(cat.children, level + 1))
          }
        }
      }
      return result
    }

    const toggleExpand = (transactionId) => {
      if (expandedTransactions.value.has(transactionId)) {
        expandedTransactions.value.delete(transactionId)
      } else {
        expandedTransactions.value.add(transactionId)
      }
      // Создаем новый Set для триггера реактивности
      expandedTransactions.value = new Set(expandedTransactions.value)
    }

    const loadTransactions = async () => {
      console.log('loadTransactions вызван')
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value
        }

        Object.keys(activeFilters.value).forEach(key => {
          if (activeFilters.value[key] && activeFilters.value[key] !== '') {
            params[key] = activeFilters.value[key]
          }
        })

        console.log('Отправляем запрос с параметрами:', params)
        const response = await apiService.getTransactions(params)
        console.log('Получен ответ:', response)

        // Обрабатываем транзакции, добавляя информацию о типе из категории
        const processedTransactions = (response.results || []).map(transaction => {
          // Если у транзакции нет типа, но есть категория, добавляем тип из категории
          if (!transaction.transaction_type && transaction.category && transaction.category.type_transaction) {
            transaction.transaction_type = transaction.category.type_transaction
          }
          return transaction
        })

        transactions.value = processedTransactions
        totalItems.value = response.count || 0
        totalPages.value = Math.ceil(totalItems.value / pageSize.value)

        console.log(`Загружено ${transactions.value.length} транзакций`)
        // Выводим первую транзакцию для отладки
        if (transactions.value.length > 0) {
          console.log('Пример транзакции:', transactions.value[0])
          console.log('Тип первой транзакции:', getTransactionType(transactions.value[0]))
        }
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
      console.log('=== НАЧАЛО ЗАГРУЗКИ СЧЕТОВ ===')
      try {
        const response = await apiService.getAccounts(1, 100)
        console.log('Ответ от API счетов:', response)

        let accountsData = []

        if (response.results && response.results.length > 0 && response.results[0].accounts) {
          accountsData = response.results[0].accounts
          console.log('Счета из response.results[0].accounts:', accountsData)
        } else if (response.results && Array.isArray(response.results)) {
          accountsData = response.results
        } else if (response.accounts && Array.isArray(response.accounts)) {
          accountsData = response.accounts
        } else if (Array.isArray(response)) {
          accountsData = response
        } else {
          console.log('Неизвестная структура ответа:', response)
          accountsData = []
        }

        accounts.value = accountsData
        console.log(`Загружено ${accounts.value.length} счетов`)

        accounts.value.forEach((acc, index) => {
          console.log(`Счет ${index + 1}: ${acc.name} (ID: ${acc.id}), баланс: ${acc.balance}, активен: ${acc.is_active}`)
        })

      } catch (error) {
        console.error('Ошибка при загрузке счетов:', error)
        accounts.value = []
      }
      console.log('=== ЗАГРУЗКА СЧЕТОВ ЗАВЕРШЕНА ===')
    }

    const loadCategories = async () => {
      console.log('Загрузка категорий...')
      try {
        // Загружаем все категории без фильтрации по типу
        const allCategoriesResponse = await apiService.getCategories('', 1, 100, true)
        console.log('Все категории:', allCategoriesResponse)

        let allCategories = []
        if (allCategoriesResponse.results && Array.isArray(allCategoriesResponse.results)) {
          allCategories = allCategoriesResponse.results
        } else if (Array.isArray(allCategoriesResponse)) {
          allCategories = allCategoriesResponse
        } else if (allCategoriesResponse.data && Array.isArray(allCategoriesResponse.data)) {
          allCategories = allCategoriesResponse.data
        }

        // Разделяем категории по типу
        incomeCategories.value = allCategories.filter(cat => cat.type_transaction === 'income')
        expenseCategories.value = allCategories.filter(cat => cat.type_transaction === 'expense')

        console.log('Категории доходов:', incomeCategories.value.length)
        console.log('Категории расходов:', expenseCategories.value.length)
      } catch (error) {
        console.error('Error loading categories:', error)
        incomeCategories.value = []
        expenseCategories.value = []
      }
    }

    const applyFilters = () => {
      console.log('Применяем фильтры:', localFilters.value)
      activeFilters.value = { ...localFilters.value }
      currentPage.value = 1
      loadTransactions()
    }

    const resetFilters = () => {
      console.log('Сброс фильтров')
      localFilters.value = {
        type: '',
        account_name: '',
        category_name: '',
        amount_gte: '',
        amount_lte: '',
        create_at_after: '',
        create_at_before: ''
      }
      activeFilters.value = { ...localFilters.value }
      currentPage.value = 1
      loadTransactions()
    }

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        loadTransactions()
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        loadTransactions()
      }
    }

    const onTypeChange = () => {
      formData.value.category = ''
    }

    const openAddModal = () => {
      console.log('Открытие модального окна, доступные счета:', activeAccounts.value)
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
        await loadTransactions()
        await loadAccounts()
      } catch (error) {
        console.error('Error saving transaction:', error)
        alert('Ошибка при сохранении транзакции')
      }
    }

    const editTransaction = (transaction) => {
      editingTransaction.value = transaction
      const transactionType = getTransactionType(transaction)
      formData.value = {
        type: transactionType,
        amount: transaction.amount,
        category: transaction.category?.id || '',
        account: transaction.account?.id || '',
        create_at: transaction.create_at?.slice(0, 16) || new Date().toISOString().slice(0, 16),
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
      if (!value && value !== 0) return '0 ₽'
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

    const formatShortDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(async () => {
      console.log('=== КОМПОНЕНТ СМОНТИРОВАН ===')
      await Promise.all([loadTransactions(), loadAccounts(), loadCategories()])
      console.log('=== ВСЕ ДАННЫЕ ЗАГРУЖЕНЫ ===')
      console.log('Доступные счета для выбора:', activeAccounts.value)
    })

    return {
      transactions,
      activeAccounts,
      availableCategories,
      loading,
      currentPage,
      totalPages,
      totalItems,
      localFilters,
      showFilters,
      showAddModal,
      showDeleteModal,
      editingTransaction,
      transactionToDelete,
      formData,
      expandedTransactions,
      getTransactionType,
      toggleExpand,
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
      formatDate,
      formatShortDate
    }
  }
}
</script>

<style scoped>
/* ... все стили остаются без изменений ... */
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

/* Компактные карточки для мобильных устройств */
.mobile-transactions {
  display: none;
}

.transaction-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  margin-bottom: 0.5rem;
  overflow: hidden;
  transition: all 0.3s ease;
}

.transaction-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.transaction-compact:hover {
  background-color: #f9fafb;
}

.compact-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.transaction-date-compact {
  font-size: 0.75rem;
  color: var(--gray-color);
  min-width: 70px;
}

.compact-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.transaction-amount-compact {
  font-size: 1rem;
  font-weight: 700;
}

.expand-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: var(--gray-color);
  transition: color 0.3s;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.expand-icon:hover {
  background-color: var(--light-color);
  color: var(--primary-color);
}

.transaction-expanded {
  padding: 1rem;
  border-top: 1px solid var(--light-color);
  background-color: #fafafa;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.transaction-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
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
  gap: 0.5rem;
}

.detail-value {
  color: var(--dark-color);
  text-align: right;
  word-break: break-word;
  max-width: 60%;
}

.transaction-actions-expanded {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.transaction-actions-expanded .btn-sm {
  padding: 0.5rem 1rem;
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

  .compact-left {
    gap: 0.5rem;
  }

  .transaction-date-compact {
    min-width: 60px;
    font-size: 0.7rem;
  }

  .transaction-amount-compact {
    font-size: 0.9rem;
  }

  .badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
  }

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

  .form-control {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .transaction-compact {
    padding: 0.6rem 0.75rem;
  }

  .compact-left {
    gap: 0.4rem;
  }

  .transaction-date-compact {
    min-width: 55px;
    font-size: 0.65rem;
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

  .transaction-actions-expanded {
    flex-direction: column;
  }

  .transaction-actions-expanded .btn-sm {
    width: 100%;
  }
}
</style>