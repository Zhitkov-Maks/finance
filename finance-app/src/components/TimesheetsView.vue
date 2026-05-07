<template>
  <div class="timesheets-container">
    <!-- Заголовок -->
    <div class="page-header">
      <h1 class="page-title">
        <i class="fas fa-calendar-alt"></i>
        Мой график
      </h1>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="openSettingsModal">
          <i class="fas fa-cog"></i>
          Настройки
        </button>
        <button class="btn btn-primary" @click="openAddManyModal">
          <i class="fas fa-layer-group"></i>
          Проставить смены
        </button>
        <button class="btn btn-info" @click="openYearStatsModal">
          <i class="fas fa-chart-line"></i>
          Статистика за год
        </button>
      </div>
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
          'weekend-day': day.isCurrentMonth && day.isWeekend && !day.hasShift,
          'weekend-with-shift': day.isCurrentMonth && day.isWeekend && day.hasShift,
          'today': day.isCurrentMonth && day.isToday,
          'has-shift': day.isCurrentMonth && day.hasShift && !day.isWeekend
        }"
        @click="openShiftModal(day)"
      >
        <div class="day-number">{{ day.dayNumber }}</div>
        <div v-if="day.isCurrentMonth && day.hasShift && day.earned" class="day-earned">
          {{ formatNumberShort(day.earned) }} ₽
        </div>
        <div v-else-if="day.isCurrentMonth && !day.hasShift" class="day-empty">
          <i class="fas fa-plus-circle"></i>
        </div>
      </div>
    </div>

    <!-- Детальная статистика за месяц -->
    <div class="month-statistics" v-if="monthlyStats">
      <div class="stats-container">
        <div class="stat-card" v-if="hasPeriodData(monthlyStats.period_one)">
          <div class="stat-card-header" @click="toggleSection('period1')">
            <i class="fas" :class="openSections.period1 ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
            <h3>Период 1 (1-15)</h3>
            <span class="total-earned">{{ formatNumber(monthlyStats.period_one.total_earned) }} ₽</span>
          </div>
          <div v-show="openSections.period1" class="stat-card-body">
            <div v-if="monthlyStats.period_one.total_base_hours" class="stat-line">
              <span class="stat-label">Часы:</span>
              <span class="stat-number">{{ monthlyStats.period_one.total_base_hours }} ч</span>
            </div>
            <div v-if="monthlyStats.period_one.total_earned_hours" class="stat-line">
              <span class="stat-label">Заработано за часы:</span>
              <span class="stat-number">{{ formatNumber(monthlyStats.period_one.total_earned_hours) }} ₽</span>
            </div>
            <div v-if="monthlyStats.period_one.total_earned_cold" class="stat-line">
              <span class="stat-label">Доплата за холод:</span>
              <span class="stat-number">{{ formatNumber(monthlyStats.period_one.total_earned_cold) }} ₽</span>
            </div>
            <div v-if="monthlyStats.period_one.total_award" class="stat-line award-line">
              <span class="stat-label">🏆 Мотивация:</span>
              <span class="stat-number award">{{ formatNumber(monthlyStats.period_one.total_award) }} ₽</span>
            </div>
            <div v-if="monthlyStats.period_one.total_overtime" class="stat-line">
              <span class="stat-label">Доплата за переработку:</span>
              <span class="stat-number overtime">{{ formatNumber(monthlyStats.period_one.total_overtime) }} ₽</span>
            </div>
            <div v-if="monthlyStats.period_one.total_hours_overtime" class="stat-line">
              <span class="stat-label">Часов переработки:</span>
              <span class="stat-number">{{ monthlyStats.period_one.total_hours_overtime }} ч</span>
            </div>
            <div v-if="monthlyStats.period_one.total_operations" class="stat-line">
              <span class="stat-label">Кол-во операций:</span>
              <span class="stat-number">{{ monthlyStats.period_one.total_operations }}</span>
            </div>
            <div class="currency-block" v-if="hasCurrencyData(monthlyStats.period_one)">
              <div class="currency-header" @click="toggleCurrency('period1')">
                <i class="fas" :class="openCurrency.period1 ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
                <span>💱 Заработано в валюте:</span>
              </div>
              <div v-show="openCurrency.period1" class="currency-list">
                <div v-if="monthlyStats.period_one.dollar" class="currency-line">🇺🇸 Доллар: ${{ formatNumber(monthlyStats.period_one.dollar) }}</div>
                <div v-if="monthlyStats.period_one.euro" class="currency-line">🇪🇺 Евро: €{{ formatNumber(monthlyStats.period_one.euro) }}</div>
                <div v-if="monthlyStats.period_one.yena" class="currency-line">🇨🇳 Юань: ¥{{ formatNumber(monthlyStats.period_one.yena) }}</div>
                <div v-if="monthlyStats.period_one.som" class="currency-line">🇰🇬 Сом: {{ formatNumber(monthlyStats.period_one.som) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="stat-card" v-if="hasPeriodData(monthlyStats.period_two)">
          <div class="stat-card-header" @click="toggleSection('period2')">
            <i class="fas" :class="openSections.period2 ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
            <h3>Период 2 (16-31)</h3>
            <span class="total-earned">{{ formatNumber(monthlyStats.period_two.total_earned) }} ₽</span>
          </div>
          <div v-show="openSections.period2" class="stat-card-body">
            <div v-if="monthlyStats.period_two.total_base_hours" class="stat-line">
              <span class="stat-label">Часы:</span>
              <span class="stat-number">{{ monthlyStats.period_two.total_base_hours }} ч</span>
            </div>
            <div v-if="monthlyStats.period_two.total_earned_hours" class="stat-line">
              <span class="stat-label">Заработано за часы:</span>
              <span class="stat-number">{{ formatNumber(monthlyStats.period_two.total_earned_hours) }} ₽</span>
            </div>
            <div v-if="monthlyStats.period_two.total_earned_cold" class="stat-line">
              <span class="stat-label">Доплата за холод:</span>
              <span class="stat-number">{{ formatNumber(monthlyStats.period_two.total_earned_cold) }} ₽</span>
            </div>
            <div v-if="monthlyStats.period_two.total_award" class="stat-line award-line">
              <span class="stat-label">🏆 Мотивация:</span>
              <span class="stat-number award">{{ formatNumber(monthlyStats.period_two.total_award) }} ₽</span>
            </div>
            <div v-if="monthlyStats.period_two.total_overtime" class="stat-line">
              <span class="stat-label">Доплата за переработку:</span>
              <span class="stat-number overtime">{{ formatNumber(monthlyStats.period_two.total_overtime) }} ₽</span>
            </div>
            <div v-if="monthlyStats.period_two.total_hours_overtime" class="stat-line">
              <span class="stat-label">Часов переработки:</span>
              <span class="stat-number">{{ monthlyStats.period_two.total_hours_overtime }} ч</span>
            </div>
            <div v-if="monthlyStats.period_two.total_operations" class="stat-line">
              <span class="stat-label">Кол-во операций:</span>
              <span class="stat-number">{{ monthlyStats.period_two.total_operations }}</span>
            </div>
            <div class="currency-block" v-if="hasCurrencyData(monthlyStats.period_two)">
              <div class="currency-header" @click="toggleCurrency('period2')">
                <i class="fas" :class="openCurrency.period2 ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
                <span>💱 Заработано в валюте:</span>
              </div>
              <div v-show="openCurrency.period2" class="currency-list">
                <div v-if="monthlyStats.period_two.dollar" class="currency-line">🇺🇸 Доллар: ${{ formatNumber(monthlyStats.period_two.dollar) }}</div>
                <div v-if="monthlyStats.period_two.euro" class="currency-line">🇪🇺 Евро: €{{ formatNumber(monthlyStats.period_two.euro) }}</div>
                <div v-if="monthlyStats.period_two.yena" class="currency-line">🇨🇳 Юань: ¥{{ formatNumber(monthlyStats.period_two.yena) }}</div>
                <div v-if="monthlyStats.period_two.som" class="currency-line">🇰🇬 Сом: {{ formatNumber(monthlyStats.period_two.som) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="stat-card total-card">
          <div class="stat-card-header" @click="toggleSection('total')">
            <i class="fas" :class="openSections.total ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
            <h3>📊 Итого за месяц</h3>
            <span class="total-earned">{{ formatNumber(monthlyStats.total?.total_earned) }} ₽</span>
          </div>
          <div v-show="openSections.total" class="stat-card-body">
            <div v-if="monthlyStats.total?.total_base_hours" class="stat-line">
              <span class="stat-label">Часы:</span>
              <span class="stat-number">{{ monthlyStats.total.total_base_hours }} ч</span>
            </div>
            <div v-if="monthlyStats.total?.total_earned_hours" class="stat-line">
              <span class="stat-label">Заработано за часы:</span>
              <span class="stat-number">{{ formatNumber(monthlyStats.total.total_earned_hours) }} ₽</span>
            </div>
            <div v-if="monthlyStats.total?.total_earned_cold" class="stat-line">
              <span class="stat-label">Доплата за холод:</span>
              <span class="stat-number">{{ formatNumber(monthlyStats.total.total_earned_cold) }} ₽</span>
            </div>
            <div v-if="monthlyStats.total?.total_award" class="stat-line award-line">
              <span class="stat-label">🏆 Мотивация:</span>
              <span class="stat-number award">{{ formatNumber(monthlyStats.total.total_award) }} ₽</span>
            </div>
            <div v-if="monthlyStats.total?.total_overtime" class="stat-line">
              <span class="stat-label">Доплата за переработку:</span>
              <span class="stat-number overtime">{{ formatNumber(monthlyStats.total.total_overtime) }} ₽</span>
            </div>
            <div v-if="monthlyStats.total?.total_hours_overtime" class="stat-line">
              <span class="stat-label">Часов переработки:</span>
              <span class="stat-number">{{ monthlyStats.total.total_hours_overtime }} ч</span>
            </div>
            <div v-if="monthlyStats.total?.total_operations" class="stat-line">
              <span class="stat-label">Кол-во операций:</span>
              <span class="stat-number">{{ monthlyStats.total.total_operations }}</span>
            </div>
            <div class="currency-block" v-if="hasCurrencyData(monthlyStats.total)">
              <div class="currency-header" @click="toggleCurrency('total')">
                <i class="fas" :class="openCurrency.total ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
                <span>💱 Заработано в валюте:</span>
              </div>
              <div v-show="openCurrency.total" class="currency-list">
                <div v-if="monthlyStats.total?.dollar" class="currency-line">🇺🇸 Доллар: ${{ formatNumber(monthlyStats.total.dollar) }}</div>
                <div v-if="monthlyStats.total?.euro" class="currency-line">🇪🇺 Евро: €{{ formatNumber(monthlyStats.total.euro) }}</div>
                <div v-if="monthlyStats.total?.yena" class="currency-line">🇨🇳 Юань: ¥{{ formatNumber(monthlyStats.total.yena) }}</div>
                <div v-if="monthlyStats.total?.som" class="currency-line">🇰🇬 Сом: {{ formatNumber(monthlyStats.total.som) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальные окна (остаются без изменений) -->
    <div v-if="showAddManyModal" class="modal" @click.self="closeAddManyModal">
      <div class="modal-content large">
        <div class="modal-header">
          <h3>
            <i class="fas fa-layer-group"></i>
            Отметить смены
          </h3>
          <button class="modal-close" @click="closeAddManyModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label required">Количество часов</label>
            <input type="number" v-model.number="manyShiftsData.hours" class="form-control" step="0.5" required />
          </div>
          <div class="form-group">
            <label class="form-label">Выбор месяца</label>
            <div class="month-selector">
              <button class="btn-month-nav" @click="prevSelectionMonth">
                <i class="fas fa-chevron-left"></i>
              </button>
              <span class="selected-month">{{ selectionMonthName }} {{ selectionYear }}</span>
              <button class="btn-month-nav" @click="nextSelectionMonth">
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Выберите даты:</label>
            <div class="selection-calendar">
              <div class="selection-weekdays">
                <div v-for="day in weekDays" :key="day" class="selection-weekday">{{ day }}</div>
              </div>
              <div class="selection-grid" :style="{ gridTemplateRows: `repeat(${selectionCalendarRows}, 1fr)` }">
                <div
                  v-for="(date, idx) in selectionDates"
                  :key="idx"
                  class="selection-day"
                  :class="{
                    'selected': isDateSelected(date.fullDate),
                    'has-shift': date.hasShift,
                    'other-month-date': !date.isCurrentMonth
                  }"
                  @click="toggleDateSelection(date.fullDate)"
                >
                  <span class="selection-day-number">{{ date.dayNumber }}</span>
                  <i v-if="isDateSelected(date.fullDate)" class="fas fa-check-circle check-icon"></i>
                  <i v-else-if="date.hasShift" class="fas fa-calendar-check shift-icon"></i>
                </div>
              </div>
            </div>
            <div class="selected-count">
              Выбрано дат: <strong>{{ manyShiftsData.selectedDates.length }}</strong>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <div class="footer-buttons-grid four-buttons">
            <button class="btn-success" @click="selectAllDatesInMonth">
              <i class="fas fa-check-double"></i>
              <span>Все</span>
            </button>
            <button class="btn-warning" @click="clearAllDates">
              <i class="fas fa-times"></i>
              <span>Очистить</span>
            </button>
            <button class="btn-primary" @click="saveManyShifts" :disabled="!manyShiftsData.hours || manyShiftsData.selectedDates.length === 0">
              <i class="fas fa-save"></i>
              <span>Добавить ({{ manyShiftsData.selectedDates.length }})</span>
            </button>
            <button class="btn-secondary" @click="closeAddManyModal">
              <i class="fas fa-times"></i>
              <span>Отмена</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Остальные модальные окна... -->
    <div v-if="showShiftModal" class="modal" @click.self="closeShiftModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <i class="fas fa-calendar-day"></i>
            {{ formatDateShort(selectedDay?.fullDate) }}
          </h3>
          <button class="modal-close" @click="closeShiftModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="shiftDetails" class="shift-details">
            <div class="stat-line">
              <span class="stat-label">Отработано:</span>
              <span class="stat-number">{{ shiftDetails.base_hours }} ч</span>
            </div>
            <div class="stat-line">
              <span class="stat-label">Заработано за часы:</span>
              <span class="stat-number">{{ formatNumber(shiftDetails.earned_hours) }} ₽</span>
            </div>
            <div class="stat-line">
              <span class="stat-label">Доплата за холод:</span>
              <span class="stat-number">{{ formatNumber(shiftDetails.earned_cold) }} ₽</span>
            </div>
            <div v-if="shiftDetails.earned_overtime" class="stat-line">
              <span class="stat-label">Переработка:</span>
              <span class="stat-number overtime">{{ formatNumber(shiftDetails.earned_overtime) }} ₽</span>
            </div>
            <div v-if="shiftDetails.award_amount" class="stat-line award-line">
              <span class="stat-label">🏆 Мотивация:</span>
              <span class="stat-number award">{{ formatNumber(shiftDetails.award_amount) }} ₽</span>
            </div>
            <div v-if="shiftDetails.count_operations" class="stat-line">
              <span class="stat-label">Кол-во операций:</span>
              <span class="stat-number">{{ shiftDetails.count_operations }}</span>
            </div>
            <div class="stat-line total-line">
              <span class="stat-label">💰 Всего:</span>
              <span class="stat-number total">{{ formatNumber(shiftDetails.earned) }} ₽</span>
            </div>
            <div class="currency-block">
              <div class="currency-header" @click="toggleShiftCurrency">
                <i class="fas" :class="showShiftCurrency ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
                <span>💱 В валюте:</span>
              </div>
              <div v-show="showShiftCurrency" class="currency-list">
                <div v-if="shiftDetails.valute?.dollar" class="currency-line">🇺🇸 Доллар: ${{ shiftDetails.valute.dollar }}</div>
                <div v-if="shiftDetails.valute?.euro" class="currency-line">🇪🇺 Евро: €{{ shiftDetails.valute.euro }}</div>
                <div v-if="shiftDetails.valute?.yena" class="currency-line">🇨🇳 Юань: ¥{{ shiftDetails.valute.yena }}</div>
                <div v-if="shiftDetails.valute?.som" class="currency-line">🇰🇬 Сом: {{ formatNumber(shiftDetails.valute.som) }}</div>
              </div>
            </div>
          </div>
          <div class="shift-actions">
            <div class="form-group">
              <label class="form-label">Количество часов</label>
              <input type="number" v-model.number="editHours" class="form-control" min="0" step="0.5" />
            </div>
            <div v-if="selectedDay?.hasShift" class="award-section">
              <div class="award-divider"></div>
              <div class="award-title">
                <i class="fas fa-trophy"></i>
                <span>Добавить мотивацию</span>
              </div>
              <div class="form-group">
                <label class="form-label">Количество операций:</label>
                <input type="number" v-model.number="operationsCount" class="form-control" min="0" placeholder="Введите количество операций" />
              </div>
              <button class="btn-award" @click="addAward" :disabled="!operationsCount">
                <i class="fas fa-gift"></i>
                Рассчитать мотивацию
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <div class="footer-buttons-grid three-buttons">
            <button class="btn-primary" @click="saveShift">
              <i class="fas fa-save"></i>
              <span>{{ selectedDay?.hasShift ? 'Обновить' : 'Создать' }}</span>
            </button>
            <button v-if="selectedDay?.hasShift" class="btn-danger" @click="deleteShift">
              <i class="fas fa-trash"></i>
              <span>Удалить</span>
            </button>
            <button class="btn-secondary" @click="closeShiftModal">
              <i class="fas fa-times"></i>
              <span>Отмена</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showSettingsModal" class="modal" @click.self="closeSettingsModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <i class="fas fa-cog"></i>
            Настройки оплаты
          </h3>
          <button class="modal-close" @click="closeSettingsModal">&times;</button>
        </div>
        <div class="modal-body">
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
          <div class="form-group">
            <label class="form-label">Стоимость операции</label>
            <input type="number" v-model.number="settings.price_award" class="form-control" step="0.1" />
          </div>
        </div>
        <div class="modal-footer">
          <div class="footer-buttons-grid three-buttons">
            <button class="btn-danger" @click="deleteSettings" v-if="hasSettings">
              <i class="fas fa-trash"></i>
              <span>Удалить</span>
            </button>
            <button class="btn-primary" @click="saveSettings">
              <i class="fas fa-save"></i>
              <span>Сохранить</span>
            </button>
            <button class="btn-secondary" @click="closeSettingsModal">
              <i class="fas fa-times"></i>
              <span>Отмена</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Замените модальное окно статистики за год на это: -->

    <div v-if="showYearStatsModal" class="modal" @click.self="closeYearStatsModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <i class="fas fa-chart-line"></i>
            Статистика за год
          </h3>
          <button class="modal-close" @click="closeYearStatsModal">&times;</button>
        </div>
        <div class="modal-body">
          <!-- Добавлен выбор года -->
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
            <div class="currency-block year-currency">
              <div class="currency-header" @click="toggleYearCurrency">
                <i class="fas" :class="showYearCurrency ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
                <span>💱 Заработано в валюте</span>
              </div>
              <div v-show="showYearCurrency" class="currency-list">
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
          <div class="footer-buttons-grid one-button">
            <button class="btn-secondary" @click="closeYearStatsModal">
              <i class="fas fa-times"></i>
              <span>Закрыть</span>
            </button>
          </div>
        </div>
      </div>
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
      price_award: 0
    })
    const hasSettings = ref(false)

    const showShiftModal = ref(false)
    const showSettingsModal = ref(false)
    const showAddManyModal = ref(false)
    const showYearStatsModal = ref(false)
    const selectedDay = ref(null)
    const shiftDetails = ref(null)
    const editHours = ref(0)
    const operationsCount = ref(0)
    const showShiftCurrency = ref(false)
    const showYearCurrency = ref(false)

    const openSections = ref({
      period1: true,
      period2: true,
      total: true
    })
    const openCurrency = ref({
      period1: false,
      period2: false,
      total: false
    })

    const selectionDate = ref(new Date())

    const manyShiftsData = ref({
      hours: 12,
      selectedDates: []
    })
    const selectedYear = ref(new Date().getFullYear())
    const availableYears = ref([])

    const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

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
             period.total_award > 0
    }

    const hasCurrencyData = (period) => {
      if (!period) return false
      return !!(period.dollar || period.euro || period.yena || period.som)
    }

    // Общая функция для обработки ошибок API
    const handleApiError = (error, defaultMessage = 'Произошла ошибка') => {
      console.error('API Error:', error)
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        
        if (Array.isArray(detail)) {
          // Формируем сообщение для каждого поля
          const errors = detail.map(err => {
            const field = err.loc?.filter(l => l !== 'body').join('.') || 'неизвестное поле'
            // Убираем префикс "Value error, " если он есть
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

    const loadShifts = async () => {
      try {
        const month = currentDate.value.getMonth() + 1
        const year = currentDate.value.getFullYear()
        const response = await apiService.getShiftsByMonth(month, year)
        shifts.value = response.result || []
      } catch (error) {
        handleApiError(error, 'Ошибка при загрузке смен')
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
      }
    }

    const loadYearStatistics = async () => {
      try {
        const year = currentDate.value.getFullYear()
        const response = await apiService.getYearlyStatistics(year)
        yearStats.value = response
        yearStatsYear.value = year
      } catch (error) {
        handleApiError(error, 'Ошибка при загрузке годовой статистики')
      }
    }

    const loadSettings = async () => {
      try {
        const response = await apiService.getTimesheetSettings()
        settings.value = {
          price_time: response.price_time || 0,
          price_overtime: response.price_overtime || 0,
          price_cold: response.price_cold || 0,
          price_award: response.price_award || 0
        }
        hasSettings.value = true
      } catch (error) {
        console.log('No settings found')
        hasSettings.value = false
      }
    }

    const showNotification = (message, type = 'success') => {
      const notification = document.createElement('div')
      notification.className = `notification notification-${type}`
      notification.innerHTML = `
        <div class="notification-content">
          <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
          <span>${message}</span>
        </div>
      `
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        cursor: pointer;
      `
      document.body.appendChild(notification)
      setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease'
        setTimeout(() => {
          if (document.body.contains(notification)) {
            document.body.removeChild(notification)
          }
        }, 300)
      }, 3000)
      notification.onclick = () => {
        notification.style.animation = 'slideOut 0.3s ease'
        setTimeout(() => {
          if (document.body.contains(notification)) {
            document.body.removeChild(notification)
          }
        }, 300)
      }
    }

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
          dayNumber: date,
          fullDate: fullDate,
          isCurrentMonth: false,
          isWeekend: isWeekendDay(fullDate),
          isToday: false,
          hasShift: false
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

        const dayObject = {
          dayNumber: i,
          fullDate: fullDate,
          isCurrentMonth: true,
          isWeekend: isWeekendDay(fullDate),
          isToday: fullDate.toDateString() === today.toDateString(),
          hasShift: !!shift,
          dateStr: dateStr
        }

        if (shift) {
          Object.assign(dayObject, shift)
        }

        days.push(dayObject)
      }

      const remainingCells = totalCells - days.length
      for (let i = 1; i <= remainingCells; i++) {
        const fullDate = new Date(year, month + 1, i)
        days.push({
          dayNumber: i,
          fullDate: fullDate,
          isCurrentMonth: false,
          isWeekend: isWeekendDay(fullDate),
          isToday: false,
          hasShift: false
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

      for (let i = startingDayOfWeek - 1; i > 0; i--) {
        const date = daysInPrevMonth - i + 1
        const fullDate = new Date(year, month - 1, date)
        const yearStr = fullDate.getFullYear()
        const monthStr = String(fullDate.getMonth() + 1).padStart(2, '0')
        const dayStr = String(fullDate.getDate()).padStart(2, '0')
        const dateStr = `${yearStr}-${monthStr}-${dayStr}`

        const hasShift = currentShifts.some(s => {
          const shiftDate = s.date ? s.date.split(' ')[0] : ''
          return shiftDate === dateStr
        })

        dates.push({
          dayNumber: date,
          fullDate: dateStr,
          hasShift: hasShift,
          isCurrentMonth: false
        })
      }

      for (let i = 1; i <= daysInMonth; i++) {
        const fullDate = new Date(year, month, i)
        const yearStr = fullDate.getFullYear()
        const monthStr = String(fullDate.getMonth() + 1).padStart(2, '0')
        const dayStr = String(fullDate.getDate()).padStart(2, '0')
        const dateStr = `${yearStr}-${monthStr}-${dayStr}`

        const hasShift = currentShifts.some(s => {
          const shiftDate = s.date ? s.date.split(' ')[0] : ''
          return shiftDate === dateStr
        })

        dates.push({
          dayNumber: i,
          fullDate: dateStr,
          hasShift: hasShift,
          isCurrentMonth: true
        })
      }

      const remainingCells = totalCells - dates.length
      for (let i = 1; i <= remainingCells; i++) {
        const fullDate = new Date(year, month + 1, i)
        const yearStr = fullDate.getFullYear()
        const monthStr = String(fullDate.getMonth() + 1).padStart(2, '0')
        const dayStr = String(fullDate.getDate()).padStart(2, '0')
        const dateStr = `${yearStr}-${monthStr}-${dayStr}`

        const hasShift = currentShifts.some(s => {
          const shiftDate = s.date ? s.date.split(' ')[0] : ''
          return shiftDate === dateStr
        })

        dates.push({
          dayNumber: i,
          fullDate: dateStr,
          hasShift: hasShift,
          isCurrentMonth: false
        })
      }

      return dates
    })

    const selectionMonthName = computed(() => {
      return selectionDate.value.toLocaleString('ru', { month: 'long' })
    })

    const selectionYear = computed(() => {
      return selectionDate.value.getFullYear()
    })

    const currentMonthName = computed(() => {
      return currentDate.value.toLocaleString('ru', { month: 'long' })
    })

    const currentYear = computed(() => {
      return currentDate.value.getFullYear()
    })

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

    const toggleSection = (section) => {
      openSections.value[section] = !openSections.value[section]
    }

    const toggleCurrency = (section) => {
      openCurrency.value[section] = !openCurrency.value[section]
    }

    const toggleShiftCurrency = () => {
      showShiftCurrency.value = !showShiftCurrency.value
    }

    const toggleYearCurrency = () => {
      showYearCurrency.value = !showYearCurrency.value
    }

    const isDateSelected = (date) => {
      return manyShiftsData.value.selectedDates.includes(date)
    }

    const toggleDateSelection = (date) => {
      const index = manyShiftsData.value.selectedDates.indexOf(date)
      if (index === -1) {
        manyShiftsData.value.selectedDates.push(date)
      } else {
        manyShiftsData.value.selectedDates.splice(index, 1)
      }
    }

    const selectAllDatesInMonth = () => {
      manyShiftsData.value.selectedDates = selectionDates.value.filter(d => d.isCurrentMonth).map(d => d.fullDate)
    }

    const clearAllDates = () => {
      manyShiftsData.value.selectedDates = []
    }

    const openShiftModal = async (day) => {
      if (!day.isCurrentMonth) return

      selectedDay.value = day
      editHours.value = day.base_hours || 0
      operationsCount.value = 0
      showShiftCurrency.value = false

      if (day.hasShift && day.day_id) {
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
      operationsCount.value = 0
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

    const addAward = async () => {
      if (!selectedDay.value?.day_id || !operationsCount.value) {
        showNotification('Введите количество операций', 'error')
        return
      }

      try {
        await apiService.addAward(selectedDay.value.day_id, operationsCount.value)
        const updatedShift = await apiService.getShiftById(selectedDay.value.day_id)
        shiftDetails.value = updatedShift
        await loadData()
        showNotification('Премия успешно добавлена', 'success')
      } catch (error) {
        handleApiError(error, 'Ошибка при добавлении премии')
      }
    }

    const openSettingsModal = () => {
      showSettingsModal.value = true
    }

    const closeSettingsModal = () => {
      showSettingsModal.value = false
    }

    const saveSettings = async () => {
      if (!settings.value.price_time) {
        showNotification('Цена за час обязательна для заполнения', 'error')
        return
      }

      try {
        await apiService.updateTimesheetSettings(settings.value)
        showNotification('Настройки сохранены', 'success')
        closeSettingsModal()
        await loadData()
      } catch (error) {
        handleApiError(error, 'Ошибка при сохранении настроек')
      }
    }

    const deleteSettings = async () => {
      if (confirm('Вы уверены, что хотите удалить настройки?')) {
        try {
          await apiService.deleteTimesheetSettings()
          settings.value = { price_time: 0, price_overtime: 0, price_cold: 0, price_award: 0 }
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

    const closeAddManyModal = () => {
      showAddManyModal.value = false
    }

    const saveManyShifts = async () => {
      if (!manyShiftsData.value.hours) {
        showNotification('Введите количество часов', 'error')
        return
      }
      if (manyShiftsData.value.selectedDates.length === 0) {
        showNotification('Выберите хотя бы одну дату', 'error')
        return
      }

      try {
        await apiService.addManyShifts(manyShiftsData.value.hours, manyShiftsData.value.selectedDates)
        showNotification('Смены успешно добавлены', 'success')
        closeAddManyModal()
        await loadData()
      } catch (error) {
        handleApiError(error, 'Ошибка при добавлении смен')
      }
    }

    const closeYearStatsModal = () => {
      showYearStatsModal.value = false
      yearStats.value = null
    }

    const loadData = async () => {
      await Promise.all([loadShifts(), loadStatistics(), loadSettings()])
    }

    const formatNumber = (num) => {
      if (!num && num !== 0) return '0'
      return num.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    const formatNumberShort = (num) => {
      if (!num && num !== 0) return '0'
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k'
      }
      return num.toLocaleString('ru-RU')
    }

    const formatDateShort = (date) => {
      if (!date) return ''
      const d = date instanceof Date ? date : new Date(date)
      return d.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    }

    const generateAvailableYears = () => {
      const currentYear = new Date().getFullYear()
      const years = []
      for (let i = currentYear - 10; i <= currentYear + 2; i++) {
        years.push(i)
      }
      availableYears.value = years
    }

    const loadYearStatisticsForYear = async (year) => {
      try {
        const response = await apiService.getYearlyStatistics(year)
        yearStats.value = response
      } catch (error) {
        console.error('Error loading year statistics:', error)
        yearStats.value = null
        if (error.response?.status === 404) {
          return
        }
        handleApiError(error, 'Ошибка при загрузке годовой статистики')
      }
    }

    const openYearStatsModal = async () => {
      generateAvailableYears()
      selectedYear.value = currentDate.value.getFullYear()
      await loadYearStatisticsForYear(selectedYear.value)
      showYearStatsModal.value = true
    }

    const onYearChange = async () => {
      await loadYearStatisticsForYear(selectedYear.value)
    }

    const prevYear = async () => {
      selectedYear.value = selectedYear.value - 1
      await loadYearStatisticsForYear(selectedYear.value)
    }

    const nextYear = async () => {
      selectedYear.value = selectedYear.value + 1
      await loadYearStatisticsForYear(selectedYear.value)
    }

    const addNotificationStyles = () => {
      if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style')
        style.id = 'notification-styles'
        style.textContent = `
          @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
          }
          @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
          }
          .notification {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin-bottom: 10px;
            min-width: 300px;
            max-width: 400px;
          }
          .notification-content {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
          }
          .notification-success { border-left: 4px solid #10b981; }
          .notification-success i { color: #10b981; }
          .notification-error { border-left: 4px solid #ef4444; }
          .notification-error i { color: #ef4444; }
          .notification-info { border-left: 4px solid #3b82f6; }
          .notification-info i { color: #3b82f6; }
          @media (max-width: 768px) {
            .notification {
              min-width: auto;
              width: calc(100% - 40px);
              max-width: none;
            }
          }
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
      currentDate,
      shifts,
      monthlyStats,
      yearStats,
      yearStatsYear,
      settings,
      hasSettings,
      showShiftModal,
      showSettingsModal,
      showAddManyModal,
      showYearStatsModal,
      selectedDay,
      shiftDetails,
      editHours,
      operationsCount,
      showShiftCurrency,
      showYearCurrency,
      openSections,
      openCurrency,
      manyShiftsData,
      selectionDate,
      weekDays,
      calendarDays,
      calendarRows,
      selectionDates,
      selectionCalendarRows,
      selectionMonthName,
      selectionYear,
      currentMonthName,
      currentYear,
      previousMonth,
      nextMonth,
      goToToday,
      prevSelectionMonth,
      nextSelectionMonth,
      toggleSection,
      toggleCurrency,
      toggleShiftCurrency,
      toggleYearCurrency,
      isDateSelected,
      toggleDateSelection,
      selectAllDatesInMonth,
      clearAllDates,
      openShiftModal,
      closeShiftModal,
      saveShift,
      deleteShift,
      addAward,
      openSettingsModal,
      closeSettingsModal,
      saveSettings,
      deleteSettings,
      openAddManyModal,
      closeAddManyModal,
      saveManyShifts,
      openYearStatsModal,
      closeYearStatsModal,
      formatNumber,
      formatNumberShort,
      formatDateShort,
      hasPeriodData,
      hasCurrencyData,
      selectedYear,
      availableYears,
      prevYear,
      nextYear,
      onYearChange
    }
  }
}
</script>

<style scoped>
:root {
  --radius: 8px;
}

.timesheets-container {
  padding: 0.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.5rem;
  color: #1e293b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.month-navigation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.btn-nav {
  background: #f0f9ff;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: #0284c7;
}

.btn-nav:hover {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  color: white;
  transform: scale(1.05);
}

.current-month h2 {
  font-size: 1.25rem;
  text-transform: capitalize;
  margin: 0;
  color: #1e293b;
}

.btn-today {
  padding: 0.5rem 1rem;
  background: #f0f9ff;
  color: #0284c7;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.3s;
}

.btn-today:hover {
  background: #0284c7;
  color: white;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.weekday {
  text-align: center;
  padding: 0.75rem;
  font-weight: 600;
  background: #fef3c7;
  border-radius: var(--radius);
  color: #92400e;
}

.weekday.weekend {
  background: #fee2e2;
  color: #dc2626;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.calendar-day {
  border-radius: var(--radius);
  padding: 0.5rem;
  min-height: 80px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e5e7eb;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: white;
}

.calendar-day:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.calendar-day.other-month {
  opacity: 0;
  background: transparent;
  border: 1px solid transparent;
  cursor: default;
  pointer-events: none;
}

.calendar-day.other-month .day-number {
  visibility: hidden;
}

.calendar-day.weekend-day {
  background: #fee2e2;
  border-color: #fecaca;
  color: #991b1b;
}

.calendar-day.weekend-with-shift {
  background: #8B0000;
  color: white;
}

.calendar-day.has-shift {
  background: linear-gradient(135deg, #3b82f6 0%, #000080 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(59,130,246,0.3);
}

.calendar-day.today {
  border: 2px solid #f59e0b;
  box-shadow: 0 0 0 2px #fef3c7;
}

.day-number {
  font-weight: 700;
  font-size: 1.125rem;
  margin-bottom: 0.25rem;
}

.day-earned {
  font-size: 0.75rem;
  font-weight: 500;
  text-align: right;
  margin-top: auto;
}

.day-empty {
  text-align: right;
  color: #9ca3af;
  margin-top: auto;
}

.stats-container {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1.5rem;
}

.stat-card {
  flex: 1;
  min-width: 280px;
  background: white;
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stat-card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  background: #f1f5f9;
  transition: background 0.3s;
}

.stat-card-header:hover {
  background: #e2e8f0;
}

.stat-card-header i {
  color: #3b82f6;
  font-size: 0.875rem;
}

.stat-card-header h3 {
  flex: 1;
  font-size: 0.9rem;
  margin: 0;
  font-weight: 600;
  color: #1e293b;
}

.total-earned {
  font-weight: 700;
  color: #10b981;
  font-size: 1rem;
}

.stat-card-body {
  padding: 0.75rem;
}

.stat-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-line:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
}

.stat-number {
  font-weight: 600;
  font-size: 0.85rem;
  color: #1e293b;
}

.stat-number.award {
  color: #d97706;
}

.stat-number.overtime {
  color: #dc2626;
}

.stat-number.total {
  color: #10b981;
  font-size: 1rem;
}

.award-line {
  background: #fef3c7;
  margin: 0.25rem 0;
  padding: 0.5rem;
  border-radius: var(--radius);
}

.total-line {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 2px solid #e5e7eb;
}

.total-card .stat-card-header {
  background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
  color: white;
}

.total-card .stat-card-header i,
.total-card .total-earned {
  color: white;
}

.currency-block {
  margin-top: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
}

.currency-header {
  cursor: pointer;
  padding: 0.3rem 0;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #3b82f6;
  font-size: 0.8rem;
  font-weight: 500;
}

.currency-header:hover {
  opacity: 0.7;
}

.currency-list {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.currency-line {
  font-size: 0.75rem;
  padding: 0.3rem 0.5rem;
  background: #f1f5f9;
  border-radius: var(--radius);
}

.selection-calendar {
  background: white;
  border-radius: var(--radius);
  padding: 1rem;
  border: 1px solid #e5e7eb;
}

.selection-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.selection-weekday {
  text-align: center;
  padding: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  background: #fef3c7;
  border-radius: var(--radius);
  color: #92400e;
}

.selection-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
}

.selection-day {
  position: relative;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e5e7eb;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  background: white;
  color: #1e293b;
}

.selection-day:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.selection-day.has-shift {
  background: #dbeafe;
  border-color: #3b82f6;
  color: #1e40af;
}

.selection-day.selected {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.selection-day.other-month-date {
  opacity: 0.3;
  background: #f3f4f6;
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
  font-size: 0.7rem;
}

.shift-icon {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 0.6rem;
  color: #3b82f6;
}

.selection-day.selected .shift-icon {
  color: white;
}

.selected-count {
  margin-top: 0.75rem;
  padding: 0.5rem;
  background: #f1f5f9;
  border-radius: var(--radius);
  text-align: center;
  font-size: 0.875rem;
}

.month-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0.5rem;
  background: #f1f5f9;
  border-radius: var(--radius);
}

.btn-month-nav {
  background: white;
  border: 1px solid #e5e7eb;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.btn-month-nav:hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
  transform: scale(1.05);
}

.selected-month {
  font-size: 1rem;
  font-weight: 600;
  min-width: 150px;
  text-align: center;
  text-transform: capitalize;
  color: #1e293b;
}

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
}

.modal-content {
  background: white;
  border-radius: var(--radius);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  padding: 0px;
}

.modal-content.large {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
}

.modal-close:hover {
  color: #1e293b;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f8fafc;
  display: flex;
  justify-content: center;
}

.footer-buttons-grid {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

.footer-buttons-grid.one-button {
  justify-content: center;
}

.footer-buttons-grid.one-button button {
  min-width: 120px;
}

.footer-buttons-grid.three-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
}

.footer-buttons-grid.three-buttons button {
  min-width: 120px;
}

.footer-buttons-grid.four-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  width: 100%;
}

.footer-buttons-grid.four-buttons button {
  width: 100%;
}

.btn, button:not(.btn-nav):not(.btn-month-nav):not(.btn-award):not(.modal-close) {
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

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}

.btn-secondary {
  background: #8B0000;
  color: white;
}

.btn-secondary:hover {
  background: #FF0000;
  transform: translateY(-1px);
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover {
  background: #059669;
  transform: translateY(-1px);
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover {
  background: #d97706;
  transform: translateY(-1px);
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.btn-info {
  background: #06b6d4;
  color: white;
}

.btn-info:hover {
  background: #0891b2;
  transform: translateY(-1px);
}

.btn-award {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
}

.btn-award:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245,158,11,0.3);
}

.btn-award:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.shift-details {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: var(--radius);
}

.shift-actions {
  margin-top: 1rem;
}

.award-section {
  margin-top: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%);
  border-radius: var(--radius);
  border: 1px solid #fde68a;
}

.award-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #fde68a, transparent);
  margin: -1rem -1rem 1rem -1rem;
}

.award-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
  color: #d97706;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: #1e293b;
}

.form-label.required:after {
  content: " *";
  color: #ef4444;
}

.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: var(--radius);
  font-size: 0.875rem;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.1);
}

.year-stats {
  padding: 0.5rem;
}

.stat-big-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f1f5f9;
  border-radius: var(--radius);
  margin-bottom: 1rem;
}

.stat-icon-large {
  width: 60px;
  height: 60px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  color: #3b82f6;
}

.stat-info-large {
  flex: 1;
}

.stat-value-large {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
}

.year-currency {
  margin-top: 1rem;
}

.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  animation: slideIn 0.3s ease;
  cursor: pointer;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.notification-success {
  border-left: 4px solid #10b981;
}

.notification-success i {
  color: #10b981;
}

.notification-error {
  border-left: 4px solid #ef4444;
}

.notification-error i {
  color: #ef4444;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

@media (max-width: 768px) {
  .timesheets-container {
    padding: 0.25rem;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title {
    text-align: center;
  }

  .header-actions {
    flex-direction: column;
  }

  .header-actions .btn {
    width: 100%;
    justify-content: center;
  }

  .stats-container {
    flex-direction: column;
  }

  .stat-card {
    min-width: auto;
  }

  .calendar-day {
    min-height: 65px;
  }

  .day-number {
    font-size: 0.875rem;
  }

  .day-earned {
    font-size: 0.625rem;
  }

  .footer-buttons-grid.three-buttons {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
    width: 100%;
  }

  .footer-buttons-grid.three-buttons button {
    width: 100%;
  }

  .footer-buttons-grid.four-buttons {
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .calendar-day {
    min-height: 55px;
    padding: 0.25rem;
  }

  .day-earned {
    font-size: 0.5rem;
  }

  .weekday {
    font-size: 0.625rem;
    padding: 0.35rem;
  }
}

.year-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 0.5rem;
  background: #f1f5f9;
  border-radius: var(--radius);
}

.btn-year-nav {
  background: white;
  border: 1px solid #e5e7eb;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.btn-year-nav:hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
  transform: scale(1.05);
}

.year-select {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  border: 1px solid #e5e7eb;
  border-radius: var(--radius);
  background: white;
  color: #1e293b;
  cursor: pointer;
  outline: none;
  min-width: 100px;
  text-align: center;
}

.year-select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.1);
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

.no-data i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #cbd5e1;
}

.no-data p {
  margin: 0;
  font-size: 1rem;
}
</style>
