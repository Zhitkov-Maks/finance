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

    setupInterceptors() {
        this.client.interceptors.request.use(config => {
            const token = localStorage.getItem('auth_token')
            // Добавляем токен для всех запросов, кроме логина и регистрации
            if (token && !config.url.includes('/auth/token/login/') && !config.url.includes('/auth/users/')) {
                config.headers['Authorization'] = `Token ${token}`
            }
            console.log(`Making request to: ${config.url}`, config.headers)
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

    // Аутентификация
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

    async getUserInfo() {
        const response = await this.client.get('/auth/users/')
        return response.data
    }

    // ==================== User Profile ====================
    async getCurrentUser() {
        try {
            const token = localStorage.getItem('auth_token')
            console.log('Getting current user with token:', token ? 'Token present' : 'No token')

            const response = await this.client.get('/auth/users/me/', {
                headers: {
                    'Authorization': `Token ${token}`
                }
            })
            console.log('User info response:', response.data)
            return response.data
        } catch (error) {
            console.error('Error fetching current user:', error.response?.data || error.message)
            throw error
        }
    }

    async changePassword(currentPassword, newPassword) {
        try {
            const token = localStorage.getItem('auth_token')
            console.log('Changing password with token:', token ? 'Token present' : 'No token')

            const response = await this.client.post('/auth/users/set_password/', {
                current_password: currentPassword,
                new_password: newPassword
            }, {
                headers: {
                    'Authorization': `Token ${token}`
                }
            })
            console.log('Password change response:', response.data)
            return response.data
        } catch (error) {
            console.error('Error changing password:', error.response?.data || error.message)
            throw error
        }
    }

    // Счета
    async getAccounts(page = 1, pageSize = 10) {
        const response = await this.client.get('/accounts/', {
            params: { page, page_size: pageSize }
        })
        return response.data
    }

    async createAccount(name, balance) {
        const response = await this.client.post('/accounts/', {
            name,
            balance
        })
        return response.data
    }

    async getAccount(id) {
        const response = await this.client.get(`/accounts/${id}/`)
        return response.data
    }

    async updateAccount(id, data) {
        const response = await this.client.put(`/accounts/${id}/`, data)
        return response.data
    }

    async patchAccount(id, data) {
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

    // Категории
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

    // Транзакции
    async getTransactions(params) {
        const response = await this.client.get('/transaction/', { params })
        return response.data
    }

    async createTransaction(type, data) {
        const response = await this.client.post('/transaction/', data, {
            params: { type }
        })
        return response.data
    }

    async getTransaction(id) {
        const response = await this.client.get(`/transaction/${id}/`)
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

    async getStatistics(month, year, type) {
        const response = await this.client.get('/transaction/statistics/', {
            params: { month, year, type }
        })
        return response.data
    }

    // Переводы
    async createTransfer(sourceAccount, destinationAccount, amount, timestamp) {
        const response = await this.client.post('/transfer/', {
            source_account: sourceAccount,
            destination_account: destinationAccount,
            amount,
            timestamp
        })
        return response.data
    }

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

    async updateTransfer(id, data) {
        const response = await this.client.put(`/transfer/${id}/`, data)
        return response.data
    }

    async deleteTransfer(id) {
        await this.client.delete(`/transfer/${id}/`)
    }

    // Долги
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

    async getDebt(id) {
        const response = await this.client.get(`/debts/${id}/`)
        return response.data
    }

    async getDebts(page = 1, pageSize = 10, type = null) {
        const params = { page, page_size: pageSize }
        if (type) params.type = type
        const response = await this.client.get('/debts/', { params })
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

    // Аналитика
    async getMonthlyAnalytics(year, type) {
        const response = await this.client.get('/analitycs/month/', {
            params: { year, type }
        })
        return response.data
    }

    // Статистика по категориям за месяц
    async getMonthStatistics(month, year, type) {
        try {
            const response = await this.client.get('/transaction/statistics/', {
                params: {
                    month: month,
                    year: year,
                    type: type
                }
            })
            return response.data
        } catch (error) {
            console.error('Error loading month statistics:', error)
            throw error
        }
    }

    clearAuth() {
        this.clearToken()
        delete this.client.defaults.headers.common['Authorization']
        localStorage.removeItem('auth_token')
        sessionStorage.clear()
    }

    async changeEmail(currentPassword, newEmail) {
        try {
            const token = localStorage.getItem('auth_token')
            console.log('Changing email with token:', token ? 'Token present' : 'No token')

            const response = await this.client.post('/auth/users/set_email/', {
                current_password: currentPassword,
                new_email: newEmail
            }, {
                headers: {
                    'Authorization': `Token ${token}`
                }
            })
            console.log('Email change response:', response.data)
            return response.data
        } catch (error) {
            console.error('Error changing email:', error.response?.data || error.message)
            throw error
        }
    }
    async getTimesheetSettings() {
        try {
            const response = await this.client.get('/timesheets/settings/')
            return response.data
        } catch (error) {
            console.error('Error fetching timesheet settings:', error.response?.data || error.message)
            throw error
        }
    }

    // Создание/обновление настроек пользователя
    async updateTimesheetSettings(settings) {
        try {
            const response = await this.client.post('/timesheets/settings/', settings)
            return response.data
        } catch (error) {
            console.error('Error updating timesheet settings:', error.response?.data || error.message)
            throw error
        }
    }

    // Удаление настроек пользователя
    async deleteTimesheetSettings() {
        try {
            await this.client.delete('/timesheets/settings/')
            return true
        } catch (error) {
            console.error('Error deleting timesheet settings:', error.response?.data || error.message)
            throw error
        }
    }

    // Получение смен за выбранный месяц
    async getShiftsByMonth(month, year) {
        try {
            const response = await this.client.get('/timesheets/shifts/', {
                params: { month, year }
            })
            return response.data
        } catch (error) {
            console.error('Error fetching shifts:', error.response?.data || error.message)
            throw error
        }
    }

    // Создание смены за выбранный день
    async createShift(date, hours) {
        try {
            const response = await this.client.post('/timesheets/shifts/', {
                date,
                time: hours
            })
            return response.data
        } catch (error) {
            console.error('Error creating shift:', error.response?.data || error.message)
            throw error
        }
    }

    // Обновление данных смены
    async updateShift(date, hours) {
        try {
            const response = await this.client.put('/timesheets/shifts/', {
                date,
                time: hours
            })
            return response.data
        } catch (error) {
            console.error('Error updating shift:', error.response?.data || error.message)
            throw error
        }
    }

    // Получение данных за конкретный день
    async getShiftById(dayId) {
        try {
            const response = await this.client.get(`/timesheets/shifts/${dayId}/`)
            return response.data
        } catch (error) {
            console.error('Error fetching shift details:', error.response?.data || error.message)
            throw error
        }
    }

    // Добавление премии за конкретный день
    async addAward(dayId, countOperations) {
        try {
            const response = await this.client.post(
                `/timesheets/shifts/${dayId}/?count_operations=${countOperations}`,
                {}
            )
            return response.data
        } catch (error) {
            console.error('Error adding award:', error.response?.data || error.message)
            throw error
        }
    }

    // Удаление смены
    async deleteShift(dayId) {
        try {
            await this.client.delete(`/timesheets/shifts/${dayId}/`)
            return true
        } catch (error) {
            console.error('Error deleting shift:', error.response?.data || error.message)
            throw error
        }
    }

    // Массовое добавление смен за определенный месяц
    async addManyShifts(hours, dates) {
        try {
            const response = await this.client.post('/timesheets/add-many-shifts/', {
                hours,
                dates
            })
            return response.data
        } catch (error) {
            console.error('Error adding many shifts:', error.response?.data || error.message)
            throw error
        }
    }

    // Статистика за месяц
    async getMonthlyStatistics(month, year) {
        try {
            const response = await this.client.get('/timesheets/statistics/month/', {
                params: { month, year }
            })
            return response.data
        } catch (error) {
            console.error('Error fetching monthly statistics:', error.response?.data || error.message)
            throw error
        }
    }

    // Статистика за год
    async getYearlyStatistics(year) {
        try {
            const response = await this.client.get('/timesheets/statistics/year/', {
                params: { year }
            })
            return response.data
        } catch (error) {
            console.error('Error fetching yearly statistics:', error.response?.data || error.message)
            throw error
        }
    }
}
export default new ApiService()