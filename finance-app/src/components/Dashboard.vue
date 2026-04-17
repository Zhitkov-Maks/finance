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
      <button @click="showAddAccount = true" class="btn btn-primary">
        <i class="fas fa-plus"></i> Добавить счет
      </button>
      <button @click="showAddTransaction = true" class="btn btn-success">
        <i class="fas fa-exchange-alt"></i> Добавить транзакцию
      </button>
      <button @click="showAddCategory = true" class="btn btn-info">
        <i class="fas fa-tags"></i> Добавить категорию
      </button>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Последние транзакции</h3>
        <router-link to="/transactions" class="btn btn-secondary">Все транзакции</router-link>
      </div>
      
      <div class="table-responsive">
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
              <td>{{ transaction.account?.name || '—' }} </td>
              <td>{{ transaction.comment || '—' }} </td>
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
        <button @click="showAddAccount = true" class="btn btn-primary btn-sm">
          <i class="fas fa-plus"></i> Добавить счет
        </button>
      </div>
      
      <div class="table-responsive">
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
    
    <!-- Modal: Добавить счет -->
    <div v-if="showAddAccount" class="modal" @click.self="showAddAccount = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Добавить счет</h3>
          <button class="modal-close" @click="showAddAccount = false">&times;</button>
        </div>
        
        <form @submit.prevent="createAccount">
          <div class="form-group">
            <label class="form-label">Название счета</label>
            <input type="text" v-model="newAccount.name" class="form-control" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">Начальный баланс</label>
            <input type="number" v-model="newAccount.balance" class="form-control" step="0.01" required>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="showAddAccount = false" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Создать счет</button>
          </div>
        </form>
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
    
    <!-- Modal: Добавить категорию -->
    <div v-if="showAddCategory" class="modal" @click.self="showAddCategory = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Добавить категорию</h3>
          <button class="modal-close" @click="showAddCategory = false">&times;</button>
        </div>
        
        <form @submit.prevent="createCategory">
          <div class="form-group">
            <label class="form-label">Тип категории</label>
            <select v-model="newCategory.type" class="form-control" required>
              <option value="income">Доход</option>
              <option value="expense">Расход</option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Название категории</label>
            <input type="text" v-model="newCategory.name" class="form-control" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">Родительская категория (опционально)</label>
            <select v-model="newCategory.parent" class="form-control">
              <option value="">Нет (корневая категория)</option>
              <option v-for="cat in parentCategories" :key="cat.id" :value="cat.id">
                {{ '—'.repeat(cat.level) }} {{ cat.name }}
              </option>
            </select>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="showAddCategory = false" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Создать категорию</button>
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
    const showAddAccount = ref(false)
    const showAddTransaction = ref(false)
    const showAddCategory = ref(false)
    const newAccount = ref({ name: '', balance: 0 })
    const newTransaction = ref({
      type: 'expense',
      amount: '',
      category: '',
      account: '',
      comment: ''
    })
    const newCategory = ref({
      type: 'expense',
      name: '',
      parent: ''
    })
    
    const totalBalance = computed(() => {
      return accounts.value.reduce((sum, acc) => sum + parseFloat(acc.balance), 0)
    })
    
    const activeAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active)
    })
    
    // Все транзакции с явным указанием типа
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
    
    const parentCategories = computed(() => {
      const categories = newCategory.value.type === 'income' ? incomeCategories.value : expenseCategories.value
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
        // Загрузка счетов
        const accountsData = await apiService.getAccounts(1, 100)
        accounts.value = accountsData.results[0]?.accounts || []
        
        // Загрузка транзакций доходов
        const incomeData = await apiService.getTransactions({ page: 1, page_size: 100, type: 'income' })
        incomeTransactions.value = incomeData.results || []
        
        // Загрузка транзакций расходов
        const expenseData = await apiService.getTransactions({ page: 1, page_size: 100, type: 'expense' })
        expenseTransactions.value = expenseData.results || []
        
        // Загрузка категорий доходов
        const incomeCatData = await apiService.getCategories('income', 1, 100, false)
        incomeCategories.value = await Promise.all(
          incomeCatData.results.map(async (cat) => {
            if (cat.has_children) {
              return await apiService.getCategory(cat.id)
            }
            return cat
          })
        )
        
        // Загрузка категорий расходов
        const expenseCatData = await apiService.getCategories('expense', 1, 100, false)
        expenseCategories.value = await Promise.all(
          expenseCatData.results.map(async (cat) => {
            if (cat.has_children) {
              return await apiService.getCategory(cat.id)
            }
            return cat
          })
        )
      } catch (error) {
        console.error('Error loading data:', error)
      } finally {
        loading.value = false
      }
    }
    
    const createAccount = async () => {
      try {
        await apiService.createAccount(newAccount.value.name, newAccount.value.balance)
        showAddAccount.value = false
        newAccount.value = { name: '', balance: 0 }
        await loadData()
      } catch (error) {
        console.error('Error creating account:', error)
        alert('Ошибка при создании счета')
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
    
    const createCategory = async () => {
      try {
        await apiService.createCategory(
          newCategory.value.name,
          newCategory.value.type,
          newCategory.value.parent || null
        )
        showAddCategory.value = false
        newCategory.value = {
          type: 'expense',
          name: '',
          parent: ''
        }
        await loadData()
      } catch (error) {
        console.error('Error creating category:', error)
        alert('Ошибка при создании категории')
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
      showAddAccount,
      showAddTransaction,
      showAddCategory,
      newAccount,
      newTransaction,
      newCategory,
      totalBalance,
      activeAccounts,
      monthlyIncome,
      monthlyExpense,
      recentTransactions: recentTransactions,
      availableCategories,
      parentCategories,
      createAccount,
      addTransaction,
      createCategory,
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

.btn-info {
  background: #3b82f6;
  color: white;
}

.btn-info:hover {
  background: #2563eb;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.table-responsive {
  overflow-x: auto;
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
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
}

.badge-danger {
  background: #fee2e2;
  color: #991b1b;
}

.badge-warning {
  background: #fed7aa;
  color: #92400e;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--light-color);
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

/* Адаптивные стили для мобильных устройств */
@media (max-width: 768px) {
  h1 {
    font-size: 1.5rem;
    margin-bottom: 1rem !important;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
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
  
  .card {
    padding: 1rem;
    margin-bottom: 1rem;
  }
  
  .card-header {
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
  
  .card-header .btn {
    width: 100%;
  }
  
  .card-title {
    font-size: 1.1rem;
  }
  
  .table-responsive {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .table {
    min-width: 500px;
  }
  
  .table th,
  .table td {
    padding: 0.5rem;
    font-size: 0.8rem;
  }
  
  .badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
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
    font-size: 16px; /* Предотвращает зумирование на iOS */
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

/* Для очень маленьких экранов */
@media (max-width: 480px) {
  h1 {
    font-size: 1.25rem;
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
  
  .table th,
  .table td {
    padding: 0.4rem;
    font-size: 0.7rem;
  }
  
  .card-header {
    flex-direction: column;
  }
  
  .btn-sm {
    width: 100%;
  }
}

/* Для планшетов */
@media (min-width: 769px) and (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .quick-actions {
    flex-wrap: wrap;
  }
  
  .quick-actions .btn {
    flex: 1;
  }
}
</style>