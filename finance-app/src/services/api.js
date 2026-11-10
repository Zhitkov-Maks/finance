import axios from 'axios'

const API_BASE_URL = '/api/v1'

class ApiService {
    constructor() {
        this.token = localStorage.getItem('auth_token')
        this.baseUrl = API_BASE_URL
        this.client = axios.create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json',
            }
        })
        this.setupInterceptors()
    }

    // ============================================================
    // ИНФРАСТРУКТУРА
    // ============================================================
    setupInterceptors() {
        this.client.interceptors.request.use(config => {
            const token = localStorage.getItem('auth_token')
            if (!token) return config

            const url = config.url || ''

            // Только эти два эндпоинта НЕ требуют токена
            const isLogin = url.includes('/auth/token/login/')
            const isRegister = url === '/auth/users/' && config.method === 'post'

            if (!isLogin && !isRegister) {
                config.headers['Authorization'] = `Token ${token}`
            }
            return config
        })
    }

    setToken(token) {
        this.token = token
        localStorage.setItem('auth_token', token)
    }

    clearToken() {
        this.token = null
        localStorage.removeItem('auth_token')
    }

    getAuthHeaders() {
        const token = localStorage.getItem('auth_token')
        return {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }

    clearAuth() {
        this.clearToken()
        delete this.client.defaults.headers.common['Authorization']
        localStorage.removeItem('auth_token')
        sessionStorage.clear()
    }

    // ============================================================
    // АУТЕНТИФИКАЦИЯ
    // ============================================================
    async register(email, password, rePassword) {
        const response = await this.client.post('/auth/users/', {
            email,
            password,
            re_password: rePassword
        })
        return response.data
    }

    async login(email, password) {
        const response = await this.client.post('/auth/token/login/', {
            email,
            password
        })
        const token = response.data.auth_token
        this.setToken(token)
        return token
    }

    async logout() {
        try {
            await this.client.post('/auth/token/logout/')
        } catch (error) {
            console.error('Logout API error:', error)
        } finally {
            this.clearAuth()
        }
    }

    // ============================================================
    // ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
    // ============================================================
    async getUserInfo() {
        const response = await this.client.get('/auth/users/')
        return response.data
    }

    async getCurrentUser() {
        const response = await this.client.get('/auth/users/me/')
        return response.data
    }

    async changePassword(currentPassword, newPassword) {
        const response = await this.client.post('/auth/users/set_password/', {
            current_password: currentPassword,
            new_password: newPassword
        })
        return response.data
    }

    async changeEmail(currentPassword, newEmail) {
        const response = await this.client.post('/auth/users/set_email/', {
            current_password: currentPassword,
            new_email: newEmail
        })
        return response.data
    }

    // ============================================================
    // СЧЕТА
    // ============================================================
    async getAccounts(page = 1, pageSize = 10, includeArchived = false) {
        const params = { page, page_size: pageSize }
        if (includeArchived) params.include_archived = 'true'
        const response = await this.client.get('/accounts/', { params })
        return response.data
    }

    async restoreAccount(id) {
        const response = await this.client.post(`/accounts/${id}/restore/`)
        return response.data
    }

    async getAccount(id) {
        const response = await this.client.get(`/accounts/${id}/`)
        return response.data
    }

    async createAccount(data) {
        const response = await this.client.post('/accounts/', data)
        return response.data
    }

    async updateAccount(id, data) {
        const response = await this.client.patch(`/accounts/${id}/`, data)
        return response.data
    }

    async deleteAccount(id) {
        await this.client.delete(`/accounts/${id}/`)
    }

    async toggleAccountActive(id, isActive) {
        const response = await this.client.patch(`/accounts/${id}/toggle-active/`, {
            is_active: isActive
        })
        return response.data
    }

    async getBalanceHistory(dateFrom, dateTo, accountId = null, includeInactive = false) {
        const response = await this.client.get('/accounts/balance-history/', {
            params: {
                date_from: dateFrom,
                date_to: dateTo,
                ...(accountId ? { account_id: accountId } : {}),
                ...(includeInactive ? { include_inactive: 'true' } : {})
            }
        })
        return response.data
    }

    // ============================================================
    // КАТЕГОРИИ
    // ============================================================
    async getCategories(type, page = 1, pageSize = 10, parent = false) {
        const response = await this.client.get('/transaction/category/', {
            params: { type, page, page_size: pageSize, parent }
        })
        return response.data
    }

    async getCategory(id) {
        const response = await this.client.get(`/transaction/category/${id}/`)
        return response.data
    }

    async createCategory(name, type, parent = null) {
        const response = await this.client.post('/transaction/category/',
            { name, parent: parent || "" },
            { params: { type } }
        )
        return response.data
    }

    async updateCategory(id, name, parent = null) {
        const response = await this.client.put(`/transaction/category/${id}/`, {
            name,
            parent: parent || ""
        })
        return response.data
    }

    async deleteCategory(id) {
        await this.client.delete(`/transaction/category/${id}/`)
    }

    // ============================================================
    // ТРАНЗАКЦИИ
    // ============================================================
    async getTransactions(params) {
        const response = await this.client.get('/transaction/', { params })
        return response.data
    }

    async getTransaction(id) {
        const response = await this.client.get(`/transaction/${id}/`)
        return response.data
    }

    async createTransaction(type, data) {
        const response = await this.client.post('/transaction/', data, {
            params: { type }
        })
        return response.data
    }

    async updateTransaction(id, data) {
        const response = await this.client.put(`/transaction/${id}/`, data)
        return response.data
    }

    async patchTransaction(id, data) {
        const response = await this.client.patch(`/transaction/${id}/`, data)
        return response.data
    }

    async deleteTransaction(id) {
        await this.client.delete(`/transaction/${id}/`)
    }

    // Статистика по категориям за месяц (объединено: getStatistics + getMonthStatistics)
    async getMonthStatistics(month, year, type) {
        const response = await this.client.get('/transaction/statistics/', {
            params: { month, year, type }
        })
        return response.data
    }

    // ============================================================
    // ПЕРЕВОДЫ
    // ============================================================
    async getTransferHistory(page = 1, pageSize = 10) {
        const response = await this.client.get('/transfer/history/', {
            params: { page, page_size: pageSize }
        })
        return response.data
    }

    async getTransfer(id) {
        const response = await this.client.get(`/transfer/${id}/`)
        return response.data
    }

    async createTransfer(sourceAccount, destinationAccount, amount, timestamp) {
        const response = await this.client.post('/transfer/', {
            source_account: sourceAccount,
            destination_account: destinationAccount,
            amount,
            timestamp
        })
        return response.data
    }

    async updateTransfer(id, data) {
        const response = await this.client.put(`/transfer/${id}/`, data)
        return response.data
    }

    async deleteTransfer(id) {
        await this.client.delete(`/transfer/${id}/`)
    }

    async getTransferAnalytics(dateFrom, dateTo) {
        const response = await this.client.get('/transfer/analytics/', {
            params: { date_from: dateFrom, date_to: dateTo }
        })
        return response.data
    }

    // ============================================================
    // ДОЛГИ
    // ============================================================
    async getDebts(page = 1, pageSize = 10, type = null) {
        const params = { page, page_size: pageSize }
        if (type) params.type = type
        const response = await this.client.get('/debts/', { params })
        return response.data
    }

    async getDebt(id) {
        const response = await this.client.get(`/debts/${id}/`)
        return response.data
    }

    async createDebtAccounts(name, userId) {
        const response = await this.client.post('/debts/create-debt-accounts/', {
            name,
            balance: "0",
            user: userId
        })
        return response.data
    }

    async createDebt(accountId, type, amount, description, date) {
        const response = await this.client.post('/debts/create-debt/', {
            account_id: accountId,
            type,
            amount,
            description,
            date
        })
        return response.data
    }

    async repayDebt(debtId, amount, type) {
        const response = await this.client.post('/debts/repay-debt/', {
            debt_id: debtId,
            amount,
            type
        })
        return response.data
    }

    async simulateCreditPlan(monthlyPayment, strategy) {
        const response = await this.client.post('/debts/credit-plan-simulate/', {
            monthly_payment: monthlyPayment,
            strategy: strategy
        })
        return response.data
    }

    // ============================================================
    // БЮДЖЕТЫ
    // ============================================================
    async getBudgetSummary(periodType = 'monthly', date = null) {
        const params = { period_type: periodType }
        if (date) params.date = date
        const response = await this.client.get('/budgets/summary/', { params })
        return response.data
    }

    async createBudget(data) {
        const response = await this.client.post('/budgets/', data)
        return response.data
    }

    async updateBudget(id, data) {
        const response = await this.client.put(`/budgets/${id}/`, data)
        return response.data
    }

    async deleteBudget(id) {
        await this.client.delete(`/budgets/${id}/`)
    }

    // ============================================================
    // РЕГУЛЯРНЫЕ ОПЕРАЦИИ
    // ============================================================
    async getRecurring(filters = {}) {
        const response = await this.client.get('/recurring/', { params: filters })
        return response.data
    }

    async getRecurringById(id) {
        const response = await this.client.get(`/recurring/${id}/`)
        return response.data
    }

    async createRecurring(data) {
        const response = await this.client.post('/recurring/', data)
        return response.data
    }

    async updateRecurring(id, data) {
        const response = await this.client.put(`/recurring/${id}/`, data)
        return response.data
    }

    async patchRecurring(id, data) {
        const response = await this.client.patch(`/recurring/${id}/`, data)
        return response.data
    }

    async deleteRecurring(id) {
        await this.client.delete(`/recurring/${id}/`)
    }

    async getUpcomingPayments(days = 30) {
        const response = await this.client.get('/recurring/upcoming/', {
            params: { days }
        })
        return response.data
    }

    // ============================================================
    // АНАЛИТИКА
    // ============================================================
    async getMonthlyAnalytics(year, type) {
        const response = await this.client.get('/analitycs/month/', {
            params: { year, type }
        })
        return response.data
    }

    async getForecast() {
        const response = await this.client.get('/analitycs/forecast/')
        return response.data
    }

    // ============================================================
    // ГРАФИК РАБОТЫ (TIMESHEETS)
    // ============================================================

    // --- Настройки оплаты ---
    async getTimesheetSettings() {
        const response = await this.client.get('/timesheets/settings/')
        return response.data
    }

    async updateTimesheetSettings(settings) {
        const response = await this.client.post('/timesheets/settings/', settings)
        return response.data
    }

    async deleteTimesheetSettings() {
        await this.client.delete('/timesheets/settings/')
        return true
    }

    // --- Смены ---
    async getShiftsByMonth(month, year) {
        const response = await this.client.get('/timesheets/shifts/', {
            params: { month, year }
        })
        return response.data
    }

    async getShiftById(dayId) {
        const response = await this.client.get(`/timesheets/shifts/${dayId}/`)
        return response.data
    }

    async createShift(date, hours) {
        const response = await this.client.post('/timesheets/shifts/', {
            date,
            time: hours
        })
        return response.data
    }

    async updateShift(date, hours) {
        const response = await this.client.post('/timesheets/shifts/', {
            date,
            time: hours
        })
        return response.data
    }

    async deleteShift(dayId) {
        await this.client.delete(`/timesheets/shifts/${dayId}/`)
        return true
    }

    async addManyShifts(hours, dates) {
        const response = await this.client.post('/timesheets/add-many-shifts/', {
            hours,
            dates
        })
        return response.data
    }

    // --- Отпуска и больничные ---
    async addVacation(data) {
        const response = await this.client.post('/timesheets/shifts/vacation/', data)
        return response.data
    }

    // --- Мотивация ---
    async addAward(dayId, countOperations, typeOperations) {
        const response = await this.client.post(
            `/timesheets/shifts/${dayId}/?count_operations=${countOperations}&type_operations=${typeOperations}`,
            {}
        )
        return response.data
    }

    async addNonProductiveWork(dayId, countHours) {
        const response = await this.client.put(
            `/timesheets/shifts/${dayId}/?hours=${countHours}`,
            {}
        )
        return response.data
    }

    // --- Статистика ---
    async getMonthlyStatistics(month, year) {
        const response = await this.client.get('/timesheets/statistics/month/', {
            params: { month, year }
        })
        return response.data
    }

    async getYearlyStatistics(year) {
        const response = await this.client.get('/timesheets/statistics/year/', {
            params: { year }
        })
        return response.data
    }

    // ============================================================
    // УВЕДОМЛЕНИЯ
    // ============================================================
    async getNotifications(unreadOnly = false, page = 1) {
        const params = { page }
        if (unreadOnly) params.unread = '1'
        const response = await this.client.get('/notifications/', { params })
        return response.data
    }

    async markNotificationRead(id) {
        await this.client.post(`/notifications/${id}/read/`)
    }

    async markAllNotificationsRead() {
        await this.client.post('/notifications/read-all/')
    }

    async deleteNotification(id) {
        await this.client.delete(`/notifications/${id}/`)
    }

    async clearReadNotifications() {
        await this.client.post('/notifications/clear-read/')
    }

    async getNotificationPreferences() {
        const response = await this.client.get('/notifications/preferences/')
        return response.data
    }

    async updateNotificationPreferences(data) {
        const response = await this.client.patch('/notifications/preferences/', data)
        return response.data
    }

    // Push-уведомления
    async getVapidPublicKey() {
        const response = await this.client.get('/notifications/vapid-public-key/')
        return response.data.public_key
    }

    async subscribePush(subscription) {
        const response = await this.client.post('/notifications/push/subscribe/', subscription)
        return response.data
    }

    async unsubscribePush(endpoint) {
        await this.client.post('/notifications/push/unsubscribe/', { endpoint })
    }

    // ============================================================
    // ИНСАЙТЫ И ГЕЙМИФИКАЦИЯ
    // ============================================================
    async getInsights(activeOnly = true) {
        const params = activeOnly ? { active: '1' } : {}
        const response = await this.client.get('/insights/', { params })
        return response.data
    }

    async dismissInsight(id) {
        await this.client.post(`/insights/${id}/dismiss/`)
    }

    async getGamificationDashboard() {
        const response = await this.client.get('/insights/gamification/')
        return response.data
    }

    async getInsightSettings() {
        const response = await this.client.get('/insights/settings/')
        return response.data
    }

    async updateInsightSettings(data) {
        const response = await this.client.patch('/insights/settings/', data)
        return response.data
    }

    // --- Цели на месяц ---
    // Единый метод: если monthStr не передан — берётся текущий месяц на бэкенде
    async getGoalCurrent(monthStr = null, goalType = 'motivation') {
        const params = { goal_type: goalType }
        if (monthStr) params.month = monthStr
        const response = await this.client.get('/insights/goals/current/', { params })
        return response.data.goal
    }

    async saveGoalCurrent(data, monthStr = null) {
        const payload = { ...data, goal_type: data.goal_type || 'motivation' }
        if (monthStr) payload.month = monthStr
        const response = await this.client.post('/insights/goals/current/', payload)
        return response.data
    }

    async deleteGoalCurrent(goalType, monthStr = null) {
        const params = { goal_type: goalType }
        if (monthStr) params.month = monthStr
        await this.client.delete('/insights/goals/current/', { params })
    }

    // ============================================================
    // ЭКСПОРТ ДАННЫХ
    // ============================================================
    async downloadExport(format = 'json') {
        try {
            const response = await this.client.get('/export/', {
                params: { export_format: format },
                responseType: 'blob',
            })

            const contentDisposition = response.headers['content-disposition'] || ''
            let filename = null
            const match = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(contentDisposition)
            if (match) {
                try {
                    filename = decodeURIComponent(match[1])
                } catch {
                    filename = match[1]
                }
            }

            return { blob: response.data, filename }
        } catch (error) {
            if (error.response?.data instanceof Blob) {
                try {
                    const text = await error.response.data.text()
                    const parsed = JSON.parse(text)
                    error.message =
                        parsed.detail ||
                        (Array.isArray(parsed.format) ? parsed.format[0] : null) ||
                        text
                } catch {
                    // не JSON — оставляем оригинальное сообщение
                }
            }
            console.error('Error downloading export:', error.response?.data || error.message)
            throw error
        }
    }

    async getExportInfo() {
        const response = await this.client.get('/export/', {
            params: { export_format: 'info' },
        })
        return response.data
    }
}

export default new ApiService()