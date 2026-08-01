// API для настроек уведомлений — телеграм бот и чат
import apiClient from './client';
import type { NotificationSettings } from './types';

// Получить текущие настройки уведомлений
export async function getNotificationSettings(): Promise<NotificationSettings> {
  const { data } = await apiClient.get<NotificationSettings>('/notifications/settings');
  return data;
}

// Сохранить настройки уведомлений
export async function updateNotificationSettings(
  settings: NotificationSettings,
): Promise<NotificationSettings> {
  const { data } = await apiClient.put<NotificationSettings>(
    '/notifications/settings',
    settings,
  );
  return data;
}

// Отправить тестовое уведомление — проверяем, что бот работает
export async function sendTestNotification(): Promise<{ success: boolean; message: string }> {
  const { data } = await apiClient.post<{ success: boolean; message: string }>(
    '/notifications/test',
  );
  return data;
}
