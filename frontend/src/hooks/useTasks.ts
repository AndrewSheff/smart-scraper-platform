// Хуки для работы с задачами — используем tanstack query для кеширования и мутаций
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  getTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  toggleTask,
  runTaskNow,
  previewTask,
} from '@/api/tasks';
import type { TaskCreate, TaskUpdate } from '@/api/types';

// Получить список задач
export function useTasks(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  is_active?: boolean;
}) {
  return useQuery({
    queryKey: ['tasks', params],
    queryFn: () => getTasks(params),
  });
}

// Получить одну задачу по id
export function useTask(id: string) {
  return useQuery({
    queryKey: ['tasks', id],
    queryFn: () => getTask(id),
    enabled: !!id,
  });
}

// Создать задачу
export function useCreateTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TaskCreate) => createTask(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Задача создана');
    },
    onError: () => {
      toast.error('Не удалось создать задачу');
    },
  });
}

// Обновить задачу
export function useUpdateTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: TaskUpdate }) =>
      updateTask(id, payload),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', id] });
      toast.success('Задача обновлена');
    },
    onError: () => {
      toast.error('Не удалось обновить задачу');
    },
  });
}

// Удалить задачу
export function useDeleteTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Задача удалена');
    },
    onError: () => {
      toast.error('Не удалось удалить задачу');
    },
  });
}

// Переключить статус задачи
export function useToggleTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => toggleTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Статус задачи изменен');
    },
    onError: () => {
      toast.error('Не удалось изменить статус');
    },
  });
}

// Запустить задачу вручную — прям сейчас
export function useRunTaskNow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => runTaskNow(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['runs'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('Задача запущена');
    },
    onError: () => {
      toast.error('Не удалось запустить задачу');
    },
  });
}

// Превью скрапинга — проверяем что получится
export function usePreviewTask() {
  return useMutation({
    mutationFn: previewTask,
  });
}
