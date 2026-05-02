<template>
  <!-- шаблон остается ТАКИМ ЖЕ, как в вашем последнем рабочем варианте -->
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'TransactionsList',
  setup() {
    const transactions = ref([]) // Только текущая страница
    const accounts = ref([])
    const incomeCategories = ref([])
    const expenseCategories = ref([])

    // Серверная пагинация и фильтрация
    const serverState = ref({
      currentPage: 1,
      pageSize: 50,
      totalPages: 1,
      totalItems: 0,
      filters: {
        type: '',
        account_name: '',
        category_name: '',
        amount_gte: '',
        amount_lte: '',
        create_at_after: '',
        create_at_before: ''
      }
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

    // Загрузка данных с сервера с текущими фильтрами и пагинацией
    const loadData = async () => {
      try {
        const params = {
          page: serverState.value.currentPage,
          page_size: serverState.value.pageSize,
          ...serverState.value.filters
        }

        // Если нет фильтра по типу, загружаем все
        const response = await apiService.getTransactions(params)
        
        transactions.value = response.results || []
        serverState.value.totalItems = response.count || 0
        serverState.value.totalPages = Math.ceil(serverState.value.totalItems / serverState.value.pageSize)
      } catch (error) {
        console.error('Error loading transactions:', error)
        transactions.value = []
        serverState.value.totalItems = 0
        serverState.value.totalPages = 1
      }
    }

    const loadAccounts = async () => {
      try {
        const data = await apiService.getAccounts(1, 100)
        accounts.value = data.results[0]?.accounts || []
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
      } catch (error) {
        console.error('Error loading categories:', error)
        incomeCategories.value = []
        expenseCategories.value = []
      }
    }

    // Применение фильтров - сбрасываем на первую страницу и загружаем
    const applyFilters = () => {
      serverState.value.currentPage = 1
      loadData()
    }

    // Debounced фильтрация для текстовых полей
    let debounceTimer = null
    const applyFiltersDebounced = () => {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        serverState.value.currentPage = 1
        loadData()
      }, 300)
    }

    // Навигация по страницам
    const goToPage = (page) => {
      if (page >= 1 && page <= serverState.value.totalPages) {
        serverState.value.currentPage = page
        loadData()
      }
    }

    const prevPage = () => goToPage(serverState.value.currentPage - 1)
    const nextPage = () => goToPage(serverState.value.currentPage + 1)

    const resetFilters = () => {
      serverState.value.filters = {
        type: '',
        account_name: '',
        category_name: '',
        amount_gte: '',
        amount_lte: '',
        create_at_after: '',
        create_at_before: ''
      }
      serverState.value.currentPage = 1
      loadData()
    }

    // Watchers для автоматического применения фильтров
    watch(() => serverState.value.filters.type, () => {
      serverState.value.currentPage = 1
      loadData()
    })

    watch(() => serverState.value.filters.create_at_after, applyFilters)
    watch(() => serverState.value.filters.create_at_before, applyFilters)

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
        await loadData() // Перезагружаем текущую страницу
        await loadAccounts()
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
        if (transactions.value.length === 1 && serverState.value.currentPage > 1) {
          serverState.value.currentPage--
        }
        await loadData()
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
      await Promise.all([loadData(), loadAccounts(), loadCategories()])
    })

    return {
      // Данные для шаблона
      transactions, // Текущая страница транзакций
      activeAccounts,
      availableCategories,
      
      // Состояние сервера
      serverState,
      
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
      applyFiltersDebounced,
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