<template>
  <div class="notifications-page">
    <div class="page-header">
      <h1>Уведомления</h1>

      <div class="header-actions">
        <button
          v-if="hasRead"
          @click="clearRead"
          class="btn btn-outline-danger"
          :disabled="clearing"
          title="Удалить все прочитанные"
        >
          <i class="fas fa-broom"></i> Очистить
        </button>
        <button
          v-if="hasUnread"
          @click="markAllRead"
          class="btn btn-secondary"
          :disabled="markingAll"
        >
          <i class="fas fa-check-double"></i>
          {{ markingAll ? 'Отмечаем...' : 'Прочитать все' }}
        </button>
      </div>
    </div>

    <!-- Push-подписка -->
    <div v-if="pushSupported" class="push-card">
      <div class="push-info">
        <i class="push-icon fas" :class="subscribed ? 'fa-bell' : 'fa-bell-slash'"></i>
        <div>
          <div class="push-title">
            {{ subscribed ? 'Push-уведомления включены' : 'Push-уведомления выключены' }}
          </div>
          <div class="push-hint">
            {{ subscribed ? 'Вы получаете уведомления о платежах и превышении бюджета' : 'Подпишитесь, чтобы не пропустить важные события' }}
          </div>
        </div>
      </div>
      <button @click="togglePush" class="btn" :class="subscribed ? 'btn-secondary' : 'btn-primary'" :disabled="pushLoading">
        <i class="fas" :class="pushLoading ? 'fa-spinner fa-spin' : (subscribed ? 'fa-bell-slash' : 'fa-bell')"></i>
        {{ pushLoading ? 'Обработка...' : (subscribed ? 'Отписаться' : 'Подписаться') }}
      </button>
    </div>
    <div v-else class="push-unsupported">
      <i class="fas fa-info-circle"></i>
      Браузер не поддерживает push-уведомления. На iPhone добавьте приложение на главный экран.
    </div>

    <!-- Настройки -->
    <div class="card settings-card">
      <div class="settings-header" @click="settingsOpen = !settingsOpen">
        <h3><i class="fas fa-cog"></i> Настройки уведомлений</h3>
        <i class="fas" :class="settingsOpen ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
      </div>

      <div v-if="settingsOpen" class="settings-body">
        <div class="setting-row">
          <label class="setting-label">
            <input type="checkbox" v-model="prefs.budget_alerts" @change="savePreferences" />
            Уведомления о бюджетах
          </label>
        </div>
        <div class="setting-row">
          <label class="setting-label">
            <input type="checkbox" v-model="prefs.payment_alerts" @change="savePreferences" />
            Уведомления о регулярных платежах
          </label>
        </div>
        <div class="setting-row">
          <label class="setting-label">
            <input type="checkbox" v-model="prefs.insight_alerts" @change="savePreferences" />
            Уведомления об инсайтах
          </label>
        </div>
        <div class="setting-row">
          <label class="setting-label">За сколько дней до платежа:</label>
          <input type="number" v-model.number="prefs.payment_days_before" min="0" max="30" @change="savePreferences" class="form-control short-input" />
        </div>
        <div class="setting-row">
          <label class="setting-label">Порог предупреждения о бюджете (%):</label>
          <input type="number" v-model.number="prefs.budget_warning_threshold" min="1" max="100" @change="savePreferences" class="form-control short-input" />
        </div>
        <div v-if="prefsSaved" class="prefs-saved">
          <i class="fas fa-check"></i> Сохранено
        </div>
      </div>
    </div>

    <!-- Фильтр -->
    <div class="filter-tabs">
      <button class="tab-btn" :class="{ active: !unreadOnly }" @click="setFilter(false)">
        Все
      </button>
      <button class="tab-btn" :class="{ active: unreadOnly }" @click="setFilter(true)">
        Непрочитанные
        <span v-if="unreadCount" class="tab-badge">{{ unreadCount }}</span>
      </button>
    </div>

    <!-- Состояния загрузки -->
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Загрузка...</p>
    </div>

    <div v-else-if="notifications.length === 0" class="empty-state">
      <i class="fas fa-bell-slash"></i>
      <p>{{ unreadOnly ? 'Нет непрочитанных уведомлений' : 'У вас пока нет уведомлений' }}</p>
    </div>

    <!-- Список уведомлений -->
    <div v-else class="notifications-list">
      <div
        v-for="notif in notifications"
        :key="notif.id"
        class="notification-item"
        :class="{ unread: !notif.is_read }"
      >
        <div class="notification-icon" @click="markRead(notif)" :class="getIconClass(notif.notification_type)">
          <i :class="getIcon(notif.notification_type)"></i>
        </div>

        <div class="notification-body" @click="markRead(notif)">
          <div class="notification-title">
            <span class="notification-title-text">{{ notif.title }}</span>
            <span v-if="!notif.is_read" class="unread-dot"></span>
          </div>
          <div class="notification-message">{{ notif.message }}</div>
          <div class="notification-date">{{ formatDateTime(notif.created_at) }}</div>
        </div>

        <!-- Кнопка удаления -->
        <button @click.stop="deleteOne(notif)" class="delete-btn" title="Удалить">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>

    <!-- Пагинация (Загрузить ещё) -->
    <div v-if="hasMore" class="pagination-container">
      <button @click="loadMore" class="btn btn-secondary" :disabled="loadingMore">
        <i v-if="loadingMore" class="fas fa-spinner fa-spin"></i>
        {{ loadingMore ? 'Загрузка...' : 'Загрузить ещё' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/api.js'
import {
  isPushSupported,
  subscribeToPush,
  unsubscribeFromPush,
  getCurrentSubscription,
} from '../services/pushService.js'
import { notificationStore } from '../stores/notifications.js'

export default {
  name: 'NotificationsView',
  setup() {
    const notifications = ref([])
    const loading = ref(true)
    const unreadOnly = ref(false)

    // Действия
    const markingAll = ref(false)
    const clearing = ref(false)

    // Пагинация
    const currentPage = ref(1)
    const hasMore = ref(false)
    const loadingMore = ref(false)

    // Настройки
    const settingsOpen = ref(false)
    const prefsSaved = ref(false)
    const prefs = ref({
      push_enabled: true,
      budget_alerts: true,
      payment_alerts: true,
      insight_alerts: true,
      payment_days_before: 1,
      budget_warning_threshold: 80,
    })

    // Push
    const pushLoading = ref(false)
    const subscribed = ref(false)
    const pushSupported = isPushSupported()

    // Вычисляемые
    const unreadCount = computed(() => notifications.value.filter((n) => !n.is_read).length)
    const hasUnread = computed(() => unreadCount.value > 0)
    const hasRead = computed(() => notifications.value.some((n) => n.is_read))

    // ---------- Загрузка данных ----------
    const loadNotifications = async (page = 1, append = false) => {
      if (page === 1) loading.value = true
      else loadingMore.value = true

      try {
        const data = await apiService.getNotifications(unreadOnly.value, page)
        const items = Array.isArray(data) ? data : (data.results || [])
        hasMore.value = data.next !== undefined ? !!data.next : false

        if (append) {
          notifications.value.push(...items)
        } else {
          notifications.value = items
          currentPage.value = 1
        }

        await notificationStore.refreshUnread()
      } catch (e) {
        console.error('Load notifications error:', e)
        if (!append) notifications.value = []
      } finally {
        loading.value = false
        loadingMore.value = false
      }
    }

    const loadMore = () => {
      currentPage.value++
      loadNotifications(currentPage.value, true)
    }

    const loadPreferences = async () => {
      try {
        const data = await apiService.getNotificationPreferences()
        if (data) prefs.value = { ...prefs.value, ...data }
      } catch (e) {
        console.error('Load prefs error:', e)
      }
    }

    const checkSubscription = async () => {
      const sub = await getCurrentSubscription()
      subscribed.value = !!sub
    }

    // ---------- Действия ----------
    const markRead = async (notif) => {
      if (notif.is_read) return
      try {
        await apiService.markNotificationRead(notif.id)
        notif.is_read = true
        notificationStore.decrement()

        if (unreadOnly.value) {
          notifications.value = notifications.value.filter((n) => n.id !== notif.id)
        }
      } catch (e) {
        console.error('Mark read error:', e)
      }
    }

    const markAllRead = async () => {
      markingAll.value = true
      try {
        await apiService.markAllNotificationsRead()
        notifications.value.forEach((n) => (n.is_read = true))
        notificationStore.clear()
        if (unreadOnly.value) notifications.value = []
      } catch (e) {
        console.error('Mark all read error:', e)
        alert('Ошибка при прочтении всех')
      } finally {
        markingAll.value = false
      }
    }

    const deleteOne = async (notif) => {
      try {
        await apiService.deleteNotification(notif.id)
        notifications.value = notifications.value.filter((n) => n.id !== notif.id)
        if (!notif.is_read) notificationStore.decrement()
      } catch (e) {
        console.error('Delete error:', e)
        alert('Не удалось удалить уведомление')
      }
    }

    const clearRead = async () => {
      if (!confirm('Удалить все прочитанные уведомления?')) return
      clearing.value = true
      try {
        await apiService.clearReadNotifications()
        notifications.value = notifications.value.filter((n) => !n.is_read)
      } catch (e) {
        console.error('Clear read error:', e)
        alert('Ошибка при очистке')
      } finally {
        clearing.value = false
      }
    }

    const setFilter = (val) => {
      if (unreadOnly.value === val) return
      unreadOnly.value = val
      loadNotifications(1, false)
    }

    // ---------- Настройки и Push ----------
    const savePreferences = async () => {
      try {
        await apiService.updateNotificationPreferences({
          push_enabled: prefs.value.push_enabled,
          budget_alerts: prefs.value.budget_alerts,
          payment_alerts: prefs.value.payment_alerts,
          insight_alerts: prefs.value.insight_alerts,
          payment_days_before: prefs.value.payment_days_before,
          budget_warning_threshold: prefs.value.budget_warning_threshold,
        })
        prefsSaved.value = true
        setTimeout(() => (prefsSaved.value = false), 1500)
      } catch (e) {
        console.error('Save prefs error:', e)
        alert('Не удалось сохранить настройки')
      }
    }

    const togglePush = async () => {
      pushLoading.value = true
      try {
        if (subscribed.value) {
          const sub = await getCurrentSubscription()
          await unsubscribeFromPush(sub?.endpoint)
          subscribed.value = false
        } else {
          await subscribeToPush()
          subscribed.value = true
          prefs.value.push_enabled = true
          await savePreferences()
        }
      } catch (e) {
        console.error('Push toggle error:', e)
        alert(e.message || 'Не удалось изменить подписку')
      } finally {
        pushLoading.value = false
      }
    }

    // ---------- Утилиты ----------
    const getIcon = (type) =>
      ({
        payment_upcoming: 'fas fa-clock',
        payment_today: 'fas fa-bell',
        budget_warning: 'fas fa-exclamation-triangle',
        budget_exceeded: 'fas fa-times-circle',
        insight_alert: 'fas fa-lightbulb',
      }[type] || 'fas fa-bell')

    const getIconClass = (type) =>
      ({
        payment_upcoming: 'icon-warning',
        payment_today: 'icon-danger',
        budget_warning: 'icon-warning',
        budget_exceeded: 'icon-danger',
        insight_alert: 'icon-info',
      }[type] || 'icon-info')

    const formatDateTime = (iso) => {
      if (!iso) return ''
      return new Date(iso).toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    }

    onMounted(() => {
      loadNotifications()
      loadPreferences()
      checkSubscription()
    })

    return {
      notifications,
      loading,
      unreadOnly,
      markingAll,
      clearing,
      hasMore,
      loadingMore,
      settingsOpen,
      prefsSaved,
      prefs,
      pushSupported,
      pushLoading,
      subscribed,
      unreadCount,
      hasUnread,
      hasRead,
      togglePush,
      markRead,
      markAllRead,
      deleteOne,
      clearRead,
      setFilter,
      savePreferences,
      getIcon,
      getIconClass,
      formatDateTime,
      loadMore,
    }
  },
}
</script>

<style scoped>
.notifications-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.page-header h1 {
  color: var(--dark-color);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* ===== Push card ===== */
.push-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius);
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.push-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 200px;
}
.push-icon {
  font-size: 1.75rem;
  opacity: 0.9;
}
.push-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}
.push-hint {
  font-size: 0.813rem;
  opacity: 0.85;
}
.push-card .btn-primary {
  background: white;
  color: #4c1d95;
}
.push-card .btn-primary:hover {
  background: #f3f4f6;
}
.push-card .btn-secondary {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}
.push-card .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.25);
}
.push-unsupported {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
  border-radius: var(--radius);
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}

/* ===== Settings ===== */
.settings-card {
  padding: 0;
  overflow: hidden;
  margin-bottom: 1.5rem;
  background: var(--white);
}
.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  cursor: pointer;
  user-select: none;
}
.settings-header h3 {
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  color: var(--dark-color);
}
.settings-header:hover {
  background: var(--light-color);
}
.settings-body {
  padding: 0 1.5rem 1.25rem;
  border-top: 1px solid var(--light-color);
}
.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--light-color);
}
.setting-row:last-child {
  border-bottom: none;
}
.setting-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  flex: 1;
  color: var(--dark-color);
}
.short-input {
  width: 100px;
}
.prefs-saved {
  color: var(--secondary-color);
  font-size: 0.813rem;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

/* ===== Filter tabs ===== */
.filter-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.tab-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--light-color);
  background: var(--white);
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--gray-color);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}
.tab-btn:hover {
  background: var(--light-color);
}
.tab-btn.active {
  background: var(--primary-color);
  color: var(--white);
  border-color: var(--primary-color);
}
.tab-badge {
  background: rgba(255, 255, 255, 0.25);
  padding: 0.1rem 0.4rem;
  border-radius: 9999px;
  font-size: 0.7rem;
  font-weight: 700;
}
.tab-btn:not(.active) .tab-badge {
  background: #fee2e2;
  color: #991b1b;
}

/* ===== Loading / Empty ===== */
.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--gray-color);
  background: var(--white);
  border-radius: var(--radius);
}
.loading-state i,
.empty-state i {
  font-size: 2.5rem;
  opacity: 0.5;
  margin-bottom: 0.75rem;
  display: block;
}

/* ===== List ===== */
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* --- БАЗОВЫЕ СТИЛИ (СВЕТЛАЯ ТЕМА) --- */
.notification-item {
  display: flex;
  align-items: stretch;
  background: var(--white);
  border-radius: var(--radius);
  border-left: 4px solid transparent;
  box-shadow: var(--shadow);
  transition: all 0.2s;
  position: relative;
}
.notification-item:hover {
  transform: translateX(2px);
  box-shadow: var(--shadow-lg);
}
.notification-item.unread {
  border-left-color: var(--primary-color);
  /* Убрали жесткий background, чтобы в темной теме он переопределялся */
  background: #f0f4ff;
}

.notification-icon {
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid var(--light-color);
  cursor: pointer;
  font-size: 1.1rem;
  border-top-left-radius: var(--radius);
  border-bottom-left-radius: var(--radius);
  flex-shrink: 0;
}
.icon-info { color: #1e40af; }
.icon-warning { color: #92400e; }
.icon-danger { color: #991b1b; }

.notification-body {
  flex: 1;
  padding: 1rem;
  cursor: pointer;
  min-width: 0;
}

.notification-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--dark-color);
  margin-bottom: 0.35rem;
  line-height: 1.35;
  word-break: break-word;
}
.notification-title-text {
  flex: 1;
  min-width: 0;
}
.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary-color);
  display: inline-block;
  flex-shrink: 0;
}
.notification-message {
  font-size: 0.875rem;
  color: var(--gray-color);
  margin-bottom: 0.375rem;
  line-height: 1.4;
  word-break: break-word;
}
.notification-date {
  font-size: 0.75rem;
  color: var(--gray-color);
}
.delete-btn {
  background: transparent;
  border: none;
  padding: 0 1rem;
  color: #d1d5db;
  cursor: pointer;
  transition: color 0.2s, background 0.2s;
  border-top-right-radius: var(--radius);
  border-bottom-right-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}
.delete-btn:hover {
  color: var(--danger-color);
  background: #fee2e2;
}

/* ===== Pagination ===== */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}

/* ===== Mobile ===== */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 0.75rem;
  }
  .page-header h1 {
    text-align: center;
    width: 100%;
    margin: 0;
  }
  .header-actions {
    width: 100%;
    flex-direction: column;
  }
  .header-actions .btn {
    width: 100%;
    justify-content: center;
  }
  .push-card {
    flex-direction: column;
    align-items: stretch;
  }
  .push-card .btn {
    width: 100%;
    justify-content: center;
  }
  .setting-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .short-input {
    width: 100%;
  }
  .notification-icon {
    padding: 0.75rem;
    font-size: 1rem;
  }
  .notification-body {
    padding: 0.75rem;
    text-align: center;
  }

  /* Заголовок по центру на мобильных */
  .notification-title {
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 0.25rem;
  }
  .notification-title-text {
    text-align: center;
    width: 100%;
  }
  .unread-dot {
    order: 2;
    margin: 0;
  }

  .notification-message {
    text-align: center;
  }
  .notification-date {
    text-align: center;
  }

  .delete-btn {
    padding: 0 0.75rem;
  }
}

@media (max-width: 480px) {
  .notification-title {
    font-size: 0.95rem;
  }
  .notification-message {
    font-size: 0.85rem;
  }
}

.btn-outline-danger {
  background: transparent;
  color: var(--danger-color);
  border: 1px solid var(--danger-color);
}
.btn-outline-danger:hover {
  background: var(--danger-color);
  color: white;
}
</style>