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
    
    <!-- Быстрые действия и курсы валют -->
    <div class="actions-panel">
      <button @click="showAddTransaction = true" class="btn btn-success">
        <i class="fas fa-exchange-alt"></i> Добавить транзакцию
      </button>
      
      <div class="exchange-rates" v-if="exchangeRates.length > 0">
        <div v-for="rate in exchangeRates" :key="rate.code" class="rate-item" :title="`Курс ЦБ РФ на ${rate.date}`">
          <span class="rate-currency">{{ rate.code }}</span>
          <span class="rate-value">{{ rate.value }} ₽</span>
        </div>
        <div v-if="exchangeRatesError" class="rate-error" title="Не удалось загрузить курс валют">
          ⚠️
        </div>
      </div>
      <div v-else-if="!exchangeRatesLoading" class="exchange-rates-placeholder"></div>
    </div>
    
    <!-- Последние доходы -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Последние доходы</h3>
        <router-link to="/transactions?type=income" class="btn btn-secondary">Все доходы</router-link>
      </div>
      
      <!-- Для мобильных и планшетов: карточки -->
      <div class="mobile-transactions">
        <div v-for="transaction in recentIncomes" :key="transaction.id" class="transaction-card">
          <div class="transaction-header">
            <div class="transaction-date">{{ formatDate(transaction.create_at) }}</div>
            <span class="badge badge-success">Доход</span>
          </div>
          <div class="transaction-amount text-success">
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
        <div v-if="recentIncomes.length === 0" class="empty-state">
          Нет доходов
        </div>
      </div>
      
      <!-- Для десктопа: таблица -->
      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Сумма</th>
              <th>Категория</th>
              <th>Счет</th>
              <th>Комментарий</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in recentIncomes" :key="transaction.id">
              <td>{{ formatDate(transaction.create_at) }}</td>
              <td class="text-success">{{ formatCurrency(transaction.amount) }}</td>
              <td>{{ transaction.category?.name || '—' }}</td>
              <td>{{ transaction.account?.name || '—' }}</td>
              <td>{{ transaction.comment || '—' }}</td>
            </tr>
            <tr v-if="recentIncomes.length === 0">
              <td colspan="5" class="text-center">Нет доходов</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Последние расходы -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Последние расходы</h3>
        <router-link to="/transactions?type=expense" class="btn btn-secondary">Все расходы</router-link>
      </div>
      
      <!-- Для мобильных и планшетов: карточки -->
      <div class="mobile-transactions">
        <div v-for="transaction in recentExpenses" :key="transaction.id" class="transaction-card">
          <div class="transaction-header">
            <div class="transaction-date">{{ formatDate(transaction.create_at) }}</div>
            <span class="badge badge-danger">Расход</span>
          </div>
          <div class="transaction-amount text-danger">
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
        <div v-if="recentExpenses.length === 0" class="empty-state">
          Нет расходов
        </div>
      </div>
      
      <!-- Для десктопа: таблица -->
      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Сумма</th>
              <th>Категория</th>
              <th>Счет</th>
              <th>Комментарий</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in recentExpenses" :key="transaction.id">
              <td>{{ formatDate(transaction.create_at) }}</td>
              <td class="text-danger">{{ formatCurrency(transaction.amount) }}</td>
              <td>{{ transaction.category?.name || '—' }}</td>
              <td>{{ transaction.account?.name || '—' }}</td>
              <td>{{ transaction.comment || '—' }}</td>
            </tr>
            <tr v-if="recentExpenses.length === 0">
              <td colspan="5" class="text-center">Нет расходов</td>
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'Dashboard',
  setup() {
    const accounts = ref([])
    const incomeTransactionsList = ref([])
    const expenseTransactionsList = ref([])
    const incomeCategories = ref([])
    const expenseCategories = ref([])
    const loading = ref(false)
    const showAddTransaction = ref(false)
    const monthlyIncome = ref(0)
    const monthlyExpense = ref(0)
    const exchangeRates = ref([])
    const exchangeRatesLoading = ref(true)
    const exchangeRatesError = ref(false)
    let ratesUpdateInterval = null
    
    const newTransaction = ref({
      type: 'expense',
      amount: '',
      category: '',
      account: '',
      comment: ''
    })
    
    // --- Логика валют ---
    const CURRENCIES_TO_SHOW = ['USD', 'EUR', 'CNY']
    
    const fetchExchangeRates = async () => {
      exchangeRatesLoading.value = true
      exchangeRatesError.value = false
      try {
        const response = await fetch('https://www.cbr-xml-daily.ru/daily_json.js')
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        const data = await response.json()
        
        const rates = []
        for (const code of CURRENCIES_TO_SHOW) {
          if (data.Valute[code]) {
            const valute = data.Valute[code]
            const valuePerUnit = valute.Value / valute.Nominal
            rates.push({
              code: code,
              name: valute.Name,
              value: valuePerUnit.toFixed(2),
              date: data.Date.split('T')[0]
            })
          } else {
            console.warn(`Currency ${code} not found in response`)
          }
        }
        exchangeRates.value = rates
        exchangeRatesError.value = false
      } catch (error) {
        console.error('Failed to fetch exchange rates:', error)
        exchangeRatesError.value = true
      } finally {
        exchangeRatesLoading.value = false
      }
    }
    
    // --- Статистика за месяц ---
    const loadMonthlyStatistics = async () => {
      const now = new Date()
      const month = now.getMonth() + 1
      const year = now.getFullYear()
      
      try {
        const expenseStats = await apiService.getStatistics(month, year, 'expense')
        monthlyExpense.value = parseFloat(expenseStats.total_amount) || 0
        
        const incomeStats = await apiService.getStatistics(month, year, 'income')
        monthlyIncome.value = parseFloat(incomeStats.total_amount) || 0
        
        console.log(`Статистика за ${month}.${year}: доходы=${monthlyIncome.value}, расходы=${monthlyExpense.value}`)
      } catch (error) {
        console.error('Error loading monthly statistics:', error)
        monthlyIncome.value = 0
        monthlyExpense.value = 0
      }
    }
    
    const loadData = async () => {
      loading.value = true
      try {
        // Загрузка счетов (только для баланса и выбора в модалке)
        const accountsData = await apiService.getAccounts(1, 100)
        accounts.value = accountsData.results[0]?.accounts || []
        
        // Загрузка доходов (последние 5)
        const incomeData = await apiService.getTransactions({ page: 1, page_size: 5, type: 'income' })
        incomeTransactionsList.value = (incomeData.results || []).map(t => ({ ...t, transaction_type: 'income' }))
        
        // Загрузка расходов (последние 5)
        const expenseData = await apiService.getTransactions({ page: 1, page_size: 5, type: 'expense' })
        expenseTransactionsList.value = (expenseData.results || []).map(t => ({ ...t, transaction_type: 'expense' }))
        
        // Загрузка категорий
        const incomeCatData = await apiService.getCategories('income', 1, 100, true)
        incomeCategories.value = incomeCatData.results || []
        
        const expenseCatData = await apiService.getCategories('expense', 1, 100, true)
        expenseCategories.value = expenseCatData.results || []
        
        // Загрузка статистики за текущий месяц
        await loadMonthlyStatistics()
        
        console.log('Загружено доходов:', incomeTransactionsList.value.length)
        console.log('Загружено расходов:', expenseTransactionsList.value.length)
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
      if (!value && value !== 0) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(value)
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('ru-RU')
    }
    
    const totalBalance = computed(() => {
      return accounts.value
        .filter(acc => acc.is_active)
        .reduce((sum, acc) => sum + parseFloat(acc.balance), 0)
    })
    
    const activeAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active)
    })
    
    // Последние 5 доходов
    const recentIncomes = computed(() => {
      return [...incomeTransactionsList.value]
        .sort((a, b) => new Date(b.create_at) - new Date(a.create_at))
        .slice(0, 5)
    })
    
    // Последние 5 расходов
    const recentExpenses = computed(() => {
      return [...expenseTransactionsList.value]
        .sort((a, b) => new Date(b.create_at) - new Date(a.create_at))
        .slice(0, 5)
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
    
    onMounted(() => {
      loadData()
      fetchExchangeRates()
      ratesUpdateInterval = setInterval(fetchExchangeRates, 3600000)
    })
    
    onBeforeUnmount(() => {
      if (ratesUpdateInterval) {
        clearInterval(ratesUpdateInterval)
      }
    })
    
    return {
      accounts,
      loading,
      showAddTransaction,
      newTransaction,
      totalBalance,
      activeAccounts,
      monthlyIncome,
      monthlyExpense,
      recentIncomes,
      recentExpenses,
      availableCategories,
      exchangeRates,
      exchangeRatesLoading,
      exchangeRatesError,
      addTransaction,
      formatCurrency,
      formatDate
    }
  }
}
</script>

<style scoped>
/* Панель действий и курсы */
.actions-panel {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
}

.exchange-rates {
  display: flex;
  gap: 1rem;
  background: var(--light-color, #f3f4f6);
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  flex-wrap: wrap;
}

.rate-item {
  display: inline-flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.rate-currency {
  color: var(--gray-color, #6b7280);
}

.rate-value {
  color: var(--dark-color, #1f2937);
  font-weight: 600;
}

.rate-error {
  cursor: help;
  font-size: 1rem;
}

.exchange-rates-placeholder {
  min-width: 180px;
}

/* Стили карточек */
.card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 1.25rem;
  box-shadow: var(--shadow);
  margin-bottom: 1.5rem;
}

.card:last-child {
  margin-bottom: 0;
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
  margin: 0;
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

/* Мобильные карточки */
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

/* Адаптивные стили */
@media (max-width: 1024px) {
  .desktop-table {
    display: none;
  }
  
  .mobile-transactions {
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
  
  .actions-panel {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .exchange-rates {
    justify-content: center;
  }
}

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
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .detail-value {
    max-width: 100%;
    text-align: left;
  }
  
  .exchange-rates {
    width: 100%;
    justify-content: space-between;
  }
  
  .rate-item {
    font-size: 0.75rem;
  }
}

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
}
</style>