<template>
  <div>
    <h1 style="margin-bottom: 2rem;">Переводы между счетами</h1>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Новый перевод</h3>
      </div>

      <form @submit.prevent="createTransfer">
        <div class="form-group">
          <label class="form-label">Счет списания</label>
          <select v-model="transferData.source_account" class="form-control" required>
            <option value="">Выберите счет</option>
            <option v-for="account in activeAccounts" :key="account.id" :value="account.id">
              {{ account.name }} ({{ formatCurrency(account.balance) }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Счет зачисления</label>
          <select v-model="transferData.destination_account" class="form-control" required>
            <option value="">Выберите счет</option>
            <option v-for="account in otherAccounts" :key="account.id" :value="account.id">
              {{ account.name }} ({{ formatCurrency(account.balance) }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Сумма перевода</label>
          <input type="number" v-model="transferData.amount" class="form-control" step="0.01" required>
        </div>

        <div class="form-group">
          <label class="form-label">Дата и время</label>
          <input type="datetime-local" v-model="transferData.timestamp" class="form-control" required>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          <i class="fas fa-exchange-alt"></i>
          {{ loading ? 'Выполняется...' : 'Выполнить перевод' }}
        </button>
      </form>
    </div>

    <!-- Transfer History -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">История переводов</h3>
      </div>

      <div class="table">
        <table>
          <thead>
            <tr>
              <th>Дата</th>
              <th>Со счета</th>
              <th>На счет</th>
              <th>Сумма</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transfer in transfers" :key="transfer.id">
              <td>{{ formatDate(transfer.timestamp) }}</td>
              <td>{{ transfer.source_account_name }}</td>
              <td>{{ transfer.destination_account_name }}</td>
              <td class="text-warning">{{ formatCurrency(transfer.amount) }}</td>
              <td>
                <button @click="editTransfer(transfer)" class="btn btn-secondary btn-sm">
                  <i class="fas fa-edit"></i>
                </button>
                <button @click="confirmDelete(transfer)" class="btn btn-danger btn-sm">
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="transfers.length === 0">
              <td colspan="5" style="text-align: center;">Нет переводов</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination">
        <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-secondary">
          <i class="fas fa-chevron-left"></i> Назад
        </button>
        <span>Страница {{ currentPage }} из {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-secondary">
          Вперед <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Edit Transfer Modal -->
    <div v-if="showEditModal" class="modal" @click.self="showEditModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Редактировать перевод</h3>
          <button class="modal-close" @click="showEditModal = false">&times;</button>
        </div>

        <form @submit.prevent="updateTransfer">
          <div class="form-group">
            <label class="form-label">Сумма перевода</label>
            <input type="number" v-model="editData.amount" class="form-control" step="0.01" required>
          </div>

          <div class="form-group">
            <label class="form-label">Дата и время</label>
            <input type="datetime-local" v-model="editData.timestamp" class="form-control" required>
          </div>

          <button type="submit" class="btn btn-primary" style="width: 100%">Обновить</button>
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
        <p>Вы уверены, что хотите удалить этот перевод?</p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
          <button @click="deleteTransfer" class="btn btn-danger">Да, удалить</button>
          <button @click="showDeleteModal = false" class="btn btn-secondary">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'TransferForm',
  setup() {
    const accounts = ref([])
    const transfers = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalCount = ref(0)
    const loading = ref(false)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const editingTransfer = ref(null)
    const transferToDelete = ref(null)
    const transferData = ref({
      source_account: '',
      destination_account: '',
      amount: '',
      timestamp: new Date().toISOString().slice(0, 16)
    })
    const editData = ref({
      amount: '',
      timestamp: ''
    })

    const activeAccounts = computed(() => {
      return accounts.value.filter(acc => acc.is_active)
    })

    const otherAccounts = computed(() => {
      if (!transferData.value.source_account) return activeAccounts.value
      return activeAccounts.value.filter(acc => acc.id !== transferData.value.source_account)
    })

    const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

    const loadAccounts = async () => {
      try {
        const data = await apiService.getAccounts(1, 100)
        accounts.value = data.results[0]?.accounts || []
      } catch (error) {
        console.error('Error loading accounts:', error)
      }
    }

    const loadTransfers = async () => {
      try {
        const data = await apiService.getTransferHistory(currentPage.value, pageSize.value)
        transfers.value = data.results
        totalCount.value = data.count
      } catch (error) {
        console.error('Error loading transfers:', error)
      }
    }

    const createTransfer = async () => {
      if (!transferData.value.source_account || !transferData.value.destination_account) {
        alert('Выберите счета для перевода')
        return
      }
      
      loading.value = true
      try {
        await apiService.createTransfer(
          transferData.value.source_account,
          transferData.value.destination_account,
          transferData.value.amount,
          new Date(transferData.value.timestamp).toISOString()
        )
        transferData.value = {
          source_account: '',
          destination_account: '',
          amount: '',
          timestamp: new Date().toISOString().slice(0, 16)
        }
        await loadAccounts()
        await loadTransfers()
      } catch (error) {
        console.error('Error creating transfer:', error)
        alert('Ошибка при создании перевода')
      } finally {
        loading.value = false
      }
    }

    const editTransfer = (transfer) => {
      editingTransfer.value = transfer
      editData.value = {
        amount: transfer.amount,
        timestamp: transfer.timestamp.slice(0, 16)
      }
      showEditModal.value = true
    }

    const updateTransfer = async () => {
      try {
        await apiService.updateTransfer(editingTransfer.value.id, {
          source_account: editingTransfer.value.source_account_id,
          destination_account: editingTransfer.value.destination_account_id,
          amount: editData.value.amount,
          timestamp: new Date(editData.value.timestamp).toISOString()
        })
        showEditModal.value = false
        await loadAccounts()
        await loadTransfers()
      } catch (error) {
        console.error('Error updating transfer:', error)
      }
    }

    const confirmDelete = (transfer) => {
      transferToDelete.value = transfer
      showDeleteModal.value = true
    }

    const deleteTransfer = async () => {
      try {
        await apiService.deleteTransfer(transferToDelete.value.id)
        showDeleteModal.value = false
        await loadAccounts()
        await loadTransfers()
      } catch (error) {
        console.error('Error deleting transfer:', error)
      }
    }

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        loadTransfers()
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        loadTransfers()
      }
    }

    const formatCurrency = (value) => {
      return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(value)
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('ru-RU')
    }

    onMounted(() => {
      loadAccounts()
      loadTransfers()
    })

    return {
      accounts,
      transfers,
      currentPage,
      totalPages,
      loading,
      showEditModal,
      showDeleteModal,
      editingTransfer,
      transferToDelete,
      transferData,
      editData,
      activeAccounts,
      otherAccounts,
      createTransfer,
      editTransfer,
      updateTransfer,
      confirmDelete,
      deleteTransfer,
      prevPage,
      nextPage,
      formatCurrency,
      formatDate
    }
  }
}
</script>

<style scoped>
.text-warning {
  color: var(--warning-color);
  font-weight: 600;
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
</style>
