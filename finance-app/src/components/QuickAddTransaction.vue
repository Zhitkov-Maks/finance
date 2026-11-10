<template>
  <div>
    <!-- Floating Action Button -->
    <button
      class="fab-add-transaction"
      :title="'Добавить транзакцию'"
      aria-label="Добавить транзакцию"
      @click="openModal"
    >
      <i class="fas fa-plus"></i>
    </button>

    <!-- Модальное окно -->
    <div v-if="showModal" class="modal modal-bottom-sheet" @click.self="closeModal">
      <div class="modal-content">
        <div class="sheet-handle"></div>
        <div class="modal-header">
          <h3>Добавить транзакцию</h3>
          <button class="modal-close" @click="closeModal" aria-label="Закрыть">
            &times;
          </button>
        </div>

        <!-- Загрузка -->
        <div v-if="loadingData" class="form-loading">
          <i class="fas fa-spinner fa-spin"></i>
          <span>Загрузка данных...</span>
        </div>

        <!-- Ошибка загрузки -->
        <div v-else-if="loadError" class="form-load-error">
          <div class="modal-body">
            <div class="alert alert-danger">
              <i class="fas fa-exclamation-triangle"></i>
              <span>{{ loadError }}</span>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">Отмена</button>
            <button type="button" @click="loadData" class="btn btn-primary">
              <i class="fas fa-redo"></i> Повторить
            </button>
          </div>
        </div>

        <!-- Форма -->
        <form v-else class="modal-form" @submit.prevent="submit">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label required">Тип</label>
              <select v-model="form.type" class="form-control" required @change="onTypeChange">
                <option value="income">Доход</option>
                <option value="expense">Расход</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label required">Сумма</label>
              <input
                v-model="form.amount"
                type="number"
                class="form-control"
                step="0.01"
                min="0.01"
                required
                placeholder="0.00"
              >
            </div>

            <div class="form-group">
              <label class="form-label">Категория</label>
              <select v-model="form.category" class="form-control">
                <option value="">Без категории</option>
                <option
                  v-for="cat in availableCategories"
                  :key="cat.id"
                  :value="cat.id"
                >
                  {{ '—'.repeat(cat.level) }} {{ cat.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label required">Счет</label>
              <select v-model="form.account" class="form-control" required>
                <option value="">Выберите счет</option>
                <option
                  v-for="acc in accounts"
                  :key="acc.id"
                  :value="acc.id"
                >
                  {{ acc.name }} ({{ formatCurrency(acc.balance) }})
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Комментарий</label>
              <textarea
                v-model="form.comment"
                class="form-control"
                rows="2"
                placeholder="Необязательно"
              ></textarea>
            </div>

            <div v-if="error" class="alert alert-danger">
              <i class="fas fa-exclamation-circle"></i>
              <span>{{ error }}</span>
            </div>
          </div>

          <div class="modal-footer">
            <button
              type="button"
              @click="closeModal"
              class="btn btn-secondary"
              :disabled="submitting"
            >
              Отмена
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="submitting"
            >
              <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
              {{ submitting ? 'Добавление...' : 'Добавить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import apiService from '../services/api.js'

const defaultForm = () => ({
  type: 'expense',
  amount: '',
  category: '',
  account: '',
  comment: ''
})

export default {
  name: 'QuickAddTransaction',
  setup() {
    const showModal = ref(false)
    const submitting = ref(false)
    const loadingData = ref(false)
    const error = ref('')
    const loadError = ref('')

    const accounts = ref([])
    const incomeCategories = ref([])
    const expenseCategories = ref([])

    const form = ref(defaultForm())

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

    const availableCategories = computed(() => {
      const list = form.value.type === 'income'
        ? incomeCategories.value
        : expenseCategories.value
      return flattenCategories(list)
    })

    const formatCurrency = (value) => {
      if (value === null || value === undefined || isNaN(value)) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB'
      }).format(value)
    }

    const onTypeChange = () => {
      form.value.category = ''
    }

    const loadData = async () => {
      loadingData.value = true
      loadError.value = ''
      try {
        const [accountsData, incomeData, expenseData] = await Promise.all([
          apiService.getAccounts(1, 100),
          apiService.getCategories('income', 1, 100, true),
          apiService.getCategories('expense', 1, 100, true),
        ])
        accounts.value = accountsData.results?.[0]?.accounts || []
        incomeCategories.value = incomeData.results || []
        expenseCategories.value = expenseData.results || []
      } catch (e) {
        console.error('QuickAdd: failed to load data', e)
        loadError.value = 'Не удалось загрузить счета и категории. Проверьте соединение.'
      } finally {
        loadingData.value = false
      }
    }

    const openModal = async () => {
      form.value = defaultForm()
      error.value = ''
      loadError.value = ''
      loadingData.value = true
      showModal.value = true
      await loadData()
    }

    const closeModal = () => {
      if (submitting.value) return
      showModal.value = false
    }

    const submit = async () => {
      error.value = ''

      if (!form.value.account) {
        error.value = 'Выберите счёт'
        return
      }
      const amount = parseFloat(form.value.amount)
      if (!Number.isFinite(amount) || amount <= 0) {
        error.value = 'Введите корректную сумму'
        return
      }

      submitting.value = true
      try {
        await apiService.createTransaction(form.value.type, {
          amount: form.value.amount,
          create_at: new Date().toISOString(),
          type_transaction: form.value.type,
          category: form.value.category ? parseInt(form.value.category, 10) : null,
          account: parseInt(form.value.account, 10),
          comment: form.value.comment
        })

        window.dispatchEvent(new CustomEvent('transaction-created'))

        showModal.value = false
      } catch (e) {
        console.error('QuickAdd: failed to create transaction', e)
        if (e.response?.data) {
          const firstError = Object.values(e.response.data)[0]
          error.value = Array.isArray(firstError) ? firstError[0] : firstError
        } else {
          error.value = 'Не удалось создать транзакцию. Попробуйте ещё раз.'
        }
      } finally {
        submitting.value = false
      }
    }

    return {
      showModal,
      submitting,
      loadingData,
      error,
      loadError,
      accounts,
      form,
      availableCategories,
      formatCurrency,
      openModal,
      closeModal,
      loadData,
      onTypeChange,
      submit
    }
  }
}
</script>

<style scoped>
/* ============================================================
   FAB — плавающая кнопка
   ============================================================ */
.fab-add-transaction {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #ffffff;
  font-size: 1.5rem;
  cursor: pointer;
  z-index: 90;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 6px 20px rgba(16, 185, 129, 0.45),
    0 2px 6px rgba(16, 185, 129, 0.3);
  transition:
    transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.25s ease;
}

.fab-add-transaction:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow:
    0 10px 28px rgba(16, 185, 129, 0.55),
    0 4px 10px rgba(16, 185, 129, 0.35);
}

.fab-add-transaction:active {
  transform: translateY(-1px) scale(1.02);
  transition-duration: 0.1s;
}

.fab-add-transaction i {
  transition: transform 0.25s ease;
}

.fab-add-transaction:hover i {
  transform: rotate(90deg);
}

@media (max-width: 768px) {
  .fab-add-transaction {
    bottom: calc(1.25rem + env(safe-area-inset-bottom));
    right: 1.25rem;
    width: 56px;
    height: 56px;
    font-size: 1.35rem;
  }
}

@media (max-width: 480px) {
  .fab-add-transaction {
    bottom: calc(1rem + env(safe-area-inset-bottom));
    right: 1rem;
    width: 52px;
    height: 52px;
    font-size: 1.25rem;
  }
}

/* ============================================================
   MODAL: base layout
   ============================================================ */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 0;
  overflow: hidden;
}

.modal-content {
  background: var(--white);
  border-radius: var(--radius);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
  animation: fabModalIn 0.2s ease-out;
}

@keyframes fabModalIn {
  from { opacity: 0; transform: translateY(10px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--light-color);
  flex-shrink: 0;
  min-height: 56px;
  gap: 0.5rem;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--dark-color);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.75rem;
  line-height: 1;
  cursor: pointer;
  color: var(--gray-color);
  padding: 0 0.25rem;
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
  flex-shrink: 0;
  transition: background-color 0.15s ease;
}

.modal-close:hover {
  color: var(--dark-color);
  background: var(--light-color);
}

.modal-body {
  padding: 0.75rem 1rem;
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  overscroll-behavior: contain;
}

.modal-footer {
  padding: 0.75rem 1rem;
  padding-bottom: calc(0.75rem + env(safe-area-inset-bottom));
  border-top: 1px solid var(--light-color);
  background: var(--white);
  display: flex;
  gap: 0.5rem;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
}

.modal-form {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.sheet-handle { display: none; }

@keyframes slideUp {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}

/* ============================================================
   Load states
   ============================================================ */
.form-loading,
.form-load-error {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.form-loading {
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem 1.5rem;
  color: var(--gray-color);
  font-size: 0.9rem;
}

.form-loading i {
  font-size: 2rem;
  color: var(--primary-color);
}

/* ============================================================
   Формы
   ============================================================ */
.form-group { margin-bottom: 1rem; }

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--dark-color);
}

.form-label.required::after {
  content: " *";
  color: var(--danger-color);
}

.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--gray-color);
  border-radius: var(--radius);
  font-size: 0.875rem;
  background: var(--white);
  color: var(--dark-color);
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
}

textarea.form-control {
  resize: vertical;
  min-height: 60px;
}

/* ============================================================
   Кнопки
   ============================================================ */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: var(--primary-color);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: #4338ca;
}

.btn-secondary {
  background: #6b7280;
  color: #ffffff;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ============================================================
   Алерты
   ============================================================ */
.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  font-size: 0.875rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  line-height: 1.4;
}

.alert i {
  margin-top: 0.15rem;
  flex-shrink: 0;
}

.alert-danger {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.modal-body .alert {
  margin-top: 0.25rem;
}

:global(:root[data-theme="dark"]) .alert-danger {
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.3);
}

/* ============================================================
   BOTTOM-SHEET на мобильных
   ============================================================ */
@media (max-width: 768px) {
  .modal.modal-bottom-sheet {
    align-items: flex-end;
    justify-content: flex-start;
  }

  .modal.modal-bottom-sheet .modal-content {
    width: 100%;
    max-width: 100%;
    margin: 0;
    border-radius: 16px 16px 0 0;
    max-height: 92dvh;
    animation: slideUp 0.25s ease;
    padding-bottom: env(safe-area-inset-bottom);
  }

  .modal.modal-bottom-sheet .sheet-handle {
    display: block;
    width: 40px;
    height: 4px;
    background: #cbd5e1;
    border-radius: 2px;
    margin: 8px auto 2px;
    flex-shrink: 0;
  }

  /* Компактнее формы */
  .modal-body .form-group {
    margin-bottom: 0.55rem;
  }

  .modal-body .form-label {
    font-size: 0.8rem;
    margin-bottom: 0.3rem;
  }

  .modal-body .form-control {
    min-height: 42px;
    padding: 0.5rem 0.7rem;
    font-size: 16px; /* iOS не зумит */
  }

  .modal-footer {
    justify-content: stretch;
  }

  .modal-footer .btn {
    flex: 1;
    min-height: 44px;
  }
}

@media (max-width: 480px) {
  .modal-footer {
    flex-direction: column;
  }

  .modal-footer .btn {
    width: 100%;
  }
}
</style>