<template>
  <div>
    <h1 style="margin-bottom: 2rem; font-size: clamp(1.5rem, 5vw, 2rem);">
      Переводы
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
      <div class="desktop-table">
        <table class="table">
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

      <!-- Mobile Cards with Expand -->
      <div class="mobile-cards">
        <div v-for="transfer in transfers" :key="transfer.id" class="transfer-card">
          <!-- Компактный заголовок карточки -->
          <div class="transfer-compact" @click="toggleExpand(transfer.id)">
            <div class="compact-left">
              <div class="transfer-date-compact">{{ formatShortDate(transfer.timestamp) }}</div>
              <div class="transfer-amount-compact text-warning">
                {{ formatCurrency(transfer.amount) }}
              </div>
            </div>
            <div class="compact-right">
              <button class="expand-icon" @click.stop="toggleExpand(transfer.id)">
                <i :class="expandedTransfers.has(transfer.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>
          </div>

          <!-- Раскрывающаяся детальная информация -->
          <div v-if="expandedTransfers.has(transfer.id)" class="transfer-expanded">
            <div class="transfer-details">
              <div class="detail-item">
                <span class="detail-label">
                  <i class="fas fa-calendar"></i> Полная дата:
                </span>
                <span class="detail-value">{{ formatDate(transfer.timestamp) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">
                  <i class="fas fa-arrow-right"></i> Со счета:
                </span>
                <span class="detail-value">{{ transfer.source_account_name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">
                  <i class="fas fa-arrow-left"></i> На счет:
                </span>
                <span class="detail-value">{{ transfer.destination_account_name }}</span>
              </div>
            </div>
            <div class="transfer-actions-expanded">
              <button @click="editTransfer(transfer)" class="btn btn-sm btn-info">
                <i class="fas fa-edit"></i> Редактировать
              </button>
              <button @click="confirmDelete(transfer)" class="btn btn-sm btn-danger">
                <i class="fas fa-trash"></i> Удалить
              </button>
            </div>
          </div>
        </div>
        <div v-if="transfers.length === 0" class="empty-state">
          <i class="fas fa-exchange-alt"></i>
          <p>Нет переводов</p>
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
    <div v-if="showEditModal" class="modal" @click.self="closeEditModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Редактировать перевод</h3>
          <button class="modal-close" @click="closeEditModal">&times;</button>
        </div>

        <form @submit.prevent="updateTransfer">
          <div class="form-group">
            <label class="form-label">Счет списания</label>
            <select v-model="editData.source_account" class="form-control" required>
              <option value="">Выберите счет</option>
              <option v-for="account in activeAccounts" :key="account.id" :value="account.id">
                {{ account.name }} ({{ formatCurrency(account.balance) }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Счет зачисления</label>
            <select v-model="editData.destination_account" class="form-control" required>
              <option value="">Выберите счет</option>
              <option v-for="account in editOtherAccounts" :key="account.id" :value="account.id">
                {{ account.name }} ({{ formatCurrency(account.balance) }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Сумма перевода</label>
            <input type="number" v-model="editData.amount" class="form-control" step="0.01" required>
          </div>

          <div class="form-group">
            <label class="form-label">Дата и время</label>
            <input type="datetime-local" v-model="editData.timestamp" class="form-control" required>
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeEditModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Обновить</button>
          </div>
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
        <p class="text-muted">Сумма: {{ formatCurrency(transferToDelete?.amount) }}</p>
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-secondary">Отмена</button>
          <button @click="deleteTransfer" class="btn btn-danger">Да, удалить</button>
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
    const expandedTransfers = ref(new Set())

    const transferData = ref({
      source_account: '',
      destination_account: '',
      amount: '',
      timestamp: new Date().toISOString().slice(0, 16)
    })

    const editData = ref({
      source_account: '',
      destination_account: '',
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

    const editOtherAccounts = computed(() => {
      if (!editData.value.source_account) return activeAccounts.value
      return activeAccounts.value.filter(acc => acc.id !== editData.value.source_account)
    })

    const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

    const toggleExpand = (transferId) => {
      if (expandedTransfers.value.has(transferId)) {
        expandedTransfers.value.delete(transferId)
      } else {
        expandedTransfers.value.add(transferId)
      }
      expandedTransfers.value = new Set(expandedTransfers.value)
    }

    const loadAccounts = async () => {
      try {
        const response = await apiService.getAccounts(1, 100)
        console.log('Загружены счета:', response)

        let accountsData = []
        if (response.results && response.results.length > 0 && response.results[0].accounts) {
          accountsData = response.results[0].accounts
        } else if (response.results && Array.isArray(response.results)) {
          accountsData = response.results
        } else if (response.accounts && Array.isArray(response.accounts)) {
          accountsData = response.accounts
        } else if (Array.isArray(response)) {
          accountsData = response
        }

        accounts.value = accountsData
        console.log(`Загружено ${accounts.value.length} счетов`)
      } catch (error) {
        console.error('Error loading accounts:', error)
        accounts.value = []
      }
    }

    const loadTransfers = async () => {
      try {
        const data = await apiService.getTransferHistory(currentPage.value, pageSize.value)
        console.log('Загружены переводы:', data)
        transfers.value = data.results || []
        totalCount.value = data.count || 0
      } catch (error) {
        console.error('Error loading transfers:', error)
        transfers.value = []
        totalCount.value = 0
      }
    }

    const createTransfer = async () => {
      if (!transferData.value.source_account || !transferData.value.destination_account) {
        alert('Выберите счета для перевода')
        return
      }

      if (transferData.value.source_account === transferData.value.destination_account) {
        alert('Счета списания и зачисления должны быть разными')
        return
      }

      loading.value = true
      try {
        await apiService.createTransfer(
          transferData.value.source_account,
          transferData.value.destination_account,
          parseFloat(transferData.value.amount),
          new Date(transferData.value.timestamp).toISOString()
        )

        // Сброс формы
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
        alert('Ошибка при создании перевода: ' + (error.message || 'Неизвестная ошибка'))
      } finally {
        loading.value = false
      }
    }

    const editTransfer = async (transfer) => {
      editingTransfer.value = transfer

      // Пытаемся найти ID счетов по их названиям
      let sourceAccountId = null
      let destinationAccountId = null

      // Ищем ID счета по имени
      if (transfer.source_account_name) {
        const foundSource = accounts.value.find(acc => acc.name === transfer.source_account_name)
        if (foundSource) {
          sourceAccountId = foundSource.id
        } else {
          console.warn('Счет списания не найден:', transfer.source_account_name)
        }
      }

      if (transfer.destination_account_name) {
        const foundDest = accounts.value.find(acc => acc.name === transfer.destination_account_name)
        if (foundDest) {
          destinationAccountId = foundDest.id
        } else {
          console.warn('Счет зачисления не найден:', transfer.destination_account_name)
        }
      }

      editData.value = {
        source_account: sourceAccountId || '',
        destination_account: destinationAccountId || '',
        amount: transfer.amount,
        timestamp: transfer.timestamp ? transfer.timestamp.slice(0, 16) : new Date().toISOString().slice(0, 16)
      }

      showEditModal.value = true
    }

    const updateTransfer = async () => {
      if (!editData.value.source_account || !editData.value.destination_account) {
        alert('Выберите счета для перевода')
        return
      }

      if (editData.value.source_account === editData.value.destination_account) {
        alert('Счета списания и зачисления должны быть разными')
        return
      }

      try {
        await apiService.updateTransfer(editingTransfer.value.id, {
          source_account: parseInt(editData.value.source_account),
          destination_account: parseInt(editData.value.destination_account),
          amount: parseFloat(editData.value.amount),
          timestamp: new Date(editData.value.timestamp).toISOString()
        })

        closeEditModal()
        await loadAccounts()
        await loadTransfers()
      } catch (error) {
        console.error('Error updating transfer:', error)
        alert('Ошибка при обновлении перевода: ' + (error.message || 'Неизвестная ошибка'))
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

        // Если удалили последний элемент на странице, переходим на предыдущую
        if (transfers.value.length === 1 && currentPage.value > 1) {
          currentPage.value--
        }

        await loadAccounts()
        await loadTransfers()
      } catch (error) {
        console.error('Error deleting transfer:', error)
        alert('Ошибка при удалении перевода')
      }
    }

    const closeEditModal = () => {
      showEditModal.value = false
      editingTransfer.value = null
      editData.value = {
        source_account: '',
        destination_account: '',
        amount: '',
        timestamp: ''
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
      if (!value && value !== 0) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 2,
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

    const formatShortDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(async () => {
      await loadAccounts()
      await loadTransfers()
    })

    return {
      transfers,
      currentPage,
      totalPages,
      totalCount,
      loading,
      showEditModal,
      showDeleteModal,
      editingTransfer,
      transferToDelete,
      transferData,
      editData,
      activeAccounts,
      otherAccounts,
      editOtherAccounts,
      expandedTransfers,
      toggleExpand,
      createTransfer,
      editTransfer,
      updateTransfer,
      confirmDelete,
      deleteTransfer,
      closeEditModal,
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

/* Десктопная таблица - только для больших экранов */
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

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

/* Мобильные карточки - для планшетов и телефонов */
.mobile-cards {
  display: none;
}

.transfer-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  margin-bottom: 0.5rem;
  overflow: hidden;
  transition: all 0.3s ease;
}

/* Компактный заголовок */
.transfer-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.transfer-compact:hover {
  background-color: #f9fafb;
}

.compact-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.transfer-date-compact {
  font-size: 0.75rem;
  color: var(--gray-color);
  min-width: 70px;
}

.transfer-amount-compact {
  font-size: 1rem;
  font-weight: 700;
}

.compact-right {
  display: flex;
  align-items: center;
}

.expand-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: var(--gray-color);
  transition: color 0.3s;
  width: 28px;
  height: 28px;
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
.transfer-expanded {
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

.transfer-details {
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

.transfer-actions-expanded {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.transfer-actions-expanded .btn-sm {
  padding: 0.5rem 1rem;
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

/* Модальные окна */
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
}

/* Адаптивные стили */
/* Планшеты в вертикальной ориентации и телефоны (ширина до 1024px) */
@media (max-width: 1024px) {
  .desktop-table {
    display: none;
  }

  .mobile-cards {
    display: block;
  }

  .compact-left {
    gap: 0.75rem;
  }

  .transfer-date-compact {
    min-width: 80px;
    font-size: 0.8rem;
  }

  .transfer-amount-compact {
    font-size: 1rem;
  }
}

/* Планшеты в горизонтальной ориентации и маленькие ноутбуки (1025px - 1280px) */
@media (min-width: 1025px) and (max-width: 1280px) {
  /* Для горизонтальных планшетов все еще показываем таблицу */
  .desktop-table {
    display: block;
  }

  .mobile-cards {
    display: none;
  }

  .table th,
  .table td {
    padding: 0.5rem;
    font-size: 0.875rem;
  }

  .btn-sm {
    padding: 0.25rem 0.5rem;
  }
}

/* Большие экраны (1281px и выше) */
@media (min-width: 1281px) {
  .desktop-table {
    display: block;
  }

  .mobile-cards {
    display: none;
  }
}

/* Телефоны (до 768px) */
@media (max-width: 768px) {
  h1 {
    text-align: center;
  }

  .compact-left {
    gap: 0.5rem;
  }

  .transfer-date-compact {
    min-width: 60px;
    font-size: 0.7rem;
  }

  .transfer-amount-compact {
    font-size: 0.9rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-control {
    font-size: 16px !important;
    padding: 12px;
  }

  .btn {
    padding: 12px 16px;
    font-size: 1rem;
    min-height: 44px;
  }

  .btn-sm {
    padding: 8px 12px;
    min-height: 36px;
  }

  .btn-text {
    display: inline-block;
  }

  .page-info {
    font-size: 0.875rem;
    padding: 0 0.5rem;
  }

  .modal-content {
    width: 95%;
    margin: 1rem;
    max-height: 90vh;
    overflow-y: auto;
  }
}

/* Очень маленькие телефоны (до 480px) */
@media (max-width: 480px) {
  .pagination {
    gap: 0.5rem;
  }

  .btn-text {
    display: none;
  }

  .pagination .btn {
    padding: 10px 12px;
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

  .transfer-actions-expanded {
    flex-direction: column;
  }

  .transfer-actions-expanded .btn-sm {
    width: 100%;
    margin: 0;
  }

  .modal-footer {
    flex-direction: column;
    gap: 0.5rem;
  }

  .modal-footer .btn {
    width: 100%;
  }
}

/* Планшеты в альбомной ориентации (специальные стили) */
@media (min-width: 769px) and (max-width: 1024px) and (orientation: landscape) {
  /* Для горизонтальных планшетов можно оставить таблицу */
  .desktop-table {
    display: block;
  }

  .mobile-cards {
    display: none;
  }

  .desktop-table {
    overflow-x: auto;
  }

  .table {
    min-width: 600px;
  }
}

/* Планшеты в портретной ориентации (вертикальной) */
@media (min-width: 769px) and (max-width: 1024px) and (orientation: portrait) {
  /* Для вертикальных планшетов показываем карточки */
  .desktop-table {
    display: none;
  }

  .mobile-cards {
    display: block;
  }

  .transfer-card {
    margin-bottom: 0.75rem;
  }

  .transfer-date-compact {
    min-width: 90px;
    font-size: 0.85rem;
  }

  .transfer-amount-compact {
    font-size: 1.1rem;
  }

  .detail-item {
    font-size: 0.95rem;
  }
}

/* Специальные стили для телефонов в альбомной ориентации */
@media (max-width: 768px) and (orientation: landscape) {
  .transfer-card {
    margin-bottom: 0.5rem;
  }

  .transfer-details {
    gap: 0.5rem;
  }

  .detail-item {
    font-size: 0.8rem;
  }

  .transfer-actions-expanded .btn-sm {
    padding: 0.4rem 0.8rem;
  }
}

/* Фокус и интерактивные элементы */
.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Улучшенные touch-цели для мобильных */
@media (max-width: 768px) {
  button,
  .btn,
  .expand-icon,
  [role="button"] {
    cursor: pointer;
    touch-action: manipulation;
  }

  .expand-icon {
    min-width: 44px;
    min-height: 44px;
  }
}
</style >
