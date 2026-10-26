<template>
  <div class="card insights-widget">
    <div class="card-header">
      <div class="header-title-group">
        <div class="title-icon-wrapper">
          <i class="fas fa-lightbulb"></i>
        </div>
        <h3 class="card-title">Инсайты</h3>
      </div>
      <div class="header-actions">
        <button class="btn-icon" @click="showSettings = true" title="Настройки инсайтов">
          <i class="fas fa-sliders-h"></i>
        </button>
      </div>
    </div>

    <div v-if="loading" class="widget-loading">
      <i class="fas fa-spinner fa-spin"></i>
    </div>

    <div v-else-if="insights.length === 0" class="widget-empty">
      <div class="empty-icon-wrapper">
        <i class="fas fa-check-circle"></i>
      </div>
      <p>Пока все отлично!<br><span>Новых инсайтов нет.</span></p>
    </div>

    <div v-else class="insights-list">
      <div
        v-for="item in visibleInsights"
        :key="item.id"
        class="insight-item"
        :class="`severity-${item.severity}`"
        @click="openInsight(item)"
      >
        <div class="insight-icon">
          <i :class="getIcon(item.insight_type)"></i>
        </div>
        <div class="insight-body">
          <div class="insight-title">{{ item.title }}</div>
          <div class="insight-message">{{ item.message }}</div>
          <div class="insight-date">
            <i class="far fa-clock"></i> {{ formatDate(item.created_at) }}
          </div>
        </div>
        <button
          class="insight-dismiss"
          @click.stop="dismiss(item.id)"
          title="Скрыть"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>

    <!-- Модалка настроек инсайтов -->
    <div v-if="showSettings" class="modal" @click.self="showSettings = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Настройки инсайтов</h3>
          <button class="modal-close" @click="showSettings = false">&times;</button>
        </div>

        <form @submit.prevent="saveInsightSettings">
          <div class="form-group">
            <label class="form-label required">Порог мелких трат (₽)</label>
            <input
              type="number"
              v-model.number="settingsData.small_expense_threshold"
              class="form-control"
              step="any"
              min="1"
              required
            >
            <small class="form-hint">Покупки на меньшую сумму считаются «кофе и перекусами»</small>
          </div>

          <div class="form-group">
            <label class="form-label required">Порог простаивающих денег (₽)</label>
            <input
              type="number"
              v-model.number="settingsData.idle_cash_threshold"
              class="form-control"
              step="any"
              min="1"
              required
            >
            <small class="form-hint">Если на счетах больше этой суммы, придет совет открыть вклад</small>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showSettings = false">Отмена</button>
            <button type="submit" class="btn btn-primary" :disabled="savingSettings">
              <i v-if="savingSettings" class="fas fa-spinner fa-spin"></i>
              Сохранить
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api.js'

export default {
  name: 'InsightsWidget',
  setup() {
    const insights = ref([])
    const loading = ref(true)
    const router = useRouter()

    // Состояние для настроек
    const showSettings = ref(false)
    const savingSettings = ref(false)
    const settingsData = ref({
      small_expense_threshold: 300,
      idle_cash_threshold: 50000
    })

    const visibleInsights = computed(() => insights.value.slice(0, 3))

    const loadInsights = async () => {
      loading.value = true
      try {
        const data = await apiService.getInsights(true)
        insights.value = Array.isArray(data) ? data : (data.results || [])
      } catch (e) {
        console.error('Load insights error:', e)
        insights.value = []
      } finally {
        loading.value = false
      }
    }

    const loadSettings = async () => {
      try {
        const data = await apiService.getInsightSettings()
        if (data) settingsData.value = { ...settingsData.value, ...data }
      } catch (e) {
        console.error('Load settings error:', e)
      }
    }

    const saveInsightSettings = async () => {
      savingSettings.value = true
      try {
        await apiService.updateInsightSettings(settingsData.value)
        showSettings.value = false
      } catch (e) {
        console.error('Save settings error:', e)
        alert('Не удалось сохранить настройки')
      } finally {
        savingSettings.value = false
      }
    }

    const dismiss = async (id) => {
      try {
        await apiService.dismissInsight(id)
        insights.value = insights.value.filter(i => i.id !== id)
      } catch (e) {
        console.error('Dismiss insight error:', e)
      }
    }

    const openInsight = (item) => {
      if (item.action_url) router.push(item.action_url)
    }

    const getIcon = (type) => ({
      category_spike: 'fas fa-chart-line',
      subscription_increase: 'fas fa-arrow-up',
      transaction_duplicate: 'fas fa-copy',
      salary_spike: 'fas fa-glass-cheers',
      hidden_leak: 'fas fa-coffee',
      budget_overspend: 'fas fa-chart-pie',
      cash_gap: 'fas fa-money-bill-wave',
      deposit_forecast: 'fas fa-seedling',
      credit_card_grace: 'fas fa-hourglass-half',
      savings_improved: 'fas fa-piggy-bank',
      idle_cash: 'fas fa-hand-holding-usd',
      debt_vs_deposit: 'fas fa-balance-scale',
      budget_reallocation: 'fas fa-exchange-alt',
    }[type] || 'fas fa-lightbulb')

    const formatDate = (iso) => {
      if (!iso) return ''
      return new Date(iso).toLocaleString('ru-RU', {
        day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit',
      })
    }

    onMounted(() => {
      loadInsights()
      loadSettings()
    })

    return {
      insights,
      loading,
      visibleInsights,
      dismiss,
      openInsight,
      getIcon,
      formatDate,
      showSettings,
      savingSettings,
      settingsData,
      saveInsightSettings
    }
  }
}
</script>

<style scoped>
/* ============================================================
   СОВРЕМЕННЫЙ ДИЗАЙН (SOFT UI)
   ============================================================ */
.insights-widget {
  margin-bottom: 1.5rem;
  background: var(--white);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

/* ===== Header ===== */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  border-bottom: none;
  padding-bottom: 0;
}

.header-title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-icon-wrapper {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: rgba(251, 191, 36, 0.15); /* Мягкий желтый фон */
  color: #fbbf24;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.card-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--dark-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: var(--light-color);
  color: var(--gray-color);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: var(--gray-color);
  color: var(--white);
  transform: rotate(90deg);
}

/* ===== Состояния ===== */
.widget-loading {
  text-align: center;
  padding: 2rem;
  color: var(--gray-color);
}

.widget-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem 1rem;
  background: var(--light-color);
  border-radius: 12px;
}

.empty-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.15);
  color: var(--secondary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.widget-empty p {
  margin: 0;
  color: var(--dark-color);
  font-weight: 600;
  line-height: 1.3;
}

.widget-empty p span {
  font-weight: 400;
  color: var(--gray-color);
  font-size: 0.85rem;
}

/* ===== Список инсайтов ===== */
.insights-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.insight-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 1rem;
  border-radius: 12px;
  background: var(--white);
  border: 1px solid var(--light-color);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

/* Эффект парения при наведении */
.insight-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.06);
  border-color: transparent;
}

/* Цветная полоска слева */
.insight-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: 4px 0 0 4px;
}

.insight-item.severity-info::before { background: #3b82f6; }
.insight-item.severity-warning::before { background: #f59e0b; }
.insight-item.severity-critical::before { background: #ef4444; }

/* Иконка */
.insight-icon {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: transform 0.3s;
}

.insight-item:hover .insight-icon {
  transform: scale(1.1);
}

/* Фоны иконок в зависимости от severity */
.insight-item.severity-info .insight-icon {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}
.insight-item.severity-warning .insight-icon {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}
.insight-item.severity-critical .insight-icon {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Текст */
.insight-body {
  flex: 1;
  min-width: 0;
  padding-top: 0.15rem;
}

.insight-title {
  font-weight: 700;
  color: var(--dark-color);
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
  line-height: 1.3;
}

.insight-message {
  font-size: 0.85rem;
  color: var(--gray-color);
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.insight-date {
  font-size: 0.7rem;
  color: var(--gray-color);
  display: flex;
  align-items: center;
  gap: 0.35rem;
  opacity: 0.8;
}

/* Кнопка закрытия */
.insight-dismiss {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: transparent;
  border: none;
  color: var(--gray-color);
  font-size: 0.8rem;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s;
}

.insight-item:hover .insight-dismiss {
  opacity: 1;
}

.insight-dismiss:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

/* ============================================================
   МОДАЛКА НАСТРОЕК (осталась без изменений, только чуть округлили)
   ============================================================ */
.modal {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 1rem; box-sizing: border-box;
  backdrop-filter: blur(4px); /* Легкое размытие фона */
}

.modal-content {
  background: var(--white);
  border-radius: 16px;
  padding: 1.5rem;
  width: 100%; max-width: 450px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  margin: 0; color: var(--dark-color); font-size: 1.25rem; font-weight: 700;
}

.modal-close {
  background: none; border: none; font-size: 1.5rem;
  cursor: pointer; color: var(--gray-color);
}

.modal-close:hover { color: var(--dark-color); }

.form-group { margin-bottom: 1.25rem; }

.form-label {
  display: block; margin-bottom: 0.5rem;
  font-size: 0.9rem; font-weight: 600; color: var(--dark-color);
}

.form-label.required::after {
  content: " *"; color: var(--danger-color);
}

.form-control {
  width: 100%; padding: 0.75rem;
  border: 2px solid var(--light-color);
  border-radius: 10px;
  background: var(--white); color: var(--dark-color);
  font-size: 1rem; box-sizing: border-box;
  transition: all 0.2s;
}

.form-control:focus {
  outline: none; border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.form-hint {
  display: block; font-size: 0.75rem;
  color: var(--gray-color); margin-top: 0.35rem;
}

.modal-footer {
  display: flex; justify-content: flex-end; gap: 1rem;
  margin-top: 2rem; padding-top: 1.25rem;
  border-top: 1px solid var(--light-color);
}

.btn {
  padding: 0.65rem 1.25rem; border: none; border-radius: 10px;
  cursor: pointer; font-size: 0.95rem; font-weight: 600;
  transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.5rem;
}

.btn:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-primary {
  background: var(--primary-color); color: white;
}
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }

.btn-secondary {
  background: var(--light-color); color: var(--dark-color);
}
.btn-secondary:hover { background: var(--gray-color); color: white; }
</style>