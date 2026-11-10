<template>
  <div class="timesheets-container" v-if="monthlyStats">
    <!-- Заголовок -->
    <div class="page-header">
      <h1 class="page-title">
        <i class="fas fa-calendar-alt"></i>
        Мой график
      </h1>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="openSettingsModal">
          <i class="fas fa-cog"></i>
          <span class="btn-text">Настройки</span>
        </button>
        <button class="btn btn-primary" @click="openAddManyModal">
          <i class="fas fa-layer-group"></i>
          <span class="btn-text">Проставить смены</span>
        </button>
        <button class="btn btn-info" @click="openYearStatsModal">
          <i class="fas fa-chart-line"></i>
          <span class="btn-text">Статистика за год</span>
        </button>
        <button class="btn btn-vacation" @click="openVacationModal">
          <i class="fas fa-umbrella-beach"></i>
          <span class="btn-text">Отпуск/Больничный</span>
        </button>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- БЛОК ЦЕЛИ ПО МОТИВАЦИИ (над календарем)                       -->
    <!-- ============================================================ -->
    <div v-if="currentGoal" class="goal-progress-card" :class="goalProgressClass">
      <div class="goal-progress-header">
        <div class="goal-title">
          <span v-if="isGoalAchieved" class="goal-achieved-icon">🏆</span>
          <span v-else>🎯</span>
          Цель по мотивации
        </div>
        <div class="goal-values">
          <strong>{{ formatNumber(goalCurrentAmount) }} ₽</strong> / {{ formatNumber(currentGoal.amount) }} ₽
        </div>
      </div>

      <div class="goal-progress-bar">
        <div class="goal-progress-fill" :style="{ width: Math.min(goalProgressPercent, 100) + '%' }"></div>
        <span class="goal-percent-badge">{{ Math.round(goalProgressPercent) }}%</span>
      </div>

      <!-- Блок прогноза / результата -->
      <div v-if="goalForecastInfo" class="goal-forecast" :class="goalForecastInfo.status">
        <i class="fas" :class="goalForecastInfo.icon"></i>
        <span>{{ goalForecastInfo.text }}</span>
      </div>

      <div v-if="isGoalAchieved" class="goal-achieved-banner">
        🎉 Цель достигнута! Отличная работа!
      </div>

      <button class="goal-edit-btn" @click="openGoalModal" title="Изменить цель">
        <i class="fas fa-pen"></i>
      </button>
    </div>

    <!-- Если цели нет -->
    <div v-else class="goal-empty-card">
      <button class="btn-add-goal" @click="openGoalModal">
        <i class="fas fa-bullseye"></i> Поставить цель по мотивации на этот месяц
      </button>
    </div>

    <!-- Навигация по месяцам -->
    <div class="month-navigation">
      <button class="btn-nav" @click="previousMonth">
        <i class="fas fa-chevron-left"></i>
      </button>
      <div class="current-month">
        <h2>{{ currentMonthName }} {{ currentYear }}</h2>
      </div>
      <button class="btn-nav" @click="nextMonth">
        <i class="fas fa-chevron-right"></i>
      </button>
      <button class="btn-today" @click="goToToday">
        <i class="fas fa-calendar-day"></i>
        Сегодня
      </button>
    </div>

    <!-- Дни недели -->
    <div class="weekdays">
      <div v-for="day in weekDays" :key="day" class="weekday" :class="{'weekend': day === 'Сб' || day === 'Вс'}">
        {{ day }}
      </div>
    </div>

    <!-- Календарь -->
    <div class="calendar-grid" :style="{ gridTemplateRows: `repeat(${calendarRows}, 1fr)` }">
      <div
        v-for="(day, index) in calendarDays"
        :key="index"
        class="calendar-day"
        :class="{
          'other-month': !day.isCurrentMonth,
          'weekend-day': day.isCurrentMonth && day.isWeekend && !day.hasShift && !day.isVacation && !day.isSick,
          'weekend-with-shift': day.isCurrentMonth && day.isWeekend && day.hasShift,
          'today': day.isCurrentMonth && day.isToday,
          'has-shift': day.isCurrentMonth && day.hasShift && !day.isWeekend && !day.isVacation && !day.isSick,
          'vacation-day': day.isCurrentMonth && day.isVacation,
          'sick-day': day.isCurrentMonth && day.isSick
        }"
        @click="openShiftModal(day)"
      >
        <div class="day-number">{{ day.dayNumber }}</div>
        <div v-if="day.isCurrentMonth && day.isVacation" class="day-status vacation-status">
          <i class="fas fa-umbrella-beach"></i>
          <span>О</span>
        </div>
        <div v-else-if="day.isCurrentMonth && day.isSick" class="day-status sick-status">
          <i class="fas fa-thermometer-half"></i>
          <span>Б</span>
        </div>
        <div v-else-if="day.isCurrentMonth && day.hasShift && day.earned && day.earned > 0" class="day-earned">
          {{ formatNumberShort(day.earned) }} ₽
        </div>
        <div v-else-if="day.isCurrentMonth && !day.hasShift && !day.isVacation && !day.isSick" class="day-empty">
          <i class="fas fa-plus-circle"></i>
        </div>
      </div>
    </div>

    <!-- Детальная статистика за месяц (минималистичные кнопки) -->
    <div class="month-statistics">
      <div class="modern-stats-grid">
        <!-- Период 1 -->
        <div class="modern-stat-card" v-if="hasPeriodData(monthlyStats.period_one)" @click="openStatsModal('period1')">
          <div class="modern-stat-inner bg-green">
            <div class="modern-icon">
              <i class="fas fa-calendar-alt"></i>
            </div>
            <div class="modern-text">
              <div class="modern-title">Период 1 <span class="modern-sub">(1–15)</span></div>
              <div class="modern-amount">{{ formatNumber(monthlyStats.period_one.total_earned) }} ₽</div>
            </div>
            <i class="fas fa-chevron-right modern-arrow"></i>
          </div>
        </div>

        <!-- Период 2 -->
        <div class="modern-stat-card" v-if="hasPeriodData(monthlyStats.period_two)" @click="openStatsModal('period2')">
          <div class="modern-stat-inner bg-green">
            <div class="modern-icon">
              <i class="fas fa-calendar-alt"></i>
            </div>
            <div class="modern-text">
              <div class="modern-title">Период 2 <span class="modern-sub">(16–31)</span></div>
              <div class="modern-amount">{{ formatNumber(monthlyStats.period_two.total_earned) }} ₽</div>
            </div>
            <i class="fas fa-chevron-right modern-arrow"></i>
          </div>
        </div>

        <!-- Итого за месяц -->
        <div class="modern-stat-card" @click="openStatsModal('total')">
          <div class="modern-stat-inner bg-blue">
            <div class="modern-icon">
              <i class="fas fa-chart-pie"></i>
            </div>
            <div class="modern-text">
              <div class="modern-title">Итого за месяц</div>
              <div class="modern-amount">{{ formatNumber(monthlyStats.total?.total_earned) }} ₽</div>
            </div>
            <i class="fas fa-chevron-right modern-arrow"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- МОДАЛКА: Детальная статистика (bottom-sheet)                 -->
    <!-- ============================================================ -->
    <div v-if="showStatsModal" class="modal modal-bottom-sheet" @click.self="closeStatsModal">
      <div class="modal-content">
        <div class="sheet-handle"></div>
        <div class="modal-header" :class="selectedStatsType === 'total' ? 'total-header' : ''">
          <h3>
            <i class="fas" :class="selectedStatsType === 'total' ? 'fa-chart-bar' : 'fa-calendar-week'"></i>
            {{ statsModalTitle }}
          </h3>
          <button class="modal-close" @click="closeStatsModal">&times;</button>
        </div>

        <div class="modal-body" v-if="statsModalData">
          <!-- Часы -->
          <div v-if="statsModalData.total_base_hours" class="stat-line">
            <span class="stat-label">Часы:</span>
            <span class="stat-number">{{ statsModalData.total_base_hours }} ч</span>
          </div>

          <!-- Заработано за часы -->
          <div v-if="statsModalData.total_earned_hours" class="stat-line">
            <span class="stat-label">Заработано за часы:</span>
            <span class="stat-number">{{ formatNumber(statsModalData.total_earned_hours) }} ₽</span>
          </div>

          <!-- Доплата за холод -->
          <div v-if="statsModalData.total_earned_cold" class="stat-line">
            <span class="stat-label">Доплата за холод:</span>
            <span class="stat-number">{{ formatNumber(statsModalData.total_earned_cold) }} ₽</span>
          </div>

          <!-- Мотивация -->
          <div v-if="getMotivationTotal(statsModalData) > 0" class="stat-line award-line">
            <span class="stat-label">🏆 Мотивация (всего):</span>
            <span class="stat-number award">{{ formatNumber(getMotivationTotal(statsModalData)) }} ₽</span>
          </div>
          <div v-if="statsModalData.total_earned_collect" class="stat-line sub-line">
            <span class="stat-label">— Набор:</span>
            <span class="stat-number">{{ formatNumber(statsModalData.total_earned_collect) }} ₽ ({{ statsModalData.total_operations_collect || 0 }} оп)</span>
          </div>
          <div v-if="statsModalData.total_earned_replenishment" class="stat-line sub-line">
            <span class="stat-label">— Пополнение:</span>
            <span class="stat-number">{{ formatNumber(statsModalData.total_earned_replenishment) }} ₽ ({{ statsModalData.total_operations_replenishment || 0 }} оп)</span>
          </div>
          <div v-if="statsModalData.total_earned_placement" class="stat-line sub-line">
            <span class="stat-label">— Размещение:</span>
            <span class="stat-number">{{ formatNumber(statsModalData.total_earned_placement) }} ₽ ({{ statsModalData.total_operations_placement || 0 }} оп)</span>
          </div>
          <div v-if="statsModalData.total_earned_for_non_production" class="stat-line sub-line">
            <span class="stat-label">— Непроизводственные:</span>
            <span class="stat-number">{{ formatNumber(statsModalData.total_earned_for_non_production) }} ₽ ({{ formatNumber(statsModalData.total_hours_for_non_production) }} ч)</span>
          </div>

          <!-- Переработка (основная сумма) -->
          <div v-if="statsModalData.total_overtime" class="stat-line">
            <span class="stat-label">Доплата за переработку:</span>
            <span class="stat-number overtime">{{ formatNumber(statsModalData.total_overtime) }} ₽</span>
          </div>
          <div v-if="statsModalData.total_hours_overtime" class="stat-line">
            <span class="stat-label">Часов переработки:</span>
            <span class="stat-number">{{ statsModalData.total_hours_overtime }} ч</span>
          </div>

          <!-- ============================================== -->
          <!-- АНАЛИТИКА (Аккордеон)                          -->
          <!-- ============================================== -->
          <div v-if="hasAnalyticsContent" class="accordion-item stats-analytics-accordion">
            <div class="accordion-header" @click="openStatsAnalytics = !openStatsAnalytics">
              <span class="accordion-icon">📊</span>
              <span class="accordion-title">Аналитика</span>
              <i class="fas" :class="openStatsAnalytics ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div v-show="openStatsAnalytics" class="accordion-body">

              <!-- Операции -->
              <div v-if="getOperationsTotal(statsModalData)" class="stat-line">
                <span class="stat-label">Кол-во операций:</span>
                <span class="stat-number">{{ getOperationsTotal(statsModalData) }}</span>
              </div>

              <!-- Производительность -->
              <div v-if="getOperationsTotal(statsModalData) && statsModalData.total_base_hours" class="stat-line productivity-line">
                <span class="stat-label">⚡ Производительность:</span>
                <span class="stat-number productivity">{{ getProductivity(getOperationsTotal(statsModalData), statsModalData.total_base_hours) }} оп/ч</span>
              </div>

              <!-- Проценты (только для Итого) -->
              <template v-if="selectedStatsType === 'total'">
                <div v-if="statsModalData.total_earned_hours && statsModalData.total_earned" class="stat-line hours-percent-line">
                  <span class="stat-label">⏳ Доля оплаты за часы:</span>
                  <span class="stat-number">{{ getHoursPercent(statsModalData.total_earned_hours, statsModalData.total_earned) }}%</span>
                </div>
                <div v-if="statsModalData.total_earned_cold && statsModalData.total_earned" class="stat-line cold-percent-line">
                  <span class="stat-label">❄️ Доля доплаты за холод:</span>
                  <span class="stat-number">{{ getColdPercent(statsModalData.total_earned_cold, statsModalData.total_earned) }}%</span>
                </div>
                <div v-if="getMotivationTotal(statsModalData) > 0 && statsModalData.total_earned" class="stat-line award-percent-line">
                  <span class="stat-label">🏆 Доля мотивации:</span>
                  <span class="stat-number">{{ getAwardPercent(getMotivationTotal(statsModalData), statsModalData.total_earned) }}%</span>
                </div>
                <div v-if="statsModalData.total_earned_for_non_production && statsModalData.total_earned" class="stat-line non-productive-percent-line">
                  <span class="stat-label">🪏 Доля непроиз-х работ:</span>
                  <span class="stat-number">{{ getNonProductivePercent(statsModalData.total_earned_for_non_production, statsModalData.total_earned) }}%</span>
                </div>
                <div v-if="statsModalData.total_overtime && statsModalData.total_earned" class="stat-line overtime-percent-line">
                  <span class="stat-label">⏱️ Доля доплаты за переработку:</span>
                  <span class="stat-number overtime">{{ getOvertimePercent(statsModalData.total_overtime, statsModalData.total_earned) }}%</span>
                </div>
              </template>

              <!-- Динамика (только для Итого) -->
              <div v-if="selectedStatsType === 'total' && periodOneProductivity !== null && periodTwoProductivity !== null" class="dynamics-line">
                <div class="dynamics-header">📈 Динамика производительности</div>
                <div class="dynamics-content">
                  <span class="period1-value">{{ periodOneProductivity.toFixed(2) }} оп/ч</span>
                  <i class="fas fa-arrow-right"></i>
                  <span class="period2-value">{{ periodTwoProductivity.toFixed(2) }} оп/ч</span>
                  <span class="dynamics-change" :class="productivityChangeClass">
                    {{ productivityChangeSymbol }} {{ Math.abs(productivityChangePercent).toFixed(1) }}%
                  </span>
                </div>
              </div>

              <!-- Лучший день (Периоды) -->
              <div v-if="selectedStatsType === 'period1' && periodOneBestDay" class="best-day-period">
                <div class="best-day-header">🏆 Лучший день периода</div>
                <div class="best-day-content">
                  <span class="best-day-date">{{ periodOneBestDay.dateStr }}</span>
                  <span class="best-day-stats">{{ periodOneBestDay.count_operations }} оп / {{ periodOneBestDay.base_hours }} ч</span>
                  <span class="best-day-productivity">{{ periodOneBestDay.productivity.toFixed(2) }} оп/ч</span>
                </div>
              </div>
              <div v-if="selectedStatsType === 'period2' && periodTwoBestDay" class="best-day-period">
                <div class="best-day-header">🏆 Лучший день периода</div>
                <div class="best-day-content">
                  <span class="best-day-date">{{ periodTwoBestDay.dateStr }}</span>
                  <span class="best-day-stats">{{ periodTwoBestDay.count_operations }} оп / {{ periodTwoBestDay.base_hours }} ч</span>
                  <span class="best-day-productivity">{{ periodTwoBestDay.productivity.toFixed(2) }} оп/ч</span>
                </div>
              </div>

              <!-- Лучший день (Итого) -->
              <div v-if="selectedStatsType === 'total' && monthBestDay" class="best-day-month">
                <div class="best-day-header">🏆 Лучший день месяца</div>
                <div class="best-day-content">
                  <span class="best-day-date">{{ monthBestDay.dateStr }} ({{ monthBestDay.dayOfWeek }})</span>
                  <span class="best-day-stats">{{ monthBestDay.count_operations }} оп / {{ monthBestDay.base_hours }} ч</span>
                  <span class="best-day-productivity">{{ monthBestDay.productivity.toFixed(2) }} оп/ч</span>
                </div>
              </div>
            </div>
          </div>
          <!-- ============================================== -->

          <!-- Валюта (Переделан в стандартный аккордеон) -->
          <div v-if="hasCurrencyData(statsModalData)" class="accordion-item stats-analytics-accordion">
            <div class="accordion-header" @click="showStatsCurrency = !showStatsCurrency">
              <span class="accordion-icon">💱</span>
              <span class="accordion-title">Заработано в валюте</span>
              <i class="fas" :class="showStatsCurrency ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div v-show="showStatsCurrency" class="accordion-body">
              <div v-if="statsModalData.dollar" class="currency-line">🇺🇸 Доллар: ${{ formatNumber(statsModalData.dollar) }}</div>
              <div v-if="statsModalData.euro" class="currency-line">🇪🇺 Евро: €{{ formatNumber(statsModalData.euro) }}</div>
              <div v-if="statsModalData.yena" class="currency-line">🇨🇳 Юань: ¥{{ formatNumber(statsModalData.yena) }}</div>
              <div v-if="statsModalData.som" class="currency-line">🇰🇬 Сом: {{ formatNumber(statsModalData.som) }}</div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-primary btn-save" @click="closeStatsModal">
            <i class="fas fa-check"></i>
            <span>Понятно</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- МОДАЛКА: Настройка цели                                      -->
    <!-- ============================================================ -->
    <div v-if="showGoalModal" class="modal modal-bottom-sheet" @click.self="closeGoalModal">
      <div class="modal-content">
        <div class="sheet-handle"></div>
        <div class="modal-header">
          <h3><i class="fas fa-bullseye"></i> Цель по мотивации</h3>
          <button class="modal-close" @click="closeGoalModal">&times;</button>
        </div>
        <div class="modal-body">
          <p class="goal-modal-desc">Укажите желаемую сумму премии (мотивации) на этот месяц. Мы будем считать прогресс и прогноз по вашим сменам.</p>
          <div class="form-group">
            <label class="form-label required">Сумма цели (₽)</label>
            <input type="number" v-model.number="goalData.amount" class="form-control" min="0" step="500" placeholder="Например, 20000" />
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="currentGoal" class="btn-icon btn-danger" @click="deleteGoal" :disabled="isSavingGoal" title="Удалить цель">
            <i class="fas fa-trash"></i>
          </button>
          <button class="btn-primary btn-save" @click="saveGoal" :disabled="isSavingGoal || !goalData.amount">
            <i :class="isSavingGoal ? 'fas fa-spinner fa-spin' : 'fas fa-save'"></i>
            <span>{{ isSavingGoal ? 'Сохранение...' : 'Сохранить' }}</span>
          </button>
          <button class="btn-icon btn-secondary" @click="closeGoalModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- МОДАЛКА: Групповое проставление смен (bottom-sheet)          -->
    <!-- ============================================================ -->
    <div v-if="showAddManyModal" class="modal modal-bottom-sheet" @click.self="closeAddManyModal">
      <div class="modal-content">
        <div class="sheet-handle"></div>
        <div class="modal-header">
          <h3>
            <i class="fas fa-layer-group"></i>
            Отметить смены
          </h3>
          <div class="header-tools">
            <button class="btn-compact btn-success" @click="selectAllDatesInMonth" title="Выбрать все">
              <i class="fas fa-check-double"></i>
              <span class="btn-text-compact">Все</span>
            </button>
            <button class="btn-compact btn-warning" @click="clearAllDates" title="Очистить">
              <i class="fas fa-times"></i>
              <span class="btn-text-compact">Очистить</span>
            </button>
            <button class="modal-close" @click="closeAddManyModal">&times;</button>
          </div>
        </div>

        <div class="compact-toolbar">
          <div class="toolbar-row">
            <label>Часов:</label>
            <input type="number" v-model.number="manyShiftsData.hours" class="form-control toolbar-input" step="0.5" />
          </div>
          <div class="toolbar-row toolbar-month">
            <button class="btn-month-nav" @click="prevSelectionMonth">
              <i class="fas fa-chevron-left"></i>
            </button>
            <span class="selected-month">{{ selectionMonthName }} {{ selectionYear }}</span>
            <button class="btn-month-nav" @click="nextSelectionMonth">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>

        <div class="modal-body">
          <div class="selection-calendar">
            <div class="selection-weekdays">
              <div v-for="day in weekDays" :key="day" class="selection-weekday">{{ day }}</div>
            </div>
            <div class="selection-grid">
              <div
                v-for="(date, idx) in selectionDates"
                :key="idx"
                class="selection-day"
                :class="{
                  'selected': isDateSelected(date.fullDate),
                  'has-shift': date.hasShift || date.isVacation || date.isSick,
                  'other-month-date': !date.isCurrentMonth
                }"
                @click="toggleDateSelection(date.fullDate)"
              >
                <span class="selection-day-number">{{ date.dayNumber }}</span>
                <i v-if="isDateSelected(date.fullDate)" class="fas fa-check-circle check-icon"></i>
                <i v-else-if="date.hasShift" class="fas fa-calendar-check shift-icon"></i>
                <i v-else-if="date.isVacation" class="fas fa-umbrella-beach vacation-icon"></i>
                <i v-else-if="date.isSick" class="fas fa-thermometer-half sick-icon"></i>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-primary btn-save" @click="saveManyShifts" :disabled="isSavingMany || !manyShiftsData.hours || manyShiftsData.selectedDates.length === 0">
            <i :class="isSavingMany ? 'fas fa-spinner fa-spin' : 'fas fa-save'"></i>
            <span>{{ isSavingMany ? 'Сохранение...' : 'Сохранить (' + manyShiftsData.selectedDates.length + ')' }}</span>
          </button>
          <button class="btn-icon btn-secondary" @click="closeAddManyModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- МОДАЛКА: День (bottom-sheet с аккордеонами)                  -->
    <!-- ============================================================ -->
    <div v-if="showShiftModal" class="modal modal-bottom-sheet" @click.self="closeShiftModal">
      <div class="modal-content">
        <div class="sheet-handle"></div>
        <div class="modal-header">
          <h3>
            <i class="fas fa-calendar-day"></i>
            {{ formatDateShort(selectedDay?.fullDate) }}
          </h3>
          <button class="modal-close" @click="closeShiftModal">&times;</button>
        </div>

        <!-- Sticky summary-bar -->
        <div
          v-if="shiftDetails && !selectedDay?.isVacation && !selectedDay?.isSick"
          class="day-summary-bar"
        >
          <div class="summary-chip">
            <span>💰</span>
            <span class="summary-chip-value">{{ formatNumber(shiftDetails.earned) }} ₽</span>
          </div>
          <div class="summary-chip">
            <span>⏱</span>
            <span class="summary-chip-value">{{ shiftDetails.base_hours }} ч</span>
          </div>
          <div
            v-if="getOperationsTotal(shiftDetails) && shiftDetails.base_hours"
            class="summary-chip"
          >
            <span>⚡</span>
            <span class="summary-chip-value">
              {{ getProductivity(getOperationsTotal(shiftDetails), shiftDetails.base_hours) }} оп/ч
            </span>
            <span class="summary-chip-extra">({{ getOperationsTotal(shiftDetails) }} оп)</span>
          </div>
        </div>

        <div class="modal-body">
          <!-- Отпуск / Больничный -->
          <div v-if="selectedDay?.isVacation || selectedDay?.isSick" class="vacation-sick-details">
            <div class="vacation-sick-status">
              <i :class="selectedDay.isVacation ? 'fas fa-umbrella-beach' : 'fas fa-thermometer-half'"></i>
              <span>{{ selectedDay.isVacation ? 'Отпуск' : 'Больничный' }}</span>
            </div>
            <div class="stat-line">
              <span class="stat-label">Статус:</span>
              <span class="stat-number">{{ selectedDay.isVacation ? '📅 Отдых' : '🏥 Больничный' }}</span>
            </div>
          </div>

          <!-- Обычный день -->
          <template v-else>
            <div v-if="shiftDetails" class="day-details">
              <div class="day-breakdown-header">📋 Из чего складывается:</div>

              <div v-if="shiftDetails.earned_hours" class="simple-line">
                <span class="simple-line-label">⏳ За отработанные часы</span>
                <span class="simple-line-value">
                  {{ formatNumber(shiftDetails.earned_hours) }} ₽
                  <span class="percent-badge hours-percent-badge">{{ getHoursPercent(shiftDetails.earned_hours, shiftDetails.earned) }}%</span>
                </span>
              </div>

              <div v-if="shiftDetails.earned_cold" class="simple-line">
                <span class="simple-line-label">❄️ Доплата за холод</span>
                <span class="simple-line-value">
                  {{ formatNumber(shiftDetails.earned_cold) }} ₽
                  <span class="percent-badge cold-percent-badge">{{ getColdPercent(shiftDetails.earned_cold, shiftDetails.earned) }}%</span>
                </span>
              </div>

              <div v-if="shiftDetails.earned_overtime" class="simple-line">
                <span class="simple-line-label">⏱️ Доплата за переработку</span>
                <span class="simple-line-value">
                  {{ formatNumber(shiftDetails.earned_overtime) }} ₽
                  <span class="percent-badge overtime-percent-badge">{{ getOvertimePercent(shiftDetails.earned_overtime, shiftDetails.earned) }}%</span>
                </span>
              </div>

              <div v-if="getMotivationTotal(shiftDetails) > 0" class="accordion-item">
                <div class="accordion-header" @click="toggleDaySection('motivation')">
                  <span class="accordion-icon">🏆</span>
                  <span class="accordion-title">Мотивация / доп. работы</span>
                  <span class="accordion-value">
                    {{ formatNumber(getMotivationTotal(shiftDetails)) }} ₽
                    <span class="percent-badge award-percent-badge">{{ getAwardPercent(getMotivationTotal(shiftDetails), shiftDetails.earned) }}%</span>
                  </span>
                  <i class="fas" :class="openDaySections.motivation ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                </div>
                <div v-show="openDaySections.motivation" class="accordion-body">
                  <div v-if="shiftDetails.motivation_collect" class="stat-line sub-line">
                    <span class="stat-label">— Набор:</span>
                    <span class="stat-number">{{ formatNumber(shiftDetails.motivation_collect) }} ₽ ({{ shiftDetails.count_operations_collect || 0 }} оп)</span>
                  </div>
                  <div v-if="shiftDetails.motivation_replenishment" class="stat-line sub-line">
                    <span class="stat-label">— Пополнение:</span>
                    <span class="stat-number">{{ formatNumber(shiftDetails.motivation_replenishment) }} ₽ ({{ shiftDetails.count_operations_replenishment || 0 }} оп)</span>
                  </div>
                  <div v-if="shiftDetails.motivation_placement" class="stat-line sub-line">
                    <span class="stat-label">— Размещение:</span>
                    <span class="stat-number">{{ formatNumber(shiftDetails.motivation_placement) }} ₽ ({{ shiftDetails.count_operations_placement || 0 }} оп)</span>
                  </div>
                  <div v-if="shiftDetails.earned_for_non_productive_work" class="stat-line sub-line">
                    <span class="stat-label">— Непроизводственные:</span>
                    <span class="stat-number">{{ formatNumber(shiftDetails.earned_for_non_productive_work) }} ₽ ({{ formatNumber(shiftDetails.hours_non_productive) }} ч)</span>
                  </div>
                </div>
              </div>

              <div v-if="hasShiftCurrencyData(shiftDetails)" class="accordion-item">
                <div class="accordion-header" @click="toggleDaySection('currency')">
                  <span class="accordion-icon">💱</span>
                  <span class="accordion-title">Заработано в валюте</span>
                  <span class="accordion-value"></span>
                  <i class="fas" :class="openDaySections.currency ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                </div>
                <div v-show="openDaySections.currency" class="accordion-body">
                  <div v-if="shiftDetails.valute?.dollar" class="currency-line">🇺🇸 Доллар: ${{ shiftDetails.valute.dollar }}</div>
                  <div v-if="shiftDetails.valute?.euro" class="currency-line">🇪🇺 Евро: €{{ shiftDetails.valute.euro }}</div>
                  <div v-if="shiftDetails.valute?.yena" class="currency-line">🇨🇳 Юань: ¥{{ shiftDetails.valute.yena }}</div>
                  <div v-if="shiftDetails.valute?.som" class="currency-line">🇰🇬 Сом: {{ formatNumber(shiftDetails.valute.som) }}</div>
                </div>
              </div>
            </div>

            <div class="edit-block">
              <div class="form-group">
                <label class="form-label">Количество часов</label>
                <input type="number" v-model.number="editHours" class="form-control" min="0" step="0.5" />
              </div>
              <div v-if="selectedDay?.hasShift" class="motivation-section">
                <button
                  v-if="!isFutureDay(selectedDay)"
                  class="btn-motivation"
                  @click="openMotivationModal"
                >
                  <i class="fas fa-star"></i> Добавить мотивацию / работы
                </button>
                <div v-else class="motivation-hint">
                  <i class="fas fa-lock"></i>
                  <span>Мотивацию можно добавить только после отработки смены</span>
                </div>
              </div>
            </div>
          </template>
        </div>

        <div class="modal-footer">
          <template v-if="!selectedDay?.isVacation && !selectedDay?.isSick">
            <button class="btn-primary btn-save" @click="saveShift" :disabled="isSavingShift">
              <i :class="isSavingShift ? 'fas fa-spinner fa-spin' : 'fas fa-save'"></i>
              <span>{{ isSavingShift ? 'Сохранение...' : 'Сохранить' }}</span>
            </button>
            <button v-if="selectedDay?.hasShift" class="btn-icon btn-danger" @click="deleteShift" title="Удалить">
              <i class="fas fa-trash"></i>
            </button>
            <button class="btn-icon btn-secondary" @click="closeShiftModal" title="Закрыть">
              <i class="fas fa-times"></i>
            </button>
          </template>
          <template v-else>
            <button class="btn-danger btn-save" @click="deleteVacationOrSick">
              <i class="fas fa-trash"></i>
              <span>Удалить {{ selectedDay.isVacation ? 'отпуск' : 'больничный' }}</span>
            </button>
            <button class="btn-icon btn-secondary" @click="closeShiftModal" title="Закрыть">
              <i class="fas fa-times"></i>
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- МОДАЛКА: Мотивация (bottom-sheet)                            -->
    <!-- ============================================================ -->
    <div v-if="showMotivationModal" class="modal modal-bottom-sheet" @click.self="closeMotivationModal">
      <div class="modal-content">
        <div class="sheet-handle"></div>
        <div class="modal-header">
          <h3>
            <i class="fas fa-star"></i>
            Добавить
          </h3>
          <button class="modal-close" @click="closeMotivationModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label required">Тип</label>
            <select v-model="motivationData.type_operations" class="form-control">
              <option value="placement">Размещение</option>
              <option value="collect">Набор</option>
              <option value="replenishment">Пополнение</option>
              <option value="non_productive">Непроизводственные работы</option>
            </select>
          </div>
          <div class="form-group" v-if="motivationData.type_operations !== 'non_productive'">
            <label class="form-label required">Кол-во операций</label>
            <input type="number" v-model.number="motivationData.count_operations" class="form-control" min="0" placeholder="Введите количество" />
          </div>
          <div class="form-group" v-else>
            <label class="form-label required">Кол-во часов</label>
            <input type="number" v-model.number="motivationData.hours" class="form-control" min="0" step="0.5" placeholder="Введите часы" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary btn-save" @click="saveMotivation" :disabled="isSavingMotivation || isSaveMotivationDisabled">
            <i :class="isSavingMotivation ? 'fas fa-spinner fa-spin' : 'fas fa-save'"></i>
            <span>{{ isSavingMotivation ? 'Сохранение...' : 'Сохранить' }}</span>
          </button>
          <button class="btn-icon btn-secondary" @click="closeMotivationModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- МОДАЛКА: Настройки (bottom-sheet + аккордеон)                -->
    <!-- ============================================================ -->
    <div v-if="showSettingsModal" class="modal modal-bottom-sheet" @click.self="closeSettingsModal">
      <div class="modal-content">
        <div class="sheet-handle"></div>
        <div class="modal-header">
          <h3>
            <i class="fas fa-cog"></i>
            Настройки оплаты
          </h3>
          <button class="modal-close" @click="closeSettingsModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="accordion-item">
            <div class="accordion-header" @click="toggleSettingsSection('main')">
              <span class="accordion-icon">⚙️</span>
              <span class="accordion-title">Основное</span>
              <span class="accordion-value">
                {{ formatNumber(settings.price_time) }} ₽/ч
              </span>
              <i class="fas" :class="openSettingsSections.main ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div v-show="openSettingsSections.main" class="accordion-body">
              <div class="form-group">
                <label class="form-label required">Ставка за час</label>
                <input type="number" v-model.number="settings.price_time" class="form-control" step="1" required />
              </div>
              <div class="form-group">
                <label class="form-label">Доплата за переработку</label>
                <input type="number" v-model.number="settings.price_overtime" class="form-control" step="1" />
              </div>
              <div class="form-group">
                <label class="form-label">Доплата за холод</label>
                <input type="number" v-model.number="settings.price_cold" class="form-control" step="0.1" />
              </div>
            </div>
          </div>

          <div class="accordion-item">
            <div class="accordion-header" @click="toggleSettingsSection('motivation')">
              <span class="accordion-icon">🏆</span>
              <span class="accordion-title">Мотивация (за операцию)</span>
              <span class="accordion-value"></span>
              <i class="fas" :class="openSettingsSections.motivation ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div v-show="openSettingsSections.motivation" class="accordion-body">
              <div class="form-group">
                <label class="form-label">Стоимость набора</label>
                <input type="number" v-model.number="settings.price_collect" class="form-control" step="0.1" />
              </div>
              <div class="form-group">
                <label class="form-label">Стоимость пополнения</label>
                <input type="number" v-model.number="settings.price_replenishment" class="form-control" step="0.1" />
              </div>
              <div class="form-group">
                <label class="form-label">Стоимость размещения</label>
                <input type="number" v-model.number="settings.price_placement" class="form-control" step="0.1" />
              </div>
            </div>
          </div>

          <div class="accordion-item">
            <div class="accordion-header" @click="toggleSettingsSection('other')">
              <span class="accordion-icon">🪏</span>
              <span class="accordion-title">Прочее</span>
              <span class="accordion-value"></span>
              <i class="fas" :class="openSettingsSections.other ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div v-show="openSettingsSections.other" class="accordion-body">
              <div class="form-group">
                <label class="form-label">Час непроизводственных работ.</label>
                <input type="number" v-model.number="settings.price_non_productive_work" class="form-control" step="0.1" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="hasSettings" class="btn-icon btn-danger" @click="deleteSettings" :disabled="isSavingSettings" title="Удалить настройки">
            <i class="fas fa-trash"></i>
          </button>
          <button class="btn-primary btn-save" @click="saveSettings" :disabled="isSavingSettings">
            <i :class="isSavingSettings ? 'fas fa-spinner fa-spin' : 'fas fa-save'"></i>
            <span>{{ isSavingSettings ? 'Сохранение...' : 'Сохранить' }}</span>
          </button>
          <button class="btn-icon btn-secondary" @click="closeSettingsModal" title="Закрыть">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- МОДАЛКА: Статистика за год (bottom-sheet)                    -->
    <!-- ============================================================ -->
    <div v-if="showYearStatsModal" class="modal modal-bottom-sheet" @click.self="closeYearStatsModal">
      <div class="modal-content">
        <div class="sheet-handle"></div>
        <div class="modal-header">
          <h3>
            <i class="fas fa-chart-line"></i>
            Статистика за год
          </h3>
          <button class="modal-close" @click="closeYearStatsModal">&times;</button>
        </div>

        <div class="sticky-toolbar">
          <div class="year-selector">
            <button class="btn-year-nav" @click="prevYear">
              <i class="fas fa-chevron-left"></i>
            </button>
            <select v-model="selectedYear" @change="onYearChange" class="year-select">
              <option v-for="year in availableYears" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
            <button class="btn-year-nav" @click="nextYear">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>

        <div class="modal-body">
          <div class="year-stats" v-if="yearStats">
            <div class="stat-big-card">
              <div class="stat-icon-large">
                <i class="fas fa-clock"></i>
              </div>
              <div class="stat-info-large">
                <div class="stat-label">Отработано часов</div>
                <div class="stat-value-large">{{ yearStats.total_hours || 0 }} ч</div>
              </div>
            </div>
            <div class="stat-big-card">
              <div class="stat-icon-large">
                <i class="fas fa-ruble-sign"></i>
              </div>
              <div class="stat-info-large">
                <div class="stat-label">Заработано</div>
                <div class="stat-value-large">{{ formatNumber(yearStats.total_earned) }} ₽</div>
              </div>
            </div>

            <div v-if="getYearMotivationTotal(yearStats) > 0" class="year-motivation-block">
              <div class="year-motivation-header">
                🏆 Мотивация (всего): {{ formatNumber(getYearMotivationTotal(yearStats)) }} ₽
                <span class="percent-badge">{{ getAwardPercent(getYearMotivationTotal(yearStats), yearStats.total_earned) }}%</span>
              </div>
              <div v-if="yearStats.total_earned_collect" class="stat-line sub-line">
                <span class="stat-label">— Набор:</span>
                <span class="stat-number">{{ formatNumber(yearStats.total_earned_collect) }} ₽</span>
              </div>
              <div v-if="yearStats.total_earned_replenishment" class="stat-line sub-line">
                <span class="stat-label">— Пополнение:</span>
                <span class="stat-number">{{ formatNumber(yearStats.total_earned_replenishment) }} ₽</span>
              </div>
              <div v-if="yearStats.total_earned_placement" class="stat-line sub-line">
                <span class="stat-label">— Размещение:</span>
                <span class="stat-number">{{ formatNumber(yearStats.total_earned_placement) }} ₽</span>
              </div>
            </div>

            <div class="accordion-item stats-analytics-accordion" v-if="yearStats.dollar || yearStats.euro || yearStats.yena || yearStats.som">
              <div class="accordion-header" @click="toggleYearCurrency">
                <span class="accordion-icon">💱</span>
                <span class="accordion-title">Заработано в валюте</span>
                <i class="fas" :class="showYearCurrency ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
              </div>
              <div v-show="showYearCurrency" class="accordion-body">
                <div v-if="yearStats.dollar" class="currency-line">🇺🇸 Доллар: ${{ formatNumber(yearStats.dollar) }}</div>
                <div v-if="yearStats.euro" class="currency-line">🇪🇺 Евро: €{{ formatNumber(yearStats.euro) }}</div>
                <div v-if="yearStats.yena" class="currency-line">🇨🇳 Юань: ¥{{ formatNumber(yearStats.yena) }}</div>
                <div v-if="yearStats.som" class="currency-line">🇰🇬 Сом: {{ formatNumber(yearStats.som) }}</div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <i class="fas fa-chart-line"></i>
            <p>Нет данных за {{ selectedYear }} год</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary btn-save" @click="closeYearStatsModal">
            <i class="fas fa-times"></i>
            <span>Закрыть</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- МОДАЛКА: Отпуск / Больничный (bottom-sheet)                  -->
    <!-- ============================================================ -->
    <div v-if="showVacationModal" class="modal modal-bottom-sheet" @click.self="closeVacationModal">
      <div class="modal-content">
        <div class="sheet-handle"></div>
        <div class="modal-header">
          <h3>
            <i class="fas fa-umbrella-beach"></i>
            Отпуск / Больничный
          </h3>
          <button class="modal-close" @click="closeVacationModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label required">Тип</label>
            <select v-model="vacationData.type_days" class="form-control">
              <option value="Отпуск">Отпуск</option>
              <option value="Больничный">Больничный</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label required">Дата начала</label>
            <input type="date" v-model="vacationData.start_date" class="form-control" required />
          </div>
          <div class="form-group">
            <label class="form-label required">Количество дней</label>
            <input type="number" v-model.number="vacationData.number_of_days" class="form-control" min="1" required />
          </div>
          <div class="vacation-preview" v-if="vacationData.start_date && vacationData.number_of_days > 0">
            <p>Будет добавлено <strong>{{ vacationData.number_of_days }}</strong> дней с <strong>{{ formatDateForDisplay(vacationData.start_date) }}</strong></p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary btn-save" @click="saveVacation" :disabled="isSavingVacation || !vacationData.start_date || !vacationData.number_of_days">
            <i :class="isSavingVacation ? 'fas fa-spinner fa-spin' : 'fas fa-save'"></i>
            <span>{{ isSavingVacation ? 'Сохранение...' : 'Сохранить' }}</span>
          </button>
          <button class="btn-icon btn-secondary" @click="closeVacationModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="loading-container">
    <div v-if="hasLoadError" class="error-state">
      <i class="fas fa-exclamation-triangle text-danger"></i>
      <p>Не удалось загрузить данные. Проверьте интернет.</p>
      <button class="btn btn-primary mt-3" @click="loadData">
        <i class="fas fa-redo"></i> Повторить попытку
      </button>
    </div>
    <div v-else>
      <i class="fas fa-spinner fa-spin"></i>
      <p>Загрузка данных...</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'TimesheetsView',
  setup() {
    const currentDate = ref(new Date())
    const shifts = ref([])
    const monthlyStats = ref(null)
    const yearStats = ref(null)
    const yearStatsYear = ref(null)
    const settings = ref({
      price_time: 0,
      price_overtime: 0,
      price_cold: 0,
      price_collect: 0,
      price_replenishment: 0,
      price_placement: 0,
      price_non_productive_work: 0
    })
    const hasSettings = ref(false)

    const isLoading = ref(true)
    const hasLoadError = ref(false)
    const isSavingShift = ref(false)
    const isSavingMotivation = ref(false)
    const isSavingSettings = ref(false)
    const isSavingVacation = ref(false)
    const isSavingMany = ref(false)

    const showShiftModal = ref(false)
    const showSettingsModal = ref(false)
    const showAddManyModal = ref(false)
    const showYearStatsModal = ref(false)
    const showVacationModal = ref(false)
    const showMotivationModal = ref(false)

    // Состояния для модалки статистики
    const showStatsModal = ref(false)
    const selectedStatsType = ref('total') // 'period1', 'period2', 'total'
    const showStatsCurrency = ref(false)
    const openStatsAnalytics = ref(false)

    const motivationData = ref({
      type_operations: 'placement',
      count_operations: null,
      hours: null
    })

    const selectedDay = ref(null)
    const shiftDetails = ref(null)
    const editHours = ref(0)
    const showShiftCurrency = ref(false)
    const showYearCurrency = ref(false)

    const vacationData = ref({
      start_date: '',
      number_of_days: 14,
      type_days: 'Отпуск'
    })

    const openDaySections = ref({
      motivation: false,
      currency: false
    })
    const openSettingsSections = ref({
      main: true,
      motivation: false,
      other: false
    })

    const selectionDate = ref(new Date())
    const manyShiftsData = ref({
      hours: 12,
      selectedDates: []
    })
    const selectedYear = ref(new Date().getFullYear())
    const availableYears = ref([])

    const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    // --- ЦЕЛИ ПО МОТИВАЦИИ ---
    const currentGoal = ref(null)
    const showGoalModal = ref(false)
    const isSavingGoal = ref(false)
    const goalData = ref({ amount: null })

    const getTodayStr = () => {
      const now = new Date()
      const y = now.getFullYear()
      const m = String(now.getMonth() + 1).padStart(2, '0')
      const d = String(now.getDate()).padStart(2, '0')
      return `${y}-${m}-${d}`
    }

    const isFutureDay = (day) => {
      if (!day?.dateStr) return false
      return day.dateStr > getTodayStr()
    }

    const goalCurrentAmount = computed(() => {
      if (!currentGoal.value || !monthlyStats.value?.total) return 0
      return getMotivationTotal(monthlyStats.value.total)
    })

    const goalProgressPercent = computed(() => {
      if (!currentGoal.value || !currentGoal.value.amount) return 0
      return (goalCurrentAmount.value / currentGoal.value.amount) * 100
    })

    const isGoalAchieved = computed(() => goalProgressPercent.value >= 100)

    const goalProgressClass = computed(() => {
      if (isGoalAchieved.value) return 'goal-success'
      if (goalProgressPercent.value > 75) return 'goal-warning'
      return 'goal-normal'
    })

    // Исправленный прогноз
    const goalForecastInfo = computed(() => {
      if (!currentGoal.value || !currentGoal.value.amount) return null

      // 1. Если цель достигнута — прогноз не нужен
      if (isGoalAchieved.value) {
        return null
      }

      const todayStr = getTodayStr()

      // Определяем, закончился ли месяц, который мы смотрим
      const year = currentDate.value.getFullYear()
      const month = currentDate.value.getMonth()
      const lastDayOfMonth = new Date(year, month + 1, 0).getDate()
      const monthEndStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(lastDayOfMonth).padStart(2, '0')}`
      const isMonthEnded = todayStr > monthEndStr

      // 2. Если месяц закончился, а цель не достигнута
      if (isMonthEnded) {
        const diff = currentGoal.value.amount - goalCurrentAmount.value
        return {
          text: `Месяц завершен. Не хватило ${formatNumber(diff)} ₽ до цели`,
          status: 'danger',
          icon: 'fa-flag-checkered'
        }
      }

      // 3. Если месяц еще идет — считаем прогноз
      const workedShifts = shifts.value.filter(s => {
        if (!s.date) return false
        const shiftDate = s.date.split(' ')[0]
        if (shiftDate > todayStr) return false
        if (s.earned === -1 || s.earned === -2) return false // отпуск/больничный
        return true
      })

      const futureShifts = shifts.value.filter(s => {
        if (!s.date) return false
        const shiftDate = s.date.split(' ')[0]
        return shiftDate > todayStr
      })

      if (workedShifts.length === 0) {
        return {
          text: 'Нет отработанных смен для прогноза',
          status: 'neutral',
          icon: 'fa-info-circle'
        }
      }

      if (futureShifts.length === 0) {
        return {
          text: 'Проставьте смены на будущее для прогноза',
          status: 'neutral',
          icon: 'fa-calendar-plus'
        }
      }

      // Средняя мотивация за одну прошедшую смену
      const avgPerShift = goalCurrentAmount.value / workedShifts.length
      const forecast = goalCurrentAmount.value + (avgPerShift * futureShifts.length)

      if (forecast >= currentGoal.value.amount) {
        return {
          text: `🔥 Отличный темп! Прогноз: ${formatNumber(forecast)} ₽`,
          status: 'success',
          icon: 'fa-chart-line'
        }
      } else {
        const diff = currentGoal.value.amount - forecast
        return {
          text: `⚠️ Прогноз: ${formatNumber(forecast)} ₽ (не хватает ${formatNumber(diff)} ₽)`,
          status: 'warning',
          icon: 'fa-exclamation-triangle'
        }
      }
    })

    // --- МОДАЛКА СТАТИСТИКИ ---
    const openStatsModal = (type) => {
      selectedStatsType.value = type
      showStatsCurrency.value = false
      openStatsAnalytics.value = false // Сбрасываем аккордеон при открытии
      showStatsModal.value = true
    }

    const closeStatsModal = () => {
      showStatsModal.value = false
    }

    const statsModalData = computed(() => {
      if (!monthlyStats.value) return null
      if (selectedStatsType.value === 'period1') return monthlyStats.value.period_one
      if (selectedStatsType.value === 'period2') return monthlyStats.value.period_two
      return monthlyStats.value.total
    })

    const statsModalTitle = computed(() => {
      if (selectedStatsType.value === 'period1') return 'Период 1 (1-15)'
      if (selectedStatsType.value === 'period2') return 'Период 2 (16-31)'
      return 'Итого за месяц'
    })

    // Проверяем, есть ли хоть какие-то данные для отображения аналитики
    const hasAnalyticsContent = computed(() => {
      const data = statsModalData.value
      if (!data) return false

      const ops = getOperationsTotal(data)
      if (ops > 0) return true
      if (ops > 0 && data.total_base_hours > 0) return true

      if (selectedStatsType.value === 'total') {
        if (data.total_earned_hours) return true
        if (data.total_earned_cold) return true
        if (getMotivationTotal(data) > 0) return true
        if (data.total_earned_for_non_production) return true
        if (data.total_overtime) return true
        if (periodOneProductivity.value !== null && periodTwoProductivity.value !== null) return true
        if (monthBestDay.value) return true
      } else if (selectedStatsType.value === 'period1') {
        if (periodOneBestDay.value) return true
      } else if (selectedStatsType.value === 'period2') {
        if (periodTwoBestDay.value) return true
      }

      return false
    })
    // ---------------------------

    const getMotivationTotal = (obj) => {
      if (!obj) return 0
      return (obj.motivation_collect ?? obj.total_earned_collect ?? 0) +
             (obj.motivation_replenishment ?? obj.total_earned_replenishment ?? 0) +
             (obj.motivation_placement ?? obj.total_earned_placement ?? 0) +
             (obj.earned_for_non_productive_work ?? obj.total_earned_for_non_production ?? 0)
    }
    const getOperationsTotal = (obj) => {
      if (!obj) return 0
      return (obj.count_operations_collect ?? obj.total_operations_collect ?? 0) +
             (obj.count_operations_replenishment ?? obj.total_operations_replenishment ?? 0) +
             (obj.count_operations_placement ?? obj.total_operations_placement ?? 0)
    }
    const getYearMotivationTotal = (yearObj) => {
      if (!yearObj) return 0
      return (yearObj.total_earned_collect || 0) +
             (yearObj.total_earned_replenishment || 0) +
             (yearObj.total_earned_placement || 0)
    }
    const hasShiftCurrencyData = (shift) => {
      if (!shift?.valute) return false
      const v = shift.valute
      return !!(v.dollar || v.euro || v.yena || v.som)
    }

    const toggleDaySection = (section) => {
      openDaySections.value[section] = !openDaySections.value[section]
    }
    const toggleSettingsSection = (section) => {
      openSettingsSections.value[section] = !openSettingsSections.value[section]
    }

    const getPeriodNumber = (dateStr) => {
      if (!dateStr) return 1
      const day = parseInt(dateStr.split('-')[2])
      return isNaN(day) ? 1 : (day <= 15 ? 1 : 2)
    }

    const periodOneProductivity = computed(() => {
      const ops = getOperationsTotal(monthlyStats.value?.period_one)
      const hours = monthlyStats.value?.period_one?.total_base_hours
      if (!ops || !hours) return null
      return ops / hours
    })

    const periodTwoProductivity = computed(() => {
      const ops = getOperationsTotal(monthlyStats.value?.period_two)
      const hours = monthlyStats.value?.period_two?.total_base_hours
      if (!ops || !hours) return null
      return ops / hours
    })

    const productivityChangePercent = computed(() => {
      if (periodOneProductivity.value === null || periodTwoProductivity.value === null) return 0
      return ((periodTwoProductivity.value - periodOneProductivity.value) / periodOneProductivity.value) * 100
    })

    const productivityChangeSymbol = computed(() => {
      if (productivityChangePercent.value > 0) return '📈 +'
      if (productivityChangePercent.value < 0) return '📉 '
      return '➡️ '
    })

    const productivityChangeClass = computed(() => {
      if (productivityChangePercent.value > 0) return 'positive'
      if (productivityChangePercent.value < 0) return 'negative'
      return 'neutral'
    })

    const computeBestDay = (periodFilter) => {
      if (!shifts.value || !Array.isArray(shifts.value) || shifts.value.length === 0) return null
      const daysWithOps = shifts.value.filter(day => {
        if (!day || !day.date) return false
        const ops = getOperationsTotal(day)
        if (!ops || ops <= 0) return false
        if (!(day.base_hours > 0)) return false
        if (!(day.earned > 0)) return false
        if (periodFilter !== null && getPeriodNumber(day.date) !== periodFilter) return false
        return true
      })
      if (daysWithOps.length === 0) return null
      const best = daysWithOps.reduce((best, current) => {
        const currentProd = getOperationsTotal(current) / current.base_hours
        const bestProd = getOperationsTotal(best) / best.base_hours
        return currentProd > bestProd ? current : best
      }, daysWithOps[0])
      if (!best) return null
      const date = new Date(best.date)
      return {
        ...best,
        dateStr: date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' }),
        dayOfWeek: date.toLocaleDateString('ru-RU', { weekday: 'long' }),
        count_operations: getOperationsTotal(best),
        productivity: getOperationsTotal(best) / best.base_hours
      }
    }

    const periodOneBestDay = computed(() => computeBestDay(1))
    const periodTwoBestDay = computed(() => computeBestDay(2))
    const monthBestDay = computed(() => computeBestDay(null))

    const isWeekendDay = (date) => {
      const dayOfWeek = date.getDay()
      return dayOfWeek === 0 || dayOfWeek === 6
    }

    const getWeeksInMonth = (year, month) => {
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      const firstDayOfWeek = firstDay.getDay() === 0 ? 7 : firstDay.getDay()
      const lastDate = lastDay.getDate()
      const totalDays = firstDayOfWeek - 1 + lastDate
      return Math.ceil(totalDays / 7)
    }

    const hasPeriodData = (period) => {
      if (!period) return false
      return period.total_earned > 0 ||
             period.total_base_hours > 0 ||
             period.total_earned_hours > 0 ||
             getMotivationTotal(period) > 0
    }

    const hasCurrencyData = (period) => {
      if (!period) return false
      return !!(period.dollar || period.euro || period.yena || period.som)
    }

    const showNotification = (message, type = 'success') => {
      const notification = document.createElement('div')
      notification.className = `notification notification-${type}`
      const content = document.createElement('div')
      content.className = 'notification-content'
      const icon = document.createElement('i')
      icon.className = `fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}`
      const textSpan = document.createElement('span')
      textSpan.textContent = message
      content.appendChild(icon)
      content.appendChild(textSpan)
      notification.appendChild(content)
      notification.style.cssText = `position: fixed; top: 20px; right: 20px; z-index: 10000; animation: slideIn 0.3s ease; cursor: pointer;`
      document.body.appendChild(notification)
      setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease'
        setTimeout(() => {
          if (document.body.contains(notification)) document.body.removeChild(notification)
        }, 300)
      }, 4000)
      notification.onclick = () => {
        notification.style.animation = 'slideOut 0.3s ease'
        setTimeout(() => {
          if (document.body.contains(notification)) document.body.removeChild(notification)
        }, 300)
      }
    }

    const handleApiError = (error, defaultMessage = 'Произошла ошибка') => {
      console.error('API Error:', error)
      if (!error.response) {
        if (error.code === 'ECONNABORTED') {
          showNotification('Превышено время ожидания ответа от сервера', 'error')
        } else {
          showNotification('Ошибка сети. Проверьте подключение к интернету', 'error')
        }
        return
      }
      if (error.response.status === 401 || error.response.status === 403) {
        showNotification('Сессия истекла или нет доступа. Пожалуйста, обновите страницу.', 'error')
        return
      }
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        if (Array.isArray(detail)) {
          const errors = detail.map(err => {
            const field = err.loc?.filter(l => l !== 'body').join('.') || 'поле'
            const cleanMsg = err.msg.replace(/^Value error,\s*/, '')
            return `${field}: ${cleanMsg}`
          })
          showNotification(`Ошибка валидации:\n${errors.join('\n')}`, 'error')
        } else if (typeof detail === 'string') {
          showNotification(detail, 'error')
        } else if (detail.message) {
          showNotification(detail.message, 'error')
        } else {
          showNotification(defaultMessage, 'error')
        }
      } else if (error.message) {
        showNotification(error.message, 'error')
      } else {
        showNotification(defaultMessage, 'error')
      }
    }

    // --- ЗАГРУЗКА ДАННЫХ ---

    const loadShifts = async () => {
      try {
        const month = currentDate.value.getMonth() + 1
        const year = currentDate.value.getFullYear()
        const response = await apiService.getShiftsByMonth(month, year)
        shifts.value = response.result || []
      } catch (error) {
        handleApiError(error, 'Ошибка при загрузке смен')
        shifts.value = []
      }
    }

    const loadStatistics = async () => {
      try {
        const month = currentDate.value.getMonth() + 1
        const year = currentDate.value.getFullYear()
        const response = await apiService.getMonthlyStatistics(month, year)
        monthlyStats.value = response
      } catch (error) {
        handleApiError(error, 'Ошибка при загрузке статистики')
        monthlyStats.value = null
      }
    }

    const loadSettings = async () => {
      try {
        const response = await apiService.getTimesheetSettings()
        settings.value = {
          price_time: response.price_time || 0,
          price_overtime: response.price_overtime || 0,
          price_cold: response.price_cold || 0,
          price_collect: response.price_collect || 0,
          price_replenishment: response.price_replenishment || 0,
          price_placement: response.price_placement || 0,
          price_non_productive_work: response.price_non_productive_work || 0
        }
        hasSettings.value = true
      } catch (error) {
        if (error.response?.status === 404) {
          hasSettings.value = false
        } else {
          handleApiError(error, 'Не удалось загрузить настройки')
          hasSettings.value = false
        }
      }
    }

    const loadGoal = async () => {
      try {
        const monthStr = `${currentDate.value.getFullYear()}-${String(currentDate.value.getMonth() + 1).padStart(2, '0')}-01`
        const goal = await apiService.getGoalCurrent(monthStr)
        currentGoal.value = goal
      } catch (error) {
        if (error.response?.status !== 404) {
          console.error('Ошибка загрузки цели:', error)
        }
        currentGoal.value = null
      }
    }

    // -----------------------

    const calendarRows = computed(() => {
      const year = currentDate.value.getFullYear()
      const month = currentDate.value.getMonth()
      return getWeeksInMonth(year, month)
    })

    const calendarDays = computed(() => {
      const year = currentDate.value.getFullYear()
      const month = currentDate.value.getMonth()
      const weeksCount = calendarRows.value
      const totalCells = weeksCount * 7
      const firstDayOfMonth = new Date(year, month, 1)
      let startingDayOfWeek = firstDayOfMonth.getDay()
      startingDayOfWeek = startingDayOfWeek === 0 ? 7 : startingDayOfWeek
      const daysInMonth = new Date(year, month + 1, 0).getDate()
      const days = []
      const daysInPrevMonth = new Date(year, month, 0).getDate()
      for (let i = startingDayOfWeek - 1; i > 0; i--) {
        const date = daysInPrevMonth - i + 1
        const fullDate = new Date(year, month - 1, date)
        days.push({
          dayNumber: date, fullDate, isCurrentMonth: false,
          isWeekend: isWeekendDay(fullDate), isToday: false,
          hasShift: false, isVacation: false, isSick: false
        })
      }
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      for (let i = 1; i <= daysInMonth; i++) {
        const fullDate = new Date(year, month, i)
        const yearStr = fullDate.getFullYear()
        const monthStr = String(fullDate.getMonth() + 1).padStart(2, '0')
        const dayStr = String(fullDate.getDate()).padStart(2, '0')
        const dateStr = `${yearStr}-${monthStr}-${dayStr}`
        const shift = shifts.value.find(s => {
          const shiftDate = s.date ? s.date.split(' ')[0] : ''
          return shiftDate === dateStr
        })
        const isVacation = shift && shift.earned === -1
        const isSick = shift && shift.earned === -2
        const hasShift = !!shift && shift.earned > 0
        days.push({
          dayNumber: i, fullDate, isCurrentMonth: true,
          isWeekend: isWeekendDay(fullDate),
          isToday: fullDate.toDateString() === today.toDateString(),
          hasShift, isVacation, isSick, dateStr,
          day_id: shift?.day_id, earned: shift?.earned || 0,
          base_hours: shift?.base_hours || 0,
          count_operations: getOperationsTotal(shift)
        })
      }
      const remainingCells = totalCells - days.length
      for (let i = 1; i <= remainingCells; i++) {
        const fullDate = new Date(year, month + 1, i)
        days.push({
          dayNumber: i, fullDate, isCurrentMonth: false,
          isWeekend: isWeekendDay(fullDate), isToday: false,
          hasShift: false, isVacation: false, isSick: false
        })
      }
      return days
    })

    const selectionCalendarRows = computed(() => {
      const year = selectionDate.value.getFullYear()
      const month = selectionDate.value.getMonth()
      return getWeeksInMonth(year, month)
    })

    const selectionDates = computed(() => {
      const year = selectionDate.value.getFullYear()
      const month = selectionDate.value.getMonth()
      const weeksCount = selectionCalendarRows.value
      const totalCells = weeksCount * 7
      const firstDayOfMonth = new Date(year, month, 1)
      let startingDayOfWeek = firstDayOfMonth.getDay()
      startingDayOfWeek = startingDayOfWeek === 0 ? 7 : startingDayOfWeek
      const daysInMonth = new Date(year, month + 1, 0).getDate()
      const daysInPrevMonth = new Date(year, month, 0).getDate()
      const dates = []
      const currentShifts = shifts.value
      const makeSelectionDate = (dayNum, fullDateObj, isCurrentMonthFlag) => {
        const y = fullDateObj.getFullYear()
        const m = String(fullDateObj.getMonth() + 1).padStart(2, '0')
        const d = String(fullDateObj.getDate()).padStart(2, '0')
        const ds = `${y}-${m}-${d}`
        const shift = currentShifts.find(s => (s.date ? s.date.split(' ')[0] : '') === ds)
        return {
          dayNumber: dayNum, fullDate: ds,
          hasShift: !!(shift && shift.earned > 0),
          isVacation: !!(shift && shift.earned === -1),
          isSick: !!(shift && shift.earned === -2),
          isCurrentMonth: isCurrentMonthFlag
        }
      }
      for (let i = startingDayOfWeek - 1; i > 0; i--) {
        const date = daysInPrevMonth - i + 1
        dates.push(makeSelectionDate(date, new Date(year, month - 1, date), false))
      }
      for (let i = 1; i <= daysInMonth; i++) {
        dates.push(makeSelectionDate(i, new Date(year, month, i), true))
      }
      const remainingCells = totalCells - dates.length
      for (let i = 1; i <= remainingCells; i++) {
        dates.push(makeSelectionDate(i, new Date(year, month + 1, i), false))
      }
      return dates
    })

    const selectionMonthName = computed(() => selectionDate.value.toLocaleString('ru', { month: 'long' }))
    const selectionYear = computed(() => selectionDate.value.getFullYear())
    const currentMonthName = computed(() => currentDate.value.toLocaleString('ru', { month: 'long' }))
    const currentYear = computed(() => currentDate.value.getFullYear())

    const previousMonth = () => {
      currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
      loadData()
    }
    const nextMonth = () => {
      currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
      loadData()
    }
    const goToToday = () => {
      currentDate.value = new Date()
      loadData()
    }
    const prevSelectionMonth = () => {
      selectionDate.value = new Date(selectionDate.value.getFullYear(), selectionDate.value.getMonth() - 1, 1)
      manyShiftsData.value.selectedDates = []
    }
    const nextSelectionMonth = () => {
      selectionDate.value = new Date(selectionDate.value.getFullYear(), selectionDate.value.getMonth() + 1, 1)
      manyShiftsData.value.selectedDates = []
    }
    const toggleCurrency = (section) => { openCurrency.value[section] = !openCurrency.value[section] }
    const toggleShiftCurrency = () => { showShiftCurrency.value = !showShiftCurrency.value }
    const toggleYearCurrency = () => { showYearCurrency.value = !showYearCurrency.value }

    const isDateSelected = (date) => manyShiftsData.value.selectedDates.includes(date)
    const toggleDateSelection = (date) => {
      const index = manyShiftsData.value.selectedDates.indexOf(date)
      if (index === -1) {
        manyShiftsData.value.selectedDates.push(date)
      } else {
        manyShiftsData.value.selectedDates.splice(index, 1)
      }
    }
    const selectAllDatesInMonth = () => {
      manyShiftsData.value.selectedDates = selectionDates.value
        .filter(d => d.isCurrentMonth && !d.hasShift && !d.isVacation && !d.isSick)
        .map(d => d.fullDate)
    }
    const clearAllDates = () => { manyShiftsData.value.selectedDates = [] }

    const openShiftModal = async (day) => {
      if (!day.isCurrentMonth) return
      selectedDay.value = day
      editHours.value = day.base_hours || 0
      showShiftCurrency.value = false
      openDaySections.value = { motivation: false, currency: false }

      if ((day.hasShift || day.isVacation || day.isSick) && day.day_id) {
        try {
          shiftDetails.value = await apiService.getShiftById(day.day_id)
          editHours.value = shiftDetails.value.base_hours
        } catch (error) {
          console.error('Error loading shift details:', error)
          shiftDetails.value = null
        }
      } else {
        shiftDetails.value = null
      }
      showShiftModal.value = true
    }

    const closeShiftModal = () => {
      showShiftModal.value = false
      selectedDay.value = null
      shiftDetails.value = null
      editHours.value = 0
    }

    const saveShift = async () => {
      if (!selectedDay.value || !editHours.value) {
        showNotification('Введите количество часов', 'error')
        return
      }
      const fullDate = selectedDay.value.fullDate
      const year = fullDate.getFullYear()
      const month = String(fullDate.getMonth() + 1).padStart(2, '0')
      const day = String(fullDate.getDate()).padStart(2, '0')
      const dateStr = `${year}-${month}-${day}`
      isSavingShift.value = true
      try {
        if (selectedDay.value.hasShift) {
          await apiService.updateShift(dateStr, editHours.value)
          showNotification('Смена успешно обновлена', 'success')
        } else {
          await apiService.createShift(dateStr, editHours.value)
          showNotification('Смена успешно создана', 'success')
        }
        closeShiftModal()
        await loadData()
      } catch (error) {
        handleApiError(error, 'Ошибка при сохранении смены')
      } finally {
        isSavingShift.value = false
      }
    }

    const deleteShift = async () => {
      if (!selectedDay.value?.day_id) return
      if (confirm('Вы уверены, что хотите удалить эту смену?')) {
        try {
          await apiService.deleteShift(selectedDay.value.day_id)
          showNotification('Смена успешно удалена', 'success')
          closeShiftModal()
          await loadData()
        } catch (error) {
          handleApiError(error, 'Ошибка при удалении смены')
        }
      }
    }

    const deleteVacationOrSick = async () => {
      if (!selectedDay.value?.day_id) return
      if (confirm(`Вы уверены, что хотите удалить ${selectedDay.value.isVacation ? 'отпуск' : 'больничный'} за этот день?`)) {
        try {
          await apiService.deleteShift(selectedDay.value.day_id)
          showNotification(`${selectedDay.value.isVacation ? 'Отпуск' : 'Больничный'} успешно удален`, 'success')
          closeShiftModal()
          await loadData()
        } catch (error) {
          handleApiError(error, 'Ошибка при удалении')
        }
      }
    }

    const isSaveMotivationDisabled = computed(() => {
      if (motivationData.value.type_operations === 'non_productive') {
        return !motivationData.value.hours
      }
      return !motivationData.value.count_operations
    })

    const openMotivationModal = () => {
      if (isFutureDay(selectedDay.value)) {
        showNotification('Мотивацию можно добавить только после отработки смены', 'error')
        return
      }
      motivationData.value = { type_operations: 'placement', count_operations: null, hours: null }
      showMotivationModal.value = true
    }
    const closeMotivationModal = () => { showMotivationModal.value = false }

    const saveMotivation = async () => {
      if (isSaveMotivationDisabled.value) return

      if (isFutureDay(selectedDay.value)) {
        showNotification('Нельзя добавить мотивацию на будущую смену', 'error')
        closeMotivationModal()
        return
      }

      isSavingMotivation.value = true
      try {
        if (motivationData.value.type_operations === 'non_productive') {
          await apiService.addNonProductiveWork(selectedDay.value.day_id, motivationData.value.hours)
          showNotification('Непроизводственные работы добавлены', 'success')
        } else {
          await apiService.addAward(
            selectedDay.value.day_id,
            motivationData.value.count_operations,
            motivationData.value.type_operations
          )
          showNotification('Мотивация успешно добавлена', 'success')
        }
        const updatedShift = await apiService.getShiftById(selectedDay.value.day_id)
        shiftDetails.value = updatedShift
        await loadData()
        closeMotivationModal()
      } catch (error) {
        handleApiError(error, 'Ошибка при добавлении')
      } finally {
        isSavingMotivation.value = false
      }
    }

    const openSettingsModal = () => {
      openSettingsSections.value = { main: true, motivation: false, other: false }
      showSettingsModal.value = true
    }
    const closeSettingsModal = () => { showSettingsModal.value = false }

    const saveSettings = async () => {
      if (!settings.value.price_time) {
        showNotification('Цена за час обязательна для заполнения', 'error')
        return
      }
      isSavingSettings.value = true
      try {
        await apiService.updateTimesheetSettings(settings.value)
        showNotification('Настройки сохранены', 'success')
        closeSettingsModal()
        await loadData()
      } catch (error) {
        handleApiError(error, 'Ошибка при сохранении настроек')
      } finally {
        isSavingSettings.value = false
      }
    }

    const deleteSettings = async () => {
      if (confirm('Вы уверены, что хотите удалить настройки?')) {
        try {
          await apiService.deleteTimesheetSettings()
          settings.value = {
            price_time: 0, price_overtime: 0, price_cold: 0,
            price_collect: 0, price_replenishment: 0,
            price_placement: 0, price_non_productive_work: 0
          }
          hasSettings.value = false
          showNotification('Настройки удалены', 'success')
          closeSettingsModal()
        } catch (error) {
          handleApiError(error, 'Ошибка при удалении настроек')
        }
      }
    }

    const openAddManyModal = () => {
      manyShiftsData.value.selectedDates = []
      selectionDate.value = new Date(currentDate.value)
      showAddManyModal.value = true
    }
    const closeAddManyModal = () => { showAddManyModal.value = false }

    const saveManyShifts = async () => {
      if (!manyShiftsData.value.hours) {
        showNotification('Введите количество часов', 'error')
        return
      }
      if (manyShiftsData.value.selectedDates.length === 0) {
        showNotification('Выберите хотя бы одну дату', 'error')
        return
      }
      isSavingMany.value = true
      try {
        await apiService.addManyShifts(manyShiftsData.value.hours, manyShiftsData.value.selectedDates)
        showNotification('Смены успешно добавлены', 'success')
        closeAddManyModal()
        await loadData()
      } catch (error) {
        handleApiError(error, 'Ошибка при добавлении смен')
      } finally {
        isSavingMany.value = false
      }
    }

    const openVacationModal = () => {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      vacationData.value.start_date = `${year}-${month}-${day}`
      vacationData.value.number_of_days = 14
      vacationData.value.type_days = 'Отпуск'
      showVacationModal.value = true
    }
    const closeVacationModal = () => { showVacationModal.value = false }

    const saveVacation = async () => {
      if (!vacationData.value.start_date || !vacationData.value.number_of_days) {
        showNotification('Заполните все поля', 'error')
        return
      }
      isSavingVacation.value = true
      try {
        await apiService.addVacation({
          start_date: vacationData.value.start_date,
          number_of_days: vacationData.value.number_of_days,
          type_days: vacationData.value.type_days
        })
        showNotification(`${vacationData.value.type_days} успешно добавлен`, 'success')
        closeVacationModal()
        await loadData()
      } catch (error) {
        handleApiError(error, 'Ошибка при добавлении')
      } finally {
        isSavingVacation.value = false
      }
    }

    const closeYearStatsModal = () => {
      showYearStatsModal.value = false
      yearStats.value = null
    }

    const loadData = async () => {
      isLoading.value = true
      hasLoadError.value = false
      try {
        await Promise.all([
          loadShifts(),
          loadStatistics(),
          loadSettings(),
          loadGoal()
        ])
        if (!monthlyStats.value) hasLoadError.value = true
      } catch (e) {
        hasLoadError.value = true
      } finally {
        isLoading.value = false
      }
    }

    // --- ОПЕРАЦИИ С ЦЕЛЬЮ ---
    const openGoalModal = () => {
      goalData.value.amount = currentGoal.value ? currentGoal.value.amount : null
      showGoalModal.value = true
    }

    const closeGoalModal = () => {
      showGoalModal.value = false
    }

    const getMonthStr = () => `${currentDate.value.getFullYear()}-${String(currentDate.value.getMonth() + 1).padStart(2, '0')}-01`

    const saveGoal = async () => {
      if (!goalData.value.amount || goalData.value.amount <= 0) return
      isSavingGoal.value = true
      try {
        const payload = {
          goal_type: 'motivation',
          amount: goalData.value.amount,
          category: null
        }
        const response = await apiService.saveGoalCurrent(payload, getMonthStr())
        currentGoal.value = response
        showNotification('Цель сохранена', 'success')
        closeGoalModal()
      } catch (error) {
        handleApiError(error, 'Ошибка при сохранении цели')
      } finally {
        isSavingGoal.value = false
      }
    }

    const deleteGoal = async () => {
      if (!confirm('Удалить цель на этот месяц?')) return
      try {
        await apiService.deleteGoalCurrent('motivation', getMonthStr())
        currentGoal.value = null
        showNotification('Цель удалена', 'success')
        closeGoalModal()
      } catch (error) {
        handleApiError(error, 'Ошибка при удалении цели')
      }
    }

    // -------------------------

    const formatNumber = (num) => {
      if (!num && num !== 0) return '0'
      return num.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
    const formatNumberShort = (num) => {
      if (!num && num !== 0) return '0'
      if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
      return num.toLocaleString('ru-RU')
    }
    const formatDateShort = (date) => {
      if (!date) return ''
      const d = date instanceof Date ? date : new Date(date)
      return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
    }
    const formatDateForDisplay = (dateStr) => {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
    }
    const getProductivity = (operations, hours) => {
      if (!operations || !hours || hours === 0) return '0'
      return (operations / hours).toFixed(2)
    }
    const getColdPercent = (coldEarned, totalEarned) => {
      if (!coldEarned || !totalEarned || totalEarned === 0) return '0'
      return ((coldEarned / totalEarned) * 100).toFixed(1)
    }
    const getHoursPercent = (hoursEarned, totalEarned) => {
      if (!hoursEarned || !totalEarned || totalEarned === 0) return '0'
      return ((hoursEarned / totalEarned) * 100).toFixed(1)
    }
    const getNonProductivePercent = (nonProductiveEarned, totalEarned) => {
      if (!nonProductiveEarned || !totalEarned || totalEarned === 0) return '0'
      return ((nonProductiveEarned / totalEarned) * 100).toFixed(1)
    }
    const getAwardPercent = (award, totalEarned) => {
      if (!award || !totalEarned || totalEarned === 0) return '0'
      return ((award / totalEarned) * 100).toFixed(1)
    }
    const getOvertimePercent = (overtimeEarned, totalEarned) => {
      if (!overtimeEarned || !totalEarned || totalEarned === 0) return '0'
      return ((overtimeEarned / totalEarned) * 100).toFixed(1)
    }

    const generateAvailableYears = () => {
      const currentYear = new Date().getFullYear()
      const years = []
      for (let i = currentYear - 10; i <= currentYear + 2; i++) years.push(i)
      availableYears.value = years
    }

    const loadYearStatisticsForYear = async (year) => {
      try {
        const response = await apiService.getYearlyStatistics(year)
        yearStats.value = response
      } catch (error) {
        console.error('Error loading year statistics:', error)
        yearStats.value = null
        if (error.response?.status === 404) return
        handleApiError(error, 'Ошибка при загрузке годовой статистики')
      }
    }

    const openYearStatsModal = async () => {
      generateAvailableYears()
      selectedYear.value = currentDate.value.getFullYear()
      await loadYearStatisticsForYear(selectedYear.value)
      showYearStatsModal.value = true
    }
    const onYearChange = async () => { await loadYearStatisticsForYear(selectedYear.value) }
    const prevYear = async () => { selectedYear.value -= 1; await loadYearStatisticsForYear(selectedYear.value) }
    const nextYear = async () => { selectedYear.value += 1; await loadYearStatisticsForYear(selectedYear.value) }

    const addNotificationStyles = () => {
      if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style')
        style.id = 'notification-styles'
        style.textContent = `
          @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
          @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
          .notification { background: var(--white, #fff); color: var(--dark-color, #1e293b); border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 10px; min-width: 300px; max-width: 400px; }
          .notification-content { display: flex; align-items: center; gap: 12px; padding: 12px 16px; }
          .notification-success { border-left: 4px solid #10b981; }
          .notification-success i { color: #10b981; }
          .notification-error { border-left: 4px solid #ef4444; }
          .notification-error i { color: #ef4444; }
          .notification-info { border-left: 4px solid #3b82f6; }
          .notification-info i { color: #3b82f6; }
          @media (max-width: 768px) { .notification { min-width: auto; width: calc(100% - 40px); max-width: none; } }
        `
        document.head.appendChild(style)
      }
    }

    onMounted(() => {
      loadData()
      addNotificationStyles()
      generateAvailableYears()
    })

    return {
      currentDate, shifts, monthlyStats, yearStats, yearStatsYear, settings, hasSettings,
      isLoading, hasLoadError, isSavingShift, isSavingMotivation, isSavingSettings,
      isSavingVacation, isSavingMany,
      showShiftModal, showSettingsModal, showAddManyModal, showYearStatsModal,
      showVacationModal, showMotivationModal,
      showStatsModal, selectedStatsType, showStatsCurrency, openStatsAnalytics, hasAnalyticsContent,
      motivationData, selectedDay, shiftDetails, editHours,
      showShiftCurrency, showYearCurrency,
      openDaySections, openSettingsSections,
      manyShiftsData, selectionDate, weekDays,
      calendarDays, calendarRows, selectionDates, selectionCalendarRows,
      selectionMonthName, selectionYear, currentMonthName, currentYear,
      previousMonth, nextMonth, goToToday, prevSelectionMonth, nextSelectionMonth,
      toggleCurrency, toggleShiftCurrency, toggleYearCurrency,
      toggleDaySection, toggleSettingsSection,
      isDateSelected, toggleDateSelection, selectAllDatesInMonth, clearAllDates,
      openShiftModal, closeShiftModal, saveShift, deleteShift, deleteVacationOrSick,
      openMotivationModal, closeMotivationModal, saveMotivation, isSaveMotivationDisabled,
      openSettingsModal, closeSettingsModal, saveSettings, deleteSettings,
      openAddManyModal, closeAddManyModal, saveManyShifts,
      openVacationModal, closeVacationModal, saveVacation,
      openYearStatsModal, closeYearStatsModal,
      openStatsModal, closeStatsModal, statsModalData, statsModalTitle,
      formatNumber, formatNumberShort, formatDateShort, formatDateForDisplay,
      hasPeriodData, hasCurrencyData, hasShiftCurrencyData,
      selectedYear, availableYears, prevYear, nextYear, onYearChange,
      getProductivity, getColdPercent, getHoursPercent, getNonProductivePercent,
      getAwardPercent, getOvertimePercent,
      getMotivationTotal, getOperationsTotal, getYearMotivationTotal,
      periodOneBestDay, periodTwoBestDay, monthBestDay,
      periodOneProductivity, periodTwoProductivity,
      productivityChangePercent, productivityChangeSymbol, productivityChangeClass,
      vacationData,
      // --- Цели ---
      currentGoal, showGoalModal, isSavingGoal, goalData,
      goalCurrentAmount, goalProgressPercent, isGoalAchieved, goalProgressClass, goalForecastInfo,
      openGoalModal, closeGoalModal, saveGoal, deleteGoal, isFutureDay, getMonthStr
    }
  }
}
</script>

<style scoped>
:root {
  --radius: 8px;
}

/* ================================================================
   НОВЫЕ СТИЛИ ДЛЯ КАРТОЧЕК СТАТИСТИКИ (Минимализм)
   ================================================================ */
.month-statistics {
  margin-top: 2rem;
  margin-bottom: 2rem;
}

.modern-stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

/* Для планшетов и десктопа */
@media (min-width: 768px) {
  .modern-stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }
}

.modern-stat-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow: hidden;
}

.modern-stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.modern-stat-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  color: white;
  gap: 0.75rem;
}

@media (max-width: 767px) {
  .modern-stat-inner {
    padding: 0.85rem 1rem;
  }
}

/* Градиенты */
.bg-green {
  background: linear-gradient(135deg, #10b981 0%, #047857 100%);
}

.bg-blue {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.modern-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

@media (max-width: 360px) {
  .modern-icon {
    display: none; /* На самых узких экранах скрываем иконку */
  }
}

.modern-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* Чтобы текст мог сжиматься */
}

.modern-title {
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.modern-sub {
  font-size: 0.75rem;
  opacity: 0.7;
  font-weight: 400;
}

.modern-amount {
  font-size: 1.15rem;
  font-weight: 800;
  margin-top: 0.1rem;
  white-space: nowrap;
}

.modern-arrow {
  font-size: 0.8rem;
  opacity: 0.6;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.modern-stat-card:hover .modern-arrow {
  transform: translateX(3px);
  opacity: 1;
}

/* Специфичные стили для планшетов (убираем лишнее, чтобы текст помещался) */
@media (min-width: 768px) and (max-width: 1024px) {
  .modern-stat-inner {
    padding: 0.75rem;
    gap: 0.5rem;
  }
  .modern-icon {
    width: 32px;
    height: 32px;
    font-size: 1rem;
  }
  .modern-sub {
    display: none; /* Скрываем (1-15) на планшетах */
  }
  .modern-arrow {
    display: none; /* Скрываем стрелку на планшетах, чтобы не мешала */
  }
  .modern-amount {
    font-size: 1.05rem;
  }
  .modern-title {
    font-size: 0.85rem;
  }
}

/* ================================================================
   БАЗОВЫЙ LAYOUT МОДАЛОК: flex-column + sticky header/footer
   ================================================================ */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  overflow: hidden;
  padding: 0;
}

.modal-content {
  background: var(--white);
  border-radius: var(--radius);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
  margin: 0;
}

/* ================================================================
   BOTTOM-SHEET (mobile) / центрированная (desktop)
   ================================================================ */
@media (max-width: 768px) {
  .modal.modal-bottom-sheet {
    align-items: flex-end;
    justify-content: stretch;
  }

  .modal.modal-bottom-sheet .modal-content {
    width: 100%;
    max-width: 100%;
    border-radius: 16px 16px 0 0;
    max-height: 92dvh;
    animation: slideUp 0.25s ease;
    padding-bottom: env(safe-area-inset-bottom);
  }

  .sheet-handle {
    display: block;
    width: 40px;
    height: 4px;
    background: #cbd5e1;
    border-radius: 2px;
    margin: 8px auto 2px;
    flex-shrink: 0;
  }
}

.sheet-handle {
  display: none;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}

/* ================================================================
   HEADER BUTTONS: (Иконки в ряд на мобилке)
   ================================================================ */
@media (max-width: 768px) {
  .header-actions {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
    width: 100%;
  }

  .header-actions .btn {
    width: 100%;
    padding: 0.5rem 0;
    min-height: 44px;
    font-size: 0.8rem;
    flex-direction: column;
    gap: 0.25rem;
  }

  .header-actions .btn .btn-text {
    display: none;
  }

  .header-actions .btn i {
    font-size: 1.25rem;
    margin: 0;
  }
}

/* ================================================================
   КОМПАКТНЫЙ ТУЛБАР (для группового проставления)
   ================================================================ */
.header-tools {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}

.btn-compact {
  padding: 0.4rem 0.6rem;
  font-size: 0.75rem;
  font-weight: 500;
  min-height: 36px;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  color: white;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: all 0.2s;
}

.btn-compact.btn-success { background: #10b981; }
.btn-compact.btn-success:hover { background: #059669; }
.btn-compact.btn-warning { background: #f59e0b; }
.btn-compact.btn-warning:hover { background: #d97706; }

.compact-toolbar {
  flex-shrink: 0;
  padding: 0.6rem 1rem;
  background: var(--white);
  border-bottom: 1px solid var(--light-color);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toolbar-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-row label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--dark-color);
  white-space: nowrap;
}

.toolbar-input {
  flex: 1;
  max-width: 120px;
}

.toolbar-month {
  justify-content: center;
}

/* ================================================================
   АДАПТАЦИЯ КАЛЕНДАРЯ ВЫБОРА (Group Add)
   ================================================================ */
.selection-calendar {
  background: var(--white);
  border-radius: var(--radius);
  padding: 0.5rem;
  border: 1px solid var(--light-color);
  width: 100%;
  box-sizing: border-box;
}

.selection-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 0.5rem;
  width: 100%;
}

.selection-weekday {
  text-align: center;
  padding: 0.5rem 0;
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--light-color);
  border-radius: var(--radius);
  color: var(--dark-color);
}

.selection-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  width: 100%;
}

.selection-day {
  position: relative;
  aspect-ratio: 1 / 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  background: var(--white);
  color: var(--dark-color);
  padding: 0;
  width: 100%;
}

.selection-day:hover {
  transform: scale(1.05);
  box-shadow: var(--shadow);
}

.selection-day.has-shift {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
  color: #3b82f6;
}

.selection-day.selected {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.selection-day.other-month-date {
  opacity: 0.3;
  background: var(--light-color);
}

.selection-day.other-month-date:hover {
  transform: none;
  opacity: 0.4;
}

.selection-day-number {
  font-weight: 500;
}

.check-icon {
  position: absolute;
  bottom: 2px;
  right: 2px;
  font-size: 0.65rem;
}

.shift-icon {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 0.55rem;
  color: #3b82f6;
}

.vacation-icon {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 0.55rem;
  color: #f59e0b;
}

.sick-icon {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 0.55rem;
  color: #ef4444;
}

.selection-day.selected .shift-icon,
.selection-day.selected .vacation-icon,
.selection-day.selected .sick-icon {
  color: white;
}

@media (max-width: 480px) {
  .selection-day {
    font-size: 0.8rem;
  }
}

/* ================================================================
   КНОПКИ В ФУТЕРЕ
   ================================================================ */
.btn-save {
  flex: 1;
  min-height: 44px;
}

.btn-icon {
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  flex-shrink: 0;
  color: white;
}

/* ================================================================
   БАЗОВЫЙ LAYOUT
   ================================================================ */
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-header.total-header h3 {
  color: #3b82f6;
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
  flex-shrink: 0;
}

/* ================================================================
   АККОРДЕОНЫ (день + настройки + аналитика)
   ================================================================ */
.accordion-item {
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  margin-bottom: 0.5rem;
  overflow: hidden;
  background: var(--white);
}

/* Специфичный отступ для аналитики, чтобы отделить от основных сумм */
.stats-analytics-accordion {
  margin-top: 1rem;
}

.accordion-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  user-select: none;
  background: var(--light-color);
  min-height: 44px;
  transition: background 0.2s;
}

.accordion-header:hover {
  filter: brightness(0.97);
}

.accordion-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.accordion-title {
  flex: 1;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--dark-color);
  text-align: left;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.accordion-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--dark-color);
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
}

.accordion-header > i {
  color: var(--gray-color);
  font-size: 0.75rem;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.accordion-body {
  padding: 0.5rem 0.75rem;
}

.accordion-body .form-group:last-child {
  margin-bottom: 0;
}

/* ================================================================
   ПРОСТЫЕ СТРОКИ (часы/холод/переработка в модалке дня)
   ================================================================ */
.simple-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.75rem;
  background: var(--white);
  border: 1px solid var(--light-color);
  border-radius: var(--radius);
  margin-bottom: 0.5rem;
  min-height: 44px;
  font-size: 0.85rem;
  color: var(--dark-color);
  gap: 0.5rem;
}

.simple-line-label {
  flex: 1;
  text-align: left;
  min-width: 0;
}

.simple-line-value {
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
}

/* ================================================================
   STICKY SUMMARY BAR (модалка дня)
   ================================================================ */
.day-summary-bar {
  display: flex;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  flex-shrink: 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.day-summary-bar::-webkit-scrollbar { display: none; }

.summary-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.7rem;
  background: rgba(255,255,255,0.2);
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.summary-chip-value {
  color: white;
}

.summary-chip-extra {
  font-size: 0.72rem;
  opacity: 0.85;
  font-weight: 500;
}

/* ================================================================
   EDIT BLOCK (модалка дня)
   ================================================================ */
.edit-block {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: var(--light-color);
  border-radius: var(--radius);
}

.motivation-section {
  margin-top: 0.5rem;
}

.btn-motivation {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 44px;
}

.btn-motivation:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245,158,11,0.3);
}

/* ================================================================
   БЕЙДЖИ ПРОЦЕНТОВ
   ================================================================ */
.percent-badge {
  display: inline-block;
  margin-left: 0.25rem;
  padding: 0.1rem 0.4rem;
  font-size: 0.7rem;
  font-weight: 600;
  background: rgba(148, 163, 184, 0.2);
  color: var(--dark-color, #e2e8f0);
  border-radius: 10px;
  vertical-align: middle;
}

.hours-percent-badge { background: rgba(16, 185, 129, 0.25); color: #34d399; }
.cold-percent-badge { background: rgba(59, 130, 246, 0.25); color: #60a5fa; }
.overtime-percent-badge { background: rgba(239, 68, 68, 0.25); color: #f87171; }
.award-percent-badge { background: rgba(245, 158, 11, 0.25); color: #fbbf24; }

/* ================================================================
   STICKY-ТУЛБАР (для года)
   ================================================================ */
.sticky-toolbar {
  flex-shrink: 0;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--light-color);
  background: var(--white);
}

/* ================================================================
   ОБЩИЕ СТИЛИ
   ================================================================ */
.btn, button:not(.btn-nav):not(.btn-month-nav):not(.btn-award):not(.modal-close):not(.btn-icon):not(.btn-compact):not(.btn-year-nav) {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; }
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(59,130,246,0.3); }
.btn-secondary { background: #8B0000; color: white; }
.btn-secondary:hover { background: #FF0000; transform: translateY(-1px); }
.btn-success { background: #10b981; color: white; }
.btn-success:hover { background: #059669; transform: translateY(-1px); }
.btn-warning { background: #f59e0b; color: white; }
.btn-warning:hover { background: #d97706; transform: translateY(-1px); }
.btn-danger { background: #ef4444; color: white; }
.btn-danger:hover { background: #dc2626; transform: translateY(-1px); }
.btn-info { background: #06b6d4; color: white; }
.btn-info:hover { background: #0891b2; transform: translateY(-1px); }
.btn-vacation { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; }
.btn-vacation:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(245,158,11,0.3); }

button:disabled { opacity: 0.5; cursor: not-allowed; }

.timesheets-container { padding: 0.5rem; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.page-title { font-size: 1.5rem; color: var(--dark-color); margin: 0; }
.header-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.month-navigation { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.btn-nav { background: var(--light-color); border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; justify-content: center; font-size: 1rem; color: #0284c7; }
.btn-nav:hover { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; transform: scale(1.05); }
.current-month h2 { font-size: 1.25rem; text-transform: capitalize; margin: 0; color: var(--dark-color); }
.btn-today { padding: 0.5rem 1rem; background: var(--light-color); color: #0284c7; border: none; border-radius: var(--radius); cursor: pointer; transition: all 0.3s; }
.btn-today:hover { background: #0284c7; color: white; }
.weekdays { display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.5rem; margin-bottom: 0.5rem; }
.weekday { text-align: center; padding: 0.75rem; font-weight: 600; background: var(--light-color); border-radius: var(--radius); color: var(--dark-color); }
.weekday.weekend { background: rgba(239, 68, 68, 0.15); color: var(--danger-color); }
.calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.5rem; margin-bottom: 1.5rem; }
.calendar-day { border-radius: var(--radius); padding: 0.5rem; min-height: 80px; cursor: pointer; transition: all 0.3s; border: 1px solid var(--light-color); position: relative; display: flex; flex-direction: column; justify-content: space-between; background: var(--white); color: var(--dark-color); }
.calendar-day:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
.calendar-day.other-month { opacity: 0; background: transparent; border: 1px solid transparent; cursor: default; pointer-events: none; }
.calendar-day.other-month .day-number { visibility: hidden; }
.calendar-day.weekend-day { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.2); color: var(--danger-color); }
.calendar-day.weekend-with-shift { background: #8B0000; color: white; }
.calendar-day.has-shift { background: linear-gradient(135deg, #3b82f6 0%, #000080 100%); color: white; box-shadow: 0 2px 8px rgba(59,130,246,0.3); }
.calendar-day.vacation-day { background: linear-gradient(135deg, #fcd34d 0%, #f59e0b 100%); color: #1e293b; border-color: #f59e0b; }
.calendar-day.sick-day { background: linear-gradient(135deg, #fca5a5 0%, #ef4444 100%); color: white; border-color: #ef4444; }
.calendar-day.today { border: 2px solid #f59e0b; box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.3); }
.day-number { font-weight: 700; font-size: 1.125rem; margin-bottom: 0.25rem; }
.day-earned { font-size: 0.75rem; font-weight: 500; text-align: right; margin-top: auto; }
.day-status { font-size: 0.6rem; font-weight: 600; text-align: right; margin-top: auto; display: flex; align-items: center; justify-content: flex-end; gap: 0.25rem; }
.vacation-status { color: #92400e; }
.sick-status { color: #7f1d1d; }
.day-empty { text-align: right; color: var(--gray-color); margin-top: auto; }

/* Вложенные стили для модалки статистики */
.stat-line { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid var(--light-color); }
.stat-line:last-child { border-bottom: none; }
.stat-label { font-size: 0.8rem; color: var(--gray-color); }
.stat-number { font-weight: 600; font-size: 0.85rem; color: var(--dark-color); }
.stat-number.award { color: #fbbf24; }
.stat-number.overtime { color: #f87171; }
.award-line { background: rgba(245, 158, 11, 0.1); margin: 0.25rem 0; padding: 0.5rem; border-radius: var(--radius); }
.stat-line.sub-line { padding-left: 1.25rem; padding-top: 0.25rem; padding-bottom: 0.25rem; border-bottom: none; }
.stat-line.sub-line .stat-label { font-size: 0.75rem; color: #94a3b8; }
.stat-line.sub-line .stat-number { font-size: 0.8rem; font-weight: 500; color: #cbd5e1; }

.currency-list { margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.3rem; }
.currency-line { font-size: 0.75rem; padding: 0.3rem 0.5rem; background: var(--light-color); border-radius: var(--radius); color: var(--dark-color); }

.vacation-sick-details { background: rgba(245, 158, 11, 0.1); padding: 1rem; border-radius: var(--radius); margin-bottom: 1rem; }
.vacation-sick-status { font-size: 1.1rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; color: var(--dark-color); }
.vacation-preview { padding: 0.75rem; background: rgba(16, 185, 129, 0.1); color: var(--dark-color); border-radius: var(--radius); margin-top: 0.5rem; text-align: center; }

.best-day-period { margin-top: 0.75rem; padding: 0.5rem; background: rgba(16, 185, 129, 0.1); border-radius: var(--radius); border-left: 3px solid #10b981; }
.best-day-month { margin-top: 0.75rem; padding: 0.75rem; background: rgba(16, 185, 129, 0.1); border-radius: var(--radius); border-left: 3px solid #10b981; }
.best-day-header { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px; color: #059669; margin-bottom: 0.25rem; font-weight: 600; }
.best-day-content { display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.5rem; }
.best-day-date { font-weight: 600; font-size: 0.8rem; color: var(--dark-color); }
.best-day-stats { font-size: 0.7rem; color: var(--gray-color); }
.best-day-productivity { background: #10b981; color: white; padding: 0.2rem 0.5rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }

.dynamics-line { margin-top: 0.75rem; padding: 0.5rem; background: var(--light-color); border-radius: var(--radius); }
.dynamics-header { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--gray-color); margin-bottom: 0.25rem; }
.dynamics-content { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.period1-value, .period2-value { font-weight: 600; font-size: 0.85rem; background: var(--white); padding: 0.2rem 0.5rem; border-radius: var(--radius); color: var(--dark-color); }
.dynamics-content i { color: #3b82f6; font-size: 0.7rem; }
.dynamics-change { font-weight: 600; font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 20px; }
.dynamics-change.positive { background: rgba(16, 185, 129, 0.2); color: #059669; }
.dynamics-change.negative { background: rgba(239, 68, 68, 0.2); color: #dc2626; }
.dynamics-change.neutral { background: var(--white); color: var(--gray-color); }

.btn-month-nav { background: var(--white); border: 1px solid var(--light-color); width: 40px; height: 40px; border-radius: 50%; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; justify-content: center; color: #3b82f6; flex-shrink: 0; }
.btn-month-nav:hover { background: #3b82f6; color: white; border-color: #3b82f6; }
.selected-month { font-size: 0.95rem; font-weight: 600; min-width: 140px; text-align: center; text-transform: capitalize; color: var(--dark-color); }

.form-group { margin-bottom: 0.75rem; }
.form-label { display: block; margin-bottom: 0.4rem; font-weight: 500; font-size: 0.875rem; color: var(--dark-color); }
.form-label.required:after { content: " *"; color: var(--danger-color); }
.form-control { width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--gray-color); border-radius: var(--radius); font-size: 0.9rem; transition: border-color 0.3s; box-sizing: border-box; background: var(--white); color: var(--dark-color); min-height: 44px; }
.form-control:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }

.year-selector { display: flex; align-items: center; justify-content: center; gap: 1rem; padding: 0.5rem; background: var(--light-color); border-radius: var(--radius); }
.btn-year-nav { background: var(--white); border: 1px solid var(--light-color); width: 40px; height: 40px; border-radius: 50%; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; justify-content: center; color: #3b82f6; flex-shrink: 0; }
.btn-year-nav:hover { background: #3b82f6; color: white; border-color: #3b82f6; }
.year-select { padding: 0.5rem 1rem; font-size: 1rem; font-weight: 600; border: 1px solid var(--light-color); border-radius: var(--radius); background: var(--white); color: var(--dark-color); cursor: pointer; outline: none; min-width: 100px; text-align: center; }
.year-select:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }

.year-stats { padding: 0.5rem 0; }
.stat-big-card { display: flex; align-items: center; gap: 1rem; padding: 1rem; background: var(--light-color); border-radius: var(--radius); margin-bottom: 1rem; }
.stat-icon-large { width: 60px; height: 60px; background: var(--white); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.75rem; color: #3b82f6; flex-shrink: 0; }
.stat-info-large { flex: 1; }
.stat-value-large { font-size: 1.5rem; font-weight: 600; color: var(--dark-color); }
.year-currency { margin-top: 1rem; }

.year-motivation-block { margin-top: 1rem; padding: 0.75rem; background: rgba(245, 158, 11, 0.1); border-radius: var(--radius); border-left: 3px solid #f59e0b; }
.year-motivation-header { font-weight: 600; font-size: 0.95rem; color: #fbbf24; margin-bottom: 0.25rem; }

.no-data { text-align: center; padding: 2rem; color: var(--gray-color); }
.no-data i { font-size: 3rem; margin-bottom: 1rem; color: var(--light-color); }
.no-data p { margin: 0; font-size: 1rem; }

/* ================================================================
   БЛОК ЦЕЛИ
   ================================================================ */
.goal-progress-card {
  position: relative;
  background: var(--white);
  border-radius: var(--radius);
  padding: 1rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
  border-left: 4px solid #3b82f6;
  transition: all 0.3s ease;
}

.goal-progress-card.goal-success {
  border-left-color: #10b981;
  background: linear-gradient(to right, rgba(16, 185, 129, 0.05), var(--white));
}

.goal-progress-card.goal-warning {
  border-left-color: #f59e0b;
}

.goal-progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
  padding-right: 1.5rem;
}

.goal-title {
  font-weight: 600;
  color: var(--dark-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.goal-values {
  font-weight: 500;
  color: var(--gray-color);
}

.goal-values strong {
  color: var(--dark-color);
  font-size: 1rem;
}

.goal-progress-bar {
  position: relative;
  height: 12px;
  background: var(--light-color);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.goal-progress-fill {
  height: 100%;
  border-radius: 6px;
  background: #3b82f6;
  transition: width 0.5s ease-out;
}

.goal-success .goal-progress-fill {
  background: linear-gradient(90deg, #10b981, #34d399);
}

.goal-warning .goal-progress-fill {
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
}

.goal-percent-badge {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--dark-color);
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 10px;
}

.goal-forecast {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  padding: 0.5rem;
  border-radius: var(--radius);
  background: var(--light-color);
}

.goal-forecast.success {
  color: #059669;
  background: rgba(16, 185, 129, 0.1);
}

.goal-forecast.warning {
  color: #d97706;
  background: rgba(245, 158, 11, 0.1);
}

.goal-forecast.neutral {
  color: var(--gray-color);
}

/* Новый статус, если месяц закончился, а цель не достигнута */
.goal-forecast.danger {
  color: #dc2626;
  background: rgba(239, 68, 68, 0.1);
}

.goal-achieved-banner {
  margin-top: 0.75rem;
  padding: 0.5rem;
  background: linear-gradient(135deg, #fcd34d 0%, #f59e0b 100%);
  color: #1e293b;
  font-weight: 700;
  text-align: center;
  border-radius: var(--radius);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
}

.goal-edit-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: var(--gray-color);
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0.25rem;
  transition: color 0.2s;
}

.goal-edit-btn:hover {
  color: #3b82f6;
}

.goal-empty-card {
  margin-bottom: 1.5rem;
}

.btn-add-goal {
  background: var(--white);
  border: 1px dashed #3b82f6;
  color: #3b82f6;
  padding: 0.8rem 1rem;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  width: 100%;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-add-goal:hover {
  background: rgba(59, 130, 246, 0.05);
  border-style: solid;
}

.goal-modal-desc {
  font-size: 0.85rem;
  color: var(--gray-color);
  margin-bottom: 1rem;
  line-height: 1.4;
}

/* ================================================================
   ЕДИНЫЙ МЕДИА-ЗАПРОС ДЛЯ МОБИЛЬНЫХ
   ================================================================ */
@media (max-width: 768px) {
  .timesheets-container { padding: 0.25rem; }
  .page-header { flex-direction: column; align-items: stretch; }
  .page-title { text-align: center; }
  .calendar-day { min-height: 65px; }
  .day-number { font-size: 0.875rem; }
  .day-earned { font-size: 0.625rem; }
  .header-actions { flex-wrap: nowrap; }
  .goal-progress-card { padding: 0.75rem; }
  .goal-values { font-size: 0.8rem; }
  .goal-values strong { font-size: 0.9rem; }
}

@media (max-width: 480px) {
  .calendar-day { min-height: 55px; padding: 0.25rem; }
  .day-earned { font-size: 0.5rem; }
  .weekday { font-size: 0.625rem; padding: 0.35rem; }
  .simple-line { font-size: 0.78rem; padding: 0.5rem 0.6rem; }
  .simple-line-label { font-size: 0.78rem; }
  .simple-line-value { font-size: 0.78rem; }
  .accordion-title { font-size: 0.8rem; }
  .accordion-value { font-size: 0.8rem; }
  .summary-chip { font-size: 0.78rem; padding: 0.3rem 0.6rem; }
  .summary-chip-extra { display: none; }
  .selected-month { min-width: 100px; font-size: 0.85rem; }
  .header-actions { flex-wrap: nowrap; }
  .goal-edit-btn { top: 0.5rem; right: 0.5rem; }
}

.motivation-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.7rem 0.75rem;
  background: rgba(148, 163, 184, 0.08);
  border: 1px dashed var(--gray-color);
  border-radius: var(--radius);
  color: var(--gray-color);
  font-size: 0.8rem;
  text-align: center;
  line-height: 1.3;
}

.motivation-hint i {
  flex-shrink: 0;
  font-size: 0.85rem;
}
</style>