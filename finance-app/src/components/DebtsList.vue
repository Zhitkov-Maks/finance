<template>
  <div>
    <div class="page-header">
      <h1>Управление долгами</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Создать долг
      </button>
    </div>

    <!-- Статистика долгов -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-title">Я должен</div>
        <div class="stat-value text-danger">{{ formatCurrency(totalBorrow) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Мне должны</div>
        <div class="stat-value text-success">{{ formatCurrency(totalLend) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Баланс долгов</div>
        <div class="stat-value" :class="netDebt >= 0 ? 'text-success' : 'text-danger'">
          {{ formatCurrency(Math.abs(netDebt)) }}
          <small>{{ netDebt >= 0 ? '(✚)' : '(-)' }}</small>
        </div>
      </div>
    </div>

    <!-- Переключатель типов -->
    <div class="type-tabs">
      <button 
        @click="currentType = 'lend'" 
        class="tab-btn" 
        :class="{ active: currentType === 'lend' }"
      >
        <i class="fas fa-hand-holding-usd"></i> Мне должны
      </button>
      <button 
        @click="currentType = 'borrow'" 
        class="tab-btn" 
        :class="{ active: currentType === 'borrow' }"
      >
        <i class="fas fa-hand-holding-heart"></i> Я должен
      </button>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Контрагент</th>
              <th>Сумма</th>
              <th>Дата</th>
              <th>Счет</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="debt in filteredDebts" :key="debt.id">
              <td>{{ debt.id }}</td>
              <td>
                <strong>{{ debt.borrower_description }}</strong>
               </td>
              <td :class="getDebtAmountClass(debt)">
                <strong>{{ formatCurrency(getDebtAmount(debt)) }}</strong>
               </td>
              <td>{{ formatDate(getDebtDate(debt)) }}</td>
              <td>
                <span class="badge badge-info">
                  {{ getAccountName(debt) }}
                </span>
               </td>
              <td>
                <span class="badge" :class="debt.is_repaid ? 'badge-success' : 'badge-warning'">
                  <i :class="debt.is_repaid ? 'fas fa-check-circle' : 'fas fa-clock'"></i>
                  {{ debt.is_repaid ? 'Погашен' : 'Активен' }}
                </span>
               </td>
              <td>
                <div class="action-buttons">
                  <button @click="viewDebt(debt)" class="btn btn-sm btn-info" title="Детали">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    v-if="!debt.is_repaid" 
                    @click="openRepayModal(debt)" 
                    class="btn btn-sm btn-success" 
                    title="Погасить"
                  >
                    <i class="fas fa-check"></i>
                  </button>
                </div>
               </td>
             </tr>
            <tr v-if="filteredDebts.length === 0">
              <td colspan="7" class="text-center">
                <div class="empty-state">
                  <i class="fas fa-hand-holding-usd"></i>
                  <p>Нет {{ currentType === 'lend' ? 'долгов перед вами' : 'ваших долгов' }}</p>
                  <button @click="openCreateModal" class="btn btn-primary">Создать долг</button>
                </div>
               </td>
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

    <!-- Модальное окно создания долга -->
    <div v-if="showCreateModal" class="modal" @click.self="closeCreateModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Создать долг</h3>
          <button class="modal-close" @click="closeCreateModal">&times;</button>
        </div>

        <form @submit.prevent="createDebt">
          <div class="form-group">
            <label class="form-label required">Тип долга</label>
            <select v-model="formData.type" class="form-control" required>
              <option value="lend">Мне должны (я одолжил кому-то)</option>
              <option value="borrow">Я должен (взял в долг у кого-то)</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Счет</label>
            <select v-model="formData.account_id" class="form-control" required>
              <option value="">Выберите счет</option>
              <option v-for="account in activeAccounts" :key="account.id" :value="account.id">
                {{ account.name }} ({{ formatCurrency(account.balance) }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Сумма</label>
            <input 
              type="number" 
              v-model="formData.amount" 
              class="form-control" 
              step="0.01" 
              required
              placeholder="Введите сумму"
            >
          </div>

          <div class="form-group">
            <label class="form-label required">Контрагент</label>
            <input 
              type="text" 
              v-model="formData.description" 
              class="form-control" 
              required
              placeholder="Кому/от кого? Например: Иван Петров"
            >
          </div>

          <div class="form-group">
            <label class="form-label required">Дата</label>
            <input 
              type="date" 
              v-model="formData.date" 
              class="form-control" 
              required
            >
          </div>

          <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            {{ getTypeDescription(formData.type) }}
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeCreateModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Создать долг</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно просмотра долга -->
    <div v-if="showViewModal" class="modal" @click.self="showViewModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Детали долга</h3>
          <button class="modal-close" @click="showViewModal = false">&times;</button>
        </div>
        
        <div v-if="currentDebt" class="debt-details">
          <div class="detail-row">
            <span class="detail-label">ID:</span>
            <span class="detail-value">{{ currentDebt.id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Контрагент:</span>
            <span class="detail-value"><strong>{{ currentDebt.borrower_description }}</strong></span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Сумма:</span>
            <span class="detail-value" :class="getDebtAmountClass(currentDebt)">
              {{ formatCurrency(getDebtAmount(currentDebt)) }}
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Дата:</span>
            <span class="detail-value">{{ formatDate(getDebtDate(currentDebt)) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Счет:</span>
            <span class="detail-value">{{ getAccountName(currentDebt) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Статус:</span>
            <span class="detail-value">
              <span class="badge" :class="currentDebt.is_repaid ? 'badge-success' : 'badge-warning'">
                {{ currentDebt.is_repaid ? 'Погашен' : 'Активен' }}
              </span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно погашения долга -->
    <div v-if="showRepayModal" class="modal" @click.self="closeRepayModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Погашение долга</h3>
          <button class="modal-close" @click="closeRepayModal">&times;</button>
        </div>

        <div class="alert alert-info">
          <i class="fas fa-info-circle"></i>
          {{ currentDebt?.borrower_description }} - {{ formatCurrency(getDebtAmount(currentDebt)) }}
        </div>

        <form @submit.prevent="repayDebt">
          <div class="form-group">
            <label class="form-label required">Сумма погашения</label>
            <input 
              type="number" 
              v-model="repayAmount" 
              class="form-control" 
              step="0.01" 
              :max="getDebtAmount(currentDebt)"
              required
            >
            <small class="form-text">Максимальная сумма: {{ formatCurrency(getDebtAmount(currentDebt)) }}</small>
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeRepayModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-success">Погасить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'DebtsList',
  setup() {
    const debts = ref([])
    const accounts = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalCount = ref(0)
    const currentType = ref('lend')
    const showCreateModal = ref(false)
    const showViewModal = ref(false)
    const showRepayModal = ref(false)
    const currentDebt = ref(null)
    const repayAmount = ref(0)
    const formData = ref({
      type: 'lend',
      account_id: '',
      amount: '',
      description: '',
      date: new Date().toISOString().slice(0, 10)
    })

    const activeAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active)
    })

    const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))
    
    // Функции для получения данных из структуры API
    const getDebtAmount = (debt) => {
      return debt.transfer?.amount || debt.amount || 0
    }
    
    const getDebtDate = (debt) => {
      return debt.transfer?.timestamp || debt.date || null
    }
    
    // Определяем тип долга на основе destination_account
    const getDebtType = (debt) => {
      // Если есть поле type в самом долге
      if (debt.type) return debt.type
      
      // Определяем по имени счета назначения
      const destAccount = debt.transfer?.destination_account
      if (destAccount) {
        // Если счет называется "debt" - это "я должен"
        if (destAccount.name === 'debt') return 'borrow'
        // Если счет называется "lend" - это "мне должны"
        if (destAccount.name === 'lend') return 'lend'
      }
      
      // По умолчанию считаем что это "мне должны"
      return 'lend'
    }
    
    // Фильтруем долги по текущему типу
    const filteredDebts = computed(() => {
      return debts.value.filter(debt => {
        const debtType = getDebtType(debt)
        if (currentType.value === 'lend') {
          return debtType === 'lend'
        } else {
          return debtType === 'borrow'
        }
      })
    })
    
    // Статистика: сумма где мне должны
    const totalLend = computed(() => {
      return debts.value
        .filter(debt => getDebtType(debt) === 'lend' && !debt.is_repaid)
        .reduce((sum, d) => sum + parseFloat(getDebtAmount(d)), 0)
    })
    
    // Статистика: сумма где я должен
    const totalBorrow = computed(() => {
      return debts.value
        .filter(debt => getDebtType(debt) === 'borrow' && !debt.is_repaid)
        .reduce((sum, d) => sum + parseFloat(getDebtAmount(d)), 0)
    })
    
    const netDebt = computed(() => totalLend.value - totalBorrow.value)
    
    // Определяем класс для суммы в зависимости от типа
    const getDebtAmountClass = (debt) => {
      const debtType = getDebtType(debt)
      return debtType === 'lend' ? 'text-success' : 'text-danger'
    }

    const loadDebts = async () => {
      try {
        // Загружаем все долги без фильтрации по типу
        const data = await apiService.getDebts(currentPage.value, pageSize.value)
        debts.value = data.results || []
        totalCount.value = data.count || 0
        console.log('Загружены все долги:', debts.value)
      } catch (error) {
        console.error('Error loading debts:', error)
        debts.value = []
      }
    }

    const loadAccounts = async () => {
      try {
        const data = await apiService.getAccounts(1, 100)
        accounts.value = data.results[0]?.accounts || []
        console.log('Загружены счета:', accounts.value)
      } catch (error) {
        console.error('Error loading accounts:', error)
      }
    }

    const getAccountName = (debt) => {
      // Показываем название счета назначения
      const destAccount = debt.transfer?.destination_account
      if (destAccount) {
        return destAccount.name
      }
      
      // Если нет информации, пытаемся найти по ID
      const accountId = debt.account || debt.account_id
      if (accountId && accounts.value.length) {
        const account = accounts.value.find(acc => acc.id === accountId)
        return account ? account.name : `Счет #${accountId}`
      }
      
      return 'Не указан'
    }

    const getTypeDescription = (type) => {
      return type === 'lend' 
        ? 'Деньги будут списаны с вашего счета (вы даете в долг)'
        : 'Деньги будут зачислены на ваш счет (вы берете в долг)'
    }

    const openCreateModal = () => {
      formData.value = {
        type: 'lend',
        account_id: '',
        amount: '',
        description: '',
        date: new Date().toISOString().slice(0, 10)
      }
      showCreateModal.value = true
    }

    const closeCreateModal = () => {
      showCreateModal.value = false
    }

    const createDebt = async () => {
      if (!formData.value.account_id) {
        alert('Выберите счет')
        return
      }
      
      if (!formData.value.amount || formData.value.amount <= 0) {
        alert('Введите корректную сумму')
        return
      }
      
      if (!formData.value.description.trim()) {
        alert('Введите описание (контрагента)')
        return
      }
      
      try {
        // Преобразуем тип для API: lend -> borrow, borrow -> debt
        const apiType = formData.value.type === 'lend' ? 'borrow' : 'debt'
        
        await apiService.createDebt(
          formData.value.account_id,
          apiType,
          formData.value.amount,
          formData.value.description,
          formData.value.date
        )
        closeCreateModal()
        await loadDebts()
        await loadAccounts()
      } catch (error) {
        console.error('Error creating debt:', error)
        alert('Ошибка при создании долга: ' + (error.message || 'Неизвестная ошибка'))
      }
    }

    const viewDebt = async (debt) => {
      try {
        const data = await apiService.getDebt(debt.id)
        currentDebt.value = data
        showViewModal.value = true
      } catch (error) {
        console.error('Error loading debt details:', error)
        alert('Ошибка при загрузке деталей долга')
      }
    }

    const openRepayModal = (debt) => {
      currentDebt.value = debt
      repayAmount.value = parseFloat(getDebtAmount(debt))
      showRepayModal.value = true
    }

    const closeRepayModal = () => {
      showRepayModal.value = false
      currentDebt.value = null
      repayAmount.value = 0
    }

    const repayDebt = async () => {
      if (repayAmount.value <= 0) {
        alert('Введите корректную сумму')
        return
      }
      
      const fullAmount = parseFloat(getDebtAmount(currentDebt.value))
      if (repayAmount.value > fullAmount) {
        alert('Сумма погашения не может превышать сумму долга')
        return
      }
      
      try {
        await apiService.repayDebt(
          currentDebt.value.id,
          repayAmount.value,
          getDebtType(currentDebt.value)
        )
        closeRepayModal()
        await loadDebts()
        await loadAccounts()
      } catch (error) {
        console.error('Error repaying debt:', error)
        alert('Ошибка при погашении долга')
      }
    }

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        loadDebts()
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        loadDebts()
      }
    }

    const formatCurrency = (value) => {
      if (!value) return '0 ₽'
      const numValue = parseFloat(value)
      if (isNaN(numValue)) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(numValue)
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('ru-RU')
    }

    onMounted(() => {
      loadDebts()
      loadAccounts()
    })

    watch(currentType, () => {
      currentPage.value = 1
      loadDebts()
    })

    return {
      debts,
      accounts,
      currentPage,
      totalPages,
      currentType,
      showCreateModal,
      showViewModal,
      showRepayModal,
      currentDebt,
      repayAmount,
      formData,
      activeAccounts,
      filteredDebts,
      totalLend,
      totalBorrow,
      netDebt,
      getDebtAmount,
      getDebtDate,
      getDebtAmountClass,
      getAccountName,
      getTypeDescription,
      openCreateModal,
      closeCreateModal,
      createDebt,
      viewDebt,
      openRepayModal,
      closeRepayModal,
      repayDebt,
      prevPage,
      nextPage,
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
}

.type-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background: var(--white);
  padding: 0.5rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.tab-btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.tab-btn.active {
  background: var(--primary-color);
  color: var(--white);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn-info {
  background: #3b82f6;
  color: white;
}

.btn-info:hover {
  background: #2563eb;
}

.badge-info {
  background: #dbeafe;
  color: #1e40af;
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
}

.badge-warning {
  background: #fed7aa;
  color: #92400e;
}

.debt-details {
  padding: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  border-bottom: 1px solid var(--light-color);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  color: var(--gray-color);
}

.detail-value {
  font-weight: 500;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.form-text {
  font-size: 0.75rem;
  color: var(--gray-color);
  margin-top: 0.25rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.text-center {
  text-align: center;
}

.table-responsive {
  overflow-x: auto;
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

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .detail-row {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>