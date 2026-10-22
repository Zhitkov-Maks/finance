<template>
  <div class="card insights-widget" v-if="insights.length > 0 || loading">
    <div class="card-header">
      <h3 class="card-title">
        <i class="fas fa-lightbulb"></i> Инсайты
      </h3>
    </div>

    <div v-if="loading" class="widget-loading">
      <i class="fas fa-spinner fa-spin"></i>
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
          <div class="insight-date">{{ formatDate(item.created_at) }}</div>
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
    }[type] || 'fas fa-lightbulb')

    const formatDate = (iso) => {
      if (!iso) return ''
      return new Date(iso).toLocaleString('ru-RU', {
        day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit',
      })
    }

    onMounted(loadInsights)

    return { insights, loading, visibleInsights, dismiss, openInsight, getIcon, formatDate }
  }
}
</script>

<style scoped>
.insights-widget { margin-bottom: 1.5rem; }

.widget-loading { text-align: center; padding: 2rem; color: var(--gray-color); }

.insights-list { display: flex; flex-direction: column; gap: 0.5rem; }

.insight-item {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  padding: 0.75rem;
  border-radius: var(--radius);
  background: var(--light-color);
  border-left: 3px solid transparent;
  cursor: pointer;
  transition: filter 0.2s;
}
.insight-item:hover { filter: brightness(0.95); }

/* Цветная полоска слева по severity */
.insight-item.severity-info { border-left-color: #3b82f6; }
.insight-item.severity-warning { border-left-color: #f59e0b; }
.insight-item.severity-critical { border-left-color: #ef4444; }

.insight-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  background: var(--white);
  color: var(--primary-color);
}
.insight-item.severity-warning .insight-icon { color: #f59e0b; }
.insight-item.severity-critical .insight-icon { color: #ef4444; }

.insight-body { flex: 1; min-width: 0; }
.insight-title {
  font-weight: 600;
  color: var(--dark-color);
  font-size: 0.9rem;
  margin-bottom: 0.2rem;
}
.insight-message {
  font-size: 0.8rem;
  color: var(--gray-color);
  line-height: 1.4;
  margin-bottom: 0.25rem;
}
.insight-date { font-size: 0.7rem; color: var(--gray-color); }

.insight-dismiss {
  background: transparent;
  border: none;
  color: var(--gray-color);
  font-size: 0.85rem;
  padding: 0.25rem;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}
.insight-dismiss:hover { color: var(--danger-color); background: rgba(239, 68, 68, 0.1); }
</style>