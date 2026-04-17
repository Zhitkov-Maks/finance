import axios from 'axios'

const API_BASE_URL = 'http://0.0.0.0:8001/api/v1'
const AUTH_URL = 'http://0.0.0.0:8001'

class ApiService {
  constructor() {
    this.token = localStorage.getItem('auth_token')
    this.setupInterceptors()
  }

  setupInterceptors() {
    axios.interceptors.request.use(config => {
      if (this.token && !config.url.includes('/auth/')) {
        config.headers['Authorization'] = `Token ${this.token}`
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

  // Аутентификация
  async register(email, password, rePassword) {
    const response = await axios.post(`${AUTH_URL}/api/v1/auth/users/`, {
      email,
      password,
      re_password: rePassword
    })
    return response.data
  }

  async login(email, password) {
    const response = await axios.post(`${AUTH_URL}/auth/token/login/`, {
      email,
      password
    })
    const token = response.data.auth_token
    this.setToken(token)
    return token
  }

  async logout() {
    await axios.post(`${AUTH_URL}/auth/token/logout/`)
    this.clearToken()
  }

  async getUserInfo() {
    const response = await axios.get(`${API_BASE_URL}/auth/users/`)
    return response.data
  }

  // Счета
  async getAccounts(page = 1, pageSize = 10) {
    const response = await axios.get(`${API_BASE_URL}/accounts/`, {
      params: { page, page_size: pageSize }
    })
    return response.data
  }

  async createAccount(name, balance) {
    const response = await axios.post(`${API_BASE_URL}/accounts/`, {
      name,
      balance
    })
    return response.data
  }

  async getAccount(id) {
    const response = await axios.get(`${API_BASE_URL}/accounts/${id}/`)
    return response.data
  }

  async updateAccount(id, data) {
    const response = await axios.put(`${API_BASE_URL}/accounts/${id}/`, data)
    return response.data
  }

  async patchAccount(id, data) {
    const response = await axios.patch(`${API_BASE_URL}/accounts/${id}/`, data)
    return response.data
  }

  async deleteAccount(id) {
    await axios.delete(`${API_BASE_URL}/accounts/${id}/`)
  }

  async toggleAccountActive(id, isActive) {
    const response = await axios.patch(`${API_BASE_URL}/accounts/${id}/toggle-active/`, {
      is_active: isActive
    })
    return response.data
  }

  // Категории
  async getCategories(type, page = 1, pageSize = 10, parent = false) {
    const response = await axios.get(`${API_BASE_URL}/transaction/category/`, {
      params: { type, page, page_size: pageSize, parent }
    })
    return response.data
  }

  async getCategory(id) {
    const response = await axios.get(`${API_BASE_URL}/transaction/category/${id}/`)
    return response.data
  }

  async createCategory(name, type, parent = null) {
    const response = await axios.post(`${API_BASE_URL}/transaction/category/`, 
      { name, parent: parent || "" },
      { params: { type } }
    )
    return response.data
  }

  async updateCategory(id, name, parent = null) {
    const response = await axios.put(`${API_BASE_URL}/transaction/category/${id}/`, {
      name,
      parent: parent || ""
    })
    return response.data
  }

  async deleteCategory(id) {
    await axios.delete(`${API_BASE_URL}/transaction/category/${id}/`)
  }

  // Транзакции
  async getTransactions(params) {
    const response = await axios.get(`${API_BASE_URL}/transaction/`, { params })
    return response.data
  }

  async createTransaction(type, data) {
    const response = await axios.post(`${API_BASE_URL}/transaction/`, data, {
      params: { type }
    })
    return response.data
  }

  async getTransaction(id) {
    const response = await axios.get(`${API_BASE_URL}/transaction/${id}/`)
    return response.data
  }

  async updateTransaction(id, data) {
    const response = await axios.put(`${API_BASE_URL}/transaction/${id}/`, data)
    return response.data
  }

  async patchTransaction(id, data) {
    const response = await axios.patch(`${API_BASE_URL}/transaction/${id}/`, data)
    return response.data
  }

  async deleteTransaction(id) {
    await axios.delete(`${API_BASE_URL}/transaction/${id}/`)
  }

  async getStatistics(month, year, type) {
    const response = await axios.get(`${API_BASE_URL}/transaction/statistics/`, {
      params: { month, year, type }
    })
    return response.data
  }

  // Переводы
  async createTransfer(sourceAccount, destinationAccount, amount, timestamp) {
    const response = await axios.post(`${API_BASE_URL}/transfer/`, {
      source_account: sourceAccount,
      destination_account: destinationAccount,
      amount,
      timestamp
    })
    return response.data
  }

  async getTransferHistory(page = 1, pageSize = 10) {
    const response = await axios.get(`${API_BASE_URL}/transfer/history/`, {
      params: { page, page_size: pageSize }
    })
    return response.data
  }

  async getTransfer(id) {
    const response = await axios.get(`${API_BASE_URL}/transfer/${id}/`)
    return response.data
  }

  async updateTransfer(id, data) {
    const response = await axios.put(`${API_BASE_URL}/transfer/${id}/`, data)
    return response.data
  }

  async deleteTransfer(id) {
    await axios.delete(`${API_BASE_URL}/transfer/${id}/`)
  }

  // Долги
  async createDebtAccounts(name, userId) {
    const response = await axios.post(`${API_BASE_URL}/debts/create-debt-accounts/`, {
      name,
      balance: "0",
      user: userId
    })
    return response.data
  }

  async createDebt(accountId, type, amount, description, date) {
    const response = await axios.post(`${API_BASE_URL}/debts/create-debt/`, {
      account_id: accountId,
      type,
      amount,
      description,
      date
    })
    return response.data
  }

  async getDebt(id) {
    const response = await axios.get(`${API_BASE_URL}/debts/${id}/`)
    return response.data
  }

  async getDebts(page = 1, pageSize = 10, type = null) {
    const params = { page, page_size: pageSize }
    if (type) params.type = type
    const response = await axios.get(`${API_BASE_URL}/debts/`, { params })
    return response.data
  }

  async repayDebt(debtId, amount, type) {
    const response = await axios.post(`${API_BASE_URL}/debts/repay-debt/`, {
      debt_id: debtId,
      amount,
      type
    })
    return response.data
  }

  // Аналитика
  async getMonthlyAnalytics(year, type) {
    const response = await axios.get(`${API_BASE_URL}/analitycs/month/`, {
      params: { year, type }
    })
    return response.data
  }

  // Статистика по категориям за месяц
  async getMonthStatistics(month, year, type) {
    try {
      // Используем правильный URL для статистики по категориям
      const response = await axios.get(`${API_BASE_URL}/transaction/statistics/`, {
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
}

export default new ApiService()