<template>
  <div>
    <div class="page-header">
      <h1>Счета и переводы</h1>
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

    <!-- 2.1 Динамика баланса по дням -->
    <div class="card balance-history-card" v-if="activeAccounts.length > 0">
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
              @click="historyRange = range.value"
            >
              {{ range.label }}
            </button>
          </div>
          <div class="history-mode">
            <button
              class="range-btn"
              :class="{ active: historyMode === 'all' }"
              @click="historyMode = 'all'"
            >
              Все счета
            </button>
            <button
              class="range-btn"
              :class="{ active: historyMode === 'total' }"
              @click="historyMode = 'total'"
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
          <button class="btn btn-sm btn-primary" @click="loadBalanceHistory">
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

          <!-- Легенда с чекбоксами -->
          <div class="history-legend" v-if="historyMode === 'all' && historyAccounts.length > 0">
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

          <!-- Сводка -->
          <div class="history-footer">
            <div class="history-stats">
              <div class="history-stat">
                <span class="history-stat-label">Изменение за период</span>
                <span
                  class="history-stat-value"
                  :class="historyChangeClass"
                >
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

    <!-- Распределение баланса по счетам + Соотношение активных/неактивных -->
    <div class="analytics-row">
      <div class="card distribution-card" v-if="activeAccounts.length > 0">
        <div class="card-header">
          <h3 class="card-title">
            <i class="fas fa-chart-pie"></i> Распределение баланса
          </h3>
          <span class="distribution-total">
            Всего: <strong>{{ formatCurrency(totalBalance) }}</strong>
          </span>
        </div>

        <div class="distribution-body" v-if="distributionData.length > 0">
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

      <div class="card accounts-ratio-card" v-if="accounts.length > 0">
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

    <!-- 1.4 Метрики переводов -->
    <div class="card transfer-metrics-card" v-if="transfers.length > 0">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-calculator"></i> Метрики переводов
        </h3>
        <span class="metrics-period">по загруженным переводам</span>
      </div>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-label">
            <i class="fas fa-ruble-sign"></i> Средний перевод
          </div>
          <div class="metric-value">{{ formatCurrency(averageTransfer) }}</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">
            <i class="fas fa-sort-amount-up"></i> Максимальный
          </div>
          <div class="metric-value text-warning">{{ formatCurrency(maxTransfer) }}</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">
            <i class="fas fa-sort-amount-down"></i> Минимальный
          </div>
          <div class="metric-value">{{ formatCurrency(minTransfer) }}</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">
            <i class="fas fa-chart-bar"></i> Медиана
          </div>
          <div class="metric-value">{{ formatCurrency(medianTransfer) }}</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">
            <i class="fas fa-hashtag"></i> Количество
          </div>
          <div class="metric-value">{{ transfersCount }}</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">
            <i class="fas fa-coins"></i> Общий оборот
          </div>
          <div class="metric-value text-success">{{ formatCurrency(totalTransfersAmount) }}</div>
        </div>
      </div>
    </div>

    <!-- 1.2 Топ счетов по обороту -->
    <div class="card top-accounts-card" v-if="topAccountsByTurnover.length > 0">
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
              <td>
                <strong>{{ item.name }}</strong>
              </td>
              <td class="text-success">{{ formatCurrency(item.incoming) }}</td>
              <td class="text-danger">{{ formatCurrency(item.outgoing) }}</td>
              <td>
                <strong>{{ formatCurrency(item.turnover) }}</strong>
              </td>
              <td>{{ item.count }}</td>
              <td>
                <div class="turnover-progress">
                  <div class="turnover-bar">
                    <div
                      class="turnover-fill"
                      :style="{ width: item.turnoverPercent + '%' }"
                    ></div>
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
            <div
              class="turnover-fill"
              :style="{ width: item.turnoverPercent + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 1.8 Топ контрагентов (пар) -->
    <div class="card top-pairs-card" v-if="topAccountPairs.length > 0">
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
              <td class="pair-arrow">
                <i class="fas fa-arrow-right"></i>
              </td>
              <td>{{ pair.destination }}</td>
              <td>
                <strong>{{ formatCurrency(pair.amount) }}</strong>
              </td>
              <td>{{ pair.count }}</td>
              <td>
                <div class="turnover-progress">
                  <div class="turnover-bar">
                    <div
                      class="turnover-fill"
                      :style="{ width: pair.percent + '%' }"
                    ></div>
                  </div>
                  <span class="turnover-percent">{{ pair.percent }}%</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="mobile-cards">
        <div
          v-for="(pair, index) in topAccountPairs"
          :key="pair.key"
          class="pair-card"
        >
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
            <div
              class="turnover-fill"
              :style="{ width: pair.percent + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 1.9 Диаграмма Санкей -->
    <div class="card sankey-card" v-if="transfers.length > 0 && sankeyData.nodes.length > 1">
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
            <span class="sankey-legend-color" style="background: #10b981;"></span>
            Входящие
          </span>
          <span class="sankey-legend-item">
            <span class="sankey-legend-color" style="background: #ef4444;"></span>
            Исходящие
          </span>
        </div>
        <div class="sankey-summary">
          <span>Всего узлов: <strong>{{ sankeyData.nodes.length }}</strong></span>
          <span>Связей: <strong>{{ sankeyData.links.length }}</strong></span>
        </div>
      </div>
    </div>

    <!-- 1.3 Активность переводов по дням -->
    <div class="card activity-card" v-if="transfers.length > 0">
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
            @click="activityRange = range.value"
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
          <span class="activity-summary-item" v-if="activityBusiestDay">
            пик: <strong>{{ activityBusiestDay.label }}</strong>
            ({{ activityBusiestDay.count }} переводов)
          </span>
        </div>
      </div>
    </div>

    <!-- 1.7 Heatmap активности переводов -->
    <div class="card heatmap-card" v-if="transfers.length > 0">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-fire"></i> Тепловая карта переводов
        </h3>
        <div class="heatmap-mode">
          <button
            class="range-btn"
            :class="{ active: heatmapMode === 'count' }"
            @click="heatmapMode = 'count'"
          >
            По количеству
          </button>
          <button
            class="range-btn"
            :class="{ active: heatmapMode === 'amount' }"
            @click="heatmapMode = 'amount'"
          >
            По сумме
          </button>
        </div>
      </div>

      <div class="heatmap-body">
        <canvas ref="heatmapCanvas" class="heatmap-canvas"></canvas>
      </div>

      <div class="heatmap-footer">
        <div class="heatmap-stats">
          <span>
            <strong>{{ heatmapActiveDays }}</strong> активных дней
            из <strong>{{ heatmapTotalDays }}</strong>
          </span>
          <span v-if="heatmapMaxDay">
            самый активный: <strong>{{ heatmapMaxDay.label }}</strong>
            ({{ heatmapMaxDay.count }} переводов, {{ formatCurrency(heatmapMaxDay.amount) }})
          </span>
        </div>
        <div class="heatmap-legend">
          <span class="heatmap-legend-label">Меньше</span>
          <span class="heatmap-cell heatmap-level-0"></span>
          <span class="heatmap-cell heatmap-level-1"></span>
          <span class="heatmap-cell heatmap-level-2"></span>
          <span class="heatmap-cell heatmap-level-3"></span>
          <span class="heatmap-cell heatmap-level-4"></span>
          <span class="heatmap-legend-label">Больше</span>
        </div>
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
              <button @click="openTransferFor(account)" class="btn btn-sm btn-primary">
                <i class="fas fa-exchange-alt"></i> Перевести
              </button>
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
              <td>
                <strong>{{ account.name }}</strong>
              </td>
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
                  <button @click="openTransferFor(account)" class="btn btn-sm btn-primary" title="Перевести">
                    <i class="fas fa-exchange-alt"></i>
                  </button>
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
              <td colspan="4" class="text-center">Нет активных счетов</td>
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
            <div class="account-activity">
              <i class="fas fa-clock"></i>
              Последняя активность:
              <strong :class="getActivityClass(account.id)">
                {{ getLastActivityLabel(account.id) }}
              </strong>
            </div>
            <div class="account-actions-expanded">
              <button @click="openTransferFor(account)" class="btn btn-sm btn-primary">
                <i class="fas fa-exchange-alt"></i> Перевести
              </button>
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
              <th>Последняя активность</th>
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
                <span class="activity-cell" :class="getActivityClass(account.id)">
                  <i :class="getActivityIcon(account.id)"></i>
                  {{ getLastActivityLabel(account.id) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="openTransferFor(account)" class="btn btn-sm btn-primary" title="Перевести">
                    <i class="fas fa-exchange-alt"></i>
                  </button>
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
              <td colspan="4" class="text-center">Нет неактивных счетов</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Переводы между счетами -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-exchange-alt"></i> Переводы между счетами
        </h3>
      </div>

      <form @submit.prevent="createTransfer" class="transfer-form">
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
            <input type="number" v-model="transferData.amount" class="form-control" step="0.01" required placeholder="0.00">
          </div>

          <div class="form-group">
            <label class="form-label required">Дата и время</label>
            <input type="datetime-local" v-model="transferData.timestamp" class="form-control" required>
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
                  <button @click="editTransfer(transfer)" class="btn btn-secondary btn-sm" title="Редактировать">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button @click="confirmDeleteTransfer(transfer)" class="btn btn-danger btn-sm" title="Удалить">
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
              <button @click="editTransfer(transfer)" class="btn btn-sm btn-info">
                <i class="fas fa-edit"></i> Редактировать
              </button>
              <button @click="confirmDeleteTransfer(transfer)" class="btn btn-sm btn-danger">
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

      <div class="pagination" v-if="totalPages > 1">
        <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-secondary">
          <i class="fas fa-chevron-left"></i> <span class="btn-text">Назад</span>
        </button>
        <span class="page-info">Страница {{ currentPage }} из {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-secondary">
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
            <input type="number" v-model="editTransferData.amount" class="form-control" step="0.01" required>
          </div>

          <div class="form-group">
            <label class="form-label required">Дата и время</label>
            <input type="datetime-local" v-model="editTransferData.timestamp" class="form-control" required>
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeEditTransferModal" class="btn btn-secondary">Отмена</button>
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
          <button @click="showDeleteModal = false" class="btn btn-secondary">Отмена</button>
          <button @click="deleteAccount" class="btn btn-danger">Да, удалить</button>
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
          <button @click="showDeleteTransferModal = false" class="btn btn-secondary">Отмена</button>
          <button @click="deleteTransfer" class="btn btn-danger">Да, удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'AccountsAndTransfers',
  setup() {
    // --- Счета ---
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

    const activeAccounts = computed(() => accounts.value.filter(acc => acc.is_active))
    const inactiveAccounts = computed(() => accounts.value.filter(acc => !acc.is_active))
    const allAccounts = computed(() => accounts.value)

    const totalBalance = computed(() => {
      return activeAccounts.value.reduce((sum, acc) => sum + parseFloat(acc.balance || 0), 0)
    })

    const activeAccountsCount = computed(() => activeAccounts.value.length)

    // --- 2.1 Динамика баланса ---
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

    const historyTooltip = ref({
      visible: false,
      x: 0,
      y: 0,
      date: '',
      rows: [],
      total: 0
    })

    // Готовим список счетов с цветами
    const historyAccounts = computed(() => {
      if (!historyRawData.value || !historyRawData.value.accounts) return []
      return historyRawData.value.accounts.map((acc, index) => {
        const series = historyRawData.value.results.map(r => ({
          date: r.date,
          value: parseFloat(r.accounts[String(acc.id)] || 0)
        }))
        const last = series.length > 0 ? series[series.length - 1].value : 0
        return {
          id: acc.id,
          name: acc.name,
          color: distributionColors[index % distributionColors.length],
          series,
          lastBalance: last
        }
      })
    })

    // Видимые счета — по умолчанию все
    watch(historyAccounts, (list) => {
      if (list.length === 0) return
      // Если изменился набор счетов — пересобираем Set
      const ids = list.map(a => a.id)
      const currentIds = Array.from(visibleHistoryAccounts.value)
      const sameSet = currentIds.length === ids.length && ids.every(id => currentIds.includes(id))
      if (!sameSet) {
        visibleHistoryAccounts.value = new Set(ids)
      }
    }, { immediate: true })

    // Суммарный ряд (итог)
    const historyTotalSeries = computed(() => {
      if (!historyRawData.value || !historyRawData.value.results) return []
      return historyRawData.value.results.map(r => ({
        date: r.date,
        value: parseFloat(r.total || 0)
      }))
    })

    // Метрики по итогу
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
      if (s.length === 0) return 0
      return Math.min(...s.map(p => p.value))
    })

    const historyMaxTotal = computed(() => {
      const s = historyTotalSeries.value
      if (s.length === 0) return 0
      return Math.max(...s.map(p => p.value))
    })

    const historyPeriodLabel = computed(() => {
      if (!historyRawData.value || historyRawData.value.results.length === 0) return ''
      const first = historyRawData.value.results[0].date
      const last = historyRawData.value.results[historyRawData.value.results.length - 1].date
      return `${formatDateShortLabel(first)} — ${formatDateShortLabel(last)}`
    })

    const formatDateShortLabel = (iso) => {
      if (!iso) return ''
      const d = new Date(iso)
      return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
    }

    const loadBalanceHistory = async () => {
      historyLoading.value = true
      historyError.value = ''
      try {
        const dateTo = new Date()
        const dateFrom = new Date()
        dateFrom.setDate(dateFrom.getDate() - historyRange.value + 1)

        const dateFromStr = formatDateKey(dateFrom)
        const dateToStr = formatDateKey(dateTo)

        const data = await apiService.getBalanceHistory(dateFromStr, dateToStr)
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

    const toggleHistoryAccount = (accountId) => {
      const s = new Set(visibleHistoryAccounts.value)
      if (s.has(accountId)) s.delete(accountId)
      else s.add(accountId)
      visibleHistoryAccounts.value = s
      scheduleHistoryDraw()
    }

    // --- Отрисовка графика динамики ---
    const historyChartMetrics = ref({ paddingLeft: 60, paddingRight: 20, paddingTop: 20, paddingBottom: 40 })

    const drawHistoryChart = () => {
      const canvas = historyCanvas.value
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const totalSeries = historyTotalSeries.value
      if (totalSeries.length === 0) {
        const wrapper = canvas.parentElement
        if (wrapper) {
          canvas.width = wrapper.clientWidth
          canvas.height = 100
        }
        return
      }

      const wrapper = canvas.parentElement
      const cssWidth = wrapper ? wrapper.clientWidth : 900
      const cssHeight = 320

      const dpr = window.devicePixelRatio || 1
      canvas.width = cssWidth * dpr
      canvas.height = cssHeight * dpr
      canvas.style.width = `${cssWidth}px`
      canvas.style.height = `${cssHeight}px`
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.scale(dpr, dpr)
      ctx.clearRect(0, 0, cssWidth, cssHeight)

      const paddingLeft = 60
      const paddingRight = 20
      const paddingTop = 20
      const paddingBottom = 40
      historyChartMetrics.value = { paddingLeft, paddingRight, paddingTop, paddingBottom }

      const chartWidth = cssWidth - paddingLeft - paddingRight
      const chartHeight = cssHeight - paddingTop - paddingBottom

      // Собираем все видимые серии
      const visibleSeries = []
      if (historyMode.value === 'total') {
        visibleSeries.push({
          id: 'total',
          name: 'Итого',
          color: '#3b82f6',
          series: totalSeries,
          isTotal: true
        })
      } else {
        historyAccounts.value.forEach(acc => {
          if (visibleHistoryAccounts.value.has(acc.id)) {
            visibleSeries.push({
              id: acc.id,
              name: acc.name,
              color: acc.color,
              series: acc.series,
              isTotal: false
            })
          }
        })
        // Жирная линия итога поверх
        visibleSeries.push({
          id: 'total',
          name: 'Итого',
          color: '#111827',
          series: totalSeries,
          isTotal: true
        })
      }

      // Диапазон значений
      const allValues = visibleSeries.flatMap(s => s.series.map(p => p.value))
      let minValue = Math.min(...allValues, 0)
      let maxValue = Math.max(...allValues, 0)
      // Немного расширим диапазон
      const range = maxValue - minValue || 1
      minValue -= range * 0.05
      maxValue += range * 0.05

      const xStep = totalSeries.length > 1 ? chartWidth / (totalSeries.length - 1) : 0
      const yScale = (v) => paddingTop + chartHeight - ((v - minValue) / (maxValue - minValue)) * chartHeight

      // Сетка
      ctx.strokeStyle = '#e5e7eb'
      ctx.lineWidth = 1
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.fillStyle = '#9ca3af'
      ctx.textAlign = 'right'
      ctx.textBaseline = 'middle'

      for (let i = 0; i <= 5; i++) {
        const value = minValue + ((maxValue - minValue) / 5) * i
        const y = paddingTop + chartHeight - (i / 5) * chartHeight
        ctx.beginPath()
        ctx.moveTo(paddingLeft, y)
        ctx.lineTo(cssWidth - paddingRight, y)
        ctx.stroke()
        ctx.fillText(formatCompactCurrency(value), paddingLeft - 6, y)
      }

      // Нулевая линия — если диапазон пересекает 0
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

      // Рисуем серии
      visibleSeries.forEach(s => {
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

        // Точки — только если точек мало
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

      // Подписи X
      ctx.fillStyle = '#6b7280'
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'top'
      const labelStep = Math.max(1, Math.ceil(totalSeries.length / 8))
      totalSeries.forEach((p, i) => {
        if (i % labelStep !== 0 && i !== totalSeries.length - 1) return
        const x = paddingLeft + i * xStep
        const d = new Date(p.date)
        const label = d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
        ctx.fillText(label, x, paddingTop + chartHeight + 8)
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

      const { paddingLeft, paddingRight, paddingTop, paddingBottom } = historyChartMetrics.value
      const cssWidth = rect.width
      const chartWidth = cssWidth - paddingLeft - paddingRight

      if (x < paddingLeft || x > cssWidth - paddingRight) {
        historyTooltip.value.visible = false
        return
      }

      const xStep = totalSeries.length > 1 ? chartWidth / (totalSeries.length - 1) : 0
      const idx = Math.round((x - paddingLeft) / xStep)
      const clampedIdx = Math.max(0, Math.min(totalSeries.length - 1, idx))
      const point = totalSeries[clampedIdx]

      // Собираем строки для тултипа
      const rows = []
      if (historyMode.value === 'total') {
        rows.push({
          id: 'total',
          name: 'Итого',
          color: '#3b82f6',
          value: point.value
        })
      } else {
        historyAccounts.value.forEach(acc => {
          if (!visibleHistoryAccounts.value.has(acc.id)) return
          const p = acc.series[clampedIdx]
          if (p) {
            rows.push({
              id: acc.id,
              name: acc.name,
              color: acc.color,
              value: p.value
            })
          }
        })
      }

      historyTooltip.value = {
        visible: true,
        x: x,
        y: y,
        date: new Date(point.date).toLocaleDateString('ru-RU', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        }),
        rows,
        total: point.value
      }
    }

    const onHistoryMouseLeave = () => {
      historyTooltip.value.visible = false
    }

    const scheduleHistoryDraw = () => {
      nextTick(() => {
        setTimeout(drawHistoryChart, 50)
      })
    }

    // --- 1.1 Распределение баланса ---
    const distributionCanvas = ref(null)
    const distributionColors = [
      '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
      '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1',
      '#14b8a6', '#a855f7'
    ]

    const distributionData = computed(() => {
      const active = activeAccounts.value.filter(acc => parseFloat(acc.balance) > 0)
      const total = active.reduce((sum, acc) => sum + parseFloat(acc.balance || 0), 0)
      if (total === 0) return []
      return active
        .map((acc, index) => {
          const balance = parseFloat(acc.balance) || 0
          return {
            id: acc.id,
            name: acc.name,
            balance,
            percent: ((balance / total) * 100).toFixed(1),
            color: distributionColors[index % distributionColors.length]
          }
        })
        .sort((a, b) => b.balance - a.balance)
    })

    const drawDistributionChart = () => {
      const canvas = distributionCanvas.value
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      const data = distributionData.value
      if (data.length === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        return
      }

      const wrapper = canvas.parentElement
      const size = wrapper ? Math.min(wrapper.clientWidth, 320) : 280
      const dpr = window.devicePixelRatio || 1
      canvas.width = size * dpr
      canvas.height = size * dpr
      canvas.style.width = `${size}px`
      canvas.style.height = `${size}px`
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.scale(dpr, dpr)

      const centerX = size / 2
      const centerY = size / 2
      const radius = size / 2 - 20

      ctx.clearRect(0, 0, size, size)

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

    // --- 1.5 Соотношение активных/неактивных ---
    const ratioCanvas = ref(null)

    const activeRatioPercent = computed(() => {
      if (accounts.value.length === 0) return 0
      return ((activeAccounts.value.length / accounts.value.length) * 100).toFixed(0)
    })

    const drawRatioChart = () => {
      const canvas = ratioCanvas.value
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      const total = accounts.value.length
      if (total === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        return
      }

      const wrapper = canvas.parentElement
      const size = wrapper ? Math.min(wrapper.clientWidth, 200) : 180
      const dpr = window.devicePixelRatio || 1
      canvas.width = size * dpr
      canvas.height = size * dpr
      canvas.style.width = `${size}px`
      canvas.style.height = `${size}px`
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.scale(dpr, dpr)

      const centerX = size / 2
      const centerY = size / 2
      const radius = size / 2 - 15
      const innerRadius = radius * 0.6

      ctx.clearRect(0, 0, size, size)

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
      ctx.arc(centerX, centerY, radius, -Math.PI / 2 + activeAngle, -Math.PI / 2 + activeAngle + inactiveAngle)
      ctx.closePath()
      ctx.fill()

      ctx.beginPath()
      ctx.fillStyle = '#ffffff'
      ctx.arc(centerX, centerY, radius * 0.6, 0, 2 * Math.PI)
      ctx.fill()
    }

    // --- Переводы ---
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
      return allAccounts.value.filter(acc => acc.id !== transferData.value.source_account)
    })

    const editOtherAccounts = computed(() => {
      if (!editTransferData.value.source_account) return allAccounts.value
      return allAccounts.value.filter(acc => acc.id !== editTransferData.value.source_account)
    })

    const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

    // --- 1.6 Последняя активность ---
    const accountLastActivity = computed(() => {
      const map = new Map()
      transfers.value.forEach(t => {
        if (!t.timestamp) return
        const time = new Date(t.timestamp).getTime()
        if (isNaN(time)) return
        const s = t.source_account_name
        const d = t.destination_account_name
        if (s) {
          if (!map.has(s) || map.get(s) < time) map.set(s, time)
        }
        if (d) {
          if (!map.has(d) || map.get(d) < time) map.set(d, time)
        }
      })
      return map
    })

    const getLastActivityTime = (accountId) => {
      const account = accounts.value.find(a => a.id === accountId)
      if (!account) return null
      return accountLastActivity.value.get(account.name) || null
    }

    const getLastActivityLabel = (accountId) => {
      const time = getLastActivityTime(accountId)
      if (!time) return 'Никогда'
      const diff = Date.now() - time
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
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

    // --- 1.2 Топ счетов по обороту ---
    const topAccountsByTurnover = computed(() => {
      if (transfers.value.length === 0) return []
      const map = new Map()
      const ensure = (name) => {
        if (!name) return null
        if (!map.has(name)) map.set(name, { name, incoming: 0, outgoing: 0, count: 0 })
        return map.get(name)
      }
      transfers.value.forEach(t => {
        const amount = parseFloat(t.amount) || 0
        const src = ensure(t.source_account_name)
        const dst = ensure(t.destination_account_name)
        if (src) { src.outgoing += amount; src.count += 1 }
        if (dst) { dst.incoming += amount; dst.count += 1 }
      })
      const list = Array.from(map.values()).map(item => ({
        ...item,
        turnover: item.incoming + item.outgoing
      }))
      const totalTurnover = list.reduce((sum, i) => sum + i.turnover, 0)
      return list
        .map(item => ({
          ...item,
          turnoverPercent: totalTurnover > 0
            ? ((item.turnover / totalTurnover) * 100).toFixed(1)
            : '0.0'
        }))
        .sort((a, b) => b.turnover - a.turnover)
    })

    // --- 1.8 Топ контрагентов (пар счёт→счёт) ---
    const topAccountPairs = computed(() => {
      if (transfers.value.length === 0) return []
      const map = new Map()
      transfers.value.forEach(t => {
        const s = t.source_account_name
        const d = t.destination_account_name
        if (!s || !d) return
        const key = `${s}→${d}`
        const amount = parseFloat(t.amount) || 0
        if (!map.has(key)) {
          map.set(key, { key, source: s, destination: d, amount: 0, count: 0 })
        }
        const entry = map.get(key)
        entry.amount += amount
        entry.count += 1
      })
      const list = Array.from(map.values())
      const totalAmount = list.reduce((sum, i) => sum + i.amount, 0)
      return list
        .map(item => ({
          ...item,
          percent: totalAmount > 0
            ? ((item.amount / totalAmount) * 100).toFixed(1)
            : '0.0'
        }))
        .sort((a, b) => b.amount - a.amount)
        .slice(0, 10)
    })

    // --- 1.9 Санкей ---
    const sankeyCanvas = ref(null)

    const sankeyData = computed(() => {
      if (transfers.value.length === 0) return { nodes: [], links: [] }

      const nodeTotals = new Map()
      const linkMap = new Map()

      transfers.value.forEach(t => {
        const s = t.source_account_name
        const d = t.destination_account_name
        if (!s || !d) return
        const amount = parseFloat(t.amount) || 0

        if (!nodeTotals.has(s)) nodeTotals.set(s, { name: s, incoming: 0, outgoing: 0 })
        if (!nodeTotals.has(d)) nodeTotals.set(d, { name: d, incoming: 0, outgoing: 0 })

        nodeTotals.get(s).outgoing += amount
        nodeTotals.get(d).incoming += amount

        const key = `${s}→${d}`
        if (!linkMap.has(key)) {
          linkMap.set(key, { source: s, destination: d, amount: 0 })
        }
        linkMap.get(key).amount += amount
      })

      const nodes = Array.from(nodeTotals.values())
        .map(n => ({ ...n, total: n.incoming + n.outgoing }))
        .sort((a, b) => b.total - a.total)
        .slice(0, 8)

      const nodeNames = new Set(nodes.map(n => n.name))
      const links = Array.from(linkMap.values())
        .filter(l => nodeNames.has(l.source) && nodeNames.has(l.destination))
        .sort((a, b) => b.amount - a.amount)

      return { nodes, links }
    })

    const drawSankey = () => {
      const canvas = sankeyCanvas.value
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const { nodes, links } = sankeyData.value
      if (nodes.length < 2) {
        const wrapper = canvas.parentElement
        if (wrapper) {
          canvas.width = wrapper.clientWidth
          canvas.height = 100
        }
        return
      }

      const wrapper = canvas.parentElement
      const cssWidth = wrapper ? wrapper.clientWidth : 900
      const cssHeight = Math.max(320, nodes.length * 60)

      const dpr = window.devicePixelRatio || 1
      canvas.width = cssWidth * dpr
      canvas.height = cssHeight * dpr
      canvas.style.width = `${cssWidth}px`
      canvas.style.height = `${cssHeight}px`
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.scale(dpr, dpr)
      ctx.clearRect(0, 0, cssWidth, cssHeight)

      const paddingX = 100
      const paddingY = 20
      const nodeWidth = 16
      const chartHeight = cssHeight - paddingY * 2

      const sources = nodes.filter(n => n.outgoing > 0)
      const destinations = nodes.filter(n => n.incoming > 0)

      const totalOutgoing = sources.reduce((s, n) => s + n.outgoing, 0) || 1
      const totalIncoming = destinations.reduce((s, n) => s + n.incoming, 0) || 1

      const sourcePositions = new Map()
      let yOffset = paddingY
      sources.forEach(n => {
        const h = Math.max(20, (n.outgoing / totalOutgoing) * chartHeight)
        sourcePositions.set(n.name, { x: paddingX, y: yOffset, h, node: n })
        yOffset += h + 8
      })

      const destPositions = new Map()
      yOffset = paddingY
      destinations.forEach(n => {
        const h = Math.max(20, (n.incoming / totalIncoming) * chartHeight)
        destPositions.set(n.name, { x: cssWidth - paddingX - nodeWidth, y: yOffset, h, node: n })
        yOffset += h + 8
      })

      const sourceOffsets = new Map()
      sources.forEach(s => sourceOffsets.set(s.name, 0))
      const destOffsets = new Map()
      destinations.forEach(d => destOffsets.set(d.name, 0))

      const sortedLinks = [...links].sort((a, b) => {
        const aSrcIdx = sources.findIndex(s => s.name === a.source)
        const bSrcIdx = sources.findIndex(s => s.name === b.source)
        if (aSrcIdx !== bSrcIdx) return aSrcIdx - bSrcIdx
        return b.amount - a.amount
      })

      sortedLinks.forEach(link => {
        const srcPos = sourcePositions.get(link.source)
        const dstPos = destPositions.get(link.destination)
        if (!srcPos || !dstPos) return

        const srcNode = srcPos.node
        const dstNode = dstPos.node
        const srcH = (link.amount / srcNode.outgoing) * srcPos.h
        const dstH = (link.amount / dstNode.incoming) * dstPos.h

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
        gradient.addColorStop(0, 'rgba(239, 68, 68, 0.35)')
        gradient.addColorStop(1, 'rgba(16, 185, 129, 0.35)')
        ctx.fillStyle = gradient
        ctx.fill()

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)'
        ctx.lineWidth = 0.5
        ctx.stroke()
      })

      sources.forEach(n => {
        const pos = sourcePositions.get(n.name)
        ctx.fillStyle = '#ef4444'
        ctx.fillRect(pos.x, pos.y, nodeWidth, pos.h)

        ctx.fillStyle = '#1f2937'
        ctx.font = 'bold 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        ctx.textAlign = 'right'
        ctx.textBaseline = 'middle'
        const label = n.name.length > 14 ? n.name.slice(0, 13) + '…' : n.name
        ctx.fillText(label, pos.x - 8, pos.y + pos.h / 2)

        ctx.fillStyle = '#6b7280'
        ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        ctx.fillText(`−${formatCompactCurrency(n.outgoing)} ₽`, pos.x - 8, pos.y + pos.h / 2 + 14)
      })

      destinations.forEach(n => {
        const pos = destPositions.get(n.name)
        ctx.fillStyle = '#10b981'
        ctx.fillRect(pos.x, pos.y, nodeWidth, pos.h)

        ctx.fillStyle = '#1f2937'
        ctx.font = 'bold 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        ctx.textAlign = 'left'
        ctx.textBaseline = 'middle'
        const label = n.name.length > 14 ? n.name.slice(0, 13) + '…' : n.name
        ctx.fillText(label, pos.x + nodeWidth + 8, pos.y + pos.h / 2)

        ctx.fillStyle = '#6b7280'
        ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        ctx.fillText(`+${formatCompactCurrency(n.incoming)} ₽`, pos.x + nodeWidth + 8, pos.y + pos.h / 2 + 14)
      })
    }

    // --- 1.4 Метрики ---
    const transfersCount = computed(() => transfers.value.length)
    const totalTransfersAmount = computed(() =>
      transfers.value.reduce((sum, t) => sum + (parseFloat(t.amount) || 0), 0)
    )
    const averageTransfer = computed(() =>
      transfersCount.value === 0 ? 0 : totalTransfersAmount.value / transfersCount.value
    )
    const maxTransfer = computed(() =>
      transfersCount.value === 0 ? 0 : Math.max(...transfers.value.map(t => parseFloat(t.amount) || 0))
    )
    const minTransfer = computed(() =>
      transfersCount.value === 0 ? 0 : Math.min(...transfers.value.map(t => parseFloat(t.amount) || 0))
    )
    const medianTransfer = computed(() => {
      if (transfersCount.value === 0) return 0
      const amounts = transfers.value.map(t => parseFloat(t.amount) || 0).sort((a, b) => a - b)
      const mid = Math.floor(amounts.length / 2)
      return amounts.length % 2 === 0
        ? (amounts[mid - 1] + amounts[mid]) / 2
        : amounts[mid]
    })

    // --- 1.3 Активность ---
    const activityCanvas = ref(null)
    const activityRange = ref(30)
    const activityRanges = [
      { value: 7, label: '7 дней' },
      { value: 14, label: '14 дней' },
      { value: 30, label: '30 дней' },
      { value: 90, label: '90 дней' }
    ]

    const formatDateKey = (d) => {
      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    const activityData = computed(() => {
      const days = activityRange.value
      const now = new Date()
      now.setHours(23, 59, 59, 999)
      const result = []
      for (let i = days - 1; i >= 0; i--) {
        const d = new Date(now)
        d.setDate(d.getDate() - i)
        d.setHours(0, 0, 0, 0)
        result.push({
          date: new Date(d),
          dateKey: formatDateKey(d),
          count: 0,
          amount: 0
        })
      }
      const map = new Map(result.map(r => [r.dateKey, r]))
      transfers.value.forEach(t => {
        if (!t.timestamp) return
        const d = new Date(t.timestamp)
        if (isNaN(d.getTime())) return
        const entry = map.get(formatDateKey(d))
        if (entry) {
          entry.count += 1
          entry.amount += parseFloat(t.amount) || 0
        }
      })
      return result
    })

    const activityTotalCount = computed(() => activityData.value.reduce((s, d) => s + d.count, 0))
    const activityTotalAmount = computed(() => activityData.value.reduce((s, d) => s + d.amount, 0))

    const activityBusiestDay = computed(() => {
      if (activityData.value.length === 0) return null
      const max = activityData.value.reduce((best, d) => d.count > best.count ? d : best, activityData.value[0])
      if (max.count === 0) return null
      const label = max.date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
      return { ...max, label }
    })

    const drawActivityChart = () => {
      const canvas = activityCanvas.value
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      const data = activityData.value
      if (data.length === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        return
      }

      const wrapper = canvas.parentElement
      const cssWidth = wrapper ? wrapper.clientWidth : 800
      const cssHeight = 260
      const dpr = window.devicePixelRatio || 1
      canvas.width = cssWidth * dpr
      canvas.height = cssHeight * dpr
      canvas.style.width = `${cssWidth}px`
      canvas.style.height = `${cssHeight}px`
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.scale(dpr, dpr)
      ctx.clearRect(0, 0, cssWidth, cssHeight)

      const paddingLeft = 50
      const paddingRight = 20
      const paddingTop = 30
      const paddingBottom = 40
      const chartWidth = cssWidth - paddingLeft - paddingRight
      const chartHeight = cssHeight - paddingTop - paddingBottom
      const maxAmount = Math.max(...data.map(d => d.amount), 1)
      const barWidth = chartWidth / data.length
      const barGap = Math.min(4, barWidth * 0.2)

      ctx.strokeStyle = '#e5e7eb'
      ctx.lineWidth = 1
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.fillStyle = '#9ca3af'
      ctx.textAlign = 'right'
      ctx.textBaseline = 'middle'

      for (let i = 0; i <= 4; i++) {
        const value = (maxAmount / 4) * i
        const y = paddingTop + chartHeight - (i / 4) * chartHeight
        ctx.beginPath()
        ctx.moveTo(paddingLeft, y)
        ctx.lineTo(cssWidth - paddingRight, y)
        ctx.stroke()
        ctx.fillText(formatCompactCurrency(value), paddingLeft - 6, y)
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

    // --- 1.7 Heatmap ---
    const heatmapCanvas = ref(null)
    const heatmapMode = ref('count')
    const heatmapWeeks = 26

    const heatmapData = computed(() => {
      const now = new Date()
      now.setHours(23, 59, 59, 999)

      const end = new Date(now)
      const dayOfWeek = (end.getDay() + 6) % 7
      end.setDate(end.getDate() + (6 - dayOfWeek))
      end.setHours(23, 59, 59, 999)

      const totalDays = heatmapWeeks * 7
      const start = new Date(end)
      start.setDate(start.getDate() - totalDays + 1)
      start.setHours(0, 0, 0, 0)

      const cells = []
      const map = new Map()

      for (let i = 0; i < totalDays; i++) {
        const d = new Date(start)
        d.setDate(d.getDate() + i)
        const key = formatDateKey(d)
        const cell = { date: new Date(d), key, count: 0, amount: 0 }
        cells.push(cell)
        map.set(key, cell)
      }

      transfers.value.forEach(t => {
        if (!t.timestamp) return
        const d = new Date(t.timestamp)
        if (isNaN(d.getTime())) return
        const cell = map.get(formatDateKey(d))
        if (cell) {
          cell.count += 1
          cell.amount += parseFloat(t.amount) || 0
        }
      })

      const values = cells.map(c => heatmapMode.value === 'count' ? c.count : c.amount)
      const maxValue = Math.max(...values, 1)
      const activeDays = cells.filter(c => (heatmapMode.value === 'count' ? c.count : c.amount) > 0).length

      return { cells, maxValue, activeDays, totalDays, start, end }
    })

    const heatmapActiveDays = computed(() => heatmapData.value.activeDays)
    const heatmapTotalDays = computed(() => heatmapData.value.totalDays)
    const heatmapMaxDay = computed(() => {
      if (heatmapData.value.cells.length === 0) return null
      const max = heatmapData.value.cells.reduce((best, c) => {
        const val = heatmapMode.value === 'count' ? c.count : c.amount
        const bestVal = heatmapMode.value === 'count' ? best.count : best.amount
        return val > bestVal ? c : best
      }, heatmapData.value.cells[0])
      if (max.count === 0) return null
      return {
        ...max,
        label: max.date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
      }
    })

    const drawHeatmap = () => {
      const canvas = heatmapCanvas.value
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const { cells, maxValue } = heatmapData.value
      if (cells.length === 0) return

      const wrapper = canvas.parentElement
      const cssWidth = wrapper ? wrapper.clientWidth : 800

      const cellSize = 13
      const cellGap = 3
      const leftPadding = 40
      const topPadding = 24
      const bottomPadding = 30

      const cssHeight = topPadding + 7 * (cellSize + cellGap) + bottomPadding

      const dpr = window.devicePixelRatio || 1
      canvas.width = cssWidth * dpr
      canvas.height = cssHeight * dpr
      canvas.style.width = `${cssWidth}px`
      canvas.style.height = `${cssHeight}px`
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.scale(dpr, dpr)
      ctx.clearRect(0, 0, cssWidth, cssHeight)

      const levels = ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127']

      const dayLabels = ['Пн', 'Ср', 'Пт']
      ctx.fillStyle = '#6b7280'
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.textAlign = 'right'
      ctx.textBaseline = 'middle'
      ;[0, 2, 4].forEach((dayIdx) => {
        const y = topPadding + dayIdx * (cellSize + cellGap) + cellSize / 2
        ctx.fillText(dayLabels[dayIdx / 2], leftPadding - 6, y)
      })

      ctx.textAlign = 'left'
      ctx.textBaseline = 'bottom'
      let lastMonth = -1
      cells.forEach((cell, i) => {
        const weekIdx = Math.floor(i / 7)
        const dayIdx = i % 7
        if (dayIdx === 0) {
          const month = cell.date.getMonth()
          if (month !== lastMonth) {
            lastMonth = month
            const x = leftPadding + weekIdx * (cellSize + cellGap)
            const monthLabel = cell.date.toLocaleDateString('ru-RU', { month: 'short' })
            ctx.fillText(monthLabel, x, topPadding - 6)
          }
        }
      })

      cells.forEach((cell, i) => {
        const weekIdx = Math.floor(i / 7)
        const dayIdx = i % 7
        const x = leftPadding + weekIdx * (cellSize + cellGap)
        const y = topPadding + dayIdx * (cellSize + cellGap)

        const value = heatmapMode.value === 'count' ? cell.count : cell.amount
        let level = 0
        if (value > 0) {
          const ratio = value / maxValue
          if (ratio <= 0.25) level = 1
          else if (ratio <= 0.5) level = 2
          else if (ratio <= 0.75) level = 3
          else level = 4
        }

        ctx.fillStyle = levels[level]
        ctx.beginPath()
        const r = 2
        ctx.moveTo(x + r, y)
        ctx.arcTo(x + cellSize, y, x + cellSize, y + cellSize, r)
        ctx.arcTo(x + cellSize, y + cellSize, x, y + cellSize, r)
        ctx.arcTo(x, y + cellSize, x, y, r)
        ctx.arcTo(x, y, x + cellSize, y, r)
        ctx.closePath()
        ctx.fill()
      })
    }

    // --- Общие функции ---
    const toggleExpand = (accountId) => {
      if (expandedAccounts.value.has(accountId)) expandedAccounts.value.delete(accountId)
      else expandedAccounts.value.add(accountId)
      expandedAccounts.value = new Set(expandedAccounts.value)
    }

    const toggleExpandTransfer = (transferId) => {
      if (expandedTransfers.value.has(transferId)) expandedTransfers.value.delete(transferId)
      else expandedTransfers.value.add(transferId)
      expandedTransfers.value = new Set(expandedTransfers.value)
    }

    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    const scheduleAllDraws = () => {
      nextTick(() => {
        setTimeout(() => {
          drawDistributionChart()
          drawRatioChart()
          drawActivityChart()
          drawHeatmap()
          drawSankey()
          drawHistoryChart()
        }, 50)
      })
    }

    // --- Загрузка ---
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

    // --- Действия со счетами ---
    const openCreateModal = () => {
      editingAccount.value = null
      formData.value = { name: '', balance: 0, is_active: true }
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
      newBalance.value = parseFloat(account.balance)
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

    const closeModal = () => {
      showAccountModal.value = false
      editingAccount.value = null
      formData.value = { name: '', balance: 0, is_active: true }
    }

    // --- Действия с переводами ---
    const openTransferFor = (account) => {
      transferData.value = {
        source_account: account.id,
        destination_account: '',
        amount: '',
        timestamp: new Date().toISOString().slice(0, 16)
      }
      setTimeout(() => {
        const transferForm = document.querySelector('.transfer-form')
        if (transferForm) transferForm.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
      let sourceAccountId = null
      let destinationAccountId = null
      if (transfer.source_account_name) {
        const foundSource = accounts.value.find(acc => acc.name === transfer.source_account_name)
        if (foundSource) sourceAccountId = foundSource.id
      }
      if (transfer.destination_account_name) {
        const foundDest = accounts.value.find(acc => acc.name === transfer.destination_account_name)
        if (foundDest) destinationAccountId = foundDest.id
      }
      editTransferData.value = {
        source_account: sourceAccountId || '',
        destination_account: destinationAccountId || '',
        amount: transfer.amount,
        timestamp: transfer.timestamp ? transfer.timestamp.slice(0, 16) : new Date().toISOString().slice(0, 16)
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
        await loadBalanceHistory()
      } catch (error) {
        console.error('Error deleting transfer:', error)
        alert('Ошибка при удалении перевода')
      }
    }

    const closeEditTransferModal = () => {
      showEditTransferModal.value = false
      editingTransfer.value = null
      editTransferData.value = { source_account: '', destination_account: '', amount: '', timestamp: '' }
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

    // --- Форматирование ---
    const formatCurrency = (value) => {
      if (!value && value !== 0) return '0 ₽'
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value)
    }

    const formatCompactCurrency = (value) => {
      if (!value && value !== 0) return '0'
      const abs = Math.abs(value)
      if (abs >= 1000000) return (value / 1000000).toFixed(1) + 'M'
      if (abs >= 1000) return (value / 1000).toFixed(0) + 'k'
      return String(Math.round(value))
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

    // --- Watchers ---
    watch(distributionData, () => scheduleAllDraws())
    watch(activityRange, () => scheduleAllDraws())
    watch(heatmapMode, () => scheduleAllDraws())
    watch([sankeyData, topAccountPairs], () => scheduleAllDraws())
    watch(historyRange, () => {
      loadBalanceHistory()
    })
    watch(historyMode, () => scheduleHistoryDraw())
    watch(visibleHistoryAccounts, () => scheduleHistoryDraw(), { deep: true })

    const handleResize = () => scheduleAllDraws()

    onMounted(async () => {
      await loadAccounts()
      await loadTransfers()
      await loadBalanceHistory()
      window.addEventListener('resize', handleResize)
      scheduleAllDraws()
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
    })

    return {
      // Счета
      accounts,
      activeAccounts,
      inactiveAccounts,
      allAccounts,
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
      // 2.1
      historyCanvas,
      historyRange,
      historyRanges,
      historyMode,
      historyLoading,
      historyError,
      historyAccounts,
      visibleHistoryAccounts,
      historyTotalSeries,
      historyStartBalance,
      historyEndBalance,
      historyChange,
      historyChangePercent,
      historyChangeClass,
      historyMinTotal,
      historyMaxTotal,
      historyPeriodLabel,
      historyTooltip,
      loadBalanceHistory,
      toggleHistoryAccount,
      onHistoryMouseMove,
      onHistoryMouseLeave,
      // 1.1
      distributionCanvas,
      distributionData,
      // 1.5
      ratioCanvas,
      activeRatioPercent,
      // 1.6
      getLastActivityLabel,
      getActivityClass,
      getActivityIcon,
      // 1.2
      topAccountsByTurnover,
      // 1.8
      topAccountPairs,
      // 1.9
      sankeyCanvas,
      sankeyData,
      // 1.3
      activityCanvas,
      activityRange,
      activityRanges,
      activityData,
      activityTotalCount,
      activityTotalAmount,
      activityBusiestDay,
      // 1.7
      heatmapCanvas,
      heatmapMode,
      heatmapActiveDays,
      heatmapTotalDays,
      heatmapMaxDay,
      // 1.4
      transfersCount,
      totalTransfersAmount,
      averageTransfer,
      maxTransfer,
      minTransfer,
      medianTransfer,
      // Переводы
      transfers,
      currentPage,
      totalPages,
      totalCount,
      transferLoading,
      showEditTransferModal,
      showDeleteTransferModal,
      editingTransfer,
      transferToDelete,
      transferData,
      editTransferData,
      otherAccounts,
      editOtherAccounts,
      expandedTransfers,
      // Методы
      toggleExpand,
      toggleExpandTransfer,
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
      openTransferFor,
      createTransfer,
      editTransfer,
      updateTransfer,
      confirmDeleteTransfer,
      deleteTransfer,
      closeEditTransferModal,
      prevPage,
      nextPage,
      formatCurrency,
      formatCompactCurrency,
      formatDate,
      formatShortDate
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

/* Санкей */
.sankey-body {
  width: 100%;
  overflow-x: auto;
  padding: 0.5rem 0;
}

.sankey-canvas { display: block; width: 100%; }

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

/* Heatmap */
.heatmap-card { margin-bottom: 1.5rem; }

.heatmap-mode {
  display: flex;
  gap: 0.25rem;
  background: var(--light-color);
  padding: 0.25rem;
  border-radius: var(--radius);
}

.heatmap-body {
  width: 100%;
  overflow-x: auto;
  padding: 0.5rem 0;
}

.heatmap-canvas { display: block; }

.heatmap-footer {
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

.heatmap-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.heatmap-stats strong { color: var(--dark-color); }

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.heatmap-legend-label {
  font-size: 0.7rem;
  color: var(--gray-color);
  margin: 0 0.25rem;
}

.heatmap-cell {
  width: 13px;
  height: 13px;
  border-radius: 3px;
  display: inline-block;
}

.heatmap-level-0 { background: #ebedf0; }
.heatmap-level-1 { background: #c6e48b; }
.heatmap-level-2 { background: #7bc96f; }
.heatmap-level-3 { background: #239a3b; }
.heatmap-level-4 { background: #196127; }

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
  .heatmap-mode { width: 100%; }
  .heatmap-footer { flex-direction: column; align-items: flex-start; }
  .history-stats { gap: 1rem; }
  .history-stat-value { font-size: 0.85rem; }
  .history-footer { flex-direction: column; align-items: flex-start; }
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
  .sankey-canvas { min-width: 500px; }
  .history-legend { gap: 0.375rem; }
  .history-legend-item { font-size: 0.7rem; padding: 0.25rem 0.5rem; }
  .history-stats { flex-direction: column; gap: 0.5rem; }
  .history-tooltip { min-width: 150px; font-size: 0.7rem; }
}
</style>