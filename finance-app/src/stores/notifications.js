import { reactive } from 'vue'
import apiService from '../services/api.js'

export const notificationStore = reactive({
  unreadCount: 0,
  _timerId: null,

  async refreshUnread() {
    try {
      // Передаем true, чтобы бэкенд вернул только unread=1
      const data = await apiService.getNotifications(true, 1)
      const list = Array.isArray(data) ? data : (data.results || [])
      this.unreadCount = data.count !== undefined ? data.count : list.length
    } catch (e) {}
  },

  decrement() {
    if (this.unreadCount > 0) this.unreadCount--
  },

  clear() {
    this.unreadCount = 0
  },

  startPolling(intervalMs = 60000) {
    this.refreshUnread()
    if (this._timerId) clearInterval(this._timerId)
    this._timerId = setInterval(() => this.refreshUnread(), intervalMs)
  },

  stopPolling() {
    if (this._timerId) {
      clearInterval(this._timerId)
      this._timerId = null
    }
  },
})
