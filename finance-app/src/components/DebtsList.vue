<template>
  <div>
    <div class="page-header">
      <h1>Управление долгами</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Создать долг
      </button>
    </div>

    <!-- ============================================================ -->
    <!-- БЛОК: ПЛАН ПОГАШЕНИЯ КРЕДИТОК                                 -->
    <!-- ============================================================ -->
    <div v-if="creditCards.length > 0" class="card debt-plan-card hoverable-card">
      <div class="card-header">
        <h3 class="card-title">💳 План погашения кредиток</h3>
        <span class="badge badge-danger">Общий долг: {{ formatCurrency(totalCreditDebt) }}</span>
      </div>

      <div class="plan-body">
        <!-- ЛЕВАЯ КОЛОНКА: Вводы + План на месяц -->
        <div class="plan-inputs">
          <div class="form-group">
            <label class="form-label">Сколько вы можете выделять в месяц?</label>
            <div class="input-with-currency">
              <input
                type="number"
                v-model.number="monthlyPayment"
                class="form-control"
                step="1000"
                min="1000"
                placeholder="Например: 15000"
              >
              <span class="currency-symbol">₽</span>
            </div>
            <small v-if="simulationError" class="text-danger mt-1 d-block">
              ⚠️ {{ simulationError }}
            </small>
          </div>

          <div class="form-group">
            <label class="form-label">Стратегия погашения</label>
            <div class="strategy-toggle">
              <button
                class="strategy-btn"
                :class="{ active: strategy === 'avalanche' }"
                @click="strategy = 'avalanche'"
              >
                🚀 Лавина
              </button>
              <button
                class="strategy-btn"
                :class="{ active: strategy === 'snowball' }"
                @click="strategy = 'snowball'"
              >
                ⛄ Снежный ком
              </button>
            </div>
            <p class="strategy-description" aria-live="polite">
              <i class="fas fa-info-circle"></i>
              <span v-if="strategy === 'avalanche'">
                <strong>Лавина</strong> — сначала гасим долг с <em>самой высокой ставкой</em>.
                Минимальная переплата по процентам.
              </span>
              <span v-else>
                <strong>Снежный ком</strong> — сначала закрываем <em>самый маленький долг</em>.
                Быстрые победы мотивируют не бросать план.
              </span>
            </p>
          </div>

          <!-- ПЛАН НА МЕСЯЦ (перенесен сюда) -->
          <div v-if="actionablePlan" class="action-plan" :class="`action-plan-${actionablePlan.type}`">
            <template v-if="actionablePlan.type === 'single'">
              <div class="action-plan-title">
                <i class="fas fa-check-circle text-success"></i> Отличные новости!
              </div>
              <div class="action-plan-text">{{ actionablePlan.message }}</div>
            </template>

            <template v-else-if="actionablePlan.type === 'warning'">
              <div class="action-plan-title">
                <i class="fas fa-exclamation-triangle text-danger"></i> Внимание
              </div>
              <div class="action-plan-text">{{ actionablePlan.message }}</div>
            </template>

            <template v-else-if="actionablePlan.type === 'split'">
              <div class="action-plan-title">
                <i class="fas fa-bullseye text-primary"></i> План на этот месяц
              </div>
              <div class="action-list">
                <div v-for="part in actionablePlan.parts" :key="part.card.id" class="action-item">
                  <div class="action-item-left">
                    <span class="action-tag" :class="part.isTarget ? 'tag-target' : 'tag-min'">
                      {{ part.isTarget ? 'Сверх мин.' : 'Минимум' }}
                    </span>
                    <span class="action-item-name">{{ part.card.name }}</span>
                    <span v-if="!part.isTarget" class="text-muted" style="font-size: 0.75rem; margin-left: 4px;">
                      ({{ part.card.minPaymentPercent }}%)
                    </span>
                  </div>
                  <div class="action-item-amount">{{ formatCurrency(part.amount) }}</div>
                </div>
              </div>
            </template>
          </div>

          <!-- ИНФО-БЛОК (заполняет пустоту) -->
          <div class="info-tips" v-if="simulationResult && !simulationError">
            <div class="info-tips-title"><i class="fas fa-lightbulb text-warning"></i> Как это работает?</div>
            <p>Сначала программа распределяет деньги на <strong>минимальные платежи</strong>, чтобы не было просрочек и штрафов. Оставшаяся сумма идет на досрочное погашение карты-цели.</p>
          </div>
        </div>

        <!-- ПРАВАЯ КОЛОНКА: Сводка, Список, График -->
        <div class="plan-results" v-if="simulationResult">
          <div class="summary-metrics">
            <div class="summary-metric">
              <div class="summary-value text-success">{{ formatDuration(simulationSummary.months) }}</div>
              <div class="summary-label">до погашения</div>
            </div>
            <div class="summary-metric">
              <div class="summary-value">{{ formatCurrency(simulationSummary.initialDebt) }}</div>
              <div class="summary-label">начальный долг</div>
            </div>
            <div class="summary-metric">
              <div class="summary-value">{{ formatCurrency(simulationSummary.totalPaid) }}</div>
              <div class="summary-label">всего заплатите</div>
            </div>
            <div class="summary-metric">
              <div class="summary-value" :class="simulationSummary.totalInterest > 0 ? 'text-danger' : 'text-success'">
                {{ formatCurrency(simulationSummary.totalInterest) }}
              </div>
              <div class="summary-label">переплата</div>
            </div>
            <div class="summary-metric" v-if="totalMinPayment > 0">
              <div class="summary-value text-warning">{{ formatCurrency(totalMinPayment) }}</div>
              <div class="summary-label">мин. платёж по всем</div>
            </div>
          </div>

          <div class="payoff-list" v-if="enrichedPayoffCards.length > 0">
            <div class="payoff-list-title">
              <i class="fas fa-list-ol"></i> Порядок закрытия
            </div>
            <div
              v-for="(card, idx) in enrichedPayoffCards"
              :key="card.id"
              class="payoff-card"
            >
              <div class="payoff-card-head">
                <div class="payoff-card-title">
                  <span class="payoff-index">{{ idx + 1 }}</span>
                  <span class="payoff-name">{{ card.name }}</span>
                </div>
                <span v-if="card.monthPaidOff" class="payoff-month-badge">
                  {{ formatMonth(card.monthPaidOff) }}
                </span>
              </div>

              <div class="payoff-card-body">
                <div class="payoff-metric">
                  <span class="metric-label">Долг</span>
                  <span class="metric-value">{{ formatCurrency(card.initialDebt) }}</span>
                </div>
                <div class="payoff-metric">
                  <span class="metric-label">Ставка</span>
                  <span class="metric-value">
                    {{ formatRate(card.rate) }}<small> год.</small>
                  </span>
                </div>
                <div class="payoff-metric">
                  <span class="metric-label">Проценты</span>
                  <span class="metric-value" :class="card.totalInterest > 0 ? 'text-danger' : 'text-success'">
                    {{ formatCurrency(card.totalInterest) }}
                  </span>
                </div>
                <div class="payoff-metric" v-if="card.hasMinPayment">
                  <span class="metric-label">Мин. платёж ({{ card.minPaymentPercent }}%)</span>
                  <span class="metric-value">{{ formatCurrency(card.minPayment) }}</span>
                </div>
              </div>

              <div class="payoff-badges" v-if="card.hasGrace">
                <span class="badge badge-success">
                  <i class="fas fa-clock"></i>
                  Льготный период: {{ card.graceDays }} дн.
                </span>
              </div>
            </div>
          </div>

          <!-- ГРАФИК ПАДЕНИЯ ДОЛГА -->
          <div class="schedule-chart-wrapper">
            <canvas v-if="hasChartData" ref="scheduleCanvas" height="160"></canvas>
            <div v-else class="chart-empty">
              <i class="fas fa-check-circle"></i>
              <div>
                <strong>Долг закрывается за 1 месяц</strong>
                <p>График падения не нужен — все карты гасятся сразу.</p>
              </div>
            </div>
          </div>

          <div class="disclaimer">
            <i class="fas fa-info-circle"></i>
            Расчет предполагает, что вы не будете совершать новые покупки с этих карт.
          </div>
        </div>
        <div v-else-if="simulationLoading" class="plan-results loading-placeholder">
          <i class="fas fa-spinner fa-spin"></i>
          <span>Рассчитываем стратегию...</span>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- БЛОК: ДОЛГИ МЕЖДУ ЛЮДЬМИ                                     -->
    <!-- ============================================================ -->
    <h2 class="section-title">Долги между людьми</h2>

    <div class="stats-grid">
      <div class="stat-card hoverable-card">
        <div class="stat-title">Я должен</div>
        <div class="stat-value text-danger">{{ formatCurrency(totalBorrow) }}</div>
      </div>
      <div class="stat-card hoverable-card">
        <div class="stat-title">Мне должны</div>
        <div class="stat-value text-success">{{ formatCurrency(totalLend) }}</div>
      </div>
      <div class="stat-card hoverable-card">
        <div class="stat-title">Баланс долгов</div>
        <div class="stat-value" :class="netDebt >= 0 ? 'text-success' : 'text-danger'">
          {{ formatCurrency(Math.abs(netDebt)) }}
          <small>{{ netDebt >= 0 ? '' : '(-)' }}</small>
        </div>
      </div>
    </div>

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

    <div class="card hoverable-card">
      <!-- Мобильные карточки -->
      <div class="mobile-debts">
        <div v-for="debt in filteredDebts" :key="debt.id" class="debt-card">
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

          <div v-if="expandedDebts.has(debt.id)" class="debt-expanded">
            <div class="debt-details-expanded">
              <div class="detail-item">
                <span class="detail-label"><i class="fas fa-user"></i> Контрагент:</span>
                <span class="detail-value">{{ debt.borrower_description }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label"><i class="fas fa-calendar"></i> Полная дата:</span>
                <span class="detail-value">{{ formatDate(getDebtDate(debt)) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label"><i class="fas fa-credit-card"></i> Счет:</span>
                <span class="detail-value">{{ getRealAccountName(debt) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label"><i class="fas fa-flag-checkered"></i> Статус:</span>
                <span class="badge" :class="debt.is_repaid ? 'badge-success' : 'badge-warning'">
                  {{ debt.is_repaid ? 'Погашен' : 'Активен' }}
                </span>
              </div>
            </div>
            <div class="debt-actions-expanded">
              <button @click="viewDebt(debt)" class="btn btn-sm btn-info">
                <i class="fas fa-eye"></i> Детали
              </button>
              <button v-if="!debt.is_repaid" @click="openRepayModal(debt)" class="btn btn-sm btn-success">
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

      <!-- Десктопная/планшетная таблица -->
      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th class="col-id">ID</th>
              <th>Контрагент</th>
              <th>Сумма</th>
              <th>Дата</th>
              <th class="col-account">Счет</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="debt in filteredDebts" :key="debt.id">
              <td class="col-id">{{ debt.id }}</td>
              <td><strong>{{ debt.borrower_description }}</strong></td>
              <td :class="getDebtAmountClass(debt)">
                <strong>{{ formatCurrency(getDebtAmount(debt)) }}</strong>
              </td>
              <td>{{ formatDate(getDebtDate(debt)) }}</td>
              <td class="col-account">
                <span class="badge badge-info">{{ getRealAccountName(debt) }}</span>
              </td>
              <td>
                <span class="badge" :class="debt.is_repaid ? 'badge-success' : 'badge-warning'">
                  {{ debt.is_repaid ? 'Погашен' : 'Активен' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="viewDebt(debt)" class="btn btn-sm btn-info" title="Детали">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button v-if="!debt.is_repaid" @click="openRepayModal(debt)" class="btn btn-sm btn-success" title="Погасить">
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

    <!-- Модальные окна (без изменений) -->
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
            <input type="number" v-model="formData.amount" class="form-control" step="0.01" required placeholder="Введите сумму">
          </div>
          <div class="form-group">
            <label class="form-label required">Контрагент</label>
            <input type="text" v-model="formData.description" class="form-control" required placeholder="Кому/от кого? Например: Иван Петров">
          </div>
          <div class="form-group">
            <label class="form-label required">Дата</label>
            <input type="date" v-model="formData.date" class="form-control" required>
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
          <div class="detail-row"><span class="detail-label">ID:</span><span class="detail-value">{{ currentDebt.id }}</span></div>
          <div class="detail-row"><span class="detail-label">Контрагент:</span><span class="detail-value"><strong>{{ currentDebt.borrower_description }}</strong></span></div>
          <div class="detail-row"><span class="detail-label">Сумма:</span><span class="detail-value" :class="getDebtAmountClass(currentDebt)">{{ formatCurrency(getDebtAmount(currentDebt)) }}</span></div>
          <div class="detail-row"><span class="detail-label">Дата:</span><span class="detail-value">{{ formatDate(getDebtDate(currentDebt)) }}</span></div>
          <div class="detail-row"><span class="detail-label">Счет:</span><span class="detail-value">{{ getRealAccountName(currentDebt) }}</span></div>
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
            <input type="number" v-model="repayAmount" class="form-control" step="0.01" :max="getDebtAmount(currentDebt)" required>
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
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'DebtsList',
  setup() {
    const debts = ref([])
    const accounts = ref([])
    const currentPage = ref(1)
    const totalCount = ref(0)
    const pageSize = 10
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

    const monthlyPayment = ref(15000)
    const strategy = ref('avalanche')
    const simulationResult = ref(null)
    const simulationLoading = ref(false)
    const simulationError = ref('')
    const scheduleCanvas = ref(null)

    let debounceTimer = null
    let simulationRequestId = 0
    let debtsRequestId = 0
    let accountsRequestId = 0
    let viewDebtRequestId = 0
    let resizeObserver = null

    const creditCards = computed(() => {
      if (!Array.isArray(accounts.value)) return []
      return accounts.value
        .filter(acc => acc && acc.account_type === 'credit_card')
        .map(acc => {
          const balance = Number(acc.balance)
          if (!Number.isFinite(balance) || balance >= 0) return null
          const rate = Number(acc.credit_rate)
          const minPercent = Number(acc.min_payment_percent)

          return {
            ...acc,
            balanceAbs: Math.abs(balance),
            rate: Number.isFinite(rate) && rate >= 0 ? rate : 30,
            minPaymentPercent: Number.isFinite(minPercent) && minPercent > 0 ? minPercent : 5
          }
        })
        .filter(Boolean)
    })

    const totalCreditDebt = computed(() =>
      creditCards.value.reduce((sum, card) => sum + card.balanceAbs, 0)
    )

    const creditCardsFingerprint = computed(() =>
      creditCards.value
        .map(c => `${c.id}:${c.balanceAbs.toFixed(2)}:${c.rate}`)
        .join('|')
    )

    const activeAccounts = computed(() =>
      Array.isArray(accounts.value) ? accounts.value.filter(a => a && a.is_active) : []
    )

    const totalPages = computed(() => {
      const count = Number(totalCount.value) || 0
      return count > 0 ? Math.ceil(count / pageSize) : 1
    })

    const filteredDebts = computed(() =>
      debts.value.filter(debt => getDebtType(debt) === currentType.value)
    )

    const totalLend = computed(() =>
      debts.value.filter(d => !d.is_repaid && getDebtType(d) === 'lend')
        .reduce((s, d) => s + getDebtAmount(d), 0)
    )
    const totalBorrow = computed(() =>
      debts.value.filter(d => !d.is_repaid && getDebtType(d) === 'borrow')
        .reduce((s, d) => s + getDebtAmount(d), 0)
    )
    const netDebt = computed(() => totalLend.value - totalBorrow.value)

    const getDebtAmount = (debt) => {
      if (!debt) return 0
      const v = debt.transfer?.amount ?? debt.amount ?? 0
      const n = Number(v)
      return Number.isFinite(n) ? n : 0
    }
    const getDebtDate = (debt) => {
      if (!debt) return null
      return debt.transfer?.timestamp || debt.date || null
    }
    const getDebtType = (debt) => {
      if (!debt) return 'lend'
      if (debt.type) return debt.type
      const dest = debt.transfer?.destination_account
      if (dest?.name === 'debt') return 'borrow'
      if (dest?.name === 'lend') return 'lend'
      return 'lend'
    }
    const getRealAccountName = (debt) => {
      if (!debt) return 'Не указан'
      const source = debt.transfer?.source_account
      if (source && source.name !== 'debt' && source.name !== 'lend') return source.name
      const accountId = debt.account ?? debt.account_id
      if (accountId != null && Array.isArray(accounts.value)) {
        const acc = accounts.value.find(a => a && a.id === accountId)
        if (acc?.name) return acc.name
      }
      return 'Не указан'
    }
    const getDebtAmountClass = (debt) =>
      getDebtType(debt) === 'lend' ? 'text-success' : 'text-danger'
    const getTypeDescription = (type) =>
      type === 'lend'
        ? 'Деньги будут списаны с вашего счета (вы даете в долг)'
        : 'Деньги будут зачислены на ваш счет (вы берете в долг)'

    const formatCurrency = (value) => {
      if (value === null || value === undefined || value === '') return '0 ₽'
      const n = Number(value)
      if (!Number.isFinite(n)) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency', currency: 'RUB', maximumFractionDigits: 0
      }).format(n)
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const d = new Date(dateString)
      if (Number.isNaN(d.getTime())) return ''
      return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
    }

    const formatShortDate = (dateString) => {
      if (!dateString) return ''
      const d = new Date(dateString)
      if (Number.isNaN(d.getTime())) return ''
      return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
    }

    const pluralize = (num, [one, few, many]) => {
      const mod10 = num % 10
      const mod100 = num % 100
      if (mod100 >= 11 && mod100 <= 14) return many
      if (mod10 === 1) return one
      if (mod10 >= 2 && mod10 <= 4) return few
      return many
    }

    const formatDuration = (months) => {
      const n = Math.round(Number(months) || 0)
      if (n <= 0) return '0 мес.'
      const monthForms = ['месяц', 'месяца', 'месяцев']
      const yearForms = ['год', 'года', 'лет']
      const years = Math.floor(n / 12)
      const rem = n % 12
      if (years === 0) return `${n} ${pluralize(n, monthForms)}`
      const yearPart = `${years} ${pluralize(years, yearForms)}`
      return rem === 0 ? yearPart : `${yearPart} ${rem} ${pluralize(rem, monthForms)}`
    }

    const formatMonth = (n) => {
      const v = Number(n)
      if (!Number.isFinite(v) || v <= 0) return ''
      return `мес. ${v}`
    }

    const formatRate = (rate) => {
      const n = Number(rate)
      if (!Number.isFinite(n) || n < 0) return '—'
      const pct = n > 0 && n < 1 ? n * 100 : n
      return `${pct.toFixed(1).replace(/\.0$/, '')}%`
    }

    const truncateText = (text, max) => {
      if (!text) return ''
      const str = String(text)
      return str.length > max ? str.substring(0, max) + '...' : str
    }

    const toggleExpand = (id) => {
      const s = new Set(expandedDebts.value)
      if (s.has(id)) s.delete(id)
      else s.add(id)
      expandedDebts.value = s
    }

    const simulationSummary = computed(() => {
      const r = simulationResult.value
      if (!r) return { months: 0, totalInterest: 0, totalPaid: 0, initialDebt: 0 }
      const months = Number(r.months) || 0
      const totalInterest = Number(r.total_interest) || 0
      const totalPaid = Number(r.total_paid) || 0
      const initialDebt = Math.max(0, totalPaid - totalInterest)
      return { months, totalInterest, totalPaid, initialDebt }
    })

    // ВОССТАНОВЛЕННЫЙ И ИСПРАВЛЕННЫЙ БЛОК
    const enrichedPayoffCards = computed(() => {
      const order = simulationResult.value?.payoff_order
      if (!Array.isArray(order)) return []

      const cardsById = new Map()
      creditCards.value.forEach(c => cardsById.set(c.id, c))

      return order
        .map((item, index) => {
          if (!item || typeof item !== 'object') return null

          const totalPaid = Number(item.total_paid) || 0
          const totalInterest = Number(item.total_interest) || 0
          const principal = Math.max(0, totalPaid - totalInterest)
          const knownCard = cardsById.get(item.id)
          const initialDebt = knownCard?.balanceAbs ?? principal
          const rate = Number(item.rate)
          const graceDays = Math.max(0, Number(item.grace_days_left) || 0)
          const monthPaidOff = Number(item.month_paid_off) || null

          const minPercent = Number(item.min_payment_percent)
                            || knownCard?.minPaymentPercent
                            || 5

          let minPayment = Number(item.min_payment) || 0
          if (minPayment <= 0) {
            minPayment = initialDebt * (minPercent / 100)
          }

          return {
            id: item.id,
            name: item.name || `Карта #${item.id}`,
            order: index + 1,
            initialDebt,
            totalPaid,
            totalInterest,
            principal,
            rate: Number.isFinite(rate) ? rate : 0,
            graceDays,
            monthPaidOff,
            hasGrace: graceDays > 0,
            minPayment,
            minPaymentPercent: minPercent,
            hasMinPayment: minPayment > 0
          }
        })
        .filter(Boolean)
    })

    const totalMinPayment = computed(() =>
      enrichedPayoffCards.value.reduce((sum, c) => sum + c.minPayment, 0)
    )

    const actionablePlan = computed(() => {
      const cards = enrichedPayoffCards.value
      if (cards.length === 0) return null

      const payment = Number(monthlyPayment.value) || 0
      if (payment <= 0) return null

      if (simulationResult.value?.months === 1) {
        return {
          type: 'single',
          message: `Долг закрывается за 1 месяц. Внесите ${formatCurrency(simulationSummary.value.totalPaid)} и все карты будут погашены.`
        }
      }

      let totalMin = 0
      const cardMins = cards.map(card => {
        let minPay = Math.min(card.minPayment, card.initialDebt)
        totalMin += minPay
        return minPay
      })

      if (payment < totalMin) {
        return {
          type: 'warning',
          message: `Платежа ${formatCurrency(payment)} не хватает даже на минимальные платежи по картам (${formatCurrency(totalMin)}). Увеличьте сумму.`
        }
      }

      let extraBudget = payment - totalMin
      const parts = []

      cards.forEach((card, i) => {
        const basePay = cardMins[i]
        const remainingDebt = card.initialDebt - basePay
        const extraPay = Math.min(extraBudget, remainingDebt)
        extraBudget -= extraPay

        const totalPay = basePay + extraPay

        if (totalPay > 0) {
          parts.push({
            card,
            amount: totalPay,
            isTarget: extraPay > 0
          })
        }
      })

      return {
        type: 'split',
        parts
      }
    })

    const fetchSimulation = async () => {
      const requestId = ++simulationRequestId

      if (creditCards.value.length === 0) {
        simulationResult.value = null
        simulationLoading.value = false
        simulationError.value = ''
        return
      }

      const payment = Number(monthlyPayment.value)
      if (!Number.isFinite(payment) || payment <= 0) {
        simulationResult.value = null
        simulationLoading.value = false
        simulationError.value = 'Введите сумму больше 0'
        return
      }

      simulationLoading.value = true
      simulationError.value = ''

      try {
        const result = await apiService.simulateCreditPlan(payment, strategy.value)
        if (requestId !== simulationRequestId) return
        simulationResult.value = result ?? null
      } catch (error) {
        if (requestId !== simulationRequestId) return
        simulationResult.value = null
        simulationError.value =
          error?.response?.data?.detail ||
          error?.response?.data?.message ||
          error?.message ||
          'Ошибка при расчете стратегии'
      } finally {
        if (requestId === simulationRequestId) {
          simulationLoading.value = false
        }
      }
    }

    const extractSchedule = (result) => {
      if (!result || typeof result !== 'object') return null

      const raw =
        result.schedule ?? result.schedule_data ?? result.payments ?? result.plan
      if (!Array.isArray(raw) || raw.length < 2) return null

      const points = []
      for (let i = 0; i < raw.length; i++) {
        const item = raw[i]
        if (!item || typeof item !== 'object') continue
        const rawValue =
          item.remaining_debt ??
          item.remainingDebt ??
          item.remaining ??
          item.balance ??
          item.debt ??
          item.total
        const value = Number(rawValue)
        if (!Number.isFinite(value)) continue
        points.push({ month: i + 1, value: Math.max(0, value) })
      }
      if (points.length < 2) return null
      const maxDebt = points.reduce((m, p) => Math.max(m, p.value), 0)
      if (!Number.isFinite(maxDebt) || maxDebt <= 0) return null
      return { points, maxDebt }
    }

    const chartData = computed(() => extractSchedule(simulationResult.value))
    const hasChartData = computed(() => chartData.value !== null)

    const drawScheduleChart = () => {
      const canvas = scheduleCanvas.value
      if (!canvas) return
      const data = chartData.value
      if (!data) return

      const parent = canvas.parentElement
      if (!parent) return

      const rect = parent.getBoundingClientRect()
      const cssWidth = rect.width || 0
      const cssHeight = 160
      if (cssWidth < 50) return

      const dpr = Math.max(window.devicePixelRatio || 1, 1)
      const pixelWidth = Math.round(cssWidth * dpr)
      const pixelHeight = Math.round(cssHeight * dpr)

      if (canvas.width !== pixelWidth) canvas.width = pixelWidth
      if (canvas.height !== pixelHeight) canvas.height = pixelHeight
      canvas.style.width = `${cssWidth}px`
      canvas.style.height = `${cssHeight}px`

      const ctx = canvas.getContext('2d')
      if (!ctx) return

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, cssWidth, cssHeight)

      const { points, maxDebt } = data
      const paddingTop = 15
      const paddingBottom = 25
      const paddingLeft = 50
      const paddingRight = 10

      const innerWidth = cssWidth - paddingLeft - paddingRight
      const innerHeight = cssHeight - paddingTop - paddingBottom

      if (innerWidth < 20 || innerHeight < 20) return

      const xFor = (i) => paddingLeft + (i / (points.length - 1)) * innerWidth
      const yFor = (v) => paddingTop + innerHeight - (v / maxDebt) * innerHeight

      ctx.strokeStyle = 'rgba(148, 163, 184, 0.15)'
      ctx.lineWidth = 1
      ctx.fillStyle = '#94a3b8'
      ctx.font = '10px sans-serif'
      ctx.textAlign = 'right'
      ctx.textBaseline = 'middle'

      const ySteps = 4
      for (let i = 0; i <= ySteps; i++) {
        const val = (maxDebt / ySteps) * i
        const y = yFor(val)

        ctx.beginPath()
        ctx.moveTo(paddingLeft, y)
        ctx.lineTo(cssWidth - paddingRight, y)
        ctx.stroke()

        let label = ''
        if (val >= 1000000) label = (val / 1000000).toFixed(1).replace(/\.0$/, '') + 'М'
        else if (val >= 1000) label = (val / 1000).toFixed(0) + 'к'
        else label = val.toFixed(0)

        ctx.fillText(label, paddingLeft - 8, y)
      }

      ctx.textAlign = 'center'
      ctx.textBaseline = 'top'

      let step = 1
      if (points.length > 24) step = 6
      else if (points.length > 12) step = 3
      else if (points.length > 6) step = 2

      for (let i = 0; i < points.length; i++) {
        if (i % step !== 0 && i !== points.length - 1) continue
        const x = xFor(i)

        ctx.beginPath()
        ctx.moveTo(x, paddingTop)
        ctx.lineTo(x, cssHeight - paddingBottom)
        ctx.stroke()

        ctx.fillText(`${i + 1}`, x, cssHeight - paddingBottom + 6)
      }

      ctx.strokeStyle = '#64748b'
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.moveTo(paddingLeft, paddingTop)
      ctx.lineTo(paddingLeft, cssHeight - paddingBottom)
      ctx.lineTo(cssWidth - paddingRight, cssHeight - paddingBottom)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(xFor(0), cssHeight - paddingBottom)
      points.forEach((p, i) => ctx.lineTo(xFor(i), yFor(p.value)))
      ctx.lineTo(xFor(points.length - 1), cssHeight - paddingBottom)
      ctx.closePath()

      const gradient = ctx.createLinearGradient(0, paddingTop, 0, cssHeight - paddingBottom)
      gradient.addColorStop(0, 'rgba(16, 185, 129, 0.3)')
      gradient.addColorStop(1, 'rgba(16, 185, 129, 0.05)')
      ctx.fillStyle = gradient
      ctx.fill()

      ctx.beginPath()
      points.forEach((p, i) => {
        const x = xFor(i)
        const y = yFor(p.value)
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      })
      ctx.strokeStyle = '#10b981'
      ctx.lineWidth = 2
      ctx.lineJoin = 'round'
      ctx.lineCap = 'round'
      ctx.stroke()

      if (points.length <= 12) {
        points.forEach((p, i) => {
          ctx.beginPath()
          ctx.arc(xFor(i), yFor(p.value), 3, 0, Math.PI * 2)
          ctx.fillStyle = '#10b981'
          ctx.fill()
          ctx.strokeStyle = '#fff'
          ctx.lineWidth = 1.5
          ctx.stroke()
        })
      } else {
        const lastIdx = points.length - 1
        ctx.beginPath()
        ctx.arc(xFor(lastIdx), yFor(points[lastIdx].value), 3, 0, Math.PI * 2)
        ctx.fillStyle = '#10b981'
        ctx.fill()
        ctx.strokeStyle = '#fff'
        ctx.lineWidth = 1.5
        ctx.stroke()
      }
    }

    const loadDebts = async () => {
      const requestId = ++debtsRequestId
      try {
        const data = await apiService.getDebts(currentPage.value, pageSize)
        if (requestId !== debtsRequestId) return
        debts.value = Array.isArray(data?.results) ? data.results : []
        totalCount.value = Number(data?.count) || 0
      } catch (error) {
        if (requestId !== debtsRequestId) return
        console.error('Error loading debts:', error)
      }
    }

    const loadAccounts = async () => {
      const requestId = ++accountsRequestId
      try {
        const data = await apiService.getAccounts(1, 100)
        if (requestId !== accountsRequestId) return
        const list = data?.results?.[0]?.accounts
        accounts.value = Array.isArray(list) ? list : []
      } catch (error) {
        if (requestId !== accountsRequestId) return
        console.error('Error loading accounts:', error)
      }
    }

    const openCreateModal = () => {
      formData.value = {
        type: 'lend', account_id: '', amount: '', description: '',
        date: new Date().toISOString().slice(0, 10)
      }
      showCreateModal.value = true
    }
    const closeCreateModal = () => { showCreateModal.value = false }

    const createDebt = async () => {
      const amount = Number(formData.value.amount)
      const description = (formData.value.description || '').trim()
      if (!formData.value.account_id) { alert('Выберите счёт'); return }
      if (!Number.isFinite(amount) || amount <= 0) { alert('Введите корректную сумму'); return }
      if (!description) { alert('Введите контрагента'); return }
      if (!formData.value.date) { alert('Укажите дату'); return }

      try {
        const apiType = formData.value.type === 'lend' ? 'borrow' : 'debt'
        await apiService.createDebt(
          formData.value.account_id, apiType, amount, description, formData.value.date
        )
        closeCreateModal()
        await Promise.all([loadDebts(), loadAccounts()])
      } catch (error) {
        console.error('Error creating debt:', error)
        alert(
          'Ошибка при создании долга: ' +
          (error?.response?.data?.detail || error?.message || 'Неизвестная ошибка')
        )
      }
    }

    const viewDebt = async (debt) => {
      if (!debt?.id) return
      const requestId = ++viewDebtRequestId
      try {
        const data = await apiService.getDebt(debt.id)
        if (requestId !== viewDebtRequestId) return
        currentDebt.value = data
        showViewModal.value = true
      } catch (error) {
        if (requestId !== viewDebtRequestId) return
        console.error('Error loading debt details:', error)
        alert('Ошибка при загрузке деталей долга')
      }
    }

    const openRepayModal = (debt) => {
      if (!debt) return
      currentDebt.value = debt
      repayAmount.value = getDebtAmount(debt)
      showRepayModal.value = true
    }
    const closeRepayModal = () => {
      showRepayModal.value = false
      currentDebt.value = null
      repayAmount.value = 0
    }

    const repayDebt = async () => {
      if (!currentDebt.value) return
      const amount = Number(repayAmount.value)
      const fullAmount = getDebtAmount(currentDebt.value)
      if (!Number.isFinite(amount) || amount <= 0) { alert('Введите корректную сумму'); return }
      if (amount > fullAmount) { alert('Сумма погашения не может превышать сумму долга'); return }

      try {
        await apiService.repayDebt(
          currentDebt.value.id, amount, getDebtType(currentDebt.value)
        )
        closeRepayModal()
        await Promise.all([loadDebts(), loadAccounts()])
      } catch (error) {
        console.error('Error repaying debt:', error)
        alert('Ошибка при погашении долга')
      }
    }

    const prevPage = () => {
      if (currentPage.value > 1) { currentPage.value--; loadDebts() }
    }
    const nextPage = () => {
      if (currentPage.value < totalPages.value) { currentPage.value++; loadDebts() }
    }

    watch(
      [monthlyPayment, strategy, creditCardsFingerprint],
      () => {
        clearTimeout(debounceTimer)
        debounceTimer = setTimeout(fetchSimulation, 400)
      },
      { immediate: true }
    )

    watch(simulationResult, async (val) => {
      if (!val) return
      await nextTick()
      requestAnimationFrame(drawScheduleChart)
    })

    watch(scheduleCanvas, (canvas) => {
      if (resizeObserver) {
        resizeObserver.disconnect()
        resizeObserver = null
      }
      if (canvas?.parentElement && typeof ResizeObserver !== 'undefined') {
        resizeObserver = new ResizeObserver(() => {
          if (simulationResult.value) drawScheduleChart()
        })
        resizeObserver.observe(canvas.parentElement)
      }
    })

    watch(currentType, () => {
      currentPage.value = 1
      loadDebts()
    })

    const handleWindowResize = () => {
      if (simulationResult.value) drawScheduleChart()
    }

    onMounted(() => {
      window.addEventListener('resize', handleWindowResize)
      loadDebts()
      loadAccounts()
    })

    onUnmounted(() => {
      clearTimeout(debounceTimer)
      window.removeEventListener('resize', handleWindowResize)
      if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
      simulationRequestId++
      debtsRequestId++
      accountsRequestId++
      viewDebtRequestId++
    })

    return {
      debts, accounts, currentPage, currentType,
      showCreateModal, showViewModal, showRepayModal,
      currentDebt, repayAmount, formData, expandedDebts,
      monthlyPayment, strategy, simulationResult, simulationLoading,
      simulationError, scheduleCanvas, hasChartData,
      creditCards, totalCreditDebt,
      activeAccounts, totalPages, filteredDebts,
      totalLend, totalBorrow, netDebt,
      simulationSummary, enrichedPayoffCards, totalMinPayment, actionablePlan,
      toggleExpand, truncateText,
      getDebtAmount, getDebtDate, getDebtAmountClass,
      getRealAccountName, getDebtType, getTypeDescription,
      formatCurrency, formatDate, formatShortDate,
      formatDuration, formatMonth, formatRate,
      openCreateModal, closeCreateModal, createDebt,
      viewDebt, openRepayModal, closeRepayModal, repayDebt,
      prevPage, nextPage
    }
  }
}
</script>

<style scoped>
/* Базовые стили */
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem; }
.page-header h1 { font-size: 1.875rem; color: var(--dark-color); }
.section-title { font-size: 1.25rem; color: var(--dark-color); margin: 2rem 0 1rem; font-weight: 600; border-bottom: 1px solid var(--light-color); padding-bottom: 0.5rem; }

.hoverable-card {
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s ease;
  will-change: transform;
}
.hoverable-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg), 0 8px 24px rgba(0, 0, 0, 0.08);
}
:global(:root[data-theme="dark"]) .hoverable-card:hover {
  box-shadow: var(--shadow-lg), 0 8px 24px rgba(0, 0, 0, 0.4);
}

/* План погашения */
.debt-plan-card { background: var(--white); border-left: 4px solid var(--primary-color); margin-bottom: 1.5rem; }
.plan-body { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media (min-width: 1100px) {
  /* Левая колонка чуть уже, правая чуть шире для графика */
  .plan-body { grid-template-columns: minmax(320px, 4fr) minmax(0, 6fr); gap: 2rem; }
}

.plan-inputs .form-group { margin-bottom: 1.25rem; }
.input-with-currency { position: relative; }
.input-with-currency .form-control { padding-right: 2rem; font-size: 1.25rem; font-weight: 700; color: var(--dark-color); }
.currency-symbol { position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); font-size: 1.25rem; font-weight: 700; color: var(--gray-color); }
.mt-1 { margin-top: 0.25rem; }
.d-block { display: block; }

.strategy-toggle { display: flex; background: var(--light-color); padding: 0.25rem; border-radius: var(--radius); gap: 0.25rem; }
.strategy-btn { flex: 1; padding: 0.5rem; border: none; background: transparent; border-radius: calc(var(--radius) - 2px); font-size: 0.9rem; font-weight: 500; color: var(--gray-color); cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.strategy-btn.active { background: var(--white); color: var(--dark-color); box-shadow: var(--shadow); font-weight: 600; }

.strategy-description { margin: 0.5rem 0 0; font-size: 0.8rem; color: var(--gray-color); line-height: 1.4; display: flex; gap: 0.4rem; align-items: flex-start; }
.strategy-description i { margin-top: 0.15rem; flex-shrink: 0; color: var(--primary-color); }
.strategy-description span { display: block; min-width: 0; }
.strategy-description strong { color: var(--dark-color); }
.strategy-description em { font-style: normal; color: var(--primary-color); font-weight: 600; }

.plan-results { background: var(--light-color); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 1rem; }
@media (min-width: 1100px) { .plan-results { padding: 1.25rem; } }

/* Сводка */
.summary-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 0.5rem;
}
.summary-metric {
  background: var(--white);
  border-radius: var(--radius);
  padding: 0.65rem 0.5rem;
  text-align: center;
  min-width: 0;
}
.summary-value {
  font-size: clamp(0.95rem, 2vw, 1.15rem);
  font-weight: 700;
  line-height: 1.2;
  color: var(--dark-color);
  word-break: break-word;
}
.summary-label {
  font-size: clamp(0.65rem, 1.2vw, 0.72rem);
  color: var(--gray-color);
  margin-top: 0.3rem;
  line-height: 1.25;
}

/* План на месяц */
.action-plan {
  background: var(--light-color);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: var(--radius);
  padding: 1rem;
  margin-top: 1rem;
}
.action-plan-single { background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.3); }
.action-plan-warning { background: rgba(239, 68, 68, 0.08); border-color: rgba(239, 68, 68, 0.3); }

.action-plan-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--dark-color);
  margin-bottom: 0.6rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.action-plan-text {
  font-size: 0.85rem;
  color: var(--dark-color);
  line-height: 1.4;
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px dashed var(--light-color);
  font-size: 0.85rem;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.action-item:last-child { border-bottom: none; }
.action-item-left { display: flex; align-items: center; gap: 0.5rem; min-width: 0; flex: 1; }
.action-item-name { font-weight: 500; color: var(--dark-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.action-item-amount { font-weight: 700; color: var(--dark-color); white-space: nowrap; }

.action-tag {
  font-size: 0.65rem;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
  flex-shrink: 0;
}
.tag-target { background: #dbeafe; color: #1e40af; }
.tag-min { background: #f3f4f6; color: #4b5563; }

/* Инфо-блок */
.info-tips {
  background: rgba(59, 130, 246, 0.05);
  border: 1px dashed rgba(59, 130, 246, 0.3);
  border-radius: var(--radius);
  padding: 1rem;
  margin-top: 1rem;
}
.info-tips-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--dark-color);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.info-tips p {
  font-size: 0.8rem;
  color: var(--gray-color);
  margin: 0;
  line-height: 1.4;
}

/* Разбивка по картам */
.payoff-list { display: flex; flex-direction: column; gap: 0.6rem; }
.payoff-list-title { font-size: 0.8rem; font-weight: 600; color: var(--gray-color); text-transform: uppercase; letter-spacing: 0.03em; display: flex; align-items: center; gap: 0.35rem; }

.payoff-card {
  background: var(--white);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: var(--radius);
  padding: 0.75rem 0.9rem;
}
.payoff-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
  flex-wrap: wrap;
}
.payoff-card-title { display: flex; align-items: center; gap: 0.5rem; min-width: 0; flex: 1; }
.payoff-index {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border-radius: 50%;
  background: var(--primary-color); color: #fff;
  font-size: 0.75rem; font-weight: 700; flex-shrink: 0;
}
.payoff-name { font-weight: 600; color: var(--dark-color); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.payoff-month-badge {
  flex-shrink: 0; font-size: 0.7rem; padding: 0.2rem 0.5rem;
  border-radius: 9999px; background: #d1fae5; color: #065f46; font-weight: 600;
}
.payoff-card-body {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(75px, 1fr));
  gap: 0.5rem;
}
.payoff-metric { display: flex; flex-direction: column; gap: 0.15rem; min-width: 0; }
.metric-label { font-size: 0.68rem; color: var(--gray-color); text-transform: uppercase; letter-spacing: 0.03em; line-height: 1.2; }
.metric-value {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--dark-color);
  line-height: 1.3;
  word-break: break-word;
}
.metric-value small { font-weight: 400; font-size: 0.72rem; color: var(--gray-color); }

.payoff-badges { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.55rem; }
.payoff-badges .badge { font-size: 0.7rem; }

/* График */
.schedule-chart-wrapper {
  width: 100%;
  border-top: 1px dashed rgba(148, 163, 184, 0.4);
  padding-top: 1rem;
  margin-top: 0.5rem;
}
.schedule-chart-wrapper canvas {
  display: block;
  width: 100%;
  height: 160px;
}

.chart-empty {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 1.1rem 1rem;
  background: rgba(16, 185, 129, 0.08);
  border: 1px dashed rgba(16, 185, 129, 0.35);
  border-radius: var(--radius);
  color: var(--dark-color);
  flex-wrap: wrap;
}
.chart-empty i { font-size: 1.75rem; color: var(--secondary-color); flex-shrink: 0; }
.chart-empty strong { display: block; margin-bottom: 0.125rem; font-size: 0.9rem; }
.chart-empty p { margin: 0; font-size: 0.8rem; color: var(--gray-color); }

.loading-placeholder { display: flex; flex-direction: column; align-items: center; gap: 1rem; color: var(--gray-color); }
.loading-placeholder i { font-size: 2rem; color: var(--primary-color); }

.disclaimer { font-size: 0.72rem; color: var(--gray-color); display: flex; gap: 0.5rem; align-items: flex-start; }
.disclaimer i { margin-top: 0.15rem; flex-shrink: 0; }

/* Статистика и остальное */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { background: var(--white); padding: 1.25rem; border-radius: var(--radius); box-shadow: var(--shadow); text-align: center; }
.stat-title { font-size: 0.875rem; color: var(--gray-color); margin-bottom: 0.5rem; }
.stat-value { font-size: clamp(1.25rem, 2.5vw, 1.75rem); font-weight: 700; }

.type-tabs { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; background: var(--white); padding: 0.5rem; border-radius: var(--radius); box-shadow: var(--shadow); }
.tab-btn { flex: 1; padding: 0.75rem; border: none; background: transparent; cursor: pointer; border-radius: var(--radius); font-weight: 500; transition: all 0.3s; display: flex; align-items: center; justify-content: center; gap: 0.5rem; color: var(--gray-color); }
.tab-btn.active { background: var(--primary-color); color: var(--white); }

.mobile-debts { display: block; }
.desktop-table { display: none; }
@media (min-width: 1024px) {
  .mobile-debts { display: none; }
  .desktop-table { display: block; }
}

.debt-card { background: var(--white); border: 1px solid var(--light-color); border-radius: var(--radius); margin-bottom: 0.5rem; overflow: hidden; transition: all 0.3s ease; }
.debt-compact { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; cursor: pointer; transition: background-color 0.2s; gap: 0.5rem; }
.debt-compact:hover { background-color: var(--light-color); }
.compact-left { display: flex; align-items: center; gap: 0.75rem; flex: 1; min-width: 0; }
.debt-date-compact { font-size: 0.75rem; color: var(--gray-color); min-width: 55px; flex-shrink: 0; }
.debt-contractor-compact { font-size: 0.875rem; flex: 1; color: var(--dark-color); min-width: 0; }
.compact-right { display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }
.debt-amount-compact { font-size: 1rem; font-weight: 700; white-space: nowrap; }
.expand-icon { background: none; border: none; cursor: pointer; color: var(--gray-color); width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.expand-icon:hover { background-color: var(--light-color); color: var(--primary-color); }

.debt-expanded { padding: 1rem; border-top: 1px solid var(--light-color); background-color: var(--light-color); animation: slideDown 0.3s ease; }
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.debt-details-expanded { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1rem; }
.detail-item { display: flex; justify-content: space-between; align-items: center; font-size: 0.875rem; gap: 0.5rem; }
.detail-label { color: var(--gray-color); font-weight: 500; display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }
.detail-value { color: var(--dark-color); text-align: right; word-break: break-word; max-width: 60%; }
.debt-actions-expanded { display: flex; gap: 0.5rem; justify-content: flex-end; flex-wrap: wrap; }

.desktop-table { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--light-color); color: var(--dark-color); }
.table th { font-weight: 600; color: var(--gray-color); }

.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.875rem; }
.btn-info { background: #3b82f6; color: white; }
.btn-info:hover { background: #2563eb; }
.btn-success { background: var(--secondary-color); color: white; }
.btn-success:hover { background: #059669; }
.badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; display: inline-flex; align-items: center; gap: 0.25rem; }
.badge-info { background: #dbeafe; color: #1e40af; }
.badge-success { background: #d1fae5; color: #065f46; }
.badge-warning { background: #fed7aa; color: #92400e; }
.badge-danger { background: #fee2e2; color: #991b1b; }
.text-warning { color: #d97706; }
.text-success { color: var(--secondary-color); }
.text-danger { color: var(--danger-color); }

.modal-footer { display: flex; justify-content: center; gap: 1rem; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--light-color); flex-wrap: wrap; }
.form-text { font-size: 0.75rem; color: var(--gray-color); margin-top: 0.25rem; }
.alert { padding: 0.75rem; border-radius: var(--radius); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.alert-info { background: #dbeafe; color: #1e40af; }
.debt-details-modal { padding: 0.5rem; }
.detail-row { display: flex; justify-content: space-between; padding: 0.75rem; border-bottom: 1px solid var(--light-color); gap: 0.5rem; }
.detail-row:last-child { border-bottom: none; }
.empty-state { text-align: center; padding: 3rem 1rem; color: var(--gray-color); }
.empty-state i { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--light-color); flex-wrap: wrap; }

/* Темная тема */
:global(:root[data-theme="dark"]) .strategy-btn.active { background: #374151; color: #fff; }
:global(:root[data-theme="dark"]) .badge-info { background: rgba(59, 130, 246, 0.2); color: #93c5fd; }
:global(:root[data-theme="dark"]) .badge-success { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; }
:global(:root[data-theme="dark"]) .badge-warning { background: rgba(245, 158, 11, 0.2); color: #fcd34d; }
:global(:root[data-theme="dark"]) .badge-danger { background: rgba(239, 68, 68, 0.2); color: #fca5a5; }
:global(:root[data-theme="dark"]) .alert-info { background: rgba(59, 130, 246, 0.15); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.3); }
:global(:root[data-theme="dark"]) .debt-plan-card { border-color: #374151; }
:global(:root[data-theme="dark"]) .payoff-month-badge { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; }
:global(:root[data-theme="dark"]) .chart-empty { background: rgba(16, 185, 129, 0.1); }
:global(:root[data-theme="dark"]) .summary-metric,
:global(:root[data-theme="dark"]) .payoff-card { background: #1f2937; border-color: #374151; }
:global(:root[data-theme="dark"]) .tag-target { background: rgba(59, 130, 246, 0.2); color: #93c5fd; }
:global(:root[data-theme="dark"]) .tag-min { background: rgba(255, 255, 255, 0.1); color: #d1d5db; }
:global(:root[data-theme="dark"]) .action-plan { background: #1f2937; border-color: #374151; }
:global(:root[data-theme="dark"]) .action-plan-single { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); }
:global(:root[data-theme="dark"]) .action-plan-warning { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); }
:global(:root[data-theme="dark"]) .text-warning { color: #fcd34d; }
:global(:root[data-theme="dark"]) .info-tips { background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3); }

@media (max-width: 479.98px) {
  .page-header { flex-direction: column; text-align: center; }
  .page-header h1 { font-size: 1.5rem; }
  .page-header .btn { width: 100%; }
  .type-tabs { flex-direction: column; }
  .strategy-toggle { flex-direction: column; }
  .debt-compact { padding: 0.6rem 0.75rem; }
  .debt-date-compact { min-width: 45px; font-size: 0.7rem; }
  .debt-actions-expanded { flex-direction: column; }
  .debt-actions-expanded .btn-sm { width: 100%; }
  .detail-item { flex-direction: column; align-items: flex-start; gap: 0.25rem; }
  .detail-value { max-width: 100%; text-align: left; }
  .expand-icon { width: 36px; height: 36px; }
  .pagination-text { display: none; }
  .pagination .btn { padding: 0.5rem; }
  .modal-content { width: 95%; margin: 1rem; max-height: 85vh; }
  .payoff-month-badge { font-size: 0.65rem; }
}
</style>