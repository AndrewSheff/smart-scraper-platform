// Хуки для управления пользователями — для админской панели
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { getUsers, createUser, updateUser, updateProfile, blockUser } from '@/api/users';
import type { UserCreate, UserUpdate } from '@/api/types';

// Список пользователей
export function useUsers(params?: {
  page?: number;
  per_page?: number;
  search?: string;
}) {
  return useQuery({
    queryKey: ['users', params],
    queryFn: () => getUsers(params),
  });
}

// Создать пользователя
export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UserCreate) => createUser(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Пользователь создан');
    },
    onError: () => {
      toast.error('Не удалось создать пользователя');
    },
  });
}

// Обновить пользователя
export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UserUpdate }) =>
      updateUser(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Пользователь обновлен');
    },
    onError: () => {
      toast.error('Не удалось обновить пользователя');
    },
  });
}

// Заблокировать/разблокировать пользователя
export function useBlockUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      blockUser(id, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Статус пользователя изменен');
    },
    onError: () => {
      toast.error('Не удалось изменить статус пользователя');
    },
  });
}

// Обновить свой профиль
export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { name?: string }) => updateProfile(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Профиль обновлен');
    },
    onError: () => {
      toast.error('Не удалось обновить профиль');
    },
  });
}
