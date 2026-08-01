// HTTP-клиент на axios — базовая настройка, перехватчики токена и редирект при 401
import axios from 'axios';

const TOKEN_KEY = 'auth_token';

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Перехватчик запросов — цепляем токен к каждому запросу, если он есть
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Перехватчик ответов — если 401, значит токен протух, чистим и кидаем на логин
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export default apiClient;
