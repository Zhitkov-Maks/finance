<template>
  <div>
    <h1 style="margin-bottom: 2rem;">Дашборд</h1>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-title">Общий баланс</div>
        <div class="stat-value">{{ formatCurrency(totalBalance) }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-title">Доходы (месяц)</div>
        <div class="stat-value text-success">{{ formatCurrency(monthlyIncome) }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-title">Расходы (месяц)</div>
        <div class="stat-value text-danger">{{ formatCurrency(monthlyExpense) }}</div>
      </div>
    </div>
    
    <!-- Быстрые действия -->
    <div class="quick-actions">
      <button @click="showAddTransaction = true" class="btn btn-success">
        <i class="fas fa-exchange-alt"></i> Добавить транзакцию
      </button>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Последние транзакции</h3>
        <router-link to="/transactions" class="btn btn-secondary">Все транзакции</router-link>
      </div>
      
      <!-- Для мобильных и планшетов: карточки вместо таблицы -->
      <div class="mobile-transactions">
        <div v-for="transaction in recentTransactions" :key="transaction.id" class="transaction-card">
          <div class="transaction-header">
            <div class="transaction-date">{{ formatDate(transaction.create_at) }}</div>
            <span class="badge" :class="transaction.transaction_type === 'income' ? 'badge-success' : 'badge-danger'">
              {{ transaction.transaction_type === 'income' ? 'Доход' : 'Расход' }}
            </span>
          </div>
          <div class="transaction-amount" :class="transaction.transaction_type === 'income' ? 'text-success' : 'text-danger'">
            {{ formatCurrency(transaction.amount) }}
          </div>
          <div class="transaction-details">
            <div class="detail-item">
              <span class="detail-label">Категория:</span>
              <span class="detail-value">{{ transaction.category?.name || '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Счет:</span>
              <span class="detail-value">{{ transaction.account?.name || '—' }}</span>
            </div>
            <div v-if="transaction.comment" class="detail-item">
              <span class="detail-label">Комментарий:</span>
              <span class="detail-value">{{ transaction.comment }}</span>
            </div>
          </div>
        </div>
        <div v-if="recentTransactions.length === 0" class="empty-state">
          Нет транзакций
        </div>
      </div>
      
      <!-- Для десктопа: таблица -->
      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Сумма</th>
              <th>Тип</th>
              <th>Категория</th>
              <th>Счет</th>
              <th>Комментарий</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in recentTransactions" :key="transaction.id">
              <td>{{ formatDate(transaction.create_at) }}</td>
              <td :class="transaction.transaction_type === 'income' ? 'text-success' : 'text-danger'">
                {{ formatCurrency(transaction.amount) }}
                </td>
              <td>
                <span class="badge" :class="transaction.transaction_type === 'income' ? 'badge-success' : 'badge-danger'">
                  {{ transaction.transaction_type === 'income' ? 'Доход' : 'Расход' }}
                </span>
                </td>
              <td>{{ transaction.category?.name || '—' }}</td>
              <td>{{ transaction.account?.name || '—' }}</td>
              <td>{{ transaction.comment || '—' }}</td>
            </tr>
            <tr v-if="recentTransactions.length === 0">
              <td colspan="6" class="text-center">Нет транзакций</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Мои счета</h3>
      </div>
      
      <!-- Для мобильных и планшетов: карточки счетов -->
      <div class="mobile-accounts">
        <div v-for="account in accounts" :key="account.id" class="account-card">
          <div class="account-name">{{ account.name }}</div>
          <div class="account-balance" :class="parseFloat(account.balance) >= 0 ? 'text-success' : 'text-danger'">
            {{ formatCurrency(account.balance) }}
          </div>
          <div class="account-status">
            <span class="badge" :class="account.is_active ? 'badge-success' : 'badge-danger'">
              {{ account.is_active ? 'Активен' : 'Неактивен' }}
            </span>
          </div>
        </div>
        <div v-if="accounts.length === 0" class="empty-state">
          Нет созданных счетов
        </div>
      </div>
      
      <!-- Для десктопа: таблица -->
      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Баланс</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="account in accounts" :key="account.id">
              <td>
                <strong>{{ account.name }}</strong>
                </td>
              <td :class="parseFloat(account.balance) >= 0 ? 'text-success' : 'text-danger'">
                {{ formatCurrency(account.balance) }}
                </td>
              <td>
                <span class="badge" :class="account.is_active ? 'badge-success' : 'badge-danger'">
                  {{ account.is_active ? 'Активен' : 'Неактивен' }}
                </span>
                </td>
              </tr>
            <tr v-if="accounts.length === 0">
              <td colspan="3" class="text-center">Нет созданных счетов</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Modal: Добавить транзакцию -->
    <div v-if="showAddTransaction" class="modal" @click.self="showAddTransaction = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Добавить транзакцию</h3>
          <button class="modal-close" @click="showAddTransaction = false">&times;</button>
        </div>
        
        <form @submit.prevent="addTransaction">
          <div class="form-group">
            <label class="form-label">Тип</label>
            <select v-model="newTransaction.type" class="form-control" required>
              <option value="income">Доход</option>
              <option value="expense">Расход</option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Сумма</label>
            <input type="number" v-model="newTransaction.amount" class="form-control" step="0.01" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">Категория</label>
            <select v-model="newTransaction.category" class="form-control" required>
              <option value="">Выберите категорию</option>
              <option v-for="cat in availableCategories" :key="cat.id" :value="cat.id">
                {{ '—'.repeat(cat.level) }} {{ cat.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Счет</label>
            <select v-model="newTransaction.account" class="form-control" required>
              <option value="">Выберите счет</option>
              <option v-for="acc in activeAccounts" :key="acc.id" :value="acc.id">
                {{ acc.name }} ({{ formatCurrency(acc.balance) }})
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Комментарий</label>
            <textarea v-model="newTransaction.comment" class="form-control" rows="2"></textarea>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="showAddTransaction = false" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Добавить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'Dashboard',
  setup() {
    const accounts = ref([])
    const incomeTransactions = ref([])
    const expenseTransactions = ref([])
    const incomeCategories = ref([])
    const expenseCategories = ref([])
    const loading = ref(false)
    const showAddTransaction = ref(false)
    const newTransaction = ref({
      type: 'expense',
      amount: '',
      category: '',
      account: '',
      comment: ''
    })
    
    const totalBalance = computed(() => {
      return accounts.value
        .filter(acc => acc.is_active)
        .reduce((sum, acc) => sum + parseFloat(acc.balance), 0)
    })

    const activeAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active)
    })
    
    const allTransactions = computed(() => {
      const income = incomeTransactions.value.map(t => ({ ...t, transaction_type: 'income' }))
      const expense = expenseTransactions.value.map(t => ({ ...t, transaction_type: 'expense' }))
      return [...income, ...expense].sort((a, b) => new Date(b.create_at) - new Date(a.create_at))
    })
    
    const monthlyIncome = computed(() => {
      const now = new Date()
      return incomeTransactions.value
        .filter(t => {
          const date = new Date(t.create_at)
          return date.getMonth() === now.getMonth() && 
                 date.getFullYear() === now.getFullYear()
        })
        .reduce((sum, t) => sum + parseFloat(t.amount), 0)
    })
    
    const monthlyExpense = computed(() => {
      const now = new Date()
      return expenseTransactions.value
        .filter(t => {
          const date = new Date(t.create_at)
          return date.getMonth() === now.getMonth() && 
                 date.getFullYear() === now.getFullYear()
        })
        .reduce((sum, t) => sum + parseFloat(t.amount), 0)
    })
    
    const recentTransactions = computed(() => {
      return allTransactions.value.slice(0, 10)
    })
    
    const availableCategories = computed(() => {
      const categories = newTransaction.value.type === 'income' ? incomeCategories.value : expenseCategories.value
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
    
    const loadData = async () => {
      loading.value = true
      try {
        const accountsData = await apiService.getAccounts(1, 100)
        accounts.value = accountsData.results[0]?.accounts || []
        
        const incomeData = await apiService.getTransactions({ page: 1, page_size: 100, type: 'income' })
        incomeTransactions.value = incomeData.results || []
        
        const expenseData = await apiService.getTransactions({ page: 1, page_size: 100, type: 'expense' })
        expenseTransactions.value = expenseData.results || []
        
        const incomeCatData = await apiService.getCategories('income', 1, 100, true)
        incomeCategories.value = incomeCatData.results || []
        
        const expenseCatData = await apiService.getCategories('expense', 1, 100, true)
        expenseCategories.value = expenseCatData.results || []
      } catch (error) {
        console.error('Error loading data:', error)
      } finally {
        loading.value = false
      }
    }
    
    const addTransaction = async () => {
      if (!newTransaction.value.category || !newTransaction.value.account) {
        alert('Заполните все поля')
        return
      }
      
      try {
        await apiService.createTransaction(newTransaction.value.type, {
          amount: newTransaction.value.amount,
          create_at: new Date().toISOString(),
          category: parseInt(newTransaction.value.category),
          account: parseInt(newTransaction.value.account),
          comment: newTransaction.value.comment
        })
        showAddTransaction.value = false
        newTransaction.value = {
          type: 'expense',
          amount: '',
          category: '',
          account: '',
          comment: ''
        }
        await loadData()
      } catch (error) {
        console.error('Error creating transaction:', error)
        alert('Ошибка при создании транзакции')
      }
    }
    
    const formatCurrency = (value) => {
      if (!value) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(value)
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('ru-RU')
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      accounts,
      incomeTransactions,
      expenseTransactions,
      loading,
      showAddTransaction,
      newTransaction,
      totalBalance,
      activeAccounts,
      monthlyIncome,
      monthlyExpense,
      recentTransactions,
      availableCategories,
      addTransaction,
      formatCurrency,
      formatDate
    }
  }
}
</script>

<style scoped>
.quick-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.text-center {
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.5rem;
  box-shadow: var(--shadow);
}

.stat-title {
  font-size: 0.875rem;
  color: var(--gray-color);
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--dark-color);
}

.text-success {
  color: var(--secondary-color);
}

.text-danger {
  color: var(--danger-color);
}

.badge {
  padding: 0.25rem 0.5rem;
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

/* Стили для карточек транзакций (мобильная и планшетная версия) */
.mobile-transactions {
  display: none;
}

.transaction-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  padding: 1rem;
  margin-bottom: 0.75rem;
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

.transaction-amount {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
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
}

.detail-value {
  color: var(--dark-color);
  text-align: right;
  word-break: break-word;
  max-width: 60%;
}

/* Стили для карточек счетов (мобильная и планшетная версия) */
.mobile-accounts {
  display: none;
}

.account-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  padding: 1rem;
  margin-bottom: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.account-name {
  font-weight: 600;
  font-size: 1rem;
  flex: 1;
}

.account-balance {
  font-weight: 700;
  font-size: 1.125rem;
}

.account-status {
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--gray-color);
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
  
  .mobile-accounts {
    display: block;
  }
  
  .stats-grid {
    gap: 1rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .card {
    padding: 1rem;
  }
  
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .card-header .btn {
    width: 100%;
    text-align: center;
  }
  
  .card-title {
    text-align: center;
  }
}

/* Для маленьких планшетов и больших телефонов (до 768px) */
@media (max-width: 768px) {
  h1 {
    font-size: 1.5rem;
    margin-bottom: 1rem !important;
    text-align: center;
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
  
  .quick-actions {
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }
  
  .quick-actions .btn {
    width: 100%;
    justify-content: center;
    padding: 0.75rem;
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
  h1 {
    font-size: 1.25rem;
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
  
  .transaction-amount {
    font-size: 1rem;
  }
  
  .account-card {
    flex-direction: column;
    text-align: center;
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
}

/* Для планшетов в горизонтальной ориентации (1024px-1280px) */
@media (min-width: 1025px) and (max-width: 1280px) {
  .desktop-table {
    display: block;
  }
  
  .mobile-transactions {
    display: none;
  }
  
  .mobile-accounts {
    display: none;
  }
  
  .table th,
  .table td {
    padding: 0.5rem;
    font-size: 0.875rem;
  }
}
</style>