// API для работы с задачами скрапинга — CRUD, запуск, превью
import apiClient from './client';
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  PaginatedResponse,
  PreviewResponse,
} from './types';

// Получить список задач с пагинацией и фильтрами
export async function getTasks(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  is_active?: boolean;
}): Promise<PaginatedResponse<Task>> {
  const { data } = await apiClient.get<PaginatedResponse<Task>>('/tasks', { params });
  return data;
}

// Получить конкретную задачу по id
export async function getTask(id: string): Promise<Task> {
  const { data } = await apiClient.get<Task>(`/tasks/${id}`);
  return data;
}

// Создать новую задачу
export async function createTask(payload: TaskCreate): Promise<Task> {
  const { data } = await apiClient.post<Task>('/tasks', payload);
  return data;
}

// Обновить существующую задачу
export async function updateTask(id: string, payload: TaskUpdate): Promise<Task> {
  const { data } = await apiClient.put<Task>(`/tasks/${id}`, payload);
  return data;
}

// Удалить задачу — прощай навсегда
export async function deleteTask(id: string): Promise<void> {
  await apiClient.delete(`/tasks/${id}`);
}

// Переключить статус задачи (вкл/выкл)
export async function toggleTask(id: string): Promise<Task> {
  const { data } = await apiClient.patch<Task>(`/tasks/${id}/toggle`);
  return data;
}

// Запустить задачу прямо сейчас, не дожидаясь крона
export async function runTaskNow(id: string): Promise<void> {
  await apiClient.post(`/tasks/${id}/run`);
}

// Превью результатов — чтобы проверить селекторы перед сохранением
export async function previewTask(payload: {
  url: string;
  fields: TaskCreate['fields'];
  headers?: Record<string, string>;
  timeout_seconds?: number;
}): Promise<PreviewResponse> {
  const { data } = await apiClient.post<PreviewResponse>('/tasks/preview', payload);
  return data;
}
