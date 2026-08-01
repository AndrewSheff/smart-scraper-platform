// Модуль авторизации — логин, регистрация, рефреш токена и прочее
import apiClient from './client';
import type { AuthTokens, User } from './types';

// Залогиниться по email и паролю
export async function login(email: string, password: string): Promise<AuthTokens> {
  const { data } = await apiClient.post<AuthTokens>('/auth/login', { email, password });
  return data;
}

// Зарегистрировать нового пользователя
export async function register(email: string, password: string, name: string): Promise<AuthTokens> {
  const { data } = await apiClient.post<AuthTokens>('/auth/register', { email, password, name });
  return data;
}

// Обновить токен по refresh_token
export async function refresh(refreshToken: string): Promise<AuthTokens> {
  const { data } = await apiClient.post<AuthTokens>('/auth/refresh', { refresh_token: refreshToken });
  return data;
}

// Сменить пароль — нужен текущий и два раза новый
export async function changePassword(
  currentPassword: string,
  newPassword: string,
  confirmPassword: string,
): Promise<void> {
  await apiClient.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
    confirm_password: confirmPassword,
  });
}

// Получить текущего пользователя по токену
export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/auth/me');
  return data;
}
