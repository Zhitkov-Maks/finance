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
          <small>{{ netDebt >= 0 ? '' : '(-)' }}</small>
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
        <i class="fas fa-hand-holding-usd"></i> <span class="tab-text">Мне должны</span>
      </button>
      <button 
        @click="currentType = 'borrow'" 
        class="tab-btn" 
        :class="{ active: currentType === 'borrow' }"
      >
        <i class="fas fa-hand-holding-heart"></i> <span class="tab-text">Я должен</span>
      </button>
    </div>

    <div class="card">
      <!-- Мобильные и планшетные карточки с раскрытием -->
      <div class="mobile-debts">
        <div v-for="debt in filteredDebts" :key="debt.id" class="debt-card">
          <!-- Компактный заголовок карточки -->
          <div class="debt-compact" @click="toggleExpand(debt.id)">
            <div class="compact-left">
              <div class="debt-date-compact">{{ formatShortDate(getDebtDate(debt)) }}</div>
              <div class="debt-contractor-compact">
                <strong>{{ truncateText(debt.borrower_description, 20) }}</strong>
              </div>
            </div>
            <div class="compact-right">
              <div class="debt-amount-compact" :class="getDebtAmountClass(debt)">
                {{ formatCurrency(getDebtAmount(debt)) }}
              </div>
              <button class="expand-icon" @click.stop="toggleExpand(debt.id)">
                <i :class="expandedDebts.has(debt.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>
          </div>

          <!-- Раскрывающаяся детальная информация -->
          <div v-if="expandedDebts.has(debt.id)" class="debt-expanded">
            <div class="debt-details-expanded">
              <div class="detail-item">
                <span class="detail-label">
                  <i class="fas fa-user"></i> Контрагент:
                </span>
                <span class="detail-value">{{ debt.borrower_description }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">
                  <i class="fas fa-calendar"></i> Полная дата:
                </span>
                <span class="detail-value">{{ formatDate(getDebtDate(debt)) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">
                  <i class="fas fa-credit-card"></i> Счет:
                </span>
                <span class="detail-value">{{ getRealAccountName(debt) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">
                  <i class="fas fa-flag-checkered"></i> Статус:
                </span>
                <span class="badge" :class="debt.is_repaid ? 'badge-success' : 'badge-warning'">
                  <i :class="debt.is_repaid ? 'fas fa-check-circle' : 'fas fa-clock'"></i>
                  {{ debt.is_repaid ? 'Погашен' : 'Активен' }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">
                  <i class="fas fa-tag"></i> Тип:
                </span>
                <span class="badge" :class="getDebtType(debt) === 'lend' ? 'badge-success' : 'badge-danger'">
                  {{ getDebtType(debt) === 'lend' ? 'Мне должны' : 'Я должен' }}
                </span>
              </div>
            </div>
            <div class="debt-actions-expanded">
              <button @click="viewDebt(debt)" class="btn btn-sm btn-info">
                <i class="fas fa-eye"></i> Детали
              </button>
              <button
                v-if="!debt.is_repaid"
                @click="openRepayModal(debt)"
                class="btn btn-sm btn-success"
              >
                <i class="fas fa-check"></i> Погасить
              </button>
            </div>
          </div>
        </div>
        <div v-if="filteredDebts.length === 0" class="empty-state">
          <i class="fas fa-hand-holding-usd"></i>
          <p>Нет {{ currentType === 'lend' ? 'долгов перед вами' : 'ваших долгов' }}</p>
          <button @click="openCreateModal" class="btn btn-primary">Создать долг</button>
        </div>
      </div>

      <!-- Десктопная таблица -->
      <div class="desktop-table">
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
                  {{ getRealAccountName(debt) }}
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
          <i class="fas fa-chevron-left"></i> <span class="pagination-text">Назад</span>
        </button>
        <span class="pagination-info">Страница {{ currentPage }} из {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-secondary">
          <span class="pagination-text">Вперед</span> <i class="fas fa-chevron-right"></i>
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

        <div v-if="currentDebt" class="debt-details-modal">
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
            <span class="detail-value">{{ getRealAccountName(currentDebt) }}</span>
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
          <strong>{{ currentDebt?.borrower_description }}</strong><br>
          Сумма долга: {{ formatCurrency(getDebtAmount(currentDebt)) }}
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
    const expandedDebts = ref(new Set())

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

    const toggleExpand = (debtId) => {
      if (expandedDebts.value.has(debtId)) {
        expandedDebts.value.delete(debtId)
      } else {
        expandedDebts.value.add(debtId)
      }
      expandedDebts.value = new Set(expandedDebts.value)
    }

    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    const getDebtAmount = (debt) => {
      return debt.transfer?.amount || debt.amount || 0
    }

    const getDebtDate = (debt) => {
      return debt.transfer?.timestamp || debt.date || null
    }

    const getDebtType = (debt) => {
      if (debt.type) return debt.type

      const destAccount = debt.transfer?.destination_account
      if (destAccount) {
        if (destAccount.name === 'debt') return 'borrow'
        if (destAccount.name === 'lend') return 'lend'
      }

      return 'lend'
    }

    const getRealAccountName = (debt) => {
      const sourceAccount = debt.transfer?.source_account
      if (sourceAccount && sourceAccount.name !== 'debt' && sourceAccount.name !== 'lend') {
        return sourceAccount.name
      }

      const accountId = debt.account || debt.account_id
      if (accountId && accounts.value.length) {
        const account = accounts.value.find(acc => acc.id === accountId)
        if (account) {
          return account.name
        }
      }

      if (debt.transfer_id && accounts.value.length) {
        for (const acc of accounts.value) {
          if (acc.id === debt.transfer_id) {
            return acc.name
          }
        }
      }

      return 'Не указан'
    }

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

    const totalLend = computed(() => {
      return debts.value
        .filter(debt => getDebtType(debt) === 'lend' && !debt.is_repaid)
        .reduce((sum, d) => sum + parseFloat(getDebtAmount(d)), 0)
    })

    const totalBorrow = computed(() => {
      return debts.value
        .filter(debt => getDebtType(debt) === 'borrow' && !debt.is_repaid)
        .reduce((sum, d) => sum + parseFloat(getDebtAmount(d)), 0)
    })

    const netDebt = computed(() => totalLend.value - totalBorrow.value)

    const getDebtAmountClass = (debt) => {
      const debtType = getDebtType(debt)
      return debtType === 'lend' ? 'text-success' : 'text-danger'
    }

    const loadDebts = async () => {
      try {
        const data = await apiService.getDebts(currentPage.value, pageSize.value)
        debts.value = data.results || []
        totalCount.value = data.count || 0
      } catch (error) {
        console.error('Error loading debts:', error)
        debts.value = []
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
      return new Date(dateString).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    }

    const formatShortDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit'
      })
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
      expandedDebts,
      toggleExpand,
      truncateText,
      getDebtAmount,
      getDebtDate,
      getDebtAmountClass,
      getRealAccountName,
      getDebtType,
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
      formatDate,
      formatShortDate
    }
  }
}
</script>

<style scoped>
/* Общие стили */
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

/* Статистика */
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
  text-align: center;
}

.stat-title {
  font-size: 0.875rem;
  color: var(--gray-color);
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
}

/* Табы */
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

/* Мобильные карточки */
.mobile-debts {
  display: none;
}

.debt-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  margin-bottom: 0.5rem;
  overflow: hidden;
  transition: all 0.3s ease;
}

/* Компактный заголовок */
.debt-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.debt-compact:hover {
  background-color: #f9fafb;
}

.compact-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.debt-date-compact {
  font-size: 0.75rem;
  color: var(--gray-color);
  min-width: 55px;
}

.debt-contractor-compact {
  font-size: 0.875rem;
  flex: 1;
}

.compact-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.debt-amount-compact {
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
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.expand-icon:hover {
  background-color: var(--light-color);
  color: var(--primary-color);
}

/* Раскрывающаяся часть */
.debt-expanded {
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

.debt-details-expanded {
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

.debt-actions-expanded {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.debt-actions-expanded .btn-sm {
  padding: 0.5rem 1rem;
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

/* Кнопки и бейджи */
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

.btn-success {
  background: var(--secondary-color);
  color: white;
}

.btn-success:hover {
  background: #059669;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
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

.badge-danger {
  background: #fee2e2;
  color: #991b1b;
}

.text-success {
  color: var(--secondary-color);
}

.text-danger {
  color: var(--danger-color);
}

/* Модальные окна */
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

.alert {
  padding: 0.75rem;
  border-radius: var(--radius);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.alert-info {
  background: #dbeafe;
  color: #1e40af;
}

.debt-details-modal {
  padding: 0.5rem;
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

/* Пустое состояние */
.empty-state {
  text-align: center;
  padding: 3rem;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Пагинация */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

/* Адаптивные стили */
@media (max-width: 1024px) {
  .desktop-table {
    display: none;
  }

  .mobile-debts {
    display: block;
  }

  .stats-grid {
    gap: 1rem;
  }

  .stat-value {
    font-size: 1.5rem;
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

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-title {
    font-size: 0.75rem;
  }

  .stat-value {
    font-size: 1.25rem;
  }

  .type-tabs {
    flex-direction: column;
  }

  .compact-left {
    gap: 0.5rem;
  }

  .debt-date-compact {
    min-width: 50px;
    font-size: 0.7rem;
  }

  .debt-contractor-compact {
    font-size: 0.8rem;
  }

  .debt-amount-compact {
    font-size: 0.9rem;
  }

  .modal-content {
    width: 95%;
    margin: 1rem;
    max-height: 85vh;
  }

  .modal-footer {
    flex-direction: column;
  }

  .modal-footer .btn {
    width: 100%;
  }

  .pagination {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .debt-compact {
    padding: 0.6rem 0.75rem;
  }

  .compact-left {
    gap: 0.4rem;
  }

  .debt-date-compact {
    min-width: 45px;
  }

  .debt-contractor-compact {
    font-size: 0.75rem;
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

  .debt-actions-expanded {
    flex-direction: column;
  }

  .debt-actions-expanded .btn-sm {
    width: 100%;
  }

  .expand-icon {
    width: 36px;
    height: 36px;
  }

  .pagination-text {
    display: none;
  }

  .pagination .btn {
    padding: 0.5rem;
  }
}

/* Планшеты в горизонтальной ориентации */
@media (min-width: 1025px) and (max-width: 1280px) {
  .desktop-table {
    display: block;
  }

  .mobile-debts {
    display: none;
  }

  .table th,
  .table td {
    padding: 0.5rem;
    font-size: 0.875rem;
  }
}

/* Планшеты в вертикальной ориентации */
@media (min-width: 769px) and (max-width: 1024px) and (orientation: portrait) {
  .desktop-table {
    display: none;
  }

  .mobile-debts {
    display: block;
  }
}
</style>