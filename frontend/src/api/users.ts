// API для управления пользователями — только для админов
import apiClient from './client';
import type { User, UserCreate, UserUpdate, PaginatedResponse } from './types';

// Получить список пользователей с пагинацией
export async function getUsers(params?: {
  page?: number;
  per_page?: number;
  search?: string;
}): Promise<PaginatedResponse<User>> {
  const { data } = await apiClient.get<PaginatedResponse<User>>('/users', { params });
  return data;
}

// Создать нового пользователя (админ делает)
export async function createUser(payload: UserCreate): Promise<User> {
  const { data } = await apiClient.post<User>('/users', payload);
  return data;
}

// Обновить данные пользователя
export async function updateUser(id: string, payload: UserUpdate): Promise<User> {
  const { data } = await apiClient.put<User>(`/users/${id}`, payload);
  return data;
}

// Обновить свой профиль
export async function updateProfile(payload: { name?: string }): Promise<User> {
  const { data } = await apiClient.put<User>('/auth/me', payload);
  return data;
}

// Заблокировать/разблокировать пользователя
export async function blockUser(id: string, isActive: boolean): Promise<User> {
  const { data } = await apiClient.patch<User>(`/users/${id}/block`, null, { params: { is_active: isActive } });
  return data;
}
