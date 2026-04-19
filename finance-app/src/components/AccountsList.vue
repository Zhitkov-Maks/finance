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

    <div class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Баланс</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="account in accounts" :key="account.id">
              <td>{{ account.id }}</td>
              <td>
                <strong>{{ account.name }}</strong>
              </td>
              <td :class="parseFloat(account.balance) >= 0 ? 'text-success' : 'text-danger'">
                <strong>{{ formatCurrency(account.balance) }}</strong>
              </td>
              <td>
                <span class="badge" :class="account.is_active ? 'badge-success' : 'badge-danger'">
                  <i :class="account.is_active ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
                  {{ account.is_active ? 'Активен' : 'Неактивен' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editAccount(account)" class="btn btn-sm btn-info" title="Редактировать">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button @click="toggleVisibility(account)" class="btn btn-sm" :class="account.is_active ? 'btn-warning' : 'btn-success'" :title="account.is_active ? 'Скрыть счет' : 'Показать счет'">
                    <i :class="account.is_active ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
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
            <tr v-if="accounts.length === 0">
              <td colspan="5" class="text-center">Нет созданных счетов</td>
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

          <div class="form-group" v-if="editingAccount">
            <label class="form-label">
              <input type="checkbox" v-model="formData.is_active">
              Счет активен (отображается в списке и учитывается в общем балансе)
            </label>
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
    const formData = ref({
      name: '',
      balance: 0,
      is_active: true
    })

    // Общий баланс ТОЛЬКО активных счетов
    const totalBalance = computed(() => {
      return accounts.value
        .filter(acc => acc.is_active) // Фильтруем только активные счета
        .reduce((sum, acc) => sum + parseFloat(acc.balance), 0)
    })

    // Количество активных счетов
    const activeAccountsCount = computed(() => {
      return accounts.value.filter(acc => acc.is_active).length
    })

    // Количество неактивных счетов
    const inactiveAccountsCount = computed(() => {
      return accounts.value.filter(acc => !acc.is_active).length
    })

    const loadAccounts = async () => {
      loading.value = true
      try {
        const data = await apiService.getAccounts(1, 100)
        accounts.value = data.results[0]?.accounts || []
      } catch (error) {
        console.error('Error loading accounts:', error)
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
        balance: account.balance,
        is_active: account.is_active
      }
      showAccountModal.value = true
    }

    const saveAccount = async () => {
      try {
        if (editingAccount.value) {
          // Полное обновление счета
          await apiService.updateAccount(editingAccount.value.id, {
            name: formData.value.name,
            balance: formData.value.balance,
            is_active: formData.value.is_active
          })
        } else {
          // Создание нового счета
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
      if (!value) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(value)
    }

    onMounted(() => {
      loadAccounts()
    })

    return {
      accounts,
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
      inactiveAccountsCount,
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
}

.text-danger {
  color: var(--danger-color);
}

.required:after {
  content: " *";
  color: var(--danger-color);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.text-muted {
  color: var(--gray-color);
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.table-responsive {
  overflow-x: auto;
}

.alert-info {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.75rem;
  border-radius: var(--radius);
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .btn-sm {
    width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>