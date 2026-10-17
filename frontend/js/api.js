const API_BASE_URL = 'http://127.0.0.1:5000/api';

const API = {
  getToken() {
    return localStorage.getItem('rw_token');
  },

  getUser() {
    const userStr = localStorage.getItem('rw_user');
    return userStr ? JSON.parse(userStr) : null;
  },

  setSession(token, user) {
    localStorage.setItem('rw_token', token);
    localStorage.setItem('rw_user', JSON.stringify(user));
  },

  clearSession() {
    localStorage.removeItem('rw_token');
    localStorage.removeItem('rw_user');
  },

  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || 'API Request failed');
      }
      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }
};
