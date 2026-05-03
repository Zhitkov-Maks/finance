<template>
  <div>
    <div class="page-header">
      <h1>Счета</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Создать счет
      </button>
    </div>

    <!-- Статистика счетов -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-title">Всего счетов</div>
        <div class="stat-value">{{ accounts.length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Общий баланс (активные)</div>
        <div class="stat-value text-success">{{ formatCurrency(totalBalance) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Активных счетов</div>
        <div class="stat-value">{{ activeAccountsCount }}</div>
      </div>
    </div>

    <!-- Активные счета -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-check-circle text-success"></i> Активные счета
          <span class="badge badge-success">{{ activeAccounts.length }}</span>
        </h3>
      </div>

      <!-- Мобильные и планшетные карточки -->
      <div class="mobile-accounts">
        <div v-for="account in activeAccounts" :key="account.id" class="account-card">
          <div class="account-compact" @click="toggleExpand(account.id)">
            <div class="compact-left">
              <div class="account-name-compact">
                <strong>{{ truncateText(account.name, 25) }}</strong>
              </div>
              <span class="badge badge-success">Активен</span>
            </div>
            <div class="compact-right">
              <div class="account-balance-compact text-success">
                {{ formatCurrency(account.balance) }}
              </div>
              <button class="expand-icon" @click.stop="toggleExpand(account.id)">
                <i :class="expandedAccounts.has(account.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>
          </div>

          <!-- Раскрывающаяся часть с кнопками -->
          <div v-if="expandedAccounts.has(account.id)" class="account-expanded">
            <div class="account-actions-expanded">
              <button @click="editAccount(account)" class="btn btn-sm btn-info">
                <i class="fas fa-edit"></i> Редактировать
              </button>
              <button @click="toggleVisibility(account)" class="btn btn-sm btn-warning">
                <i class="fas fa-eye-slash"></i> Скрыть
              </button>
              <button @click="openBalanceModal(account)" class="btn btn-sm btn-primary">
                <i class="fas fa-chart-line"></i> Баланс
              </button>
              <button @click="confirmDelete(account)" class="btn btn-sm btn-danger">
                <i class="fas fa-trash"></i> Удалить
              </button>
            </div>
          </div>
        </div>
        <div v-if="activeAccounts.length === 0" class="empty-state">
          <i class="fas fa-credit-card"></i>
          <p>Нет активных счетов</p>
        </div>
      </div>

      <!-- Десктопная таблица -->
      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Баланс</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="account in activeAccounts" :key="account.id">
              <td>
                <strong>{{ account.name }}</strong>
              </td>
              <td class="text-success">
                <strong>{{ formatCurrency(account.balance) }}</strong>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editAccount(account)" class="btn btn-sm btn-info" title="Редактировать">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button @click="toggleVisibility(account)" class="btn btn-sm btn-warning" title="Скрыть счет">
                    <i class="fas fa-eye-slash"></i>
                  </button>
                  <button @click="openBalanceModal(account)" class="btn btn-sm btn-primary" title="Изменить баланс">
                    <i class="fas fa-chart-line"></i>
                  </button>
                  <button @click="confirmDelete(account)" class="btn btn-sm btn-danger" title="Удалить">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="activeAccounts.length === 0">
              <td colspan="3" class="text-center">Нет активных счетов</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Неактивные счета -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-eye-slash text-muted"></i> Неактивные счета
          <span class="badge badge-secondary">{{ inactiveAccounts.length }}</span>
        </h3>
      </div>

      <div class="mobile-accounts">
        <div v-for="account in inactiveAccounts" :key="account.id" class="account-card inactive">
          <div class="account-compact" @click="toggleExpand(account.id)">
            <div class="compact-left">
              <div class="account-name-compact">
                <strong>{{ truncateText(account.name, 25) }}</strong>
              </div>
              <span class="badge badge-secondary">Неактивен</span>
            </div>
            <div class="compact-right">
              <div class="account-balance-compact text-muted">
                {{ formatCurrency(account.balance) }}
              </div>
              <button class="expand-icon" @click.stop="toggleExpand(account.id)">
                <i :class="expandedAccounts.has(account.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>
          </div>

          <div v-if="expandedAccounts.has(account.id)" class="account-expanded">
            <div class="account-actions-expanded">
              <button @click="editAccount(account)" class="btn btn-sm btn-info">
                <i class="fas fa-edit"></i> Редактировать
              </button>
              <button @click="toggleVisibility(account)" class="btn btn-sm btn-success">
                <i class="fas fa-eye"></i> Показать
              </button>
              <button @click="openBalanceModal(account)" class="btn btn-sm btn-primary">
                <i class="fas fa-chart-line"></i> Баланс
              </button>
              <button @click="confirmDelete(account)" class="btn btn-sm btn-danger">
                <i class="fas fa-trash"></i> Удалить
              </button>
            </div>
          </div>
        </div>
        <div v-if="inactiveAccounts.length === 0" class="empty-state">
          <i class="fas fa-credit-card"></i>
          <p>Нет неактивных счетов</p>
        </div>
      </div>

      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Баланс</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="account in inactiveAccounts" :key="account.id">
              <td>
                <strong>{{ account.name }}</strong>
              </td>
              <td class="text-muted">
                <strong>{{ formatCurrency(account.balance) }}</strong>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editAccount(account)" class="btn btn-sm btn-info" title="Редактировать">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button @click="toggleVisibility(account)" class="btn btn-sm btn-success" title="Показать счет">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button @click="openBalanceModal(account)" class="btn btn-sm btn-primary" title="Изменить баланс">
                    <i class="fas fa-chart-line"></i>
                  </button>
                  <button @click="confirmDelete(account)" class="btn btn-sm btn-danger" title="Удалить">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="inactiveAccounts.length === 0">
              <td colspan="3" class="text-center">Нет неактивных счетов</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования счета -->
    <div v-if="showAccountModal" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingAccount ? 'Редактировать счет' : 'Создать счет' }}</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>

        <form @submit.prevent="saveAccount">
          <div class="form-group">
            <label class="form-label required">Название счета</label>
            <input
              type="text"
              v-model="formData.name"
              class="form-control"
              required
              placeholder="Например: Сбербанк, Наличные, Тинькофф"
            >
          </div>

          <div class="form-group">
            <label class="form-label required">Начальный баланс</label>
            <input
              type="number"
              v-model="formData.balance"
              class="form-control"
              step="0.01"
              required
              :placeholder="editingAccount ? 'Новый баланс' : '0.00'"
            >
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">
              {{ editingAccount ? 'Обновить' : 'Создать' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно изменения баланса -->
    <div v-if="showBalanceModal" class="modal" @click.self="showBalanceModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Изменить баланс счета "{{ balanceAccount?.name }}"</h3>
          <button class="modal-close" @click="showBalanceModal = false">&times;</button>
        </div>

        <form @submit.prevent="updateBalance">
          <div class="form-group">
            <label class="form-label required">Текущий баланс</label>
            <input
              type="text"
              class="form-control"
              :value="formatCurrency(balanceAccount?.balance)"
              disabled
            >
          </div>

          <div class="form-group">
            <label class="form-label required">Новый баланс</label>
            <input
              type="number"
              v-model="newBalance"
              class="form-control"
              step="0.01"
              required
              placeholder="Введите новую сумму"
            >
          </div>

          <div class="alert alert-info" v-if="balanceAccount && !balanceAccount.is_active">
            <i class="fas fa-info-circle"></i>
            Этот счет неактивен и не учитывается в общем балансе.
          </div>

          <div class="modal-footer">
            <button type="button" @click="showBalanceModal = false" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="showDeleteModal" class="modal" @click.self="showDeleteModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Подтверждение удаления</h3>
          <button class="modal-close" @click="showDeleteModal = false">&times;</button>
        </div>

        <div class="alert alert-danger">
          <i class="fas fa-exclamation-triangle"></i>
          Внимание! Удаление счета приведет к удалению всех связанных транзакций!
        </div>

        <p>Вы уверены, что хотите удалить счет <strong>"{{ accountToDelete?.name }}"</strong>?</p>
        <p class="text-muted">Баланс счета: {{ formatCurrency(accountToDelete?.balance) }}</p>

        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-secondary">Отмена</button>
          <button @click="deleteAccount" class="btn btn-danger">Да, удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'AccountsList',
  setup() {
    const accounts = ref([])
    const loading = ref(false)
    const showAccountModal = ref(false)
    const showBalanceModal = ref(false)
    const showDeleteModal = ref(false)
    const editingAccount = ref(null)
    const balanceAccount = ref(null)
    const accountToDelete = ref(null)
    const newBalance = ref(0)
    const expandedAccounts = ref(new Set())

    const formData = ref({
      name: '',
      balance: 0,
      is_active: true
    })

    const activeAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active)
    })

    const inactiveAccounts = computed(() => {
      return accounts.value.filter(acc => !acc.is_active)
    })

    const totalBalance = computed(() => {
      return activeAccounts.value.reduce((sum, acc) => sum + parseFloat(acc.balance), 0)
    })

    const activeAccountsCount = computed(() => {
      return activeAccounts.value.length
    })

    const toggleExpand = (accountId) => {
      if (expandedAccounts.value.has(accountId)) {
        expandedAccounts.value.delete(accountId)
      } else {
        expandedAccounts.value.add(accountId)
      }
      expandedAccounts.value = new Set(expandedAccounts.value)
    }

    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    const loadAccounts = async () => {
      loading.value = true
      try {
        const data = await apiService.getAccounts(1, 100)

        if (data.results && Array.isArray(data.results)) {
          if (data.results.length > 0 && data.results[0].accounts) {
            accounts.value = data.results[0].accounts
          } else {
            accounts.value = data.results
          }
        } else if (Array.isArray(data)) {
          accounts.value = data
        } else if (data.accounts) {
          accounts.value = data.accounts
        } else {
          accounts.value = []
        }

        console.log(`Загружено счетов: ${accounts.value.length}`)
      } catch (error) {
        console.error('Error loading accounts:', error)
        alert('Ошибка при загрузке счетов')
        accounts.value = []
      } finally {
        loading.value = false
      }
    }

    const openCreateModal = () => {
      editingAccount.value = null
      formData.value = {
        name: '',
        balance: 0,
        is_active: true
      }
      showAccountModal.value = true
    }

    const editAccount = (account) => {
      editingAccount.value = account
      formData.value = {
        name: account.name,
        balance: parseFloat(account.balance),
        is_active: account.is_active
      }
      showAccountModal.value = true
    }

    const saveAccount = async () => {
      try {
        if (editingAccount.value) {
          await apiService.updateAccount(editingAccount.value.id, {
            name: formData.value.name,
            balance: formData.value.balance,
            is_active: formData.value.is_active
          })
        } else {
          await apiService.createAccount(formData.value.name, formData.value.balance)
        }
        closeModal()
        await loadAccounts()
      } catch (error) {
        console.error('Error saving account:', error)
        alert('Ошибка при сохранении счета')
      }
    }

    const toggleVisibility = async (account) => {
      try {
        await apiService.toggleAccountActive(account.id, !account.is_active)
        await loadAccounts()
      } catch (error) {
        console.error('Error toggling account visibility:', error)
        alert('Ошибка при изменении видимости счета')
      }
    }

    const openBalanceModal = (account) => {
      balanceAccount.value = account
      newBalance.value = parseFloat(account.balance)
      showBalanceModal.value = true
    }

    const updateBalance = async () => {
      try {
        await apiService.patchAccount(balanceAccount.value.id, {
          balance: newBalance.value
        })
        showBalanceModal.value = false
        await loadAccounts()
      } catch (error) {
        console.error('Error updating balance:', error)
        alert('Ошибка при обновлении баланса')
      }
    }

    const confirmDelete = (account) => {
      accountToDelete.value = account
      showDeleteModal.value = true
    }

    const deleteAccount = async () => {
      try {
        await apiService.deleteAccount(accountToDelete.value.id)
        showDeleteModal.value = false
        await loadAccounts()
      } catch (error) {
        console.error('Error deleting account:', error)
        alert('Ошибка при удалении счета')
      }
    }

    const closeModal = () => {
      showAccountModal.value = false
      editingAccount.value = null
      formData.value = {
        name: '',
        balance: 0,
        is_active: true
      }
    }

    const formatCurrency = (value) => {
      if (!value && value !== 0) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value)
    }

    onMounted(() => {
      loadAccounts()
    })

    return {
      accounts,
      activeAccounts,
      inactiveAccounts,
      loading,
      showAccountModal,
      showBalanceModal,
      showDeleteModal,
      editingAccount,
      balanceAccount,
      accountToDelete,
      newBalance,
      formData,
      totalBalance,
      activeAccountsCount,
      expandedAccounts,
      toggleExpand,
      truncateText,
      openCreateModal,
      editAccount,
      saveAccount,
      toggleVisibility,
      openBalanceModal,
      updateBalance,
      confirmDelete,
      deleteAccount,
      closeModal,
      formatCurrency
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

.card {
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
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
  margin-left: 0.5rem;
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
}

.badge-secondary {
  background: #e5e7eb;
  color: #4b5563;
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

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover {
  background: #d97706;
}

.btn-success {
  background: var(--secondary-color);
  color: white;
}

.btn-success:hover {
  background: #059669;
}

.text-success {
  color: var(--secondary-color);
}

.text-muted {
  color: var(--gray-color);
}

/* Мобильные карточки */
.mobile-accounts {
  display: none;
}

.account-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  margin-bottom: 0.5rem;
  overflow: hidden;
  transition: all 0.3s ease;
}

.account-card.inactive {
  opacity: 0.85;
  background: #f9fafb;
}

/* Компактный заголовок */
.account-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.account-compact:hover {
  background-color: #f9fafb;
}

.compact-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.account-name-compact {
  font-size: 0.875rem;
}

.compact-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.account-balance-compact {
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
.account-expanded {
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

.account-actions-expanded {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.account-actions-expanded .btn-sm {
  flex: 1;
  min-width: calc(50% - 0.25rem);
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

/* Модальные окна */
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

.alert-danger {
  background: #fee2e2;
  color: #991b1b;
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

.empty-state p {
  margin: 0;
}

/* Адаптивные стили */
@media (max-width: 1024px) {
  .desktop-table {
    display: none;
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

  .compact-left {
    gap: 0.5rem;
  }

  .account-name-compact {
    font-size: 0.8rem;
  }

  .account-balance-compact {
    font-size: 0.9rem;
  }

  .badge {
    font-size: 0.65rem;
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
  .account-compact {
    padding: 0.6rem 0.75rem;
  }

  .compact-left {
    gap: 0.4rem;
    flex-wrap: wrap;
  }

  .account-name-compact {
    width: 100%;
    margin-bottom: 0.25rem;
  }

  .account-actions-expanded {
    flex-direction: column;
  }

  .account-actions-expanded .btn-sm {
    width: 100%;
  }

  .expand-icon {
    width: 36px;
    height: 36px;
  }
}

/* Планшеты в горизонтальной ориентации */
@media (min-width: 1025px) and (max-width: 1280px) {
  .desktop-table {
    display: block;
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