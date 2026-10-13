<template>
  <div>
    <div class="page-header">
      <h1>Счета и переводы</h1>
      <button class="btn btn-primary" @click="openCreateModal">
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

    <!-- ============================================================ -->
    <!-- 1. АКТИВНЫЕ СЧЕТА                                            -->
    <!-- ============================================================ -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-check-circle text-success"></i> Активные счета
          <span class="badge badge-success">{{ activeAccounts.length }}</span>
        </h3>
      </div>

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

          <div v-if="expandedAccounts.has(account.id)" class="account-expanded">
            <div class="account-activity">
              <i class="fas fa-clock"></i>
              Последняя активность:
              <strong :class="getActivityClass(account.id)">
                {{ getLastActivityLabel(account.id) }}
              </strong>
            </div>
            <div class="account-actions-expanded">
              <button class="btn btn-sm btn-primary" @click="openTransferFor(account)">
                <i class="fas fa-exchange-alt"></i> Перевести
              </button>
              <button class="btn btn-sm btn-info" @click="editAccount(account)">
                <i class="fas fa-edit"></i> Редактировать
              </button>
              <button class="btn btn-sm btn-warning" @click="toggleVisibility(account)">
                <i class="fas fa-eye-slash"></i> Скрыть
              </button>
              <button class="btn btn-sm btn-primary" @click="openBalanceModal(account)">
                <i class="fas fa-chart-line"></i> Баланс
              </button>
              <button class="btn btn-sm btn-danger" @click="confirmDelete(account)">
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

      <div class="desktop-table">
        <table class="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Баланс</th>
              <th>Последняя активность</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="account in activeAccounts" :key="account.id">
              <td><strong>{{ account.name }}</strong></td>
              <td class="text-success">
                <strong>{{ formatCurrency(account.balance) }}</strong>
              </td>
              <td>
                <span class="activity-cell" :class="getActivityClass(account.id)">
                  <i :class="getActivityIcon(account.id)"></i>
                  {{ getLastActivityLabel(account.id) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn btn-sm btn-primary" title="Перевести" @click="openTransferFor(account)">
                    <i class="fas fa-exchange-alt"></i>
                  </button>
                  <button class="btn btn-sm btn-info" title="Редактировать" @click="editAccount(account)">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn btn-sm btn-warning" title="Скрыть счет" @click="toggleVisibility(account)">
                    <i class="fas fa-eye-slash"></i>
                  </button>
                  <button class="btn btn-sm btn-primary" title="Изменить баланс" @click="openBalanceModal(account)">
                    <i class="fas fa-chart-line"></i>
                  </button>
                  <button class="btn btn-sm btn-danger" title="Удалить" @click="confirmDelete(account)">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="activeAccounts.length === 0">
              <td colspan="4" class="text-center">Нет активных счетов</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- 2. НЕАКТИВНЫЕ СЧЕТА                                          -->
    <!-- ============================================================ -->
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
            <div class="account-activity">
              <i class="fas fa-clock"></i>
              Последняя активность:
              <strong :class="getActivityClass(account.id)">
                {{ getLastActivityLabel(account.id) }}
              </strong>
            </div>
            <div class="account-actions-expanded">
              <button class="btn btn-sm btn-primary" @click="openTransferFor(account)">
                <i class="fas fa-exchange-alt"></i> Перевести
              </button>
              <button class="btn btn-sm btn-info" @click="editAccount(account)">
                <i class="fas fa-edit"></i> Редактировать
              </button>
              <button class="btn btn-sm btn-success" @click="toggleVisibility(account)">
                <i class="fas fa-eye"></i> Показать
              </button>
              <button class="btn btn-sm btn-primary" @click="openBalanceModal(account)">
                <i class="fas fa-chart-line"></i> Баланс
              </button>
              <button class="btn btn-sm btn-danger" @click="confirmDelete(account)">
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
              <th>Последняя активность</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="account in inactiveAccounts" :key="account.id">
              <td><strong>{{ account.name }}</strong></td>
              <td class="text-muted">
                <strong>{{ formatCurrency(account.balance) }}</strong>
              </td>
              <td>
                <span class="activity-cell" :class="getActivityClass(account.id)">
                  <i :class="getActivityIcon(account.id)"></i>
                  {{ getLastActivityLabel(account.id) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn btn-sm btn-primary" title="Перевести" @click="openTransferFor(account)">
                    <i class="fas fa-exchange-alt"></i>
                  </button>
                  <button class="btn btn-sm btn-info" title="Редактировать" @click="editAccount(account)">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn btn-sm btn-success" title="Показать счет" @click="toggleVisibility(account)">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn btn-sm btn-primary" title="Изменить баланс" @click="openBalanceModal(account)">
                    <i class="fas fa-chart-line"></i>
                  </button>
                  <button class="btn btn-sm btn-danger" title="Удалить" @click="confirmDelete(account)">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="inactiveAccounts.length === 0">
              <td colspan="4" class="text-center">Нет неактивных счетов</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- 3. АНАЛИТИКА (сворачиваемая)                                 -->
    <!-- ============================================================ -->
    <section class="analytics-section">
      <div
        class="analytics-section-header"
        @click="toggleAnalytics"
      >
        <div class="analytics-section-title">
          <i class="fas fa-chart-line"></i>
          <span>Аналитика</span>
          <small v-if="!analyticsExpanded" class="analytics-section-hint">
            {{ analyticsPeriodLabel }}
          </small>
        </div>
        <button
          type="button"
          class="analytics-toggle-btn"
          :aria-expanded="analyticsExpanded"
          @click.stop="toggleAnalytics"
        >
          <span>{{ analyticsExpanded ? 'Свернуть' : 'Развернуть' }}</span>
          <i :class="analyticsExpanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
        </button>
      </div>

      <div v-show="analyticsExpanded" class="analytics-section-body">
        <!-- 3.1 Метрики переводов -->
        <div v-if="analyticsLoading" class="card">
          <div class="history-loading">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Загрузка аналитики...</span>
          </div>
        </div>

        <div
          v-else-if="analyticsRaw && analyticsMetrics.count > 0"
          class="card transfer-metrics-card"
        >
          <div class="card-header">
            <h3 class="card-title">
              <i class="fas fa-calculator"></i> Метрики переводов
            </h3>
            <span class="metrics-period">
              {{ analyticsPeriodLabel }}
            </span>
          </div>

          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-label">
                <i class="fas fa-ruble-sign"></i> Средний перевод
              </div>
              <div class="metric-value">{{ formatCurrency(analyticsMetrics.average) }}</div>
            </div>

            <div class="metric-card">
              <div class="metric-label">
                <i class="fas fa-sort-amount-up"></i> Максимальный
              </div>
              <div class="metric-value text-warning">{{ formatCurrency(analyticsMetrics.max) }}</div>
            </div>

            <div class="metric-card">
              <div class="metric-label">
                <i class="fas fa-sort-amount-down"></i> Минимальный
              </div>
              <div class="metric-value">{{ formatCurrency(analyticsMetrics.min) }}</div>
            </div>

            <div class="metric-card">
              <div class="metric-label">
                <i class="fas fa-chart-bar"></i> Медиана
              </div>
              <div class="metric-value">{{ formatCurrency(analyticsMetrics.median) }}</div>
            </div>

            <div class="metric-card">
              <div class="metric-label">
                <i class="fas fa-hashtag"></i> Количество
              </div>
              <div class="metric-value">{{ analyticsMetrics.count }}</div>
            </div>

            <div class="metric-card">
              <div class="metric-label">
                <i class="fas fa-coins"></i> Общий оборот
              </div>
              <div class="metric-value text-success">
                {{ formatCurrency(analyticsMetrics.total_amount) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 3.2 Динамика баланса -->
        <div v-if="activeAccounts.length > 0" class="card balance-history-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="fas fa-chart-line"></i> Динамика баланса
            </h3>
            <div class="history-controls">
              <div class="history-range">
                <button
                  v-for="range in historyRanges"
                  :key="range.value"
                  class="range-btn"
                  :class="{ active: historyRange === range.value }"
                  @click.stop="historyRange = range.value"
                >
                  {{ range.label }}
                </button>
              </div>
              <div class="history-mode">
                <button
                  class="range-btn"
                  :class="{ active: historyMode === 'all' }"
                  @click.stop="historyMode = 'all'"
                >
                  Все счета
                </button>
                <button
                  class="range-btn"
                  :class="{ active: historyMode === 'total' }"
                  @click.stop="historyMode = 'total'"
                >
                  Только итог
                </button>
              </div>
            </div>
          </div>

          <div class="history-body">
            <div v-if="historyLoading" class="history-loading">
              <i class="fas fa-spinner fa-spin"></i>
              <span>Загрузка истории...</span>
            </div>

            <div v-else-if="historyError" class="history-error">
              <i class="fas fa-exclamation-triangle"></i>
              <span>{{ historyError }}</span>
              <button class="btn btn-sm btn-primary" @click.stop="loadBalanceHistory">
                <i class="fas fa-redo"></i> Повторить
              </button>
            </div>

            <template v-else>
              <div class="history-chart-wrapper">
                <canvas
                  ref="historyCanvas"
                  class="history-canvas"
                  @mousemove="onHistoryMouseMove"
                  @mouseleave="onHistoryMouseLeave"
                ></canvas>

                <div
                  v-if="historyTooltip.visible"
                  class="history-tooltip"
                  :style="{
                    left: historyTooltip.x + 'px',
                    top: historyTooltip.y + 'px'
                  }"
                >
                  <div class="history-tooltip-date">{{ historyTooltip.date }}</div>
                  <div
                    v-for="row in historyTooltip.rows"
                    :key="row.id"
                    class="history-tooltip-row"
                  >
                    <span class="history-tooltip-color" :style="{ background: row.color }"></span>
                    <span class="history-tooltip-name">{{ row.name }}</span>
                    <span class="history-tooltip-value">{{ formatCurrency(row.value) }}</span>
                  </div>
                  <div class="history-tooltip-total">
                    <span>Итого:</span>
                    <strong>{{ formatCurrency(historyTooltip.total) }}</strong>
                  </div>
                </div>
              </div>

              <div v-if="historyMode === 'all' && historyAccounts.length > 0" class="history-legend">
                <button
                  v-for="acc in historyAccounts"
                  :key="acc.id"
                  class="history-legend-item"
                  :class="{ 'is-off': !visibleHistoryAccounts.has(acc.id) }"
                  @click="toggleHistoryAccount(acc.id)"
                >
                  <span class="history-legend-color" :style="{ background: acc.color }"></span>
                  <span class="history-legend-name">{{ acc.name }}</span>
                  <span class="history-legend-value">
                    {{ formatCompactCurrency(acc.lastBalance) }}
                  </span>
                </button>
              </div>

              <div class="history-footer">
                <div class="history-stats">
                  <div class="history-stat">
                    <span class="history-stat-label">Изменение за период</span>
                    <span class="history-stat-value" :class="historyChangeClass">
                      {{ historyChange >= 0 ? '+' : '' }}{{ formatCurrency(historyChange) }}
                      <small>({{ historyChangePercent > 0 ? '+' : '' }}{{ historyChangePercent }}%)</small>
                    </span>
                  </div>
                  <div class="history-stat">
                    <span class="history-stat-label">Начало периода</span>
                    <span class="history-stat-value">{{ formatCurrency(historyStartBalance) }}</span>
                  </div>
                  <div class="history-stat">
                    <span class="history-stat-label">Конец периода</span>
                    <span class="history-stat-value">{{ formatCurrency(historyEndBalance) }}</span>
                  </div>
                  <div class="history-stat">
                    <span class="history-stat-label">Минимум / Максимум</span>
                    <span class="history-stat-value">
                      {{ formatCompactCurrency(historyMinTotal) }} /
                      {{ formatCompactCurrency(historyMaxTotal) }}
                    </span>
                  </div>
                </div>
                <div class="history-period-label">
                  {{ historyPeriodLabel }}
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- 3.3 Распределение + Активные/неактивные -->
        <div class="analytics-row">
          <div v-if="activeAccounts.length > 0" class="card distribution-card">
            <div class="card-header">
              <h3 class="card-title">
                <i class="fas fa-chart-pie"></i> Распределение баланса
              </h3>
              <span class="distribution-total">
                Всего: <strong>{{ formatCurrency(totalBalance) }}</strong>
              </span>
            </div>

            <div v-if="distributionData.length > 0" class="distribution-body">
              <div class="distribution-chart-wrapper">
                <canvas ref="distributionCanvas" class="distribution-canvas"></canvas>
              </div>

              <div class="distribution-legend">
                <div
                  v-for="item in distributionData"
                  :key="item.id"
                  class="legend-row"
                >
                  <span class="legend-color" :style="{ backgroundColor: item.color }"></span>
                  <span class="legend-name" :title="item.name">{{ item.name }}</span>
                  <span class="legend-value">{{ formatCurrency(item.balance) }}</span>
                  <span class="legend-percent">{{ item.percent }}%</span>
                </div>
              </div>
            </div>

            <div v-else class="distribution-empty">
              <i class="fas fa-chart-pie"></i>
              <p>Нет активных счетов с положительным балансом</p>
            </div>
          </div>

          <div v-if="accounts.length > 0" class="card accounts-ratio-card">
            <div class="card-header">
              <h3 class="card-title">
                <i class="fas fa-toggle-on"></i> Активные и неактивные
              </h3>
            </div>

            <div class="accounts-ratio-body">
              <div class="ratio-chart-wrapper">
                <canvas ref="ratioCanvas" class="ratio-canvas"></canvas>
                <div class="ratio-center-label">
                  <div class="ratio-center-percent">{{ activeRatioPercent }}%</div>
                  <div class="ratio-center-caption">активных</div>
                </div>
              </div>

              <div class="ratio-stats">
                <div class="ratio-stat-row">
                  <span class="ratio-color" style="background: #10b981;"></span>
                  <span class="ratio-label">Активные</span>
                  <span class="ratio-value">{{ activeAccounts.length }}</span>
                </div>
                <div class="ratio-stat-row">
                  <span class="ratio-color" style="background: #9ca3af;"></span>
                  <span class="ratio-label">Неактивные</span>
                  <span class="ratio-value">{{ inactiveAccounts.length }}</span>
                </div>
                <div class="ratio-stat-row total">
                  <span class="ratio-color" style="background: transparent;"></span>
                  <span class="ratio-label">Всего</span>
                  <span class="ratio-value">{{ accounts.length }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3.4 Топ счетов по обороту -->
        <div v-if="topAccountsByTurnover.length > 0" class="card top-accounts-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="fas fa-trophy"></i> Топ счетов по обороту
            </h3>
            <span class="metrics-period">входящие + исходящие переводы</span>
          </div>

          <div class="desktop-table">
            <table class="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Счёт</th>
                  <th>Входящие</th>
                  <th>Исходящие</th>
                  <th>Оборот</th>
                  <th>Переводов</th>
                  <th>Доля</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in topAccountsByTurnover" :key="item.name">
                  <td>
                    <span class="rank-badge" :class="'rank-' + Math.min(index + 1, 3)">
                      {{ index + 1 }}
                    </span>
                  </td>
                  <td><strong>{{ item.name }}</strong></td>
                  <td class="text-success">{{ formatCurrency(item.incoming) }}</td>
                  <td class="text-danger">{{ formatCurrency(item.outgoing) }}</td>
                  <td><strong>{{ formatCurrency(item.turnover) }}</strong></td>
                  <td>{{ item.count }}</td>
                  <td>
                    <div class="turnover-progress">
                      <div class="turnover-bar">
                        <div class="turnover-fill" :style="{ width: item.turnoverPercent + '%' }"></div>
                      </div>
                      <span class="turnover-percent">{{ item.turnoverPercent }}%</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mobile-cards">
            <div
              v-for="(item, index) in topAccountsByTurnover"
              :key="item.name"
              class="top-account-card"
            >
              <div class="top-account-header">
                <span class="rank-badge" :class="'rank-' + Math.min(index + 1, 3)">
                  {{ index + 1 }}
                </span>
                <span class="top-account-name">{{ item.name }}</span>
                <span class="top-account-turnover">{{ formatCurrency(item.turnover) }}</span>
              </div>
              <div class="top-account-details">
                <div class="top-detail">
                  <span class="top-detail-label">Входящие</span>
                  <span class="top-detail-value text-success">{{ formatCurrency(item.incoming) }}</span>
                </div>
                <div class="top-detail">
                  <span class="top-detail-label">Исходящие</span>
                  <span class="top-detail-value text-danger">{{ formatCurrency(item.outgoing) }}</span>
                </div>
                <div class="top-detail">
                  <span class="top-detail-label">Переводов</span>
                  <span class="top-detail-value">{{ item.count }}</span>
                </div>
                <div class="top-detail">
                  <span class="top-detail-label">Доля</span>
                  <span class="top-detail-value">{{ item.turnoverPercent }}%</span>
                </div>
              </div>
              <div class="turnover-bar mobile">
                <div class="turnover-fill" :style="{ width: item.turnoverPercent + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3.5 Топ контрагентов -->
        <div v-if="topAccountPairs.length > 0" class="card top-pairs-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="fas fa-people-arrows"></i> Топ контрагентов
            </h3>
            <span class="metrics-period">самые активные пары счёт → счёт</span>
          </div>

          <div class="desktop-table">
            <table class="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Откуда</th>
                  <th></th>
                  <th>Куда</th>
                  <th>Сумма</th>
                  <th>Переводов</th>
                  <th>Доля</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(pair, index) in topAccountPairs" :key="pair.key">
                  <td>
                    <span class="rank-badge" :class="'rank-' + Math.min(index + 1, 3)">
                      {{ index + 1 }}
                    </span>
                  </td>
                  <td>{{ pair.source }}</td>
                  <td class="pair-arrow"><i class="fas fa-arrow-right"></i></td>
                  <td>{{ pair.destination }}</td>
                  <td><strong>{{ formatCurrency(pair.amount) }}</strong></td>
                  <td>{{ pair.count }}</td>
                  <td>
                    <div class="turnover-progress">
                      <div class="turnover-bar">
                        <div class="turnover-fill" :style="{ width: pair.percent + '%' }"></div>
                      </div>
                      <span class="turnover-percent">{{ pair.percent }}%</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mobile-cards">
            <div v-for="(pair, index) in topAccountPairs" :key="pair.key" class="pair-card">
              <div class="pair-header">
                <span class="rank-badge" :class="'rank-' + Math.min(index + 1, 3)">
                  {{ index + 1 }}
                </span>
                <span class="pair-amount">{{ formatCurrency(pair.amount) }}</span>
              </div>
              <div class="pair-route">
                <span class="pair-account">{{ pair.source }}</span>
                <i class="fas fa-arrow-right pair-arrow-icon"></i>
                <span class="pair-account">{{ pair.destination }}</span>
              </div>
              <div class="pair-footer">
                <span>{{ pair.count }} переводов</span>
                <span class="pair-percent">{{ pair.percent }}%</span>
              </div>
              <div class="turnover-bar mobile">
                <div class="turnover-fill" :style="{ width: pair.percent + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3.6 Санкей -->
        <div
          v-if="sankeyData.nodes.length > 1"
          class="card sankey-card"
        >
          <div class="card-header">
            <h3 class="card-title">
              <i class="fas fa-diagram-project"></i> Потоки между счетами
            </h3>
            <span class="metrics-period">кто кому сколько перевёл</span>
          </div>

          <div class="sankey-body">
            <canvas ref="sankeyCanvas" class="sankey-canvas"></canvas>
          </div>

          <div class="sankey-footer">
            <div class="sankey-legend">
              <span class="sankey-legend-item">
                <span class="sankey-legend-color" style="background: #ef4444;"></span>
                Исходящие (слева)
              </span>
              <span class="sankey-legend-item">
                <span class="sankey-legend-color" style="background: #10b981;"></span>
                Входящие (справа)
              </span>
            </div>
            <div class="sankey-summary">
              <span>Счетов: <strong>{{ sankeyData.nodes.length }}</strong></span>
              <span>Связей: <strong>{{ sankeyData.links.length }}</strong></span>
            </div>
          </div>
        </div>

        <!-- 3.7 Активность переводов -->
        <div v-if="activityData.length > 0" class="card activity-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="fas fa-chart-column"></i> Активность переводов
            </h3>
            <div class="activity-range">
              <button
                v-for="range in activityRanges"
                :key="range.value"
                class="range-btn"
                :class="{ active: activityRange === range.value }"
                @click.stop="activityRange = range.value"
              >
                {{ range.label }}
              </button>
            </div>
          </div>

          <div class="activity-body">
            <canvas ref="activityCanvas" class="activity-canvas"></canvas>
          </div>

          <div class="activity-footer">
            <div class="activity-summary">
              <span class="activity-summary-item">
                <strong>{{ activityTotalCount }}</strong> переводов
              </span>
              <span class="activity-summary-item">
                на сумму <strong>{{ formatCurrency(activityTotalAmount) }}</strong>
              </span>
              <span v-if="activityBusiestDay" class="activity-summary-item">
                пик: <strong>{{ activityBusiestDay.label }}</strong>
                ({{ activityBusiestDay.count }} переводов)
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============================================================ -->
    <!-- 4. ПЕРЕВОДЫ                                                  -->
    <!-- ============================================================ -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-exchange-alt"></i> Переводы между счетами
        </h3>
      </div>

      <form class="transfer-form" @submit.prevent="createTransfer">
        <div class="transfer-form-grid">
          <div class="form-group">
            <label class="form-label required">Счет списания</label>
            <select v-model="transferData.source_account" class="form-control" required>
              <option value="">Выберите счет</option>
              <option v-for="account in allAccounts" :key="account.id" :value="account.id">
                {{ account.name }} ({{ formatCurrency(account.balance) }})
                <template v-if="!account.is_active"> — неактивен</template>
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Счет зачисления</label>
            <select v-model="transferData.destination_account" class="form-control" required>
              <option value="">Выберите счет</option>
              <option v-for="account in otherAccounts" :key="account.id" :value="account.id">
                {{ account.name }} ({{ formatCurrency(account.balance) }})
                <template v-if="!account.is_active"> — неактивен</template>
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Сумма перевода</label>
            <input
              v-model="transferData.amount"
              type="number"
              class="form-control"
              step="0.01"
              required
              placeholder="0.00"
            >
          </div>

          <div class="form-group">
            <label class="form-label required">Дата и время</label>
            <input
              v-model="transferData.timestamp"
              type="datetime-local"
              class="form-control"
              required
            >
          </div>
        </div>

        <div class="transfer-form-actions">
          <button type="submit" class="btn btn-primary" :disabled="transferLoading">
            <i class="fas fa-exchange-alt"></i>
            {{ transferLoading ? 'Выполняется...' : 'Выполнить перевод' }}
          </button>
        </div>
      </form>

      <div class="card-header" style="margin-top: 1.5rem;">
        <h3 class="card-title">История переводов</h3>
      </div>

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
                  <button class="btn btn-secondary btn-sm" title="Редактировать" @click="editTransfer(transfer)">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn btn-danger btn-sm" title="Удалить" @click="confirmDeleteTransfer(transfer)">
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

      <div class="mobile-cards">
        <div v-for="transfer in transfers" :key="transfer.id" class="transfer-card">
          <div class="transfer-compact" @click="toggleExpandTransfer(transfer.id)">
            <div class="compact-left">
              <div class="transfer-date-compact">{{ formatShortDate(transfer.timestamp) }}</div>
              <div class="transfer-amount-compact text-warning">
                {{ formatCurrency(transfer.amount) }}
              </div>
            </div>
            <div class="compact-right">
              <button class="expand-icon" @click.stop="toggleExpandTransfer(transfer.id)">
                <i :class="expandedTransfers.has(transfer.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>
          </div>

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
              <button class="btn btn-sm btn-info" @click="editTransfer(transfer)">
                <i class="fas fa-edit"></i> Редактировать
              </button>
              <button class="btn btn-sm btn-danger" @click="confirmDeleteTransfer(transfer)">
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

      <div v-if="totalPages > 1" class="pagination">
        <button class="btn btn-secondary" :disabled="currentPage === 1" @click="prevPage">
          <i class="fas fa-chevron-left"></i> <span class="btn-text">Назад</span>
        </button>
        <span class="page-info">Страница {{ currentPage }} из {{ totalPages }}</span>
        <button class="btn btn-secondary" :disabled="currentPage === totalPages" @click="nextPage">
          <span class="btn-text">Вперед</span> <i class="fas fa-chevron-right"></i>
        </button>
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
              v-model="formData.name"
              type="text"
              class="form-control"
              required
              placeholder="Например: Сбербанк, Наличные, Тинькофф"
            >
          </div>

          <div class="form-group">
            <label class="form-label required">Начальный баланс</label>
            <input
              v-model="formData.balance"
              type="number"
              class="form-control"
              step="0.01"
              required
              :placeholder="editingAccount ? 'Новый баланс' : '0.00'"
            >
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Отмена</button>
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
              v-model="newBalance"
              type="number"
              class="form-control"
              step="0.01"
              required
              placeholder="Введите новую сумму"
            >
          </div>

          <div v-if="balanceAccount && !balanceAccount.is_active" class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            Этот счет неактивен и не учитывается в общем балансе.
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showBalanceModal = false">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно редактирования перевода -->
    <div v-if="showEditTransferModal" class="modal" @click.self="closeEditTransferModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Редактировать перевод</h3>
          <button class="modal-close" @click="closeEditTransferModal">&times;</button>
        </div>

        <form @submit.prevent="updateTransfer">
          <div class="form-group">
            <label class="form-label required">Счет списания</label>
            <select v-model="editTransferData.source_account" class="form-control" required>
              <option value="">Выберите счет</option>
              <option v-for="account in allAccounts" :key="account.id" :value="account.id">
                {{ account.name }} ({{ formatCurrency(account.balance) }})
                <template v-if="!account.is_active"> — неактивен</template>
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Счет зачисления</label>
            <select v-model="editTransferData.destination_account" class="form-control" required>
              <option value="">Выберите счет</option>
              <option v-for="account in editOtherAccounts" :key="account.id" :value="account.id">
                {{ account.name }} ({{ formatCurrency(account.balance) }})
                <template v-if="!account.is_active"> — неактивен</template>
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Сумма перевода</label>
            <input
              v-model="editTransferData.amount"
              type="number"
              class="form-control"
              step="0.01"
              required
            >
          </div>

          <div class="form-group">
            <label class="form-label required">Дата и время</label>
            <input
              v-model="editTransferData.timestamp"
              type="datetime-local"
              class="form-control"
              required
            >
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeEditTransferModal">Отмена</button>
            <button type="submit" class="btn btn-primary">Обновить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления счета -->
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
          <button class="btn btn-secondary" @click="showDeleteModal = false">Отмена</button>
          <button class="btn btn-danger" @click="deleteAccount">Да, удалить</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления перевода -->
    <div v-if="showDeleteTransferModal" class="modal" @click.self="showDeleteTransferModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Подтверждение удаления</h3>
          <button class="modal-close" @click="showDeleteTransferModal = false">&times;</button>
        </div>
        <p>Вы уверены, что хотите удалить этот перевод?</p>
        <p class="text-muted">Сумма: {{ formatCurrency(transferToDelete?.amount) }}</p>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDeleteTransferModal = false">Отмена</button>
          <button class="btn btn-danger" @click="deleteTransfer">Да, удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import apiService from '../services/api.js'

// =============================================================================
// Константы
// =============================================================================
const SANKEY_VIRTUAL_W = 900
const SANKEY_MIN_CANVAS_WIDTH = 560
const ANALYTICS_RANGE_DAYS = 90
const ANALYTICS_EXPANDED_KEY = 'accounts:analyticsExpanded'

const DISTRIBUTION_COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1',
  '#14b8a6', '#a855f7'
]

// =============================================================================
// Утилиты
// =============================================================================
const formatDateKey = (d) => {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const toNumber = (value) => {
  const n = parseFloat(value)
  return Number.isFinite(n) ? n : 0
}

const parentWidth = (canvas, fallback = 800) => {
  const wrapper = canvas.parentElement
  return wrapper ? wrapper.clientWidth : fallback
}

const setupCanvas = (canvas, cssWidth, cssHeight) => {
  const dpr = window.devicePixelRatio || 1
  canvas.width = cssWidth * dpr
  canvas.height = cssHeight * dpr
  canvas.style.width = `${cssWidth}px`
  canvas.style.height = `${cssHeight}px`
  const ctx = canvas.getContext('2d')
  ctx.setTransform(1, 0, 0, 1, 0, 0)
  ctx.scale(dpr, dpr)
  ctx.clearRect(0, 0, cssWidth, cssHeight)
  return { ctx, cssWidth, cssHeight }
}

const setupCanvasVirtual = (canvas, virtualW, virtualH, minScale = 0.6, minWidth = 0) => {
  const measuredWidth = parentWidth(canvas, virtualW)
  const cssWidth = Math.max(measuredWidth, minWidth)
  const scale = Math.max(minScale, Math.min(1, cssWidth / virtualW))
  const cssHeight = virtualH * scale

  const dpr = window.devicePixelRatio || 1
  canvas.width = cssWidth * dpr
  canvas.height = cssHeight * dpr
  canvas.style.width = `${cssWidth}px`
  canvas.style.height = `${cssHeight}px`

  const ctx = canvas.getContext('2d')
  ctx.setTransform(1, 0, 0, 1, 0, 0)
  ctx.scale(dpr * scale, dpr * scale)
  ctx.clearRect(0, 0, virtualW, virtualH)
  return { ctx, scale, cssWidth, cssHeight }
}

const readAnalyticsExpanded = () => {
  try {
    return localStorage.getItem(ANALYTICS_EXPANDED_KEY) === 'true'
  } catch {
    return false
  }
}

const writeAnalyticsExpanded = (value) => {
  try {
    localStorage.setItem(ANALYTICS_EXPANDED_KEY, value ? 'true' : 'false')
  } catch {
    /* no-op */
  }
}

export default {
  name: 'AccountsAndTransfers',

  setup() {
    // =========================================================================
    // Состояние — счета
    // =========================================================================
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

    const formData = ref({ name: '', balance: 0, is_active: true })

    // =========================================================================
    // Computed — счета
    // =========================================================================
    const activeAccounts = computed(() => accounts.value.filter((a) => a.is_active))
    const inactiveAccounts = computed(() => accounts.value.filter((a) => !a.is_active))
    const allAccounts = computed(() => accounts.value)
    const activeAccountsCount = computed(() => activeAccounts.value.length)

    const totalBalance = computed(() =>
      activeAccounts.value.reduce((sum, a) => sum + toNumber(a.balance), 0)
    )

    // =========================================================================
    // Состояние — сворачивание аналитики
    // =========================================================================
    const analyticsExpanded = ref(readAnalyticsExpanded())

    const toggleAnalytics = () => {
      analyticsExpanded.value = !analyticsExpanded.value
      writeAnalyticsExpanded(analyticsExpanded.value)
      if (analyticsExpanded.value) {
        // Перерисовываем canvas'ы после того, как Vue отрендерит блок
        scheduleAllDraws()
      }
    }

    // =========================================================================
    // Состояние — динамика баланса (2.1)
    // =========================================================================
    const historyCanvas = ref(null)
    const historyRange = ref(30)
    const historyRanges = [
      { value: 7, label: '7 дней' },
      { value: 30, label: '30 дней' },
      { value: 90, label: '90 дней' },
      { value: 180, label: '180 дней' }
    ]
    const historyMode = ref('all')
    const historyLoading = ref(false)
    const historyError = ref('')
    const historyRawData = ref(null)
    const visibleHistoryAccounts = ref(new Set())
    const historyChartMetrics = ref({
      paddingLeft: 60, paddingRight: 20, paddingTop: 20, paddingBottom: 40
    })

    const historyTooltip = ref({
      visible: false, x: 0, y: 0, date: '', rows: [], total: 0
    })

    const historyAccounts = computed(() => {
      if (!historyRawData.value?.accounts) return []
      return historyRawData.value.accounts.map((acc, index) => {
        const series = historyRawData.value.results.map((r) => ({
          date: r.date,
          value: toNumber(r.accounts[String(acc.id)])
        }))
        return {
          id: acc.id,
          name: acc.name,
          color: DISTRIBUTION_COLORS[index % DISTRIBUTION_COLORS.length],
          series,
          lastBalance: series.length > 0 ? series[series.length - 1].value : 0
        }
      })
    })

    const historyTotalSeries = computed(() => {
      if (!historyRawData.value?.results) return []
      return historyRawData.value.results.map((r) => ({
        date: r.date,
        value: toNumber(r.total)
      }))
    })

    const historyStartBalance = computed(() => {
      const s = historyTotalSeries.value
      return s.length > 0 ? s[0].value : 0
    })

    const historyEndBalance = computed(() => {
      const s = historyTotalSeries.value
      return s.length > 0 ? s[s.length - 1].value : 0
    })

    const historyChange = computed(() => historyEndBalance.value - historyStartBalance.value)

    const historyChangePercent = computed(() => {
      if (historyStartBalance.value === 0) return 0
      return ((historyChange.value / Math.abs(historyStartBalance.value)) * 100).toFixed(1)
    })

    const historyChangeClass = computed(() => {
      if (historyChange.value > 0) return 'text-success'
      if (historyChange.value < 0) return 'text-danger'
      return ''
    })

    const historyMinTotal = computed(() => {
      const s = historyTotalSeries.value
      return s.length === 0 ? 0 : Math.min(...s.map((p) => p.value))
    })

    const historyMaxTotal = computed(() => {
      const s = historyTotalSeries.value
      return s.length === 0 ? 0 : Math.max(...s.map((p) => p.value))
    })

    const historyPeriodLabel = computed(() => {
      const results = historyRawData.value?.results
      if (!results?.length) return ''
      const first = results[0].date
      const last = results[results.length - 1].date
      return `${formatDateShortLabel(first)} — ${formatDateShortLabel(last)}`
    })

    const formatDateShortLabel = (iso) => {
      if (!iso) return ''
      return new Date(iso).toLocaleDateString('ru-RU', {
        day: '2-digit', month: '2-digit', year: 'numeric'
      })
    }

    // =========================================================================
    // Состояние — распределение (1.1) и соотношение (1.5)
    // =========================================================================
    const distributionCanvas = ref(null)
    const ratioCanvas = ref(null)

    const distributionData = computed(() => {
      const active = activeAccounts.value.filter((a) => toNumber(a.balance) > 0)
      const total = active.reduce((sum, a) => sum + toNumber(a.balance), 0)
      if (total === 0) return []
      return active
        .map((acc, index) => {
          const balance = toNumber(acc.balance)
          return {
            id: acc.id,
            name: acc.name,
            balance,
            percent: ((balance / total) * 100).toFixed(1),
            color: DISTRIBUTION_COLORS[index % DISTRIBUTION_COLORS.length]
          }
        })
        .sort((a, b) => b.balance - a.balance)
    })

    const activeRatioPercent = computed(() => {
      if (accounts.value.length === 0) return 0
      return ((activeAccounts.value.length / accounts.value.length) * 100).toFixed(0)
    })

    // =========================================================================
    // Состояние — переводы (только для таблицы истории)
    // =========================================================================
    const transfers = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalCount = ref(0)
    const transferLoading = ref(false)
    const showEditTransferModal = ref(false)
    const showDeleteTransferModal = ref(false)
    const editingTransfer = ref(null)
    const transferToDelete = ref(null)
    const expandedTransfers = ref(new Set())

    const transferData = ref({
      source_account: '',
      destination_account: '',
      amount: '',
      timestamp: new Date().toISOString().slice(0, 16)
    })

    const editTransferData = ref({
      source_account: '',
      destination_account: '',
      amount: '',
      timestamp: ''
    })

    const otherAccounts = computed(() => {
      if (!transferData.value.source_account) return allAccounts.value
      return allAccounts.value.filter((a) => a.id !== transferData.value.source_account)
    })

    const editOtherAccounts = computed(() => {
      if (!editTransferData.value.source_account) return allAccounts.value
      return allAccounts.value.filter((a) => a.id !== editTransferData.value.source_account)
    })

    const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

    // =========================================================================
    // Состояние — аналитика переводов (с бэкенда)
    // =========================================================================
    const analyticsRaw = ref(null)
    const analyticsLoading = ref(false)
    const analyticsError = ref('')

    const analyticsMetrics = computed(() => {
      return analyticsRaw.value?.metrics || {
        count: 0,
        total_amount: 0,
        average: 0,
        median: 0,
        max: 0,
        min: 0,
      }
    })

    const analyticsPeriodLabel = computed(() => {
      const period = analyticsRaw.value?.period
      if (!period) return `за последние ${ANALYTICS_RANGE_DAYS} дней`
      const from = new Date(period.date_from).toLocaleDateString('ru-RU', {
        day: '2-digit', month: '2-digit', year: 'numeric'
      })
      const to = new Date(period.date_to).toLocaleDateString('ru-RU', {
        day: '2-digit', month: '2-digit', year: 'numeric'
      })
      return `за период ${from} — ${to}`
    })

    const topAccountsByTurnover = computed(() => {
      const list = analyticsRaw.value?.top_accounts || []
      return list.map((item) => ({
        name: item.name,
        incoming: item.incoming,
        outgoing: item.outgoing,
        turnover: item.turnover,
        count: item.count,
        turnoverPercent: item.turnover_percent.toFixed(1),
      }))
    })

    const topAccountPairs = computed(() => {
      const list = analyticsRaw.value?.top_pairs || []
      return list.map((item) => ({
        key: item.key,
        source: item.source,
        destination: item.destination,
        amount: item.amount,
        count: item.count,
        percent: item.percent.toFixed(1),
      }))
    })

    const sankeyCanvas = ref(null)

    const sankeyData = computed(() => {
      const raw = analyticsRaw.value?.sankey
      if (!raw || raw.nodes.length < 2) return { nodes: [], links: [] }

      const idToName = new Map(raw.nodes.map((n) => [n.id, n.name]))

      return {
        nodes: raw.nodes.map((n) => ({
          name: n.name,
          incoming: n.incoming,
          outgoing: n.outgoing,
          total: n.total,
        })),
        links: raw.links.map((l) => ({
          source: idToName.get(l.source) || '',
          destination: idToName.get(l.destination) || '',
          amount: l.amount,
        })),
      }
    })

    // =========================================================================
    // Состояние — активность (1.3)
    // =========================================================================
    const activityCanvas = ref(null)
    const activityRange = ref(30)
    const activityRanges = [
      { value: 7, label: '7 дней' },
      { value: 14, label: '14 дней' },
      { value: 30, label: '30 дней' },
      { value: 90, label: '90 дней' }
    ]

    const activityData = computed(() => {
      const raw = analyticsRaw.value?.daily_activity || []
      const days = activityRange.value
      const sliced = raw.slice(-days)
      return sliced.map((d) => ({
        date: new Date(d.date),
        dateKey: d.date,
        count: d.count,
        amount: d.amount,
      }))
    })

    const activityTotalCount = computed(() =>
      activityData.value.reduce((s, d) => s + d.count, 0)
    )

    const activityTotalAmount = computed(() =>
      activityData.value.reduce((s, d) => s + d.amount, 0)
    )

    const activityBusiestDay = computed(() => {
      if (activityData.value.length === 0) return null
      const max = activityData.value.reduce(
        (best, d) => (d.count > best.count ? d : best),
        activityData.value[0]
      )
      if (max.count === 0) return null
      const label = max.date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
      return { ...max, label }
    })

    // =========================================================================
    // Последняя активность по счетам — из таблицы истории
    // =========================================================================
    const accountLastActivity = computed(() => {
      const map = new Map()
      transfers.value.forEach((t) => {
        if (!t.timestamp) return
        const time = new Date(t.timestamp).getTime()
        if (Number.isNaN(time)) return
        const names = [t.source_account_name, t.destination_account_name]
        names.forEach((name) => {
          if (!name) return
          if (!map.has(name) || map.get(name) < time) map.set(name, time)
        })
      })
      return map
    })

    const getLastActivityTime = (accountId) => {
      const account = accounts.value.find((a) => a.id === accountId)
      if (!account) return null
      return accountLastActivity.value.get(account.name) || null
    }

    const getLastActivityLabel = (accountId) => {
      const time = getLastActivityTime(accountId)
      if (!time) return 'Никогда'
      const days = Math.floor((Date.now() - time) / (1000 * 60 * 60 * 24))
      if (days === 0) return 'Сегодня'
      if (days === 1) return 'Вчера'
      if (days < 7) return `${days} дн. назад`
      if (days < 30) return `${Math.floor(days / 7)} нед. назад`
      if (days < 365) return `${Math.floor(days / 30)} мес. назад`
      return `${Math.floor(days / 365)} г. назад`
    }

    const getActivityClass = (accountId) => {
      const time = getLastActivityTime(accountId)
      if (!time) return 'activity-never'
      const days = (Date.now() - time) / (1000 * 60 * 60 * 24)
      if (days <= 7) return 'activity-recent'
      if (days <= 30) return 'activity-medium'
      return 'activity-old'
    }

    const getActivityIcon = (accountId) => {
      const time = getLastActivityTime(accountId)
      if (!time) return 'fas fa-circle-xmark'
      const days = (Date.now() - time) / (1000 * 60 * 60 * 24)
      if (days <= 7) return 'fas fa-circle-check'
      if (days <= 30) return 'fas fa-clock'
      return 'fas fa-triangle-exclamation'
    }

    // =========================================================================
    // Отрисовка графиков
    // =========================================================================

    const drawHistoryChart = () => {
      const canvas = historyCanvas.value
      if (!canvas) return
      const totalSeries = historyTotalSeries.value

      if (totalSeries.length === 0) {
        setupCanvas(canvas, parentWidth(canvas, 900), 100)
        return
      }

      const cssWidth = parentWidth(canvas, 900)
      const cssHeight = 320
      const { ctx } = setupCanvas(canvas, cssWidth, cssHeight)

      const paddingLeft = 60
      const paddingRight = 20
      const paddingTop = 20
      const paddingBottom = 40
      historyChartMetrics.value = { paddingLeft, paddingRight, paddingTop, paddingBottom }

      const chartWidth = cssWidth - paddingLeft - paddingRight
      const chartHeight = cssHeight - paddingTop - paddingBottom

      const visibleSeries = []
      if (historyMode.value === 'total') {
        visibleSeries.push({
          id: 'total', name: 'Итого', color: '#3b82f6',
          series: totalSeries, isTotal: true
        })
      } else {
        historyAccounts.value.forEach((acc) => {
          if (visibleHistoryAccounts.value.has(acc.id)) {
            visibleSeries.push({
              id: acc.id, name: acc.name, color: acc.color,
              series: acc.series, isTotal: false
            })
          }
        })
        visibleSeries.push({
          id: 'total', name: 'Итого', color: '#111827',
          series: totalSeries, isTotal: true
        })
      }

      const allValues = visibleSeries.flatMap((s) => s.series.map((p) => p.value))
      let minValue = Math.min(...allValues, 0)
      let maxValue = Math.max(...allValues, 0)
      const range = maxValue - minValue || 1
      minValue -= range * 0.05
      maxValue += range * 0.05

      const xStep = totalSeries.length > 1 ? chartWidth / (totalSeries.length - 1) : 0
      const yScale = (v) =>
        paddingTop + chartHeight - ((v - minValue) / (maxValue - minValue)) * chartHeight

      ctx.strokeStyle = '#e5e7eb'
      ctx.lineWidth = 1
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.fillStyle = '#9ca3af'
      ctx.textAlign = 'right'
      ctx.textBaseline = 'middle'

      for (let i = 0; i <= 5; i++) {
        const y = paddingTop + chartHeight - (i / 5) * chartHeight
        ctx.beginPath()
        ctx.moveTo(paddingLeft, y)
        ctx.lineTo(cssWidth - paddingRight, y)
        ctx.stroke()
        ctx.fillText(formatCompactCurrency(minValue + ((maxValue - minValue) / 5) * i), paddingLeft - 6, y)
      }

      if (minValue < 0 && maxValue > 0) {
        const y0 = yScale(0)
        ctx.strokeStyle = '#9ca3af'
        ctx.setLineDash([4, 4])
        ctx.beginPath()
        ctx.moveTo(paddingLeft, y0)
        ctx.lineTo(cssWidth - paddingRight, y0)
        ctx.stroke()
        ctx.setLineDash([])
      }

      visibleSeries.forEach((s) => {
        if (s.series.length === 0) return
        ctx.beginPath()
        ctx.strokeStyle = s.color
        ctx.lineWidth = s.isTotal ? 3 : 1.75
        ctx.lineJoin = 'round'
        ctx.lineCap = 'round'

        s.series.forEach((p, i) => {
          const x = paddingLeft + i * xStep
          const y = yScale(p.value)
          if (i === 0) ctx.moveTo(x, y)
          else ctx.lineTo(x, y)
        })
        ctx.stroke()

        if (s.series.length <= 40) {
          s.series.forEach((p, i) => {
            const x = paddingLeft + i * xStep
            const y = yScale(p.value)
            ctx.beginPath()
            ctx.fillStyle = s.color
            ctx.arc(x, y, s.isTotal ? 3 : 2, 0, 2 * Math.PI)
            ctx.fill()
          })
        }
      })

      ctx.fillStyle = '#6b7280'
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'top'

      const MIN_LABEL_SPACING = 36
      const maxLabels = Math.max(2, Math.floor(chartWidth / MIN_LABEL_SPACING))
      const step = Math.max(1, Math.ceil(totalSeries.length / maxLabels))

      let lastLabelX = -Infinity
      totalSeries.forEach((p, i) => {
        const isFirst = i === 0
        const isLast = i === totalSeries.length - 1
        const showByStep = i % step === 0
        if (!isFirst && !isLast && !showByStep) return

        const x = paddingLeft + i * xStep
        if (x - lastLabelX < MIN_LABEL_SPACING * 0.9) {
          if (!isFirst) return
        }

        const label = new Date(p.date).toLocaleDateString('ru-RU', {
          day: '2-digit', month: '2-digit'
        })
        ctx.fillText(label, x, paddingTop + chartHeight + 8)
        lastLabelX = x
      })
    }

    const onHistoryMouseMove = (event) => {
      const canvas = historyCanvas.value
      if (!canvas) return
      const totalSeries = historyTotalSeries.value
      if (totalSeries.length === 0) return

      const rect = canvas.getBoundingClientRect()
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top

      const { paddingLeft, paddingRight } = historyChartMetrics.value
      const chartWidth = rect.width - paddingLeft - paddingRight

      if (x < paddingLeft || x > rect.width - paddingRight) {
        historyTooltip.value.visible = false
        return
      }

      const xStep = totalSeries.length > 1 ? chartWidth / (totalSeries.length - 1) : 0
      const idx = Math.round((x - paddingLeft) / xStep)
      const clampedIdx = Math.max(0, Math.min(totalSeries.length - 1, idx))
      const point = totalSeries[clampedIdx]

      const rows = []
      if (historyMode.value === 'total') {
        rows.push({ id: 'total', name: 'Итого', color: '#3b82f6', value: point.value })
      } else {
        historyAccounts.value.forEach((acc) => {
          if (!visibleHistoryAccounts.value.has(acc.id)) return
          const p = acc.series[clampedIdx]
          if (p) {
            rows.push({ id: acc.id, name: acc.name, color: acc.color, value: p.value })
          }
        })
      }

      historyTooltip.value = {
        visible: true,
        x,
        y,
        date: new Date(point.date).toLocaleDateString('ru-RU', {
          day: '2-digit', month: '2-digit', year: 'numeric'
        }),
        rows,
        total: point.value
      }
    }

    const onHistoryMouseLeave = () => {
      historyTooltip.value.visible = false
    }

    const drawDistributionChart = () => {
      const canvas = distributionCanvas.value
      if (!canvas) return
      const data = distributionData.value
      const wrapper = canvas.parentElement
      const size = wrapper ? Math.min(wrapper.clientWidth, 320) : 280

      if (data.length === 0) {
        setupCanvas(canvas, size, size)
        return
      }

      const { ctx } = setupCanvas(canvas, size, size)

      const centerX = size / 2
      const centerY = size / 2
      const radius = size / 2 - 20

      let startAngle = -Math.PI / 2
      data.forEach((item) => {
        const percent = parseFloat(item.percent) / 100
        const angle = percent * 2 * Math.PI
        const endAngle = startAngle + angle

        ctx.beginPath()
        ctx.fillStyle = item.color
        ctx.moveTo(centerX, centerY)
        ctx.arc(centerX, centerY, radius, startAngle, endAngle)
        ctx.closePath()
        ctx.fill()

        ctx.strokeStyle = '#ffffff'
        ctx.lineWidth = 2
        ctx.stroke()

        if (percent > 0.08) {
          const midAngle = startAngle + angle / 2
          const textRadius = radius * 0.68
          const x = centerX + Math.cos(midAngle) * textRadius
          const y = centerY + Math.sin(midAngle) * textRadius

          ctx.fillStyle = '#ffffff'
          ctx.font = `bold ${size < 260 ? 11 : 13}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.shadowColor = 'rgba(0,0,0,0.3)'
          ctx.shadowBlur = 3
          ctx.fillText(`${item.percent}%`, x, y)
          ctx.shadowBlur = 0
        }

        startAngle = endAngle
      })
    }

    const drawRatioChart = () => {
      const canvas = ratioCanvas.value
      if (!canvas) return
      const total = accounts.value.length
      const wrapper = canvas.parentElement
      const size = wrapper ? Math.min(wrapper.clientWidth, 200) : 180

      if (total === 0) {
        setupCanvas(canvas, size, size)
        return
      }

      const { ctx } = setupCanvas(canvas, size, size)

      const centerX = size / 2
      const centerY = size / 2
      const radius = size / 2 - 15

      const activePercent = activeAccounts.value.length / total
      const inactivePercent = inactiveAccounts.value.length / total

      const activeAngle = activePercent * 2 * Math.PI
      ctx.beginPath()
      ctx.fillStyle = '#10b981'
      ctx.moveTo(centerX, centerY)
      ctx.arc(centerX, centerY, radius, -Math.PI / 2, -Math.PI / 2 + activeAngle)
      ctx.closePath()
      ctx.fill()

      const inactiveAngle = inactivePercent * 2 * Math.PI
      ctx.beginPath()
      ctx.fillStyle = '#9ca3af'
      ctx.moveTo(centerX, centerY)
      ctx.arc(
        centerX, centerY, radius,
        -Math.PI / 2 + activeAngle,
        -Math.PI / 2 + activeAngle + inactiveAngle
      )
      ctx.closePath()
      ctx.fill()

      ctx.beginPath()
      ctx.fillStyle = '#ffffff'
      ctx.arc(centerX, centerY, radius * 0.6, 0, 2 * Math.PI)
      ctx.fill()
    }

    const drawSankey = () => {
      const canvas = sankeyCanvas.value
      if (!canvas) return
      const { nodes, links } = sankeyData.value

      if (nodes.length < 2) {
        setupCanvas(canvas, parentWidth(canvas, 900), 100)
        return
      }

      const VIRTUAL_W = SANKEY_VIRTUAL_W
      const VIRTUAL_H = Math.max(520, nodes.length * 90)

      const { ctx } = setupCanvasVirtual(
        canvas,
        VIRTUAL_W,
        VIRTUAL_H,
        0.6,
        SANKEY_MIN_CANVAS_WIDTH
      )

      const paddingX = 130
      const paddingY = 30
      const nodeWidth = 22
      const nodeGap = 18
      const chartHeight = VIRTUAL_H - paddingY * 2

      const sources = nodes.filter((n) => n.outgoing > 0)
      const destinations = nodes.filter((n) => n.incoming > 0)

      const totalOutgoing = sources.reduce((s, n) => s + n.outgoing, 0) || 1
      const totalIncoming = destinations.reduce((s, n) => s + n.incoming, 0) || 1

      const sourcesGaps = Math.max(0, sources.length - 1) * nodeGap
      const destsGaps = Math.max(0, destinations.length - 1) * nodeGap
      const sourceScale = (chartHeight - sourcesGaps) / totalOutgoing
      const destScale = (chartHeight - destsGaps) / totalIncoming

      const MIN_NODE_H = 36

      const sourcePositions = new Map()
      let yOffset = paddingY
      sources.forEach((n) => {
        const h = Math.max(MIN_NODE_H, n.outgoing * sourceScale)
        sourcePositions.set(n.name, { x: paddingX, y: yOffset, h, node: n })
        yOffset += h + nodeGap
      })

      const destPositions = new Map()
      yOffset = paddingY
      destinations.forEach((n) => {
        const h = Math.max(MIN_NODE_H, n.incoming * destScale)
        destPositions.set(n.name, { x: VIRTUAL_W - paddingX - nodeWidth, y: yOffset, h, node: n })
        yOffset += h + nodeGap
      })

      const sourceOffsets = new Map()
      sources.forEach((s) => sourceOffsets.set(s.name, 0))
      const destOffsets = new Map()
      destinations.forEach((d) => destOffsets.set(d.name, 0))

      const sortedLinks = [...links].sort((a, b) => {
        const aSrcIdx = sources.findIndex((s) => s.name === a.source)
        const bSrcIdx = sources.findIndex((s) => s.name === b.source)
        if (aSrcIdx !== bSrcIdx) return aSrcIdx - bSrcIdx
        return b.amount - a.amount
      })

      sortedLinks.forEach((link) => {
        const srcPos = sourcePositions.get(link.source)
        const dstPos = destPositions.get(link.destination)
        if (!srcPos || !dstPos) return

        const srcH = (link.amount / srcPos.node.outgoing) * srcPos.h
        const dstH = (link.amount / dstPos.node.incoming) * dstPos.h

        const srcY = srcPos.y + sourceOffsets.get(link.source)
        const dstY = dstPos.y + destOffsets.get(link.destination)

        sourceOffsets.set(link.source, sourceOffsets.get(link.source) + srcH)
        destOffsets.set(link.destination, destOffsets.get(link.destination) + dstH)

        const x1 = srcPos.x + nodeWidth
        const x2 = dstPos.x
        const midX = (x1 + x2) / 2

        ctx.beginPath()
        ctx.moveTo(x1, srcY)
        ctx.bezierCurveTo(midX, srcY, midX, dstY, x2, dstY)
        ctx.lineTo(x2, dstY + dstH)
        ctx.bezierCurveTo(midX, dstY + dstH, midX, srcY + srcH, x1, srcY + srcH)
        ctx.closePath()

        const gradient = ctx.createLinearGradient(x1, 0, x2, 0)
        gradient.addColorStop(0, 'rgba(239, 68, 68, 0.55)')
        gradient.addColorStop(1, 'rgba(16, 185, 129, 0.55)')
        ctx.fillStyle = gradient
        ctx.fill()

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)'
        ctx.lineWidth = 0.75
        ctx.stroke()
      })

      const drawNode = (name, pos, color, sign, value) => {
        const isSource = sign === '−'

        ctx.font = 'bold 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        const label = name.length > 16 ? name.slice(0, 15) + '…' : name
        const labelW = ctx.measureText(label).width

        ctx.font = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        const subLabel = `${sign}${formatCompactCurrency(value)} ₽`
        const subLabelW = ctx.measureText(subLabel).width
        const maxLabelW = Math.max(labelW, subLabelW)

        const padding = 6
        const bgW = maxLabelW + padding * 2
        const bgH = 34
        const bgX = isSource
          ? pos.x - nodeWidth - 8 - bgW
          : pos.x + nodeWidth + 8
        const bgY = pos.y + pos.h / 2 - bgH / 2

        ctx.fillStyle = 'rgba(255, 255, 255, 0.92)'
        ctx.beginPath()
        const r = 6
        ctx.moveTo(bgX + r, bgY)
        ctx.arcTo(bgX + bgW, bgY, bgX + bgW, bgY + bgH, r)
        ctx.arcTo(bgX + bgW, bgY + bgH, bgX, bgY + bgH, r)
        ctx.arcTo(bgX, bgY + bgH, bgX, bgY, r)
        ctx.arcTo(bgX, bgY, bgX + bgW, bgY, r)
        ctx.closePath()
        ctx.fill()

        ctx.fillStyle = color
        ctx.fillRect(pos.x, pos.y, nodeWidth, pos.h)

        ctx.fillStyle = '#1f2937'
        ctx.font = 'bold 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        ctx.textAlign = isSource ? 'right' : 'left'
        ctx.textBaseline = 'middle'
        const labelX = isSource
          ? pos.x - nodeWidth - 8 - padding
          : pos.x + nodeWidth + 8 + padding
        ctx.fillText(label, labelX, pos.y + pos.h / 2 - 6)

        ctx.fillStyle = '#6b7280'
        ctx.font = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        ctx.fillText(subLabel, labelX, pos.y + pos.h / 2 + 8)
      }

      sources.forEach((n) => {
        drawNode(n.name, sourcePositions.get(n.name), '#ef4444', '−', n.outgoing)
      })
      destinations.forEach((n) => {
        drawNode(n.name, destPositions.get(n.name), '#10b981', '+', n.incoming)
      })
    }

    const drawActivityChart = () => {
      const canvas = activityCanvas.value
      if (!canvas) return
      const data = activityData.value
      const cssWidth = parentWidth(canvas, 800)
      const cssHeight = 260
      const { ctx } = setupCanvas(canvas, cssWidth, cssHeight)

      if (data.length === 0) return

      const paddingLeft = 50
      const paddingRight = 20
      const paddingTop = 30
      const paddingBottom = 40
      const chartWidth = cssWidth - paddingLeft - paddingRight
      const chartHeight = cssHeight - paddingTop - paddingBottom
      const maxAmount = Math.max(...data.map((d) => d.amount), 1)
      const barWidth = chartWidth / data.length
      const barGap = Math.min(4, barWidth * 0.2)

      ctx.strokeStyle = '#e5e7eb'
      ctx.lineWidth = 1
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.fillStyle = '#9ca3af'
      ctx.textAlign = 'right'
      ctx.textBaseline = 'middle'

      for (let i = 0; i <= 4; i++) {
        const y = paddingTop + chartHeight - (i / 4) * chartHeight
        ctx.beginPath()
        ctx.moveTo(paddingLeft, y)
        ctx.lineTo(cssWidth - paddingRight, y)
        ctx.stroke()
        ctx.fillText(formatCompactCurrency((maxAmount / 4) * i), paddingLeft - 6, y)
      }

      data.forEach((d, i) => {
        const x = paddingLeft + i * barWidth + barGap / 2
        const w = barWidth - barGap
        const h = maxAmount > 0 ? (d.amount / maxAmount) * chartHeight : 0
        const y = paddingTop + chartHeight - h

        if (d.count === 0) {
          ctx.fillStyle = '#f3f4f6'
          ctx.fillRect(x, paddingTop + chartHeight - 2, w, 2)
          return
        }

        const gradient = ctx.createLinearGradient(0, y, 0, paddingTop + chartHeight)
        gradient.addColorStop(0, '#3b82f6')
        gradient.addColorStop(1, '#93c5fd')
        ctx.fillStyle = gradient

        const r = Math.min(4, w / 2, h)
        ctx.beginPath()
        ctx.moveTo(x, y + r)
        ctx.arcTo(x, y, x + r, y, r)
        ctx.lineTo(x + w - r, y)
        ctx.arcTo(x + w, y, x + w, y + r, r)
        ctx.lineTo(x + w, paddingTop + chartHeight)
        ctx.lineTo(x, paddingTop + chartHeight)
        ctx.closePath()
        ctx.fill()

        if (d.count > 0 && barWidth > 16) {
          ctx.fillStyle = '#1f2937'
          ctx.font = 'bold 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
          ctx.textAlign = 'center'
          ctx.textBaseline = 'bottom'
          ctx.fillText(String(d.count), x + w / 2, y - 2)
        }
      })

      ctx.fillStyle = '#6b7280'
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'top'
      const labelStep = Math.max(1, Math.ceil(data.length / 10))
      data.forEach((d, i) => {
        if (i % labelStep !== 0 && i !== data.length - 1) return
        const x = paddingLeft + i * barWidth + barWidth / 2
        const label = d.date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
        ctx.fillText(label, x, paddingTop + chartHeight + 8)
      })
    }

    // =========================================================================
    // Расписание перерисовок
    // =========================================================================
    const scheduleHistoryDraw = () => {
      nextTick(() => setTimeout(drawHistoryChart, 50))
    }

    const scheduleAllDraws = () => {
      nextTick(() => {
        setTimeout(() => {
          drawDistributionChart()
          drawRatioChart()
          drawActivityChart()
          drawSankey()
          drawHistoryChart()
        }, 50)
      })
    }

    // =========================================================================
    // Загрузка данных
    // =========================================================================
    const loadBalanceHistory = async () => {
      historyLoading.value = true
      historyError.value = ''
      try {
        const dateTo = new Date()
        const dateFrom = new Date()
        dateFrom.setDate(dateFrom.getDate() - historyRange.value + 1)

        const data = await apiService.getBalanceHistory(
          formatDateKey(dateFrom),
          formatDateKey(dateTo)
        )
        historyRawData.value = data
        scheduleHistoryDraw()
      } catch (error) {
        console.error('Error loading balance history:', error)
        historyError.value = 'Не удалось загрузить историю баланса. Проверьте соединение.'
        historyRawData.value = null
      } finally {
        historyLoading.value = false
      }
    }

    const loadAccounts = async () => {
      loading.value = true
      try {
        const data = await apiService.getAccounts(1, 100)
        if (data.results && Array.isArray(data.results)) {
          accounts.value = data.results[0]?.accounts || data.results
        } else if (Array.isArray(data)) {
          accounts.value = data
        } else if (data.accounts) {
          accounts.value = data.accounts
        } else {
          accounts.value = []
        }
        scheduleAllDraws()
      } catch (error) {
        console.error('Error loading accounts:', error)
        alert('Ошибка при загрузке счетов')
        accounts.value = []
      } finally {
        loading.value = false
      }
    }

    const loadTransfers = async () => {
      try {
        const data = await apiService.getTransferHistory(currentPage.value, pageSize.value)
        transfers.value = data.results || []
        totalCount.value = data.count || 0
        scheduleAllDraws()
      } catch (error) {
        console.error('Error loading transfers:', error)
        transfers.value = []
        totalCount.value = 0
      }
    }

    const loadTransferAnalytics = async () => {
      analyticsLoading.value = true
      analyticsError.value = ''
      try {
        const dateTo = new Date()
        const dateFrom = new Date()
        dateFrom.setDate(dateFrom.getDate() - ANALYTICS_RANGE_DAYS + 1)

        const data = await apiService.getTransferAnalytics(
          formatDateKey(dateFrom),
          formatDateKey(dateTo)
        )
        analyticsRaw.value = data
        scheduleAllDraws()
      } catch (error) {
        console.error('Error loading transfer analytics:', error)
        analyticsError.value = 'Не удалось загрузить аналитику переводов'
        analyticsRaw.value = null
      } finally {
        analyticsLoading.value = false
      }
    }

    // =========================================================================
    // Переключения видимости
    // =========================================================================
    const toggleHistoryAccount = (accountId) => {
      const s = new Set(visibleHistoryAccounts.value)
      if (s.has(accountId)) s.delete(accountId)
      else s.add(accountId)
      visibleHistoryAccounts.value = s
      scheduleHistoryDraw()
    }

    const toggleExpand = (accountId) => {
      const s = new Set(expandedAccounts.value)
      if (s.has(accountId)) s.delete(accountId)
      else s.add(accountId)
      expandedAccounts.value = s
    }

    const toggleExpandTransfer = (transferId) => {
      const s = new Set(expandedTransfers.value)
      if (s.has(transferId)) s.delete(transferId)
      else s.add(transferId)
      expandedTransfers.value = s
    }

    // =========================================================================
    // Действия со счетами
    // =========================================================================
    const openCreateModal = () => {
      editingAccount.value = null
      formData.value = { name: '', balance: 0, is_active: true }
      showAccountModal.value = true
    }

    const editAccount = (account) => {
      editingAccount.value = account
      formData.value = {
        name: account.name,
        balance: toNumber(account.balance),
        is_active: account.is_active
      }
      showAccountModal.value = true
    }

    const closeModal = () => {
      showAccountModal.value = false
      editingAccount.value = null
      formData.value = { name: '', balance: 0, is_active: true }
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
        await loadBalanceHistory()
      } catch (error) {
        console.error('Error saving account:', error)
        alert('Ошибка при сохранении счета')
      }
    }

    const toggleVisibility = async (account) => {
      try {
        await apiService.toggleAccountActive(account.id, !account.is_active)
        await loadAccounts()
        await loadBalanceHistory()
      } catch (error) {
        console.error('Error toggling account visibility:', error)
        alert('Ошибка при изменении видимости счета')
      }
    }

    const openBalanceModal = (account) => {
      balanceAccount.value = account
      newBalance.value = toNumber(account.balance)
      showBalanceModal.value = true
    }

    const updateBalance = async () => {
      try {
        await apiService.patchAccount(balanceAccount.value.id, { balance: newBalance.value })
        showBalanceModal.value = false
        await loadAccounts()
        await loadBalanceHistory()
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
        await loadBalanceHistory()
      } catch (error) {
        console.error('Error deleting account:', error)
        alert('Ошибка при удалении счета')
      }
    }

    // =========================================================================
    // Действия с переводами
    // =========================================================================
    const openTransferFor = (account) => {
      transferData.value = {
        source_account: account.id,
        destination_account: '',
        amount: '',
        timestamp: new Date().toISOString().slice(0, 16)
      }
      setTimeout(() => {
        document.querySelector('.transfer-form')?.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        })
      }, 100)
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
      transferLoading.value = true
      try {
        await apiService.createTransfer(
          transferData.value.source_account,
          transferData.value.destination_account,
          parseFloat(transferData.value.amount),
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
        await loadTransferAnalytics()
        await loadBalanceHistory()
      } catch (error) {
        console.error('Error creating transfer:', error)
        alert('Ошибка при создании перевода: ' + (error.message || 'Неизвестная ошибка'))
      } finally {
        transferLoading.value = false
      }
    }

    const editTransfer = (transfer) => {
      editingTransfer.value = transfer
      const sourceAccount = accounts.value.find(
        (acc) => acc.name === transfer.source_account_name
      )
      const destinationAccount = accounts.value.find(
        (acc) => acc.name === transfer.destination_account_name
      )
      editTransferData.value = {
        source_account: sourceAccount?.id || '',
        destination_account: destinationAccount?.id || '',
        amount: transfer.amount,
        timestamp: transfer.timestamp
          ? transfer.timestamp.slice(0, 16)
          : new Date().toISOString().slice(0, 16)
      }
      showEditTransferModal.value = true
    }

    const updateTransfer = async () => {
      if (!editTransferData.value.source_account || !editTransferData.value.destination_account) {
        alert('Выберите счета для перевода')
        return
      }
      if (editTransferData.value.source_account === editTransferData.value.destination_account) {
        alert('Счета списания и зачисления должны быть разными')
        return
      }
      try {
        await apiService.updateTransfer(editingTransfer.value.id, {
          source_account: parseInt(editTransferData.value.source_account),
          destination_account: parseInt(editTransferData.value.destination_account),
          amount: parseFloat(editTransferData.value.amount),
          timestamp: new Date(editTransferData.value.timestamp).toISOString()
        })
        closeEditTransferModal()
        await loadAccounts()
        await loadTransfers()
        await loadTransferAnalytics()
        await loadBalanceHistory()
      } catch (error) {
        console.error('Error updating transfer:', error)
        alert('Ошибка при обновлении перевода: ' + (error.message || 'Неизвестная ошибка'))
      }
    }

    const confirmDeleteTransfer = (transfer) => {
      transferToDelete.value = transfer
      showDeleteTransferModal.value = true
    }

    const deleteTransfer = async () => {
      try {
        await apiService.deleteTransfer(transferToDelete.value.id)
        showDeleteTransferModal.value = false
        if (transfers.value.length === 1 && currentPage.value > 1) currentPage.value--
        await loadAccounts()
        await loadTransfers()
        await loadTransferAnalytics()
        await loadBalanceHistory()
      } catch (error) {
        console.error('Error deleting transfer:', error)
        alert('Ошибка при удалении перевода')
      }
    }

    const closeEditTransferModal = () => {
      showEditTransferModal.value = false
      editingTransfer.value = null
      editTransferData.value = {
        source_account: '', destination_account: '', amount: '', timestamp: ''
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

    // =========================================================================
    // Форматирование
    // =========================================================================
    const formatCurrency = (value) => {
      if (value === null || value === undefined || value === '') return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value)
    }

    const formatCompactCurrency = (value) => {
      if (value === null || value === undefined || value === '') return '0'
      const abs = Math.abs(value)
      if (abs >= 1_000_000) return (value / 1_000_000).toFixed(1) + 'M'
      if (abs >= 1_000) return (value / 1_000).toFixed(0) + 'k'
      return String(Math.round(value))
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ru-RU', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      })
    }

    const formatShortDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ru-RU', {
        day: '2-digit', month: '2-digit',
        hour: '2-digit', minute: '2-digit'
      })
    }

    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    // =========================================================================
    // Watchers
    // =========================================================================
    watch(
      historyAccounts,
      (list) => {
        if (list.length === 0) return
        const ids = list.map((a) => a.id)
        const currentIds = Array.from(visibleHistoryAccounts.value)
        const sameSet =
          currentIds.length === ids.length && ids.every((id) => currentIds.includes(id))
        if (!sameSet) visibleHistoryAccounts.value = new Set(ids)
      },
      { immediate: true }
    )

    watch(distributionData, () => {
      if (analyticsExpanded.value) scheduleAllDraws()
    })
    watch(activityRange, () => {
      if (analyticsExpanded.value) scheduleAllDraws()
    })
    watch([sankeyData, topAccountPairs], () => {
      if (analyticsExpanded.value) scheduleAllDraws()
    })
    watch(historyRange, () => loadBalanceHistory())
    watch(historyMode, () => {
      if (analyticsExpanded.value) scheduleHistoryDraw()
    })
    watch(visibleHistoryAccounts, () => {
      if (analyticsExpanded.value) scheduleHistoryDraw()
    }, { deep: true })

    const handleResize = () => {
      if (analyticsExpanded.value) scheduleAllDraws()
    }

    // =========================================================================
    // Lifecycle
    // =========================================================================
    onMounted(async () => {
      await Promise.all([
        loadAccounts(),
        loadTransfers(),
        loadBalanceHistory(),
        loadTransferAnalytics()
      ])
      window.addEventListener('resize', handleResize)
      if (analyticsExpanded.value) {
        scheduleAllDraws()
      }
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
    })

    // =========================================================================
    // Публичный API
    // =========================================================================
    return {
      // Счета
      accounts, activeAccounts, inactiveAccounts, allAccounts, loading,
      showAccountModal, showBalanceModal, showDeleteModal,
      editingAccount, balanceAccount, accountToDelete, newBalance,
      formData, totalBalance, activeAccountsCount, expandedAccounts,

      // Сворачивание аналитики
      analyticsExpanded, toggleAnalytics,

      // 2.1 Динамика баланса
      historyCanvas, historyRange, historyRanges, historyMode,
      historyLoading, historyError, historyAccounts, visibleHistoryAccounts,
      historyTotalSeries, historyStartBalance, historyEndBalance,
      historyChange, historyChangePercent, historyChangeClass,
      historyMinTotal, historyMaxTotal, historyPeriodLabel, historyTooltip,
      loadBalanceHistory, toggleHistoryAccount,
      onHistoryMouseMove, onHistoryMouseLeave,

      // 1.1 Распределение
      distributionCanvas, distributionData,

      // 1.5 Соотношение
      ratioCanvas, activeRatioPercent,

      // 1.6 Активность аккаунта
      getLastActivityLabel, getActivityClass, getActivityIcon,

      // 1.4 Метрики (из бэкенда)
      analyticsRaw, analyticsLoading, analyticsError,
      analyticsMetrics, analyticsPeriodLabel,

      // 1.2 Топ счетов (из бэкенда)
      topAccountsByTurnover,

      // 1.8 Топ пар (из бэкенда)
      topAccountPairs,

      // 1.9 Санкей (из бэкенда)
      sankeyCanvas, sankeyData,

      // 1.3 Активность (из бэкенда)
      activityCanvas, activityRange, activityRanges, activityData,
      activityTotalCount, activityTotalAmount, activityBusiestDay,

      // Переводы (только для таблицы истории)
      transfers, currentPage, totalPages, totalCount, transferLoading,
      showEditTransferModal, showDeleteTransferModal,
      editingTransfer, transferToDelete, transferData, editTransferData,
      otherAccounts, editOtherAccounts, expandedTransfers,

      // Методы
      toggleExpand, toggleExpandTransfer, truncateText,
      openCreateModal, editAccount, saveAccount, toggleVisibility,
      openBalanceModal, updateBalance, confirmDelete, deleteAccount, closeModal,
      openTransferFor, createTransfer, editTransfer, updateTransfer,
      confirmDeleteTransfer, deleteTransfer, closeEditTransferModal,
      prevPage, nextPage,
      formatCurrency, formatCompactCurrency, formatDate, formatShortDate
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
  flex-wrap: wrap;
  gap: 0.75rem;
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

.badge-success { background: #d1fae5; color: #065f46; }
.badge-secondary { background: #e5e7eb; color: #4b5563; }

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn-info { background: #3b82f6; color: white; }
.btn-info:hover { background: #2563eb; }

.btn-warning { background: #f59e0b; color: white; }
.btn-warning:hover { background: #d97706; }

.btn-success { background: var(--secondary-color); color: white; }
.btn-success:hover { background: #059669; }

.text-success { color: var(--secondary-color); }
.text-danger { color: var(--danger-color); }
.text-muted { color: var(--gray-color); }
.text-warning { color: var(--warning-color); font-weight: 600; }

/* ===== Аналитика — сворачиваемый блок ===== */
.analytics-section {
  margin-bottom: 1.5rem;
}

.analytics-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: var(--white);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.analytics-section-header:hover {
  background: #f9fafb;
}

.analytics-section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--dark-color);
  min-width: 0;
}

.analytics-section-title i {
  color: var(--primary-color);
}

.analytics-section-hint {
  font-size: 0.8rem;
  color: var(--gray-color);
  font-weight: 400;
  font-style: italic;
  margin-left: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.analytics-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  border: 1px solid var(--light-color);
  background: var(--white);
  border-radius: var(--radius);
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.2s;
}

.analytics-toggle-btn:hover {
  background: var(--light-color);
  border-color: var(--primary-color);
}

.analytics-toggle-btn i {
  font-size: 0.75rem;
}

.analytics-section-body {
  margin-top: 1.5rem;
}

/* ===== 2.1 Динамика баланса ===== */
.balance-history-card {
  margin-bottom: 1.5rem;
}

.history-controls {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.history-range,
.history-mode {
  display: flex;
  gap: 0.25rem;
  background: var(--light-color);
  padding: 0.25rem;
  border-radius: var(--radius);
}

.history-body {
  padding: 0.5rem 0;
}

.history-loading,
.history-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  color: var(--gray-color);
  font-size: 0.9rem;
}

.history-error {
  flex-direction: column;
  color: var(--danger-color);
}

.history-error i {
  font-size: 2rem;
}

.history-chart-wrapper {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.history-canvas {
  display: block;
  width: 100%;
  cursor: crosshair;
}

.history-tooltip {
  position: absolute;
  z-index: 10;
  background: rgba(17, 24, 39, 0.95);
  color: white;
  border-radius: var(--radius);
  padding: 0.625rem 0.75rem;
  font-size: 0.75rem;
  pointer-events: none;
  transform: translate(-50%, -100%);
  margin-top: -10px;
  min-width: 180px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.history-tooltip::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: rgba(17, 24, 39, 0.95);
  border-bottom: none;
}

.history-tooltip-date {
  font-weight: 700;
  font-size: 0.8rem;
  margin-bottom: 0.4rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.history-tooltip-row {
  display: grid;
  grid-template-columns: 10px 1fr auto;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.25rem;
}

.history-tooltip-color {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.history-tooltip-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-tooltip-value {
  font-weight: 600;
  white-space: nowrap;
}

.history-tooltip-total {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.4rem;
  padding-top: 0.4rem;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  font-weight: 700;
}

.history-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.history-legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  background: #f9fafb;
  border: 1px solid var(--light-color);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--dark-color);
}

.history-legend-item:hover {
  background: var(--light-color);
}

.history-legend-item.is-off {
  opacity: 0.4;
  text-decoration: line-through;
}

.history-legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}

.history-legend-name {
  font-weight: 500;
}

.history-legend-value {
  color: var(--gray-color);
  font-size: 0.75rem;
}

.history-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
  flex-wrap: wrap;
  gap: 1rem;
}

.history-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.history-stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.history-stat-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: var(--gray-color);
  font-weight: 500;
}

.history-stat-value {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--dark-color);
}

.history-stat-value small {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--gray-color);
}

.history-period-label {
  font-size: 0.8rem;
  color: var(--gray-color);
  font-style: italic;
}

/* ===== Аналитический ряд ===== */
.analytics-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

/* ===== Распределение ===== */
.distribution-card { margin-bottom: 0; }

.distribution-total {
  font-size: 0.875rem;
  color: var(--gray-color);
}

.distribution-total strong {
  color: var(--dark-color);
  font-size: 1rem;
}

.distribution-body {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 0.5rem 0;
}

.distribution-chart-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
  width: 320px;
  max-width: 100%;
}

.distribution-canvas {
  display: block;
  max-width: 100%;
  height: auto;
}

.distribution-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}

.legend-row {
  display: grid;
  grid-template-columns: 14px 1fr auto auto;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius);
  background: #f9fafb;
  transition: background 0.2s;
  font-size: 0.875rem;
}

.legend-row:hover { background: var(--light-color); }

.legend-color {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  flex-shrink: 0;
}

.legend-name {
  font-weight: 500;
  color: var(--dark-color);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.legend-value {
  color: var(--gray-color);
  font-weight: 500;
  white-space: nowrap;
}

.legend-percent {
  font-weight: 700;
  color: var(--dark-color);
  min-width: 48px;
  text-align: right;
  white-space: nowrap;
}

.distribution-empty {
  text-align: center;
  padding: 2rem;
  color: var(--gray-color);
}

.distribution-empty i {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
  opacity: 0.5;
}

.distribution-empty p {
  margin: 0;
  font-size: 0.875rem;
}

/* ===== Соотношение ===== */
.accounts-ratio-card { margin-bottom: 0; }

.accounts-ratio-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;
}

.ratio-chart-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 200px;
  height: 200px;
}

.ratio-canvas { display: block; }

.ratio-center-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.ratio-center-percent {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--secondary-color);
  line-height: 1;
}

.ratio-center-caption {
  font-size: 0.7rem;
  color: var(--gray-color);
  margin-top: 0.2rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ratio-stats {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ratio-stat-row {
  display: grid;
  grid-template-columns: 14px 1fr auto;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius);
  background: #f9fafb;
  font-size: 0.875rem;
}

.ratio-stat-row.total {
  background: transparent;
  border-top: 1px solid var(--light-color);
  border-radius: 0;
  margin-top: 0.25rem;
  padding-top: 0.75rem;
}

.ratio-color { width: 14px; height: 14px; border-radius: 4px; }
.ratio-label { color: var(--dark-color); font-weight: 500; }
.ratio-value { font-weight: 700; color: var(--dark-color); }

/* ===== Метрики ===== */
.transfer-metrics-card { margin-bottom: 1.5rem; }

.metrics-period {
  font-size: 0.75rem;
  color: var(--gray-color);
  font-style: italic;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.metric-card {
  background: #f9fafb;
  border-radius: var(--radius);
  padding: 1rem;
  text-align: center;
  transition: all 0.2s;
}

.metric-card:hover {
  background: var(--light-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.metric-label {
  font-size: 0.75rem;
  color: var(--gray-color);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  font-weight: 500;
}

.metric-label i { color: var(--primary-color); }

.metric-value {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--dark-color);
  word-break: break-word;
}

/* ===== Топ счетов, пары, санкей ===== */
.top-accounts-card,
.top-pairs-card,
.sankey-card { margin-bottom: 1.5rem; }

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  background: var(--light-color);
  color: var(--gray-color);
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(245, 158, 11, 0.4);
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(156, 163, 175, 0.4);
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(234, 88, 12, 0.4);
}

.turnover-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 120px;
}

.turnover-bar {
  flex: 1;
  height: 6px;
  background: var(--light-color);
  border-radius: 9999px;
  overflow: hidden;
}

.turnover-bar.mobile { height: 4px; margin-top: 0.5rem; }

.turnover-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6 0%, #93c5fd 100%);
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.turnover-percent {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--gray-color);
  min-width: 40px;
  text-align: right;
}

.top-account-card,
.pair-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  padding: 0.875rem;
  margin-bottom: 0.5rem;
}

.top-account-header,
.pair-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--light-color);
}

.top-account-name {
  flex: 1;
  font-weight: 600;
  color: var(--dark-color);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.top-account-turnover,
.pair-amount {
  font-weight: 700;
  color: var(--primary-color);
}

.top-account-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.top-detail {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  padding: 0.25rem 0;
}

.top-detail-label { color: var(--gray-color); }
.top-detail-value { font-weight: 600; }

.pair-header .pair-amount { margin-left: auto; }

.pair-route {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.pair-account {
  font-weight: 600;
  color: var(--dark-color);
  background: var(--light-color);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.pair-arrow-icon { color: var(--gray-color); font-size: 0.75rem; }
.pair-arrow { color: var(--gray-color); text-align: center; }

.pair-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--gray-color);
}

.pair-percent { font-weight: 700; color: var(--dark-color); }

/* Санкей — горизонтальный скролл на мобильных */
.sankey-body {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  padding: 0.5rem 0;
}

.sankey-canvas { display: block; }

.sankey-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: var(--gray-color);
}

.sankey-legend { display: flex; gap: 1rem; }

.sankey-legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.sankey-legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.sankey-summary { display: flex; gap: 1rem; }
.sankey-summary strong { color: var(--dark-color); }

/* Активность */
.activity-card { margin-bottom: 1.5rem; }

.activity-range {
  display: flex;
  gap: 0.25rem;
  background: var(--light-color);
  padding: 0.25rem;
  border-radius: var(--radius);
}

.range-btn {
  padding: 0.375rem 0.75rem;
  border: none;
  background: transparent;
  border-radius: calc(var(--radius) - 2px);
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--gray-color);
  cursor: pointer;
  transition: all 0.2s;
}

.range-btn:hover { color: var(--dark-color); }

.range-btn.active {
  background: var(--white);
  color: var(--primary-color);
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.activity-body { width: 100%; overflow: hidden; }
.activity-canvas { display: block; width: 100%; }

.activity-footer {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.activity-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  font-size: 0.875rem;
  color: var(--gray-color);
}

.activity-summary-item strong {
  color: var(--dark-color);
  font-weight: 700;
}

/* 1.6 Последняя активность */
.activity-cell {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8rem;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-weight: 500;
}

.activity-cell.activity-recent { background: #d1fae5; color: #065f46; }
.activity-cell.activity-medium { background: #fef3c7; color: #92400e; }
.activity-cell.activity-old { background: #fee2e2; color: #991b1b; }
.activity-cell.activity-never { background: #f3f4f6; color: #6b7280; }

.account-activity {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem;
  background: var(--white);
  border-radius: var(--radius);
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
  color: var(--gray-color);
}

.account-activity strong.activity-recent { color: #065f46; }
.account-activity strong.activity-medium { color: #92400e; }
.account-activity strong.activity-old { color: #991b1b; }
.account-activity strong.activity-never { color: #6b7280; }

/* Мобильные карточки */
.mobile-accounts { display: none; }

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

.account-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.account-compact:hover { background-color: #f9fafb; }

.compact-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.account-name-compact { font-size: 0.875rem; }

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

.account-expanded {
  padding: 1rem;
  border-top: 1px solid var(--light-color);
  background-color: #fafafa;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
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

/* Таблицы */
.desktop-table { display: block; overflow-x: auto; }

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

.table th { font-weight: 600; color: var(--gray-color); }

/* Форма переводов */
.transfer-form { padding: 1rem 0; }

.transfer-form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.transfer-form-actions {
  display: flex;
  justify-content: flex-end;
}

/* Мобильные карточки переводов */
.mobile-cards { display: none; }

.transfer-card {
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  margin-bottom: 0.5rem;
  overflow: hidden;
  transition: all 0.3s ease;
}

.transfer-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.transfer-compact:hover { background-color: #f9fafb; }

.transfer-date-compact {
  font-size: 0.75rem;
  color: var(--gray-color);
  min-width: 70px;
}

.transfer-amount-compact {
  font-size: 1rem;
  font-weight: 700;
}

.transfer-expanded {
  padding: 1rem;
  border-top: 1px solid var(--light-color);
  background-color: #fafafa;
  animation: slideDown 0.3s ease;
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

.transfer-actions-expanded .btn-sm { padding: 0.5rem 1rem; }

/* Пагинация */
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

.page-info { font-size: 0.875rem; }

/* Модальные окна */
.modal-footer {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--light-color);
}

.required:after { content: " *"; color: var(--danger-color); }

.alert {
  padding: 0.75rem;
  border-radius: var(--radius);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.alert-info { background: #dbeafe; color: #1e40af; }
.alert-danger { background: #fee2e2; color: #991b1b; }

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

.empty-state p { margin: 0; }

/* Адаптив */
@media (max-width: 1200px) {
  .analytics-row { grid-template-columns: 1fr; }
  .ratio-chart-wrapper { width: 180px; height: 180px; }
}

@media (max-width: 1024px) {
  .desktop-table { display: none; }
  .mobile-accounts,
  .mobile-cards { display: block; }
  .stats-grid { gap: 1rem; }
  .stat-value { font-size: 1.5rem; }
  .card { padding: 1rem; }
  .transfer-form-grid { grid-template-columns: 1fr; }
  .transfer-form-actions { justify-content: stretch; }
  .transfer-form-actions .btn { width: 100%; }
  .distribution-body {
    flex-direction: column;
    gap: 1.25rem;
  }
  .distribution-chart-wrapper { width: 280px; }
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .history-controls { flex-direction: column; width: 100%; }
  .history-range,
  .history-mode { width: 100%; }
}

@media (min-width: 1025px) and (max-width: 1280px) {
  .desktop-table { display: block; }
  .mobile-accounts,
  .mobile-cards { display: none; }
  .table th,
  .table td { padding: 0.5rem; font-size: 0.875rem; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; text-align: center; }
  .page-header h1 { font-size: 1.5rem; }
  .page-header .btn { width: 100%; }
  .stats-grid { grid-template-columns: 1fr; }
  .stat-card { padding: 1rem; }
  .stat-title { font-size: 0.75rem; }
  .stat-value { font-size: 1.25rem; }
  .compact-left { gap: 0.5rem; }
  .account-name-compact { font-size: 0.8rem; }
  .account-balance-compact { font-size: 0.9rem; }
  .badge { font-size: 0.65rem; }
  .modal-content { width: 95%; margin: 1rem; max-height: 85vh; }
  .modal-header h3 { font-size: 1.1rem; }
  .form-group { margin-bottom: 0.75rem; }
  .form-label { font-size: 0.8rem; }
  .form-control { font-size: 16px; padding: 0.5rem; }
  .modal-footer { gap: 0.5rem; }
  .pagination { flex-direction: row; }
  .pagination button { width: auto; }
  .transfer-date-compact { min-width: 60px; font-size: 0.7rem; }
  .transfer-amount-compact { font-size: 0.9rem; }
  .distribution-chart-wrapper { width: 240px; }
  .legend-row {
    grid-template-columns: 12px 1fr auto auto;
    gap: 0.5rem;
    padding: 0.5rem;
    font-size: 0.8rem;
  }
  .legend-color { width: 12px; height: 12px; }
  .legend-percent { min-width: 42px; }
  .metrics-grid { grid-template-columns: 1fr 1fr; gap: 0.75rem; }
  .metric-card { padding: 0.75rem; }
  .metric-value { font-size: 1rem; }
  .activity-range { width: 100%; }
  .range-btn { flex: 1; font-size: 0.7rem; padding: 0.375rem 0.25rem; }
  .activity-summary { gap: 0.75rem; font-size: 0.75rem; }
  .history-stats { gap: 1rem; }
  .history-stat-value { font-size: 0.85rem; }
  .history-footer { flex-direction: column; align-items: flex-start; }
  .analytics-section-title { font-size: 1.1rem; }
  .analytics-section-hint { display: none; }
}

@media (max-width: 480px) {
  .account-compact { padding: 0.6rem 0.75rem; }
  .compact-left { gap: 0.4rem; flex-wrap: wrap; }
  .account-name-compact { width: 100%; margin-bottom: 0.25rem; }
  .account-actions-expanded { flex-direction: column; }
  .account-actions-expanded .btn-sm { width: 100%; }
  .expand-icon { width: 36px; height: 36px; }
  .pagination { gap: 0.5rem; }
  .btn-text { display: none; }
  .pagination .btn { padding: 10px 12px; }
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  .detail-value { max-width: 100%; text-align: left; }
  .transfer-actions-expanded { flex-direction: column; }
  .transfer-actions-expanded .btn-sm { width: 100%; margin: 0; }
  .modal-footer { flex-direction: column; gap: 0.5rem; }
  .distribution-chart-wrapper { width: 200px; }
  .legend-value { display: none; }
  .legend-row { grid-template-columns: 12px 1fr auto; }
  .distribution-total { font-size: 0.75rem; }
  .distribution-total strong { font-size: 0.875rem; }
  .metrics-grid { grid-template-columns: 1fr; }
  .ratio-chart-wrapper { width: 150px; height: 150px; }
  .ratio-center-percent { font-size: 1.35rem; }
  .pair-route { font-size: 0.75rem; }
  .sankey-footer { flex-direction: column; align-items: flex-start; }
  .history-legend { gap: 0.375rem; }
  .history-legend-item { font-size: 0.7rem; padding: 0.25rem 0.5rem; }
  .history-stats { flex-direction: column; gap: 0.5rem; }
  .history-tooltip { min-width: 150px; font-size: 0.7rem; }
  .analytics-section-header { padding: 0.875rem 1rem; }
  .analytics-section-title { font-size: 1rem; }
  .analytics-toggle-btn { font-size: 0.75rem; padding: 0.375rem 0.625rem; }
}
</style>