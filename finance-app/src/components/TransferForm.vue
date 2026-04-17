<template>
  <div>
    <h1 style="margin-bottom: 2rem; font-size: clamp(1.5rem, 5vw, 2rem);">
      Переводы между счетами
    </h1>

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

      <!-- Desktop Table -->
      <div class="table desktop-table">
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
              <td data-label="Дата">{{ formatDate(transfer.timestamp) }}</td>
              <td data-label="Со счета">{{ transfer.source_account_name }}</td>
              <td data-label="На счет">{{ transfer.destination_account_name }}</td>
              <td data-label="Сумма" class="text-warning">{{ formatCurrency(transfer.amount) }}</td>
              <td data-label="Действия">
                <div class="action-buttons">
                  <button @click="editTransfer(transfer)" class="btn btn-secondary btn-sm">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button @click="confirmDelete(transfer)" class="btn btn-danger btn-sm">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="transfers.length === 0">
              <td colspan="5" style="text-align: center;">Нет переводов</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Cards -->
      <div class="mobile-cards">
        <div v-for="transfer in transfers" :key="transfer.id" class="transfer-card">
          <div class="transfer-card-header">
            <span class="transfer-amount">{{ formatCurrency(transfer.amount) }}</span>
            <div class="transfer-actions">
              <button @click="editTransfer(transfer)" class="btn btn-secondary btn-sm">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="confirmDelete(transfer)" class="btn btn-danger btn-sm">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          <div class="transfer-card-body">
            <div class="transfer-info">
              <span class="info-label">Дата:</span>
              <span class="info-value">{{ formatDate(transfer.timestamp) }}</span>
            </div>
            <div class="transfer-info">
              <span class="info-label">Со счета:</span>
              <span class="info-value">{{ transfer.source_account_name }}</span>
            </div>
            <div class="transfer-info">
              <span class="info-label">На счет:</span>
              <span class="info-value">{{ transfer.destination_account_name }}</span>
            </div>
          </div>
        </div>
        <div v-if="transfers.length === 0" class="empty-state">
          Нет переводов
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination">
        <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-secondary">
          <i class="fas fa-chevron-left"></i> <span class="btn-text">Назад</span>
        </button>
        <span class="page-info">Страница {{ currentPage }} из {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-secondary">
          <span class="btn-text">Вперед</span> <i class="fas fa-chevron-right"></i>
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
        <div class="modal-buttons">
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
/* Адаптивные стили */
.text-warning {
  color: var(--warning-color);
  font-weight: 600;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
  flex-wrap: wrap;
}

/* Скрываем мобильные карточки на десктопе */
.mobile-cards {
  display: none;
}

/* Стили для мобильных устройств */
@media (max-width: 768px) {
  /* Скрываем таблицу на мобильных */
  .desktop-table {
    display: none;
  }
  
  /* Показываем карточки */
  .mobile-cards {
    display: block;
  }
  
  /* Стили для карточек переводов */
  .transfer-card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid var(--light-color);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  .transfer-card:active {
    transform: scale(0.99);
  }
  
  .transfer-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .transfer-amount {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--warning-color);
  }
  
  .transfer-actions {
    display: flex;
    gap: 0.5rem;
  }
  
  .transfer-card-body {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .transfer-info {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 0.875rem;
    line-height: 1.4;
  }
  
  .info-label {
    font-weight: 600;
    color: #6b7280;
    min-width: 70px;
  }
  
  .info-value {
    color: #1f2937;
    text-align: right;
    word-break: break-word;
    flex: 1;
  }
  
  .empty-state {
    text-align: center;
    padding: 2rem;
    color: #6b7280;
    background: #f9fafb;
    border-radius: 12px;
  }
  
  /* Улучшаем отступы для формы */
  .form-group {
    margin-bottom: 1rem;
  }
  
  .form-control {
    font-size: 16px !important; /* Предотвращает зумирование на iOS */
    padding: 12px;
  }
  
  /* Увеличиваем кнопки для удобства нажатия */
  .btn {
    padding: 12px 16px;
    font-size: 1rem;
    min-height: 44px; /* Минимальный размер для touch-цели */
  }
  
  .btn-sm {
    padding: 8px 12px;
    min-height: 36px;
  }
  
  /* Улучшаем пагинацию */
  .btn-text {
    display: inline-block;
  }
  
  .page-info {
    font-size: 0.875rem;
    padding: 0 0.5rem;
  }
  
  /* Модальные окна на мобильных */
  .modal-content {
    width: 95%;
    margin: 1rem;
    max-height: 90vh;
    overflow-y: auto;
  }
  
  .modal-buttons {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
    flex-wrap: wrap;
  }
  
  .modal-buttons .btn {
    flex: 1;
    min-width: 120px;
  }
  
  /* Улучшаем select на мобильных */
  select.form-control {
    background-size: 12px;
    padding-right: 32px;
  }
}

/* Планшеты */
@media (min-width: 769px) and (max-width: 1024px) {
  .desktop-table {
    overflow-x: auto;
  }
  
  .desktop-table table {
    min-width: 600px;
  }
  
  .action-buttons {
    display: flex;
    gap: 0.5rem;
  }
}

/* Очень маленькие экраны */
@media (max-width: 480px) {
  .pagination {
    gap: 0.5rem;
  }
  
  .btn-text {
    display: none; /* Скрываем текст, оставляем только иконки на очень маленьких экранах */
  }
  
  .pagination .btn {
    padding: 10px 12px;
  }
  
  .transfer-info {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .info-label {
    min-width: auto;
  }
  
  .info-value {
    text-align: left;
  }
}

/* Альбомная ориентация на мобильных */
@media (max-width: 768px) and (orientation: landscape) {
  .transfer-card {
    padding: 0.75rem;
  }
  
  .transfer-card-header {
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .transfer-info {
    font-size: 0.8rem;
  }
}

/* Стили для кнопок действий на десктопе */
.action-buttons {
  display: flex;
  gap: 0.5rem;
}

/* Улучшенные стили для полей ввода */
.form-control {
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Стили для disabled состояний */
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>