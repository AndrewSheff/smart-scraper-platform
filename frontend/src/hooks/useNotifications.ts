// Хуки для настроек уведомлений — телеграм и прочее
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  getNotificationSettings,
  updateNotificationSettings,
  sendTestNotification,
} from '@/api/notifications';
import type { NotificationSettings } from '@/api/types';

// Получить текущие настройки
export function useNotificationSettings() {
  return useQuery({
    queryKey: ['notifications', 'settings'],
    queryFn: getNotificationSettings,
  });
}

// Сохранить настройки
export function useUpdateNotificationSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (settings: NotificationSettings) =>
      updateNotificationSettings(settings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      toast.success('Настройки сохранены');
    },
    onError: () => {
      toast.error('Не удалось сохранить настройки');
    },
  });
}

// Отправить тестовое уведомление
export function useSendTestNotification() {
  return useMutation({
    mutationFn: sendTestNotification,
    onSuccess: (result) => {
      if (result.success) {
        toast.success('Тестовое сообщение отправлено!');
      } else {
        toast.error(result.message || 'Не удалось отправить');
      }
    },
    onError: () => {
      toast.error('Ошибка отправки тестового сообщения');
    },
  });
}
