import axios from 'axios'

const API_BASE_URL = '/api/v1'

class ApiService {
  constructor() {
    this.token = localStorage.getItem('auth_token')
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
      if (token && !config.url.includes('/auth/')) {
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

  // Аутентификация - используем правильные URL
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
}

export default new ApiService()